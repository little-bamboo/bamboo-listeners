from scrapy.spiders import Spider
import scrapy
import json

class SeattleTimesSpiderAuth(Spider):

        name='seattletimes-auth'
        searchTerm='clinton'
        
        loginURL= 'https://secure.seattletimes.com/accountcenter/login'
        filename = name + '_' + searchTerm

        allowed_domains = ["seattletimes.com"]
        start_urls = [loginURL]

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
                        
                        startURL = 'http://www.seattletimes.com/search-api?query='+self.searchTerm+'&page=1&perpage=20000'
                        yield scrapy.Request(url=startURL, callback=self.parseJSON)

        def parseJSON(self, response):
                #print "parseJSON response: " + str(response.body)
                items=dict()
                index=0
                links = []
                jsonresponse = json.loads(response.body_as_unicode())

                if jsonresponse["hits"]["hits"]:
                        for article in jsonresponse["hits"]["hits"]:     
                                item=dict()
                                item["id"]=index
                                item["searchIndex"]=self.filename
                                item["publish_date"]=str(article["fields"]["publish_date"])
                                item["title"]=article["fields"]["title"]
                                item["summary"]=article["fields"]["summary"]
                                #print "article[\"fields\"][\"url\"]: " + str(article["fields"]["url"])
                                links.append(str(article["fields"]["url"]))

                                if (item):
                                        items[index]=item
                                        #print "Item: " + item
                                index += 1
                                print "index: " + str(index)

                        print "createJson called with filename: " + self.filename
                        jsonFile = self.filename + '.json'
                        jsonPath = '../../data/election2016/'
                        jsonExport = jsonPath + jsonFile
                        with open(jsonExport, 'w') as fp:
                                json.dump(items, fp)

                print "links: " + str(links)
                if(links > 0):
                        for link in links:
                                yield scrapy.Request(url=link, callback=self.begin_scrapy)


        def begin_scrapy(self, response):
                print "begin_scrapy response: " + str(response)

                for sel in response.xpath('//*[contains(@class, "article-header")]'):
                        #print "sel: " , str(sel)
                        #print "sel.xpath: " , str(sel.xpath)
                        print sel.xpath('h1/text()').extract()

                # Once we've obtained the title, lets move on to get the content of the article
                # The article's content for SeattleTimes is stored in the paragraph tags contained
                # within the article-content tag
                # Get the xpath for t
                articleContent = response.xpath('//*[contains(@id, "article-content")]')

                xpathIndex=0
                for sel in articleContent:
                        print "xpathIndex: " + str(xpathIndex)
                        #print "sel.extract(): "+ sel.extract()
                        xpathIndex+=1

