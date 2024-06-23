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

df = wrangle('diesel_brl')
gen_graph(df, 'diesel_brl')
text = gen_text(df, 'diesel_brl')
# print(text)
create_tweet(text, f"data/{today}_diesel_brl.jpg")