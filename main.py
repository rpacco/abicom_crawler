from src.gen_viz import *
from src.tweet import *
from datetime import datetime, timedelta
import subprocess
import sys
import os


# Get the current working directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path for the output files
data_dir = os.path.join(current_dir, 'data')

# Create the output directory if it doesn't exist
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

today = datetime.today().date()

try:
    subprocess.run([
        'scrapy', 
        'runspider', 
        'abicom/spiders/ppi_crawler.py', 
        '-O', os.path.join(data_dir, f'{today}_output.json')
        ])
except subprocess.CalledProcessError as e:
    print(f"Error running Scrapy spider: {e}")
    sys.exit(1)

options = ['diesel_brl', 'gasolina_brl']

for comb in options:
    df = wrangle(comb, today, data_dir)
    gen_graph(df, comb, data_dir)
    text = gen_text(df, comb)
    # create_tweet(text, f"data/{today}_{comb}.jpg")