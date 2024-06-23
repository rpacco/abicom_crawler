from typing import Iterable
import scrapy
from datetime import datetime
import pandas as pd
from abicom.items import PpiItem


class PpiCrawlerSpider(scrapy.Spider):
    name = "ppi_crawler"
    allowed_domains = ["abicom.com.br"]
    # start_urls = ["https://abicom.com.br/categoria/ppi/page/1"]
    today = datetime.today().date()

    date_range = pd.date_range(end=today, periods=520, freq='B').strftime('%d-%m-%Y')

    url = 'https://abicom.com.br/ppi/ppi-{}/'

    def start_requests(self) -> Iterable[scrapy.Request]:
        for date in self.date_range:
            yield scrapy.Request(self.url.format(date), meta={'date': date})

    def parse(self, response):
        date = response.meta['date']
        content = response.css('div.page-content.blog-content strong::text, div.page-content.blog-content u::text').getall()

        ppi_item = PpiItem()
        ppi_item['date'] = date
        ppi_item['content'] = content

        yield ppi_item
