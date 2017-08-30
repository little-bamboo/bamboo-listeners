# -*- coding: utf-8 -*-

import scrapy
from scrapy.http import FormRequest
from loginform import fill_login_form
import re
import time

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

            profile_list_url = 'http://boards.cruisecritic.com/memberlist.php?&pp=100&order=asc&sort=joindate'



            yield scrapy.Request(url=profile_list_url, callback=self.get_page_count)

    def get_page_count(self, response):

        # Capture total number of pages div.page-number
        #   Parse Page 1 of NUMBER and assign to Number variable
        #   re.search('Updated: ([\w, ]+)', s).group(1).strip()
        # while page_num is <= total_num:
        #
        # new_url = 'http://boards.cruisecritic.com/memberlist.php?order=ASC&sort=joindate&page=1
        # profile_page = http://boards.cruisecritic.com/search.php?do=finduser&u=169

        total_pages = response.xpath('//div[@class="page-number"]/text()').re('Page 1 of ([\w, ]+)')[0]

        page_num = 1

        while page_num <= total_pages:

            profile_list_url = 'http://boards.cruisecritic.com/memberlist.php?&pp=100&order=asc&sort=joindate&page=' + str(page_num)
            page_num += 1
            # Meter call requests
            time.sleep(2)

            yield scrapy.Request(url=profile_list_url, callback=self.obtain_profiles)

    def obtain_profiles(self, response):
        item = CruisecriticItem()

        print response.xpath('//div[@class="page-number"]/text()')

