from scrapy.spiders import Spider
import scrapy
from scrapy.utils.markup import remove_tags

import json
from urlparse import urlparse
import re

import time
from datetime import datetime

import urllib2

from seattletimes.items import SeattletimesItem


class SeattleTimesSpider(Spider):

    name = 'seattletimes-auth'
    allowed_domains = ['seattletimes.com']
    start_urls = ['https://secure.seattletimes.com/accountcenter/login']

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
        self.searchterm = search
        print self.date
        print self.searchterm
        print datapath

        # TODO: Import logging and setup logging for each step in process
        # TODO: Log information statement in one line (summarized)

        dateFilter = self.date
        self.datetimeFilter=datetime.strptime(dateFilter, '%Y-%m-%d')

        self.articleCount = 0
        self.filename = "seattletimes" + '_' + self.searchterm

    def stringReplace(self, string):
        return re.sub(self.full_pattern, '', string)

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
            pageNum = 1
            while pageNum <= 10:
                time.sleep(3)
                startURL='http://www.seattletimes.com/search-api?query='+self.searchterm+'&page='+str(pageNum)+'&perpage=1000'
                pageNum += 1

                yield scrapy.Request(
                    url=startURL,
                    callback=self.obtainURLs)

    def obtainURLs(self, response): 
        #print "obtainURLs response: "
        #print response



        urls = []
        jsonresponse = json.loads(response.body_as_unicode())

        # Check if there are any hits and assign them to the articles array
        if jsonresponse["hits"]["hits"]:
                for article in jsonresponse["hits"]["hits"]:
                    articleDate = str(article["fields"]["publish_date"]).split("T")[0]
                    articleDate = datetime.strptime(articleDate, '%Y-%m-%d')

                    if str(article["fields"]["url"]) and (articleDate > self.datetimeFilter):
                        urls.append(str(article["fields"]["url"]))

        for u in urls:
            print "Processing URL: " + u
            if (u):
                yield scrapy.Request(u, callback=self.process_request)
            else:
                print "empty url, moving on..."

    def process_request(self, response):

        url = str(response.url)

        item=SeattletimesItem()
        item['searchIndex']=str(self.filename)+"_"+str(self.articleCount)

        # Determine re pattern for matching against the specific keys:
        #   postIDBase64=window.SEATIMESCO.comments.info.postIDBase64
        #   window.SEATIMESCO.comments.info.postID
        #   window.SEATIMESCO.comments.info.postIDBase64
        # JavaScript link will be http://data.livefyre.com/bs3/v3.1/seattletimes.fyre.co/316317/MTAyMTk4MDM=/init
        # template will be http://data.livefyre.com/bs3/v3.1/seattletimes.fyre.co/'+self.siteID+'/'+self.postIDBase64+'=/init'
        siteID = "window.SEATIMESCO.comments.info.siteID"
        postIDBase64 = "window.SEATIMESCO.comments.info.postIDBase64"
        scriptheaderdata = response.xpath('//script[contains(., "window.SEATIMESCO.comments.info.siteID")]') \
            .extract()[0].encode('utf-8').strip()

        # Collect the necessary settings to build the xhr response for the comments
        commentSettings = []
        for line in scriptheaderdata.split("\n"):
            line = re.sub(r"\s+", "", line, flags=re.UNICODE)
            if (siteID in line) or (postIDBase64 in line):
                commentSettings += [line]
        settingsDict = dict(line.split("=", 1) for line in commentSettings)

        # Construct the url used to retrieve the comment data
        commentjsURL = ""
        for key, value in settingsDict.iteritems():
            value = re.sub(self.full_pattern, '', value)
            settingsDict[key] = value
            commentjsURL = 'http://data.livefyre.com/bs3/v3.1/seattletimes.fyre.co/' + \
                           settingsDict[siteID] + '/' + settingsDict[postIDBase64] + '=/init'

        # Trigger the comment response using urllib2
        if commentjsURL:
            try:
                commentResponse = urllib2.urlopen(commentjsURL)
                commentJSON = json.load(commentResponse)
                # print commentJSON["headDocument"]["content"]
                print "Storing Comments Data"
                # Store the json comment blob for export as child within each story
                item['comData']=commentJSON["headDocument"]["content"]

            except urllib2.HTTPError, e:
                print "No response: " + str(e.code) + " " + str(e.msg)

        articleid = response.xpath('//*[contains(@id, "post-")]/@id')

        if articleid:
            articleid = articleid.extract()
            articleid = articleid[0].encode('utf-8').strip()
            item['articleID']=articleid

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

        self.articleCount += 1

        print item
        return item

