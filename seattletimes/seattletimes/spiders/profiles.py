from scrapy.spiders import Spider
import scrapy

import urllib

import time

import json
import re

import sqlalchemy
from sqlalchemy import create_engine

from seattletimes.items import SeattletimesProfile

##
# Sample profile URL - capture name, location, about, liked_count, comment_count, date_joined
# http://www.seattletimes.com/profile/hometown206/
# Sample API return call
# https://secure.seattletimes.com/accountcenter/profile.js?method=ajax&displayname=flyingking

class ProfilesSpider(Spider):
    name = 'profiles'
    allowed_domains = ['seattletimes.com', 'data.livefyre.com']
    start_urls = ['http://seattletimes.com/']

    base_profile_url = 'https://secure.seattletimes.com/accountcenter/profile.js?method=ajax&displayname='

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
    def __init__(self, date='', search='', datapath='', mysqlauth='../../config/mysqlauth.json'):
        # Call super to initialize the instance
        super(Spider, self).__init__()

        print("sqlalchemy version: " + str(sqlalchemy.__version__))
        self.app_name = "profiles"
        mysql_auth = json.loads(open(mysqlauth, 'r').read())
        self.user = mysql_auth['user']
        self.password = mysql_auth['password']
        self.database = mysql_auth['database']
        self.host = mysql_auth['host']
        self.port = mysql_auth['port']
        self.table_name = "comment_list"

    # Override parse entrypoint into the class that begins the event flow once a response from the start_urls
    def parse(self, response):
        # Get list of profileURLs from comment db

        print ("reading articles table for comment URL list")
        engine = create_engine('mysql+mysqlconnector://'+self.user+':'+self.password+'@'+self.host+':'+self.port+'/'+self.database)
        # engine = create_engine('mysql+mysqlconnector://briansc:BigBamboo99@10.0.1.10:3306/django')


        conn = engine.connect()

        # Add 'LIMIT 200' to query for testing
        # TODO:  Incorporate command line variables for sql date, sort, where articleid=xyz
        display_name_list = conn.execute("SELECT DISTINCT displayName, profileID, profileURL FROM " + self.table_name + "").fetchall()

        counter = 0
        for item in display_name_list:

            display_name = item[0]
            profile_id = item[1]
            profile_url = item[2]

            if display_name:
                counter += 1
                print(str(counter) + ' ' + display_name)

                # Convert string to unicode and append to base URL

                unicode_display_name = unicode(display_name)
                profile_url_unicode = self.base_profile_url+unicode_display_name
                time.sleep(0.1)
                yield scrapy.Request(url=profile_url_unicode, callback=self.get_profile_page, meta={'profileID': profile_id})

    def get_profile_page(self, response):
        # obtain profile information from profile page
        data = response.body_as_unicode().replace('\\n', ' ')
        profile_id = response.meta['profileID']

        profile_item = SeattletimesProfile()

        json_data = json.loads(data)

        about = ''
        comment_count = 0;
        profile_created = ''
        display_name = ''
        location = ''
        comment_likes = 0

        try:

            comment_count = json_data['commentCount']
            about = json_data['profiledata']['about']
            profile_created = json_data['profiledata']['datecreated']
            display_name = json_data['profiledata']['displayname']
            location = json_data['profiledata']['location']
            comment_likes = json_data['receivedLikes']

        except KeyError, err:
            print err

        if comment_count:
            profile_item['commentCount'] = comment_count
        else:
            profile_item['commentCount'] = ''

        if about:
            profile_item['about'] = about
        else:
            profile_item['about'] = ''

        if profile_created:
            profile_item['profileCreated'] = profile_created
        else:
            profile_item['profileCreated'] = ''

        if display_name:
            profile_item['displayName'] = display_name
            profile_item['profileUrl'] = 'www.seattletimes.com/profile/' + urllib.quote(display_name)
        else:
            profile_item['displayName'] = ''
            profile_item['profileUrl'] = ''

        if location:
            profile_item['location'] = location
        else:
            profile_item['location'] = ''

        if comment_likes:
            profile_item['commentLikes'] = comment_likes
        else:
            profile_item['commentLikes'] = 0

        profile_item['profileID'] = profile_id

        # print profile_item

        yield profile_item
