from scrapy.spiders import Spider
import json



class TimesSpider(Spider):
        # Create name for instance that concantenates the domain with the query terms and append the current DDMMYYYY
        # Receive arguments built using a configuration file built from the WebUI 
        name = "timescrawler"
        allowed_domains = ["seattletimes.com"]
        start_urls = ['http://www.seattletimes.com/search-api?query=trump&page=1&perpage=10000']

        def parse(self, response):
                items=dict()
                index=0
                jsonresponse = json.loads(response.body_as_unicode())
                
                for article in jsonresponse["hits"]["hits"]:
                        print article
                        item=dict()
                        item["index"]=index
                        item["publish_date"]=str(article["fields"]["publish_date"])
                        item["title"]=article["fields"]["title"]
                        item["summary"]=article["fields"]["summary"]
                        if (item):
                                items[index]=item
                        index += 1

                # Create a json file with format root/article/title/date/summary
                # ensure there are items in the list
                # print items
                self.createJson(items,self.name)

        # Open the file you plan to save the results to and dump the items.
        def createJson(self, itemDict, fileName):
                print "createJson called with filename: " + fileName
                jsonFile = fileName + '.json'
                with open(jsonFile, 'w') as fp:
                        json.dump(itemDict, fp)



        def loginAuth(self, user):
                print "login called"
                # Part 2 - Parse returned URL pages for detail 
                # Part 3 - Parse comments in details pages
                # Login Form
                # Seattletimes action URL: https://secure.seattletimes.com/accountcenter/login
                # form id = "login"
                # class="validatedForm"
                # method="post"
                # input type="email"
                # Store authenticated return object somewhere (but where?) and use for detail pages

