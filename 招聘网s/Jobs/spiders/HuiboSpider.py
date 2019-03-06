# -*- coding: utf-8 -*-
import scrapy


class HuibospiderSpider(scrapy.Spider):
    name = 'HuiboSpider'
    allowed_domains = ['www.huibo.com']
    start_urls = ['http://www.huibo.com/']

    def parse(self, response):
        pass
