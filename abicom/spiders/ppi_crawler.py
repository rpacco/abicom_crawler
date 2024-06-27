from typing import Iterable
import scrapy
from datetime import datetime
import pandas as pd
from abicom.items import PpiItem

class PpiCrawlerSpider(scrapy.Spider):
    name = "ppi_crawler"
    allowed_domains = ["abicom.com.br"]
    start_urls = ["https://abicom.com.br/categoria/ppi/page/1"]
    today = datetime.today().date()

    def start_requests(self) -> Iterable[scrapy.Request]:
        url_date = 'https://abicom.com.br/categoria/ppi/'
        yield scrapy.Request(url_date, callback=self.check_date)

    def check_date(self, response):
        last_date_text = response.css('div.card-date::text').get()
        last_date = pd.to_datetime(last_date_text, dayfirst=True).date()

        if last_date == self.today:
            self.log("Latest date matches today's date, continuing the script.")
            date_range = pd.date_range(end=self.today, periods=520, freq='B').strftime('%d-%m-%Y')
            url = 'https://abicom.com.br/ppi/ppi-{}/'

            for date in date_range:
                yield scrapy.Request(url.format(date), meta={'date': date}, callback=self.parse)
        else:
            self.log("Latest date does not match today's date, stopping the spider.")
            return

    def parse(self, response):
        date = response.meta['date']
        content = response.css('div.page-content.blog-content strong::text, div.page-content.blog-content u::text').getall()

        ppi_item = PpiItem()
        ppi_item['date'] = date
        ppi_item['content'] = content

        yield ppi_item
