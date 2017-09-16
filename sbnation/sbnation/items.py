# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SBNationArticle(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    body = scrapy.Field()
    created_on = scrapy.Field()
    url = scrapy.Field()
    search_index = scrapy.Field()
    article_id = scrapy.Field()
    categories = scrapy.Field()
    author = scrapy.Field()
    comment_num = scrapy.Field()
    recommended_num = scrapy.Field()
    pass


class SBNationComment(scrapy.Item):
    # define list of fields for sbnation comment stream
    id = scrapy.Field()
    parent_id = scrapy.Field()
    user_id = scrapy.Field()
    spam_flags = scrapy.Field()
    troll_flags = scrapy.Field()
    inappropriate_flags = scrapy.Field()
    recommended_flags = scrapy.Field()
    created_timestamp = scrapy.Field()
    created_on = scrapy.Field()
    body = scrapy.Field()
    username = scrapy.Field()
    title = scrapy.Field()
    signature = scrapy.Field()
    article_id = scrapy.Field()


class SBNationUser(scrapy.Item):
    id = scrapy.Field()
    username = scrapy.Field()
    created_on = scrapy.Field()
    profile_url = scrapy.Field()
    image_url = scrapy.Field()
    comment_num = scrapy.Field()
    post_num = scrapy.Field()
    fan_of = scrapy.Field()
    blog_membership = scrapy.Field()