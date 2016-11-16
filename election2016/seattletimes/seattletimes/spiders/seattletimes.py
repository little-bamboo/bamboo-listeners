from scrapy.spiders import Spider
import json
import sys

class TimesSpider(Spider):

        name='seattletimes'
        searchTerm='trump'
        startURLs = 'http://www.seattletimes.com/search-api?query='+searchTerm+'&page=1&perpage=20000'
        filename = name+'_'+searchTerm

        print "startURLs: " + startURLs

        allowed_domains = ["seattletimes.com"]
        start_urls = [startURLs]

        def parse(self, response):
                items=dict()
                index=0
                jsonresponse = json.loads(response.body_as_unicode())
                
                for article in jsonresponse["hits"]["hits"]:
                        
                        item=dict()
                        item["id"]=index
                        item["searchIndex"]=self.filename
                        item["publish_date"]=str(article["fields"]["publish_date"])
                        item["title"]=article["fields"]["title"]
                        item["summary"]=article["fields"]["summary"]

                        if (item):
                                items[index]=item
                                print item
                        index += 1

                
                print "createJson called with filename: " + self.filename
                jsonFile = self.filename + '.json'
                jsonPath = '../../data/election2016/'
                jsonExport = jsonPath + jsonFile
                with open(jsonExport, 'w') as fp:
                        json.dump(items, fp)

        #def loginAuth(user):
                #print "login called"
                # Part 2 - Parse returned URL pages for detail 
                # Part 3 - Parse comments in details pages
                # Login Form
                # Seattletimes action URL: https://secure.seattletimes.com/accountcenter/login
                # form id = "login"
                # class="validatedForm"
                # method="post"
                # input type="email"
                # Store authenticated return object somewhere (but where?) and use for detail pages

