# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb
import pprint


from seattletimes.items import SeattletimesArticle, SeattletimesComment, SeattletimesProfile


class SQLStore(object):

    def __init__(self):
        self.conn = MySQLdb.connect(user='briansc', passwd='BigBamboo99', db='django', host='10.0.1.10', charset="utf8mb4", use_unicode=True)
        self.cursor = self.conn.cursor()
        # log data to json file

    def process_item(self, item, spider):
        if isinstance(item, SeattletimesArticle):
            try:
                self.cursor.execute("""REPLACE INTO bs_articleList(title, articleURL, body, postID, articleID, author, category, commentjsURL, `date`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", \
                                    (item['title'], item['articleURL'], item['body'], item['post_id_base64'], \
                                     item['articleID'].encode("unicode_escape"), item['author'], item['category'], item['commentjsURL'], item['date']))

                self.conn.commit()

            except MySQLdb.Error, e:
                print "Error %d: %s" % (e.args[0], e.args[1])

            if item is not None:
                # pprint.pprint(item)
                print(str(item['date'] + ' ' + item['title'] + ' ' + item['articleURL']))
                return item

        elif isinstance(item, SeattletimesComment):
            try:
                self.cursor.execute("""REPLACE INTO bs_commentList(bodyHtml, articleID, commentID, profileID, parentID, createdDate, displayName, profileURL) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", (item['bodyHtml'], item['articleID'], item['id'], item['profileID'], item['parentID'], item['createdDate'], item['displayName'], item['profileURL']))
                self.conn.commit()

            except MySQLdb.Error, e:
                print "Error %d: %s" % (e.args[0], e.args[1])

            if item is not None:
                pprint.pprint(item)
                return item

        elif isinstance(item, SeattletimesProfile):
            try:
                self.cursor.execute("""REPLACE INTO bs_profileList(commentCount, about, profileCreated, displayName, location, commentLikes, profileID) VALUES (%s, %s, %s,%s, %s, %s, %s)""", (item['commentCount'], item['about'], item['profileCreated'], item['displayName'], item['location'], item['commentLikes'], item['profileID']))
                self.conn.commit()

            except MySQLdb.Error, e:
                print "Error %d: %s" % (e.args[0], e.args[1])
        if item is not None:
            return item