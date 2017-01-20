# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sys
import MySQLdb
import hashlib
from scrapy.exceptions import DropItem
from scrapy.http import Request

import MySQLdb
db=MySQLdb.connect

class CruisecriticPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('bambooiq.ddns.net', 'dbBambooDev', 'B@mboo99', 'dbBambooDev', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()


    def process_item(self, item, spider):
        try:
            # self.cursor.execute("""INSERT INTO dbBambooDev.cc VALUES (%s)""", (item['name']))

            #self.conn.commit()

            pass


        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])

        return item