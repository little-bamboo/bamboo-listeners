# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SeattletimesArticle(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    body = scrapy.Field()
    date = scrapy.Field()
    articleURL = scrapy.Field()
    searchIndex = scrapy.Field()
    articleID = scrapy.Field()
    category = scrapy.Field()
    authorAffiliation = scrapy.Field()
    author = scrapy.Field()
    commentjsURL = scrapy.Field()
    siteid = scrapy.Field()
    post_id_base64 = scrapy.Field()
    pass


class SeattletimesProfile(scrapy.Item):
    commentCount = scrapy.Field()
    commentHistory = scrapy.Field()
    about = scrapy.Field()
    profileCreated = scrapy.Field()
    profileID = scrapy.Field()
    displayName = scrapy.Field()
    location = scrapy.Field()
    commentLikes = scrapy.Field()
    profileUrl = scrapy.Field()
    pass


class SeattletimesComment(scrapy.Item):
    bodyHtml = scrapy.Field()
    profileID = scrapy.Field()
    parentID = scrapy.Field()
    articleID = scrapy.Field()
    id = scrapy.Field()
    createdDate = scrapy.Field()
    displayName = scrapy.Field()
    profileURL = scrapy.Field()
    likedBy = scrapy.Field()
    pass
