# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class SeattletimesItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    link = scrapy.Field()
    body = scrapy.Field()
    date = scrapy.Field()
    url = scrapy.Field()
    searchIndex = scrapy.Field()	
    articleID = scrapy.Field()
    category = scrapy.Field()
    authorAffiliation = scrapy.Field()
    author = scrapy.Field()
    commentNum = scrapy.Field()
    commentjsURL = scrapy.Field()
    comData = scrapy.Field()
    pass
