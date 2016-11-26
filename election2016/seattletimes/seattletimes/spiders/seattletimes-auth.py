from scrapy.spiders import Spider
import scrapy
from scrapy_splash import SplashRequest
from scrapy.conf import settings
from scrapy.utils.markup import remove_tags

import json
from urlparse import urlparse
import re

from dateutil.parser import parse
from datetime import datetime

from seattletimes.items import SeattletimesItem

class SeattleTimesSpider(Spider):

    # TODO: dynamically set filename using datetime?
    name='seattletimes-auth'
    searchTerm='clinton'
    dateFilter = "2008-01-01"
    datetimeFilter=datetime.strptime(dateFilter, '%Y-%m-%d')

    articleCount=0
    filename = name + '_' + searchTerm
    dataPath = "../../../../data/election2016/"
    settings.overrides['FEED_URI'] = dataPath + filename + "-articles" + ".json"

    allowed_domains = ['seattletimes.com']
    start_urls = ['https://secure.seattletimes.com/accountcenter/login']

    headers = {
        'Accept':'*/*',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'en-US,en;q=0.8',
        'Cache-Control':'max-age=0',
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
    }

    # Entrypoint into the class that begins the event flow once a response from the start_urls
    def parse(self, response):
        print "beginning parse"

        # Push authentication
        return scrapy.FormRequest.from_response(
                response,

                formdata={'username':'briansc@gmail.com','password':'thomas7'},
                callback=self.auth_login
                )

    # Obtain the response from the login and 
    def auth_login(self, response):

        #check login success before continuing
        print "auth_login response: " + str(response)

        #print response.body
        if 'authentication failed' in response.body:
            self.logger.error("Login failed")
            return
        else:
            # Create new function that return list of URLs to parse
            # Use returned list of search URLs and iterate
            # for link in links:
            #       yield Request(url=link, callback=self.begin_scrapy)
            # print("Existing settings: %s" % self.settings.attributes.values())
            startURL = 'http://www.seattletimes.com/search-api?query='+self.searchTerm+'&page=1&perpage=15000'
            yield scrapy.Request(
                    url=startURL,
                    callback=self.obtainURLs)

    def obtainURLs(self, response): 
        print "obtainURLs response: "
        print response

        urls = []
        jsonresponse = json.loads(response.body_as_unicode())

        # Check if there are any hits and assign them to the articles array
        if jsonresponse["hits"]["hits"]:
                for article in jsonresponse["hits"]["hits"]:

                    articleDate = str(article["fields"]["publish_date"]).split("T")
                    #articleDate = articleDate.split("T")
                    articleDate = str(articleDate[0])
                    articleDate = datetime.strptime(articleDate, '%Y-%m-%d')

                    if str(article["fields"]["url"]) and (articleDate > self.datetimeFilter):
                        urls.append(str(article["fields"]["url"]))

        for u in urls:
            #print "Processing url: " + u
            if (u):
                yield SplashRequest(u, self.process_request,
                                    endpoint='render.html',
                                    args={'wait': 5.0},
                                    )
            else:
                print "empty url, moving on..."

    def process_request(self, response):
        url = str(response.url)

        item=SeattletimesItem()
        item['searchIndex']=str(self.filename)+"_"+str(self.articleCount)


        articleID = response.xpath('//*[contains(@id, "post-")]/@id').extract()[0]
        if articleID:
            articleID.encode('utf-8').strip()
            item['articleID']=articleID

        articleHeader = response.xpath('//*[contains(@class, "article-header")]')
        item['title']=articleHeader.xpath('h1/text()').extract()[0].encode('utf-8').strip()
        item['url']=response.url

        author = response.xpath('//*[contains(@class, "p-author")]')
        for auth in author:
                if auth==author[0]:
                        item['author']=remove_tags(author[0].extract()).encode('utf-8')
                elif auth==author[1]:
                        item['authorAffiliation']=remove_tags(author[1].extract()).encode('utf-8')

        item['date']=articleHeader.xpath('//time/@datetime').extract()[0].encode('utf-8').strip()

        # Parse URL and extract text between / + / for category designation
        o = urlparse(response.url)

        # take the urlparse'd object and get the attribute 'path', then break that up into pieces, 
        # use the first piece for the category value
        item['category']=o.path.split("/")[1].encode('utf-8').strip()

        for sel in response.xpath('//*[contains(@id, "article-content")]'):
            paragraphs=sel.xpath('//p').extract()
            stripped=[]
            for index, para in enumerate(paragraphs):
                    stripped += str(remove_tags(para).encode('utf-8')).strip()
            # rejoin list of strings into one
            item['body']=''.join(stripped)

        # TODO Handle errors when no comment can be found (try/except)

        commentElement = response.xpath('//*[@id="showcomments"]/span[1]/text()')
        if commentElement and (str(commentElement) != 'Comments'):
            commentNum = commentElement.extract()[0].encode('utf-8').strip().split('Comments')[0]
            commentNum = re.sub('Comments', '', commentNum)
            item['commentNum'] = commentNum.strip()
            print "Comment count: " + item['commentNum']

        self.articleCount += 1

        return item
