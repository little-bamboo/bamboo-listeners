#!/usr/bin/env python
# encoding: utf-8

from scrapy.spiders import Spider
import scrapy
from scrapy.utils.markup import remove_tags
import xml.etree.ElementTree as ET

import sqlalchemy

import requests

import json
from urlparse import urlparse

import re

import time
from datetime import datetime
import math

from seattletimes.items import SeattletimesArticle

# TODO: Import logging and setup logging for each step in process
# TODO: Log information statement in one line (summarized)
# TODO: Modify FEEDURI global property to include the search term and date parameters used for the crawl request
# TODO: Add comment number extraction (splash?) - stored use for identifying


class SeattleTimesSpider(Spider):
    name = 'seattletimes-auth'
    allowed_domains = ['seattletimes.com']
    start_urls = ['https://secure.seattletimes.com/accountcenter/login']

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

    custom_settings = {"HTTPS_PROXY":"http://brian.schaper:Sounders17!@ec2-54-214-228-124.us-west-2.compute.amazonaws.com:8888",
                       "HTTP_PROXY":"http://brian.schaper:Sounders17!@ec2-54-214-228-124.us-west-2.compute.amazonaws.com:8888"}

    # Call super and initialize external variables
    def __init__(self,
                 startdate='',
                 enddate='',
                 search='*',
                 perpage='200',
                 datapath='',
                 username='briansc@gmail.com',
                 password='thomas7',
                 mysqlauth='../../config/mysqlauth.json'):

        # Call super to initialize the instance
        super(Spider, self).__init__()
        self.startdate = startdate
        if enddate is None:
            self.enddate = (str(datetime.now()).split(" ")[0])
        else:
            self.enddate = enddate

        self.perpage = perpage

        self.searchterm = search.strip()
        self.username = username
        self.password = password

        self.articleCount = 1
        self.filename = "seattletimes" + '_' + self.searchterm + '_' + self.startdate + '-' + self.enddate

        # print("sqlalchemy version: " + str(sqlalchemy.__version__))
        self.app_name = "comments"

        mysql_auth = json.loads(open(mysqlauth, 'r').read())
        self.dbuser = mysql_auth['user']
        self.dbpassword = mysql_auth['password']
        self.database = mysql_auth['database']
        self.dbhost = mysql_auth['host']
        self.dbport = mysql_auth['port']
        self.dbtable_name = "st_articles"

        time.sleep(3)

    # Override parse endpoint into the class that begins the event flow once a response from the start_urls
    def parse(self, response):
        # Push authentication
        return scrapy.FormRequest.from_response(
            response,
            formdata={'username': self.username, 'password': self.password},
            callback=self.auth_rss
        )

    def auth_rss(self, response):
        """Code to obtain latest articles from RSS feed
        """
        engine = sqlalchemy.create_engine(
            'mysql+mysqlconnector://' + self.dbuser + ':' + self.dbpassword + '@' + self.dbhost + ':' + self.dbport +
            '/' + self.database)
        conn = engine.connect()

        # Pull articles from previous 2 days to filter out URLs we've already collected
        articleurl_list = conn.execute("SELECT articleURL FROM " + self.dbtable_name + " WHERE date > NOW() - "
                                                                                       "INTERVAL 2 DAY").fetchall()
        url_list = [url[0] for url in articleurl_list]

        # Build response object for rss feed using requests and assign content
        rss_response = requests.get('https://www.seattletimes.com/feed/')
        rss_text = rss_response.content

        # Use ElementTree to easily parse XML feed content and convert all links to list
        try:
            root = ET.fromstring(rss_text)
            root_links = root.findall('.//link')
            raw_links = [link.text for link in root_links]
            # Remove first link (it is just the standar www.seattletimes.com site)
            raw_links.pop(0)
            clean_links = [link.split('?')[0] for link in raw_links]
            new_urls = list(set(clean_links) - set(url_list))

            for rss_url in new_urls:
                yield scrapy.Request(url=rss_url, headers=self.headers, callback=self.process_article)

        except Exception, e:
            print "Exception: {0}".format(e.message)

    # Obtain the response from the login and yield the search request
    def auth_login(self, response):

        page_num = 1

        # Call original url to obtain total number of articles only
        count_url = 'http://vendorapi.seattletimes.com/st/proxy-api/v1.0/st_search/search?' \
                    'query=' + self.searchterm + \
                    '&startdate=' + self.startdate + \
                    '&enddate=' + self.enddate + \
                    '&sortby=mostrecent&page=' + str(page_num) + \
                    '&perpage=' + str(self.perpage)

        sample = requests.get(count_url)
        init_req = json.loads(sample.content)

        # Standard division using int values loses precision.  Converting values to float and round with ceiling
        page_total = int(math.ceil(float(init_req['total']) / float(self.perpage)))
        print"Search API Page Total: {0}".format(page_total)

        while page_num <= page_total:
            time.sleep(2)
            print"Search API Page Num: {0}".format(page_num)
            # Example: http://vendorapi.seattletimes.com/st/proxy-api/v1.0/st_search/search? \
            # query=the&startdate=2017-01-01&enddate=2017-10-01&sortby=mostrecent&page=1&perpage=200

            new_url = 'http://vendorapi.seattletimes.com/st/proxy-api/v1.0/st_search/search?' \
                    'query=' + self.searchterm + \
                    '&startdate=' + self.startdate + \
                    '&enddate=' + self.enddate + \
                    '&sortby=mostrecent&page=' + str(page_num) + \
                    '&perpage=' + str(self.perpage)

            # Increment page_num as this is the second call
            page_num += 1

            yield scrapy.Request(url=new_url, headers=self.headers, callback=self.obtain_articles_from_search)

    def obtain_articles_from_search(self, response):
        urls = []
        jsonresponse = json.loads(response.body_as_unicode())

        for article in jsonresponse['hits']:
            if str(article["fields"]["url"]):
                urls.append(str(article["fields"]["url"].encode('utf-8').strip()))

        for u in urls:
            if u is not None:
                yield scrapy.Request(url=u, headers=self.headers, callback=self.process_article)

            else:
                print "empty url, moving on..."

    def process_article(self, response):
        url = str(response.url)

        article = SeattletimesArticle()

        search_index = str(self.filename) + "_" + str(self.articleCount)

        if search_index:
            article['searchIndex'] = search_index
        else:
            article['searchIndex'] = search_index

        siteid = "window.SEATIMESCO.comments.info.siteID"
        post_id_base64 = "window.SEATIMESCO.comments.info.postIDBase64"
        comments_enabled = "window.SEATIMESCO.comments.info.enabled"

        script_header_settings = response.xpath('//script[contains(., "window.SEATIMESCO.comments.info.siteID")]').extract()[0].encode('utf-8').strip()

        # Collect the necessary settings to build the xhr response for the comments
        comment_settings = []
        for line in script_header_settings.split("\n"):
            line = re.sub(r"\s+", "", line, flags=re.UNICODE)
            if (siteid in line) or (post_id_base64 in line) or (comments_enabled in line):
                comment_settings += [line]

        settings_dict = dict(line.split("=", 1) for line in comment_settings)

        # Example URL
        # http://data.livefyre.com/bs3/v3.1/seattletimes.fyre.co/316317/MTAyNjk2NTM=/init
        # Obtain the initial comment stream

        for key, value in settings_dict.iteritems():
            value = re.sub(self.full_pattern, '', value)
            settings_dict[key] = value

        if settings_dict[siteid]:
            article["siteid"] = settings_dict[siteid]
            article["post_id_base64"] = settings_dict[post_id_base64]

        if settings_dict['window.SEATIMESCO.comments.info.enabled'] == 'true':
            commentjs_url = 'http://data.livefyre.com/bs3/v3.1/seattletimes.fyre.co/' + settings_dict[siteid] + '/' + settings_dict[post_id_base64] + '=/init'
            article['commentjsURL'] = commentjs_url
            # print article['commentjsURL']
        else:
            article['commentjsURL'] = ''

        articleid = response.xpath('//*[contains(@id, "post-")]/@id')

        if articleid:
            articleid = articleid.extract()
            articleid = articleid[0].encode('utf-8').strip()
            article['articleID'] = articleid
        else:
            article['articleID'] = ''

        article_header = response.xpath('//*[contains(@class, "article-header")]')

        if article_header:
            article['title'] = article_header.xpath('h1/text()').extract()[0].encode('utf-8').strip()
            article['date'] = article_header.xpath('//time/@datetime').extract()[0].encode('utf-8').strip()
        else:
            article['title'] = ''
            article['date'] = ''

        if url:
            article['articleURL'] = url
        else:
            article['articleURL'] = ''

        author = response.xpath('//*[contains(@class, "p-author")]')
        if author:
            article['author'] = remove_tags(author[0].extract()).encode('utf-8')
        else:
            article['author'] = ''

        # Parse URL and extract text between / + / for category designation
        o = urlparse(response.url)

        # take the urlparse'd object and get the attribute 'path', then break that up into pieces,
        # use the first parsed object for the category value
        article_category = o.path.split("/")[1].encode('utf-8').strip()
        if article_category:
            article['category'] = article_category
        else:
            article['category'] = ''


        article_content = response.xpath('//*[contains(@id, "article-content")]')
        if article_content:
            for sel in article_content:
                paragraphs = sel.xpath('//p').extract()
                stripped = []
                for index, para in enumerate(paragraphs):
                    stripped += str(remove_tags(para).encode('unicode_escape')).strip()
                # rejoin list of strings into one
                article['body'] = ''.join(stripped)
        else:
            article['body'] = ''

        self.articleCount += 1

        return article
