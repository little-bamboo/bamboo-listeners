# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json

import MySQLdb
from cruisecritic.items import CruisecriticProfile, CruisecriticPost


class CruisecriticPipeline(object):
    def __init__(self):

        # Pull credentials from config directory for database
        dbauth_file = '../../config/mysqlauth.json'

        try:
            dbauth = json.loads(open(dbauth_file, 'r').read())
            print(dbauth)
            self.username = dbauth['user']
            print(self.username)
            self.password = dbauth['password']
            self.database = dbauth['database']
            self.host = dbauth['host']

        except Exception, e:
            print "Error: {0}".format(e)

        self.conn = MySQLdb.connect(user=self.username, passwd=self.password, db=self.database, host=self.host,
                                    charset="utf8mb4", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        # print"Spider Name: {0}".format(spider.name)
        if isinstance(item, CruisecriticProfile):
            try:
                print "Processing user_id: {0}".format(item['user_id'])

                # Commit main profile record
                self.cursor.execute("""REPLACE INTO cc_profiles (`name`, user_id, join_date, location, post_count, 
                  last_activity, favorite_cruise_lines, post_frequency) VALUES (%s, %s, %s, %s, %s, %s, %s, 
                  %s)""", (item['name'], item['user_id'], item['join_date'], item['location'], item['post_count'],
                           item['last_activity'], item['favorite_cruise_lines'], item['post_frequency']))
                self.conn.commit()

                # Commit friends to friends table (many to many)
                if item['friends']:
                    friends = item['friends'].split(',')

                    # convert to list of tuples in format [(user_friend_id, user_id, friend_id)]
                    friend_list = [(str(item['user_id']) + '-' + friend, item['user_id'], int(friend)) for friend in
                                   friends]
                    self.cursor.executemany(
                        """REPLACE INTO cc_friends(user_friend_id, user_id, friend_id) VALUES (%s, %s, %s)""",
                        friend_list)
                    self.conn.commit()

            except MySQLdb.Error, e:
                print "Error %d: %s" % (e.args[0], e.args[1])
            except Exception, e:
                print"Error: {0}".format(e)

            return item
        elif isinstance(item, CruisecriticPost):
            try:
                print "Processing post_id: {0}".format(item['post_id'])

                # Commit post to mysql
                # self.cursor.execute("""REPLACE INTO cc_posts (post_id, post_date, forum_name, thread_title, user_id, post_url, post_body, thread_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                #                     item['post_id'], item['post_date'], item['forum_name'], item['thread_title'], item['user_id'], item['post_url'], item['post_body'], item['thread_id'])

                self.cursor.execute("""REPLACE INTO cc_posts (post_id, forum_name, post_date, post_title, post_body, thread_title, thread_id, user_id, post_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                    (item['post_id'], item['forum_name'], item['post_date'], item['post_title'], item['post_body'], item['thread_title'], item['thread_id'], item['user_id'], item['post_url']))
                self.conn.commit()

            except MySQLdb.Error, e:
                print "Error %d: %s:" % (e.args[0], e.args[1])
            except Exception, e:
                print"Error: {0}".format(e)
