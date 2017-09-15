# -*- coding: utf-8 -*-

import scrapy
from scrapy.http import FormRequest
from loginform import fill_login_form
import re
import time
import json
import string

from datetime import datetime, date

from cruisecritic.items import CruisecriticPost, CruisecriticProfile


class CruisecriticAuthSpider(scrapy.Spider):
    name = "cruisecritic-auth"
    allowed_domains = ["cruisecritic.com"]
    start_urls = ['http://boards.cruisecritic.com/']

    # Pull credentials from config directory for database
    dbauth_file = '../../config/cruisecriticauth.json'

    try:
        auth = json.loads(open(dbauth_file, 'r').read())
        print(auth)

        login_user = auth['login_user']
        login_pass = auth['login_pass']

    except:
        print "Error obtaining cruise critic credentials"


    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
         Chrome/48.0.2564.116 Safari/537.36',
        'Accept-Charset': 'utf-8'
    }

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
            base_profile_url = 'http://boards.cruisecritic.com/member.php?u='

            # Member count Sept 8 = 1583505
            num_of_members = 1582424

            while num_of_members > 0: #1583505:
                url = base_profile_url + str(num_of_members)
                num_of_members -= 1
                # time.sleep(.1)
                yield scrapy.Request(url=url, callback=self.obtain_profiles_info)

    def get_page_count(self, response):

        # Capture total number of pages div.page-number
        total_pages = response.xpath('//div[@class="page-number"]/text()').re('Page 1 of ([\w, ]+)')[0]

        page_num = 1

        while page_num <= total_pages:

            profile_list_url = 'http://boards.cruisecritic.com/memberlist.php?&pp=100&order=desc&sort=joindate&page=' \
                               + str(page_num)
            page_num += 1

            # Meter call requests
            time.sleep(1)

            yield scrapy.Request(url=profile_list_url, callback=self.obtain_profiles_list)

    def obtain_profiles_list(self, response):
        _response = response
        # Find all profiles in page that is returned
        # Profile url location td class=alt1Active a href=URL_TO_COLLECT

        profiles_list = _response.xpath('//a[contains(@href, "member.php?u=")]/@href').extract()
        for profile in profiles_list:
            profile_url = 'http://boards.cruisecritic.com/'+profile

            # Meter profile requests
            time.sleep(1)
            yield scrapy.Request(url=profile_url, callback=self.obtain_profiles_info)

    def obtain_profiles_info(self, _response):

        response = _response
        # Find profile elements and return to pipeline
        print response.url

        profile_item = CruisecriticProfile()

        # Convert datetime to usable format
        join_date_raw = response.xpath('//div[contains(text(), "Join Date: ")]').re('Join Date: ([\w, ]+)')
        if join_date_raw:
            profile_item['join_date'] = datetime.strptime(join_date_raw[0], '%b %d, %Y').strftime('%Y-%m-%d')
        else:
            profile_item['join_date'] = ''

        user_id = response.url.split('=')
        if user_id:
            profile_item['user_id'] = int(user_id[1])
        else:
            profile_item['user_id'] = ''

        # Use '//text() to extract the text from nested tags, such as when h1 has nested span tag for styling
        profile_name = response.xpath('//h1[@class="heading-l"]//text()').extract()
        if profile_name:
            profile_item['name'] = profile_name[0]
        else:
            profile_item['name'] = ''

        location = response.xpath('//div[contains(text(), "Location: ")]').re('Location: ([\w, ]+)')
        if location:
            profile_item['location'] = location[0]
        else:
            profile_item['location'] = ''

        post_count = response.xpath('//div[contains(text(), "Total Posts: ")]').re('Total Posts: ([\w, ]+)')

        if post_count:
            # Handle numbers with commas using replace
            profile_item['post_count'] = int(post_count[0].replace(',', ''))

            # if profile_item['post_count'] > 0:
            #     time.sleep(5.1)
            #     user_url = 'http://boards.cruisecritic.com/search.php?do=finduser&u=' + str(profile_item['user_id'])
            #     yield scrapy.Request(url=user_url, callback=self.obtain_user_posts)

        else:
            profile_item['post_count'] = ''

        post_frequency = response.xpath('//div[contains(text(), "Posts Per Day: ")]').re('Posts Per Day: ([\w, ]+)')

        if post_frequency:
            profile_item['post_frequency'] = float(post_frequency[0])
        else:
            profile_item['post_frequency'] = ''

        last_activity = response.xpath('//div[contains(text(), "Last Activity: ")]').re('Last Activity: ([\w, ]+)')
        if last_activity:
            # Convert today/yesterday values to strings with strip for equality check
            last = str(last_activity[0].strip())
            if last == 'Yesterday':
                # convert to yesterday's date
                profile_item['last_activity'] = date.fromordinal(date.today().toordinal() - 1).strftime('%Y-%m-%d')
            elif last == 'Today':
                # convert to today's date
                profile_item['last_activity'] = date.today().strftime('%Y-%m-%d')
            else:
                profile_item['last_activity'] = datetime.strptime(last, '%b %d, %Y').strftime('%Y-%m-%d')
        else:
            profile_item['last_activity'] = ''

        favorite_cruises = response.xpath('//div[contains(text(), "Favorite Cruise Line(s): \ '
                                          '")]').re('Favorite Cruise Line(s): ([\w, ]+)')

        if favorite_cruises:
            profile_item['favorite_cruise_lines'] = favorite_cruises[0]
        else:
            profile_item['favorite_cruise_lines'] = ''

        friends = response.xpath('//ul[@class="friends"]/li/a/@href').extract()
        if friends:
            friend_list = []
            for friend in friends:
                friend_id = friend.split('=')[1]
                friend_list.append(friend_id)
            profile_item['friends'] = ','.join(friend_list)
        else:
            profile_item['friends'] = ''

        # 'Message' indicates there is no profile for this user
        if profile_item['name'] == 'Message':
            print 'Skipped user_id: {0}'.format(profile_item['user_id'])
        else:
            yield profile_item

    def obtain_user_posts(self, response):

        # Copy to break response?
        _response = response

        post = CruisecriticPost()

        post_list = _response.xpath('//div[@class="box1"]')

        for item in post_list:
            try:
                forum_name = item.xpath('.//div[contains(@class, "pull-right")]/a//text()').extract()
                if forum_name:
                    post['forum_name'] = forum_name[0].strip()
                else:
                    post['forum_name'] = ''

                post_datetime_raw = item.xpath('.//div[contains(@class, "box-footer")]/div//text()').extract()
                if post_datetime_raw:
                    try:
                        post_datetime = datetime.strptime(post_datetime_raw[0].strip(), '%b %d, %Y, %I:%M %p')
                        # TODO:  Test for 'today' and 'yesterday' in datestring before converting to datetime stamp
                        post['post_date'] = post_datetime
                    except Exception, e:
                        print e
                        # Currently setting to current date whenever an error is encountered
                        post['post_date'] = date.today().strftime('%Y-%m-%d')
                else:
                    post['post_date'] = ''

                post_id_raw = item.xpath('.//div[contains(@class, "box-content")]/a/@href').extract()
                if post_id_raw:
                    post_id = post_id_raw[0].split('=')[1].split('#')[0]
                    post['post_id'] = int(post_id)
                else:
                    post['post_id'] = ''

                post_title = item.xpath('.//div[contains(@class, "box-content")]/a/text()').extract()
                if post_title:
                    post['post_title'] = post_title[0].strip()
                else:
                    post['post_title'] = ''

                post_body_list = item.xpath('.//div[contains(@class, "box-content")]//text()').extract()
                if post_body_list:
                    post_body = ' '.join(post_body_list[2:]).strip()
                    post['post_body'] = post_body
                else:
                    post['post_body'] = ''

                post_thread_title = item.xpath('.//div[contains(@class, "box-header")]/div[2]/a//text()').extract()
                if post_thread_title:
                    post['thread_title'] = post_thread_title[0].strip()
                else:
                    post['thread_title'] = ''

                post_thread_id = item.xpath('.//div[contains(@class, "box-header")]/div[2]/a/@href').extract()
                if post_thread_id:
                    post['thread_id'] = post_thread_id[0].split('=')[1].strip()
                else:
                    post['thread_id'] = ''

                post_user_id = item.xpath('.//div[contains(@class, "box-header")]/div[3]/a/@href').extract()
                if post_user_id:
                    post['user_id'] = post_user_id[0].split('=')[1].strip()
                else:
                    post['user_id'] = ''

                post_url = item.xpath('.//div[contains(@class, "box-content")]/a/@href').extract()
                if post_url:
                    post['post_url'] = post_url[0].strip()
                else:
                    post['post_url'] = ''

                yield post

            except Exception, e:
                print"Error: {0}".format(e)

    # TODO: Implement once profile collection is in place
    # def obtain_post_list(self, response):
    #     # Iterate through post list yielding threads
    #     print response
    #
    # def thread_parse(self, response):
    #     print response
