import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from datetime import datetime
import json

# Formatting y-axis labels
def currency_formatter(x, pos):
    return f'{x:.2f}'  # Format numbers as currency

def wrangle(combustivel: str, date: str):
    data_path = f'data/{date}_output.json'
    
    with open(data_path, 'r') as f:
        data = json.load(f)

    df = pd.json_normalize(data, sep='_', record_prefix=False)
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    df.sort_values('date', inplace=True)
    df.set_index('date', inplace=True, drop=True)
    df.columns = [x.removeprefix('content_') for x in df.columns]
    df['year_ma'] = round(df[combustivel].rolling(252).mean(), 2)
    df.index = pd.to_datetime(df.index, dayfirst=True)
    df.sort_index(inplace=True)
    df = df[[combustivel, 'year_ma']].dropna()
    
    return df

def gen_graph(df, combustivel):
    label_comb = combustivel.split('_')[0].upper()
    nlargest = df[f'{combustivel}'].nlargest(5)
    largest_filtered_indices = []
    largest_previous_indices = []

    # Iterate over the sorted Series for nlargest
    for index in nlargest.index:
        if not largest_previous_indices or all((index - prev_index).days > 30 for prev_index in largest_previous_indices):
            largest_filtered_indices.append(index)
            largest_previous_indices.append(index)
    nlargest = nlargest.loc[largest_filtered_indices]

    nsmallest = df[f'{combustivel}'].nsmallest(5)
    smallest_filtered_indices = []
    smallest_previous_indices = []

    # Iterate over the sorted Series for nsmallest
    for index in nsmallest.index:
        if not smallest_previous_indices or all((index - prev_index).days > 30 for prev_index in smallest_previous_indices):
            smallest_filtered_indices.append(index)
            smallest_previous_indices.append(index)
    nsmallest = nsmallest.loc[smallest_filtered_indices]

    today = datetime.today().date()
    plt.figure(figsize=(10, 5))

    # Plot the 'combustivel' column
    ax = sns.lineplot(data=df, y=f'{combustivel}', x=df.index, color='blue', linewidth=2, label=f'{label_comb}')
    sns.lineplot(data=df, y='year_ma', x=df.index, color='orange', linewidth=1, label='Média móvel 252 dias')

    # Formatting x-axis labels to 'Month-Year'
    date_format = mdates.DateFormatter('%b-%Y')
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=90)
    plt.xlabel('')
    plt.hlines(y=0, xmin=df.index[0], xmax=df.index[-1], linestyles='dashed', alpha=0.2)

    ax.set_title(f'Defasagem média {label_comb} nos principais polos Petrobrás\n (R$/L)', weight='bold')
    plt.figtext(0.02, 0.95, 'Fonte: Abicom', fontsize=8, color='gray')

    # Setting y-axis label and formatting
    ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))
    plt.ylabel('')

    # Remove top, right, and left spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Annotate the last value of 'combustivel'
    ax.annotate(f"{df[combustivel].values[-1]:.2f}", 
                (df.index[-1], df[combustivel].values[-1]), 
                textcoords="offset points", xytext=(5, 0), ha='left', fontsize=10, color='black', weight='bold')
    # Annotate the last value of 'year_ma'
    ax.annotate(f"{df['year_ma'].values[-1]:.2f}", 
                (df.index[-1], df['year_ma'].values[-1]), 
                textcoords="offset points", xytext=(5, 0), ha='left', fontsize=10, color='green' if df['year_ma'].values[-1] >= 0 else 'red', weight='bold')

    # Annotate the smallest values
    for value, date in zip(nsmallest.values, nsmallest.index):
        ax.annotate(f'{value:.2f}', (date, value), textcoords="offset points", xytext=(0, -10), ha='center', fontsize=10, color='red', weight='bold')

    # Annotate the largest values
    for value, date in zip(nlargest.values, nlargest.index):
        ax.annotate(f'{value:.2f}', (date, value), textcoords="offset points", xytext=(0, 5), ha='center', fontsize=10, color='green', weight='bold')

    # Remove the tick marks for both horizontal and vertical axes
    plt.tick_params(axis='both', length=0, width=0)

    # Change the color of the bottom spine
    ax.spines['bottom'].set_color('#CCCCCC')

    # Displaying the plot
    plt.tight_layout()
    plt.legend()
    plt.savefig(f'data/{today}_{combustivel}.jpg')

def gen_text(df, combustivel):
    today = datetime.today()
    # Define the Unicode characters for the red and green circles
    red_circle = "\U0001F534"
    green_circle = "\U0001F7E2"

    # Check the condition and create the text
    text = (
        f'{red_circle if df[combustivel].values[-1] < 0 else green_circle} Defasagem média {combustivel.split("_")[0].upper()} em {today.strftime("%d/%m/%Y")}: {df[combustivel].values[-1]:.2f} R$/L.\n'
        f'Média defasagem últimos 252 dias: {df["year_ma"].values[-1]:.2f} R$/L.\n'
        'Fonte: ABICOM'
      )

    return text