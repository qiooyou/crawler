# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BjzphItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()  # 标题
    url = scrapy.Field()  # 链接
    start_time = scrapy.Field()  # 开始时间
    end_time = scrapy.Field()  # 结束时间
    city = scrapy.Field()  # 招聘城市
    address = scrapy.Field()  # 详细地址
    content = scrapy.Field()  # 内容

