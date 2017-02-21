from scrapy.spiders import Spider
import scrapy
from scrapy.http import Request

import json
import re

import sqlalchemy
from sqlalchemy import create_engine

from seattletimes.items import SeattletimesComment, SeattletimesProfile

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
    custom_settings = {
        'FEED_URI': '../../../data/seattletimes/seattletimes-2016-05-01-profiles.json'
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
        self.app_name = "profiles"

        self.filename = "seattletimes-profiles"
        self.table_name = "bs_profileList"

    # Override parse entrypoint into the class that begins the event flow once a response from the start_urls
    def parse(self, response):
        # Get list of profileURLs from comment db

        print ("reading articles table for comment URL list")
        engine = create_engine('mysql+mysqlconnector://dbBambooDev:B@mboo99@bambooiq.ddns.net:3306/dbBambooDev')
        conn = engine.connect()

        # Add 'LIMIT 200' to query for testing
        # TODO:  Incorporate command line variables for sql date, sort, where articleid=xyz
        display_name_list = conn.execute(
            # Unique records from db_commentList for profileID and profileURL
            "SELECT DISTINCT displayName, profileID, profileURL FROM " + self.table_name + "").fetchall()

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

                yield scrapy.Request(url=profile_url_unicode, callback=self.get_profile_page)

    def get_profile_page(self, response):
        # obtain profile information from profile page
        print(response)

        # Get the response.url and convert it to json object
        # enumerate through the json object and pull out profiles
        # build out a list that
        # parse the elements and assign to a list
        # yield
