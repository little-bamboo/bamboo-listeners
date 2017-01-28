# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SeattletimesArticle(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    link = scrapy.Field()
    body = scrapy.Field()
    date = scrapy.Field()
    articleURL = scrapy.Field()
    searchIndex = scrapy.Field()
    articleID = scrapy.Field()
    category = scrapy.Field()
    authorAffiliation = scrapy.Field()
    author = scrapy.Field()
    commentjsURL = scrapy.Field()
    pass


class SeattletimesProfile(scrapy.Item):
    displayname = scrapy.Field()
    datejoined = scrapy.Field()
    location = scrapy.Field()
    about = scrapy.Field()

    pass


class SeattletimesComment(scrapy.Item):
    commentNum = scrapy.Field()
    commentStream = scrapy.Field()
    commentAuthor = scrapy.Field()
    commentAuthorURL = scrapy.Field()

    pass
