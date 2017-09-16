# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import MySQLdb
import json
import urllib2

from datetime import datetime, timedelta

from sbnation.items import SBNationComment, SBNationUser


class CommentsSpider(CrawlSpider):

    name = 'comments'
    update_recent_articles = True
    get_new_article_comments = False
    update_all_article_comments = False

    def __init__(self):

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

    def get_article_ids(self):
        # Get list of article IDs to obtain comments from
        try:

            query = "SELECT article_id FROM django.sbn_articles WHERE commentNum > 0 ORDER BY created_on DESC"
            conn = MySQLdb.connect(user=self.dbauth['user'], passwd=self.dbauth['password'], db=self.dbauth['database'], host=self.dbauth['host'],
                                    charset="utf8mb4", use_unicode=True)
            cursor = conn.cursor()
            cursor.execute(query)
            # Cursor returns a tuple, assign appropriately
            article_ids = cursor.fetchall()

            # Convert list of tuples into list of strings
            article_ids = [x[0] for x in article_ids]
            return article_ids

        except Exception, e:
            print"Error: {0}".format(e)

    def get_comment_article_ids(self):

        # TODO:  Query for article IDs that already have comments
        try:

            comment_query = "SELECT article_id FROM django.sbn_comments ORDER BY created_timestamp DESC"
            conn = MySQLdb.connect(user=self.dbauth['user'], passwd=self.dbauth['password'], db=self.dbauth['database'], host=self.dbauth['host'],
                                    charset="utf8mb4", use_unicode=True)
            cursor = conn.cursor()
            cursor.execute(comment_query)
            # Cursor returns a tuple, assign appropriately
            article_ids = cursor.fetchall()

            # Convert list of tuples into list of strings
            article_ids = [x[0] for x in article_ids]
            return article_ids

        except Exception, e:
            print"Error: {0}".format(e)

    def get_recent_articles(self):
        # TODO:  Query for article IDs that already have comments
        try:

            last_week = datetime.now() - timedelta(days=14)
            print last_week
            comment_query = "SELECT article_id FROM sbn_articles WHERE created_on > NOW() - INTERVAL 7 DAY;"
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

        # Run query on existing database to pull all article IDs
        # iterate through each id and yield scrapy request

        # TODO: Refactor get article IDs methods to a single method
        if self.get_new_article_comments:
            article_ids = set(self.get_article_ids())
            comment_article_ids = set(self.get_comment_article_ids())
            get_article_ids = article_ids - comment_article_ids

        elif self.update_recent_articles:
            # TODO: Query for articles for the past two weeks
            print 'updating comments from articles over last two weeks'
            get_article_ids = self.get_recent_articles()

        elif self.update_all_article_comments:
            # TODO: Query for all article IDs
            print 'updating comments for all articles'


        for article_id in get_article_ids:

            # Build URL
            commentjsURL = 'https://www.fieldgulls.com/comments/load_comments/' + str(article_id)
            yield scrapy.Request(url=commentjsURL, headers=self.headers, callback=self.parse_comments)

    def parse_comments(self, response):

        item = SBNationComment()

        # item = SBNationComment()
        # Convert response from json to dictionary
        comment_dict = json.loads(response.text)

        for comment in comment_dict['comments']:
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
                item['body'] = body
            else:
                item['body'] = ''

            username = comment['username']
            if username:
                item['username'] = username
            else:
                item['username'] = ''

            title = comment['title']
            if title:
                item['title'] = title
            else:
                item['title'] = ''

            signature = comment['signature']
            if signature:
                item['signature'] = signature
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
                user_item['username'] = username
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
