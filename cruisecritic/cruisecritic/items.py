# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CruisecriticProfile(scrapy.Item):
    # define the fields for your item here like:
    user_id = scrapy.Field()
    name = scrapy.Field()
    join_date = scrapy.Field()
    location = scrapy.Field()
    post_count = scrapy.Field()
    last_activity = scrapy.Field()
    favorite_cruise_lines = scrapy.Field()
    friends = scrapy.Field()
    post_frequency = scrapy.Field()
    pass


class CruisecriticPost(scrapy.Item):
    # define the fields for each post item
    thread_id = scrapy.Field()
    thread_title = scrapy.Field()
    post_id = scrapy.Field()
    user_id = scrapy.Field()
    post_date = scrapy.Field()
    post_body = scrapy.Field()
    post_url = scrapy.Field()
    forum_name = scrapy.Field()
    post_title = scrapy.Field()
