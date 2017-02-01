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
        'FEED_URI': '../../../data/seattletimes/seattletimes-2016-05-01-comments.json'
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
        self.table_name = "bs_articleList"

    # Override parse endpoint into the class that begins the event flow once a response from the start_urls
    def parse(self, response):
        # Get table column for articleid and commentjsurl

        print ("reading articles table for comment URL list")
        engine = create_engine('mysql+mysqlconnector://dbBambooDev:B@mboo99@bambooiq.ddns.net:3306/dbBambooDev')
        conn = engine.connect()

        comment_url_article_list = conn.execute(
            "SELECT articleID,commentjsURL FROM " + self.table_name + " LIMIT 1000").fetchall()

        counter = 0
        for item in comment_url_article_list:

            articleid = item[0]
            comment_url = item[1]

            if comment_url:
                counter += 1
                print(str(counter) + ' ' + comment_url)
                yield scrapy.Request(url=comment_url, callback=self.get_comment_pages, meta={'articleid': articleid})

    def get_comment_pages(self, response):

        # Create a dictionary to carry any comments found in init
        comment_items = []
        comment_item = {}
        comment_json = json.loads(response.body_as_unicode())

        # Set meta for passing to next comment string
        # Stored in the articleid
        article_id = response.meta['articleid']

        comment_head_document = comment_json['headDocument']['content']
        article_url_id = comment_json['collectionSettings']['bootstrapUrl']


        for com in comment_head_document:
            try:
                comment_item['bodyHtml'] = com['bodyHtml']
                comment_item['articleID'] = article_id
                comment_items.append(comment_item)
            except KeyError, e:
                #print('keyerror: ' + str(e))
                pass

        # Extract article meta id
        parsed_url = article_url_id.split('/')
        post_id_base64 = str(parsed_url[3])

        com_pages = comment_json['collectionSettings']['archiveInfo']['nPages']
        com_page_info = comment_json['collectionSettings']['archiveInfo']['pageInfo']

        if com_page_info and com_pages:
            # We can assume the page has comments, make sure they get passed

            # Build the list of URLs to parse  We will use the init to build the list
            # Init will also be passed as this first step doesn't return an item
            json_n_url_list = []
            json_n_url_list.append(response.url)

            # Build the iterator using the number supplied in the json feed
            for val in range(com_pages):
                page_number = str(val)
                print("Page #: " + str(page_number))

                # Now use the post id and page num to build the URL that will be stored in the url list
                json_n_url = 'http://data.livefyre.com/bs3/v3.1/seattletimes.fyre.co/316317/' + post_id_base64 + '/' + page_number + '.json'
                json_n_url_list.append(json_n_url)

            # Now yield through the list of URLs
            for n_url in json_n_url_list:
                yield scrapy.Request(url=n_url, callback=self.parse_comment_tree, meta={'comment_item': comment_items, 'article_id': article_id})

        else:
            if comment_items:
                for comment_dict_item in comment_items:
                    yield comment_dict_item

    def parse_comment_tree(self, response):
        print('parse additional comments')

        # Create comment item and comment list to hold the individual comments
        comment_item = SeattletimesComment()
        comment_list = []

        article_id = response.meta['article_id']
        comment_json = json.loads(response.body_as_unicode())

        # Build the comment dict and test if its available
        comment_dict_list = comment_json['content']

        if comment_dict_list:
            for item in comment_dict_list:
                try:
                    comment_item['bodyHtml'] = item['content']['bodyHtml']
                    comment_item['id'] = item['content']['id']
                    comment_item['articleID'] = article_id
                    comment_item['commentAuthor'] = item['content']['authorId']
                    comment_item['parentID'] = item['content']['parentId']
                    comment_item['createdAt'] = item['content']['createdAt']
                    #print comment_item
                    yield comment_item
                except KeyError, e:
                    #print("keyerror: ", e)
                    pass
