# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JobsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    job_name=scrapy.Field()
    salary=scrapy.Field()
    gs_name=scrapy.Field()
    site=scrapy.Field()
    work_yaoqi=scrapy.Field()
    num_pe=scrapy.Field()
    end_data=scrapy.Field()
    url=scrapy.Field()