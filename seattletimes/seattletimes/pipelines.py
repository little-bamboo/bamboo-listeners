# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb
import pprint
import json
from scrapy.conf import settings

from seattletimes.items import SeattletimesArticle, SeattletimesComment, SeattletimesProfile


class SQLStore(object):

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

        except:
            print "Error obtaining db or credentials for SQLStore"

        self.conn = MySQLdb.connect(user=self.username,
                                    passwd=self.password,
                                    db=self.database,
                                    host=self.host,
                                    charset="utf8mb4",
                                    use_unicode=True)
        self.cursor = self.conn.cursor()
        # log data to json file


    def process_item(self, item, spider):
        if isinstance(item, SeattletimesArticle):
            try:
                self.cursor.execute("""REPLACE INTO st_articles (title, articleURL, body, postID, articleID, author,
                    category, commentjsURL, `date`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                    (item['title'],
                                     item['articleURL'],
                                     item['body'],
                                     item['post_id_base64'],
                                     item['articleID'].encode("unicode_escape"),
                                     item['author'],
                                     item['category'],
                                     item['commentjsURL'],
                                     item['date']))

                self.conn.commit()

                if item is not None:
                    # pprint.pprint(item)
                    print(str(item['date'] + ' ' + item['title'] + ' ' + item['articleURL']))
                    # TODO: Add Kafka topic producer
                    return item

            except MySQLdb.Error, e:
                print "Error %d: %s" % (e.args[0], e.args[1])



        elif isinstance(item, SeattletimesComment):
            try:
                self.cursor.execute("""REPLACE INTO st_comments(bodyHtml, articleID, commentID, profileID, parentID, 
                  createdDate, displayName, profileURL) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                                    (item['bodyHtml'],
                                     item['articleID'],
                                     item['id'],
                                     item['profileID'],
                                     item['parentID'],
                                     item['createdDate'],
                                     item['displayName'],
                                     item['profileURL']))
                self.conn.commit()

            except MySQLdb.Error, e:
                print "Error %d: %s" % (e.args[0], e.args[1])

            if item is not None:
                pprint.pprint(item)
                # TODO: Add Kafka topic producer
                return item

        elif isinstance(item, SeattletimesProfile):
            try:
                self.cursor.execute("""REPLACE INTO st_profiles(commentCount, about, profileCreated, displayName, 
                  location, commentLikes, profileID, profileUrl) VALUES (%s, %s, %s,%s, %s, %s, %s, %s)""",
                                    (item['commentCount'],
                                     item['about'],
                                     item['profileCreated'],
                                     item['displayName'],
                                     item['location'],
                                     item['commentLikes'],
                                     item['profileID'],
                                     item['profileUrl']))
                self.conn.commit()

            except MySQLdb.Error, e:
                print "Error %d: %s" % (e.args[0], e.args[1])
        if item is not None:
            # Didn't meet any of the previous instance requirements
            # TODO: Add Kafka topic producer
            return item