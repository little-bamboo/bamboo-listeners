# -*- coding: utf-8 -*-
import scrapy
from nytimesarticle import articleAPI


class NytimesapiSpider(scrapy.Spider):
    name = "nytimes"
    allowed_domains = ["nytimes.com"]
    start_urls = ['http://nytimes.com/']

    api = articleAPI("038ee5e586674d6aa8c9102e6177a6ca")

    articles = api.search(q='Trump', fq={'headline': 'Trump', 'source': ['Reuters', 'AP', 'The New York Times']}, begin_date=20170101, facet_field=['source', 'day_of_week'], facet_filter=True)

    article_list = []
    article_dict = {}
    for key, value in articles.iteritems():
        if key is 'response':
            article_dict[key] = value
        article_list.append(article_dict)


    def parse(self, response):
        print response
        pass
