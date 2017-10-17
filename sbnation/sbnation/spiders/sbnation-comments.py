# -*- coding: utf-8 -*-
from scrapy.spiders import Spider, Request
import MySQLdb
import json

from sbnation.items import SBNationComment, SBNationUser


class SBNationCommentsSpider(Spider):

    name = 'sbnation-comments'

    def __init__(self, domain=''):
        # Call super to initialize the instance
        super(Spider, self).__init__()

        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
                Chrome/48.0.2564.116 Safari/537.36'
        }

        dbauth_file = '../../config/mysqlauth.json'
        try:
            self.dbauth = json.loads(open(dbauth_file, 'r').read())
        except Exception, e:
            print"DB Auth Error: {0}".format(e)

        self.domain = domain

    def get_recent_articles(self):
        # TODO:  Query for article IDs that already have comments
        try:

            comment_query = ("SELECT article_id "
                             "FROM django.sbn_articles "
                             "WHERE search_index='%s' "
                             "AND created_on > NOW() - INTERVAL 14 DAY;"
                             % self.domain)

            conn = MySQLdb.connect(user=self.dbauth['user'],
                                   passwd=self.dbauth['password'],
                                   db=self.dbauth['database'],
                                   host=self.dbauth['host'],
                                   charset="utf8mb4",
                                   use_unicode=True)
            cursor = conn.cursor()
            cursor.execute(comment_query)
            # Cursor returns a tuple, assign appropriately
            article_ids = cursor.fetchall()

            # Convert list of tuples into list of strings
            article_ids = [x[0] for x in article_ids]
            return article_ids

        except Exception, e:
            print"Error: {0}".format(e)

    def start_requests(self):

        get_article_ids = self.get_recent_articles()

        print 'Updating comments from articles over last two weeks.  Count: {0}'.format(str(len(get_article_ids)))

        for article_id in get_article_ids:
            commentjs_url = 'https://www.' + self.domain + '.com/comments/load_comments/' + str(article_id)
            yield Request(url=commentjs_url, headers=self.headers, callback=self.parse)

    def parse(self, response):

        # item = SBNationComment()
        # Convert response from json to dictionary
        comment_dict = json.loads(response.text)

        for comment in comment_dict['comments']:
            item = SBNationComment()
            # print comment

            comment_id = comment['id']
            if comment_id:
                item['id'] = comment_id
            else:
                item['id'] = 0

            parent_id = comment['parent_id']
            if parent_id:
                item['parent_id'] = parent_id
            else:
                item['parent_id'] = 0

            user_id = comment['user_id']
            if user_id:
                item['user_id'] = user_id
            else:
                item['user_id'] = 0

            spam_flags = comment['spam_flags_count']
            if spam_flags:
                item['spam_flags'] = spam_flags
            else:
                item['spam_flags'] = 0

            troll_flags = comment['troll_flags_count']
            if troll_flags:
                item['troll_flags'] = troll_flags
            else:
                item['troll_flags'] = 0

            inappropriate_flags = comment['inappropriate_flags_count']
            if inappropriate_flags:
                item['inappropriate_flags'] = inappropriate_flags
            else:
                item['inappropriate_flags'] = 0

            recommended_flags = comment['recommended_flags_count']
            if recommended_flags:
                item['recommended_flags'] = recommended_flags
            else:
                item['recommended_flags'] = 0

            created_timestamp = comment['created_on_timestamp']
            if created_timestamp:
                item['created_timestamp'] = created_timestamp
            else:
                item['created_timestamp'] = 0

            body = comment['body']
            if body:
                item['body'] = body.encode('utf-8').strip()
            else:
                item['body'] = ''

            username = comment['username']
            if username:
                item['username'] = username.encode('utf-8').strip()
            else:
                item['username'] = ''

            title = comment['title']
            if title:
                item['title'] = title.encode('utf-8').strip()
            else:
                item['title'] = ''

            signature = comment['signature']
            if signature:
                item['signature'] = signature.encode('utf-8').strip()
            else:
                item['signature'] = ''

            article_id = comment['entry_id']
            if article_id:
                item['article_id'] = article_id
            else:
                item['article_id'] = 0

            yield item

        users = comment_dict['users']
        for user in users:

            user_item = SBNationUser()
            username = user['username']
            if username:
                user_item['username'] = username.encode('utf-8')
            else:
                user_item['username'] = ''

            user_id = user['id']
            if user_id:
                user_item['id'] = user_id
            else:
                user_item['id'] = 0

            created_on = user['created_on']
            if created_on:
                user_item['created_on'] = created_on
            else:
                user_item['created_on'] = ''

            profile_url = user['network_membership']['url']
            if profile_url:
                user_item['profile_url'] = profile_url
            else:
                user_item['profile_url'] = ''

            image_url = user['network_membership']['image_url']
            if image_url:
                user_item['image_url'] = image_url
            else:
                user_item['image_url'] = ''

            # TODO: Pass user_item dict in scrapy request for User URL

            yield user_item
