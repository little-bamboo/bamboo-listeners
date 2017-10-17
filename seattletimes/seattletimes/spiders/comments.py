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

    custom_settings = {'DOWNLOAD_DELAY': '0.1'}

    full_pattern = re.compile('[^a-zA-Z0-9\\\/]|_')

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
    def __init__(self, mysqlauth='../../config/mysqlauth.json'):
        # Call super to initialize the instance
        super(Spider, self).__init__()

        self.app_name = "comments"

        mysql_auth = json.loads(open(mysqlauth, 'r').read())
        self.user = mysql_auth['user']
        self.password = mysql_auth['password']
        self.database = mysql_auth['database']
        self.host = mysql_auth['host']
        self.port = mysql_auth['port']
        self.table_name = "st_articles"

    # Override parse entrypoint into the class that begins the event flow once a response from the start_urls
    def parse(self, response):
        # Get table column for articleid and commentjsurl

        print ("reading articles table for comment URL list")
        engine = create_engine('mysql+mysqlconnector://' +
                               self.user+':' +
                               self.password+'@' +
                               self.host+':' +
                               self.port+'/' +
                               self.database)
        conn = engine.connect()

        # Add 'LIMIT 200' to query for testing
        comment_url_article_list = conn.execute(
            "SELECT articleID,commentjsURL FROM " + self.table_name + "  WHERE date > NOW() - INTERVAL 7 DAY AND "
                                                                      "commentjsURL <> '' ORDER BY `date` DESC "
                                                                      "").fetchall()

        comment_list_count = len(comment_url_article_list)
        print comment_list_count

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
        comment_json = json.loads(response.body_as_unicode())

        # Set meta for passing to next comment string
        # Stored in the articleid
        article_id = response.meta['articleid']

        com_page_info = comment_json['collectionSettings']['archiveInfo']['pageInfo']

        # If there are additional pages of comments, make sure they get passed
        base_url = 'http://data.livefyre.com/bs3/v3.1'
        for k, v in com_page_info.iteritems():
            com_url = base_url + v['url']
            print com_url
            yield scrapy.Request(url=com_url, callback=self.parse_comment_tree, meta={'article_id': article_id})

    # TODO: Convert parse tree to abstracted method for comment dict list
    # The same comment dict list parser is ran in two different methods
    def parse_comment_tree(self, response):
        print('parse additional comments')

        article_id = response.meta['article_id']
        comment_json = json.loads(response.body_as_unicode())

        # Build the comment dict and test if its available
        comment_dict_list = comment_json['content']
        profile_dict_list = comment_json['authors']

        if comment_dict_list:
            for item in comment_dict_list:
                try:
                    comment_item = SeattletimesComment()
                    comment_item['bodyHtml'] = item['content']['bodyHtml']
                    comment_item['id'] = item['content']['id']
                    comment_item['articleID'] = article_id
                    comment_item['profileID'] = item['content']['authorId']
                    comment_item['parentID'] = item['content']['parentId']
                    comment_item['createdDate'] = item['content']['createdAt']
                    comment_item['displayName'] = profile_dict_list[item['content']['authorId']]['displayName']
                    comment_item['profileURL'] = profile_dict_list[item['content']['authorId']]['profileUrl']
                    yield comment_item
                except KeyError, e:
                    print("Keyerror: ", e)
                    pass
