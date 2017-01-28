# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from seattletimes.items import SeattletimesItem


class SeattletimesPipeline(object):
	def process_item(self, item, spider):
		if isinstance(item, SeattletimesItem):
			# TODO: Add enrichment lookups here
			# TODO: Can we add 'bot' like functionality here?
			# TODO: What kind of reiforcement learning can we apply at this step?
			return item
