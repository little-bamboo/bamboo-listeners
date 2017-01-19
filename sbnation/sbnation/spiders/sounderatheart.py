from scrapy.spiders import Spider
import scrapy
from scrapy.utils.markup import remove_tags

import json
import re
import datetime

import urllib2

from sbnation.items import SBNationItem

class SounderAtHeartSpider(scrapy.Spider):
    name = 'sounderatheart'

    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
         Chrome/48.0.2564.116 Safari/537.36'
    }

    # Useful for stripping unicode and unnecessary characters
    full_pattern = re.compile('[^a-zA-Z0-9\\\/]|_')

    def __init__(self,date='',search='', datapath='', *args, **kwargs):
        super(Spider, self).__init__(*args,**kwargs)

        self.date = date
        self.currentDate = datetime.datetime.now()
        self.search_term = search
        print self.date
        print self.search_term
        print datapath

        # TODO: Import logging and setup logging for each step in process
        # TODO: Log information statement in one line (summarized)

        dateFilter = self.date
        self.datetimeFilter=datetime.strptime(dateFilter, '%Y-%m-%d')

        self.articleCount = 0
        self.filename = "sounderatheart" + '_' + self.search_term

    def stringReplace(self, string):
        return re.sub(self.full_pattern, '', string)

    def start_requests(self):

        # Build a list of URLs using the search URL and paginating through results
        search_term = 'sounders'
        url = 'http://www.sounderatheart.com/search?q=' + search_term
        yield scrapy.Request(url=url,headers=self.headers, callback=self.parse_search)

    def parse_search(self, response):

        articleLinks = response.css('td.m-profile__activity-table__content a::attr(href)').extract()

        for article in articleLinks:
            yield scrapy.Request(url=article,headers=self.headers, callback=self.parse_article)

        nextPage =  response.css('span.m-pagination__next a::attr(href)').extract()

        if nextPage is not None:
            for nextUrl in nextPage:
                nextLink = 'http://www.sounderatheart.com/' + str(nextUrl)
                print "nextLink: " + nextLink
                yield scrapy.Request(url=nextLink,headers=self.headers, callback=self.parse_search)


    def parse_article(self, response):
        item = SBNationItem()

        title = response.css('h1.c-page-title').extract()
        if len(title) > 0:
            item['aTitle']=remove_tags(title[0].strip())
        else:
            pass

        body = response.xpath('/html/body/section/section/div[2]/div[1]/div[1]').extract()
        if len(body) > 0:
            item['aBody']=remove_tags(body[0].strip())
        else:
            pass

        cdataId = response.css('div.c-entry-stat--comment ::attr(data-cdata)').extract()
        # {"id":13686549,"comment_count":108,"recommended_count":0,"url":"http://www.sounderatheart.com/2016/12/12/13922508/brad-evans-option-exercised"}

        if len(cdataId) > 0:
            # Convert cdataId to a json object, store objects into item
            cdata = json.loads(cdataId[0])
            print cdata
            item['articleID'] = cdata['id']
            item['commentNum'] = cdata['comment_count']
            item['aUrl'] = cdata['url']
            item['recommendedNum'] = cdata['recommended_count']
        else:
            pass

        author = response.css('a.c-byline__twitter-handle').extract()

        if len(author) > 0:
            item['aAuthor'] = remove_tags(author[0])
        else:
            pass

        if 'articleID' in item:
            articleId = str(item['articleID'])
            commentjsURL = 'http://www.sounderatheart.com/comments/load_comments/' + articleId
        else:
            commentjsURL = ""

        # Trigger the comment response using urllib2
        if commentjsURL:
            try:
                commentResponse = urllib2.urlopen(commentjsURL)
                commentJSON = json.load(commentResponse)
                item['commentjsURL'] = commentjsURL
                print "Storing Comments Data"
                # Store the json comment blob for export as child within each story
                item['comData']=commentJSON

            except urllib2.HTTPError, e:
                print "No response: " + str(e.code) + " " + str(e.msg)

        if 'title' in item:
            print item['title']
        return item