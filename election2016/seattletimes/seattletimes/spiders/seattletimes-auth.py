from scrapy.spiders import Spider
import scrapy

from scrapy.conf import settings
from scrapy.utils.markup import remove_tags

import json
from urlparse import urlparse
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from seattletimes.items import SeattletimesItem

class SeattleTimesSpider(Spider):

    name='seattletimes-auth'
    searchTerm='trump'
    articleCount=0
    filename = name + '_' + searchTerm
    dataPath = "../../data/election2016/"
    settings.overrides['FEED_URI'] = dataPath + filename + ".json"

    allowed_domains = ['seattletimes.com']
    start_urls = ['https://secure.seattletimes.com/accountcenter/login']

    headers = { 'Accept':'*/*',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'en-US,en;q=0.8',
    'Cache-Control':'max-age=0',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
    }

    # Constructor to build the selenium-service
    def __init__(self):
        print "constructed"
        self.driver = webdriver.Remote("http://localhost:4444/wd/hub", webdriver.DesiredCapabilities.HTMLUNIT.copy())

    # Destructor method to clean up objects from memory, save settings, cache/rm elements
    def __del__(self):
        print "decontstructed"
        self.driver.quit()

    # Entrypoint into the class that begins the event flow once a response from the start_urls
    def parse(self, response):
        print "beginning parse"
        return scrapy.FormRequest.from_response(
                response,

                formdata={'username':'briansc@gmail.com','password':'thomas7'},
                callback=self.auth_login
                )

    # Obtain the response from the login and 
    def auth_login(self, response):
        print "authorizing"
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
            startURL = 'http://www.seattletimes.com/search-api?query='+self.searchTerm+'&page=1&perpage=10000'
            yield scrapy.Request(
                    url=startURL,
                    callback=self.obtainURLs)

    def obtainURLs(self, response): 
        print "obtainURLs response: "
        print response

        urls = []
        jsonresponse = json.loads(response.body_as_unicode())

        # For larger data sets we will need to use callback functions for jsonresponse and links
        if jsonresponse["hits"]["hits"]:
                for article in jsonresponse["hits"]["hits"]:
                    if str(article["fields"]["url"]) > 0:
                        urls.append(str(article["fields"]["url"]))

        for u in urls:
                if (u):
                        #yield scrapy.Request(url=u, headers=self.headers, callback=self.begin_scrapy)
                        yield scrapy.Request(url=u, headers=self.headers, callback=self.process_request)
                else:
                        print "empty url, moving on..."

    def process_request(self, response):

        # Wait here 
        #wait = WebDriverWait(self.driver, 10)
        #WebDriverWait(self.driver, 10).until(EC.title_contains("cheese!"))
        self.driver.implicitly_wait(10) # seconds
        
        # Pull the url from the response and send it to the webdriver
        self.driver.get(response.url)

        # Process and collect comments and comment count
        commentNumberElement = self.driver.find_element_by_id("showcomments")
        print "commentNumberElement: " + str(commentNumberElement)

        commentNumberElement.click()

        commentElement = self.driver.find_element_by_xpath('//*[@id="showcomments"]/span[1]')
        element = re.sub(' Comments','',str(commentElement.text),1)

        item=SeattletimesItem()
        item['commentNum']=element

        #element.click()
        #self.driver.execute_script("return <SCRIPT>")

        #elementDriver = self.driver.ActionChains(self.driver).move_to_element(element).click(element).perform()
        #print "elementDriver.text"
        #print elementDriver.text

        # Construct the Model and construct the dict object assigned to the 
        # items object 'SeattletimesItem'
        
        item['searchIndex']=str(self.filename)+"_"+str(self.articleCount)

        articleID = response.xpath('//*[contains(@id, "post-")]/@id').extract()[0].encode('utf-8').strip()
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
                    # iterate through the list of paragraphs
                    # strip the leading and following white space
                    # once the ps are clean, 
                    stripped += [str(remove_tags(para).encode('utf-8')).strip()]            
            item['body']=stripped
            # We really are only going to count 
            self.articleCount += 1

        print str(item)

        return item



    