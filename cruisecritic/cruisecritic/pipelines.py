# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json

import MySQLdb
# db=MySQLdb.connect

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

        except:
            print "Error obtaining db or credentials for SQLStore"

        self.conn = MySQLdb.connect(user=self.username, passwd=self.password, db=self.database, host=self.host, charset="utf8mb4", use_unicode=True)
        self.cursor = self.conn.cursor()
        #TODO: log data to json file


    def process_item(self, item, spider):
        try:
            print item['name']
            self.cursor.execute("""REPLACE INTO cc_profiles (`name`) VALUES (%s)""", ([item['name']]))

        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])

        return item