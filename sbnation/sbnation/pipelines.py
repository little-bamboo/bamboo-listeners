# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sbnation.items import SBNationArticle, SBNationComment, SBNationUser
import json
import MySQLdb
import logging
import sys


class SbnationPipeline(object):

    def __init__(self):

        # Pull credentials from config directory for database
        dbauth_file = '../../config/mysqlauth.json'

        try:
            self.dbauth = json.loads(open(dbauth_file, 'r').read())

        except Exception, e:
            print "Error: {0}".format(e)

        self.conn = MySQLdb.connect(user=self.dbauth['user'],
                                    passwd=self.dbauth['password'],
                                    db=self.dbauth['database'],
                                    host=self.dbauth['host'],
                                    charset="utf8mb4",
                                    use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        if isinstance(item, SBNationArticle):
            try:
                print "Committing article_id: {0}".format(item['article_id'])

                # Commit main profile record
                self.cursor.execute("""REPLACE INTO sbn_articles (title, body, created_on, url, search_index, article_id, 
                  categories, author, commentNum, recommendNum) VALUES  (%s, %s, %s, %s, %s, %s, %s, %s, 
                  %s, %s)""", (item['title'],
                               item['body'],
                               item['created_on'],
                               item['url'],
                               item['search_index'],
                               item['article_id'],
                               item['categories'],
                               item['author'],
                               item['comment_num'],
                               item['recommended_num']))
                self.conn.commit()
            except MySQLdb.Error, e:
                print e[0], e[1], spider
                self.conn.rollback()
                self.cursor.close()
                self.conn.close()
                # print lengthy error description!!
                logging.error("Error: {0}".format(sys.exit(2)))
            except Exception, e:
                print"Error: {0}".format(e)
                logging.error("error: {0}".format(e))

        elif isinstance(item, SBNationComment):
            try:
                print "Committing commentID: {0}".format(item['id'])

                # Commit comment record
                self.cursor.execute("""REPLACE INTO sbn_comments (id, parent_id, user_id, spam_flags, troll_flags, 
                  inappropriate_flags, recommended_flags, created_timestamp, body, username, title, signature, 
                  article_id) VALUES  (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                    (item['id'], item['parent_id'], item['user_id'], item['spam_flags'],
                                     item['troll_flags'], item['inappropriate_flags'], item['recommended_flags'],
                                     item['created_timestamp'], item['body'], item['username'], item['title'],
                                     item['signature'], item['article_id']))
                self.conn.commit()
            except MySQLdb.Error, e:
                print e[0], e[1]
                self.conn.rollback()
                self.cursor.close()
                self.conn.close()
                # print lengthy error description!!
                logging.error("Error: {0}".format(sys.exit(2)))
            except Exception, e:
                print"Error: {0}".format(e)
                logging.error("error: {0}".format(e))

        elif isinstance(item, SBNationUser):
            try:
                print "Committing user: {0}".format(item['username'])

                self.cursor.execute("""REPLACE INTO sbn_users (id, username, created_on, profile_url, image_url) VALUES 
                                    (%s, %s, %s, %s, %s)""", (item['id'], item['username'], item['created_on'],
                                                              item['profile_url'], item['image_url']))
                self.conn.commit()
            except MySQLdb.Error, e:
                print e[0], e[1]
                self.conn.rollback()
                self.cursor.close()
                self.conn.close()
                # print lengthy error description!!
                logging.error("Error: {0}".format(sys.exit(2)))
            except Exception, e:
                print"Error: {0}".format(e)
                logging.error("error: {0}".format(e))
