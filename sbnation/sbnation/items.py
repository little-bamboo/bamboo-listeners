# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FieldGullsItem(scrapy.Item):
    # define the fields for your item here like:
    aTitle = scrapy.Field()
    aLink = scrapy.Field()
    aBody = scrapy.Field()
    aDate = scrapy.Field()
    aUrl = scrapy.Field()
    searchIndex = scrapy.Field()
    articleID = scrapy.Field()
    category = scrapy.Field()
    authorAffiliation = scrapy.Field()
    aAuthor = scrapy.Field()
    commentNum = scrapy.Field()
    commentjsURL = scrapy.Field()
    recommendedNum = scrapy.Field()
    comData = scrapy.Field()
    pass
