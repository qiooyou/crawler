# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaiduItem(scrapy.Item):
    # define the fields for your item here like:
    one=scrapy.Field()
    rank = scrapy.Field()
    name = scrapy.Field()
    data=scrapy.Field()
    index_str = scrapy.Field()
    actived=scrapy.Field()

