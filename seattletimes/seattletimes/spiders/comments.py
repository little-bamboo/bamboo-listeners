from scrapy.spiders import Spider
import scrapy
from scrapy.http import Request

import json
import re

import sqlalchemy
from sqlalchemy import create_engine

from seattletimes.items import SeattletimesComment

# TODO: Check if url in response body is init, head, or page number


class CommentSpider(Spider):

    name = 'comments'
    allowed_domains = ['seattletimes.com', 'data.livefyre.com']
    start_urls = ['https://secure.seattletimes.com/accountcenter/login']

    full_pattern = re.compile('[^a-zA-Z0-9\\\/]|_')
    custom_settings = {
        'FEED_URI': '../../../../data/seattletimes/seattletimes-2016-05-01-comments.json'
    }
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
         Chrome/48.0.2564.116 Safari/537.36',
        'Accept-Charset': 'utf-8'
    }

    # Call super and initialize external variables
    def __init__(self, date='', search='', datapath=''):
        # Call super to initialize the instance
        super(Spider, self).__init__()

        print("sqlalchemy version: " + str(sqlalchemy.__version__))
        self.app_name = "comments"

        self.filename = "seattletimes-comments"
        self.table_name = "bs_articlesList"

    # Override parse endpoint into the class that begins the event flow once a response from the start_urls
    def parse(self, response):
        # Get table column for articleid and commentjsurl

        print ("reading articles table for comment URL list")
        engine = create_engine('mysql+mysqlconnector://dbBambooDev:B@mboo99@bambooiq.ddns.net:3306/dbBambooDev')
        conn = engine.connect()

        comment_url_article_list = conn.execute(
            "SELECT articleID,commentjsURL FROM " + self.table_name + " LIMIT 100").fetchall()

        counter = 0
        for item in comment_url_article_list:

            articleid = item[0]
            comment_url = item[1]

            if comment_url:
                counter += 1
                print(str(counter) + ' ' + comment_url)
                # TODO: Pass articleid and counter variables in meta?
                yield scrapy.Request(url=comment_url, callback=self.get_comments, meta={'articleid': articleid})

    def get_comments(self, response):
        print("get_comments - " + str(response.url))
        com_dict = {}
        com_list = []
        comment_item = SeattletimesComment()
        comment_json = json.loads(response.body_as_unicode())
        article_id = response.meta['articleid']

        comment_header = comment_json['headDocument']['content']
        article_url_id = comment_json['collectionSettings']['bootstrapUrl']

        # Extract article meta id
        parsed_url = article_url_id.split('/')
        post_id_base64 = str(parsed_url[3])

        com_pages = comment_json['collectionSettings']['archiveInfo']['nPages']
        com_page_info = comment_json['collectionSettings']['archiveInfo']['pageInfo']

        if com_page_info and com_pages:
            for val in range(0, com_pages):
                page_number = str(val)
                print("Page #: " + str(page_number))
                json_n_url = 'http://data.livefyre.com/bs3/v3.1/seattletimes.fyre.co/316317/' + post_id_base64 + '/' + page_number + '.json'

                return Request(json_n_url, self.parse_add_comments,
                               meta={'comment_item': comment_item, 'article_id': article_id, 'page_num': com_pages})

        else:
            if comment_header:
                comment_item['commentStream'] = comment_header
                comment_item['articleID'] = article_id
                return comment_item

    def parse_add_comments(self, response):
        print('parse additional comments')
        article_id = response.meta['article_id']
        comment_add_item = SeattletimesComment()
        add_comment_json = json.loads(response.body_as_unicode())
        comment_content = add_comment_json['content']

        if comment_content:
            comment_add_item['commentStream'] = comment_content
            comment_add_item['articleID'] = article_id
            return comment_add_item
