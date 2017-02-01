# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sys
import MySQLdb
import pymongo

import hashlib
from scrapy.exceptions import DropItem
from scrapy.http import Request
import json
import os.path

from seattletimes.items import SeattletimesArticle, SeattletimesComment, SeattletimesProfile


class SQLStore(object):

    def __init__(self):
        self.conn = MySQLdb.connect(user='dbBambooDev', passwd='B@mboo99', db='dbBambooDev', host='10.0.1.10', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()
        # log data to json file


    def process_item(self, item, spider):
        if isinstance(item, SeattletimesArticle):
            try:
                self.cursor.execute("""INSERT INTO bs_articleList(title, articleURL, body, post_id, articleID, author, category, commentjsURL, `date`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", \
                                    (item['title'], item['articleURL'], item['body'], item['post_id_base64'], \
                                     item['articleID'], item['author'], item['category'], item['commentjsURL'], item['date']))
                self.conn.commit()

            except MySQLdb.Error, e:
                print "Error %d: %s" % (e.args[0], e.args[1])

            if item is not None:
                return item

        elif isinstance(item, SeattletimesComment):
            try:
                self.cursor.execute("""INSERT INTO bs_commentList(bodyHtml, articleID, id, commentAuthor, parentID, createdAt) VALUES (%s, %s, %s, %s, %s, %s)""", (item['bodyHtml'], item['articleID'], item['id'], item['commentAuthor'], item['parentID'], item['createdAt']))
                self.conn.commit()

            except MySQLdb.Error, e:
                print "Error %d: %s" % (e.args[0], e.args[1])
        if item is not None:
            return item


class MongoPipeline(object):

    collection_name = 'scrapy_items'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('bambooiq.ddns.net:23717'),
            mongo_db=crawler.settings.get('twitter', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert(dict(item))
        return item