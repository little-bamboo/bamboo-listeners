# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class CruisecriticItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    link = scrapy.Field()
    body = scrapy.Field()
    date = scrapy.Field()
    url = scrapy.Field()
    user = scrapy.Field()
    articleId = scrapy.Field()
    commentId = scrapy.Field()
    pass
