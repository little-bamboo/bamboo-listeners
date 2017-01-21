# -*- coding: utf-8 -*-

import scrapy
from scrapy.http import FormRequest

from loginform import fill_login_form

import re

import time
from datetime import datetime

from cruisecritic.items import CruisecriticItem


class CruisecriticAuthSpider(scrapy.Spider):
    name = "cruisecritic-auth"
    allowed_domains = ["cruisecritic.com"]
    start_urls = ['http://boards.cruisecritic.com/']
    login_user = "bludeeyank"
    login_pass = "thomas7"


    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
         Chrome/48.0.2564.116 Safari/537.36',
        'Accept-Charset': 'utf-8'
    }


    # Useful for stripping unicode and unnecessary characters
    full_pattern = re.compile('[^a-zA-Z0-9\\\/]|_')

    def parse(self, response):
        print "beginning authentication"

        args, url, method = fill_login_form(response.url, response.body, self.login_user, self.login_pass)

        return FormRequest(url, method=method, formdata=args, callback=self.auth_login)


    def auth_login(self, response):
        print('auth login')

        # print response.body
        if 'authentication failed' in response.body:
            self.logger.error("Login failed")
            return
        else:

            user_id = 1
            # TODO: Add flag that turns off while loop when there are no more articles (try/while)
            while user_id <= 10:
                new_url = 'http://boards.cruisecritic.com/member.php?u=' + str(user_id).strip()

                user_id += 1

                yield scrapy.Request(url=new_url, callback=self.obtain_profiles)


    def obtain_profiles(self, response):
        time.sleep(0.1)
        item = CruisecriticItem()

        title = response.xpath('//h1/text()').extract()[0].encode('utf-8').strip()

        item['name'] = title



        print item
        return item