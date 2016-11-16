from scrapy.spiders import Spider
import scrapy
import json
from scrapy.conf import settings

from seattletimes.items import SeattletimesItem

class SeattleTimesSpider(Spider):

        name='seattletimes-auth'
        searchTerm='clinton'
        articleCount=0
        filename = name + '_' + searchTerm
        dataPath = "../../data/election2016/"

        settings.overrides['FEED_URI'] = dataPath + filename + ".json"

        allowed_domains = ['seattletimes.com']
        start_urls = ['https://secure.seattletimes.com/accountcenter/login']

        def parse(self, response):
                return scrapy.FormRequest.from_response(
                        response,
                        formdata={'username':'briansc@gmail.com','password':'thomas7'},
                        callback=self.auth_login
                        )

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
                        #print("Existing settings: %s" % self.settings.attributes.values())
                        startURL = 'http://www.seattletimes.com/search-api?query='+self.searchTerm+'&page=1&perpage=20000'
                        yield scrapy.Request(url=startURL, callback=self.parseJSON)

        def parseJSON(self, response):                
                links = []
                jsonresponse = json.loads(response.body_as_unicode())

                if jsonresponse["hits"]["hits"]:
                        for article in jsonresponse["hits"]["hits"]:     
                                links.append(str(article["fields"]["url"]))

                for link in links:
                        if (link):
                                yield scrapy.Request(url=link, callback=self.begin_scrapy)
                        else:
                                print "empty url, moving on..."

        def begin_scrapy(self, response):   
          
                item=SeattletimesItem()
                item['searchIndex']=str(self.filename)+"_"+str(self.articleCount)

                for sel in response.xpath('//*[contains(@class, "article-header")]'):
                        item['title']=sel.xpath('h1/text()').extract()
                        print "item['title']: " + str(item['title'])
                        item['url']=response.url
                        item['date']=sel.xpath('//time/@datetime').extract()

                articleContent = response.xpath('//*[contains(@id, "article-content")]')
                for sel in articleContent:
                        item['body']=sel.xpath('//p').extract()
                        self.articleCount += 1
                return item



