from src.gen_viz import *
from src.tweet import *
from datetime import datetime
import subprocess
import sys

today = datetime.today().date()

try:
    subprocess.run(['scrapy', 'runspider', 'abicom/spiders/ppi_crawler.py', '-O', f'data/{today}_output.json'])
except subprocess.CalledProcessError as e:
    print(f"Error running Scrapy spider: {e}")
    sys.exit(1)

options = ['diesel_brl', 'gasolina_brl']

for comb in options:
    df = wrangle(comb)
    gen_graph(df, comb)
    text = gen_text(df, comb)
    # print(text)
    create_tweet(text, f"data/{today}_{comb}.jpg")