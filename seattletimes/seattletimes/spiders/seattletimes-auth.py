from scrapy.spiders import Spider
import scrapy
from scrapy.utils.markup import remove_tags

import json
from urlparse import urlparse
import urllib2
from scrapy_splash import SplashRequest

import re
from lxml import etree

import time
from datetime import datetime

from seattletimes.items import SeattletimesItem

# TODO: Import logging and setup logging for each step in process
# TODO: Log information statement in one line (summarized)
# TODO: Modify FEEDURI global property to include the search term and date parameters used for the crawl request

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
         Chrome/48.0.2564.116 Safari/537.36',
        'Accept-Charset': 'utf-8'
    }

    script = """

    function wait_for_element(splash, css, maxwait)
        if maxwait == nil then
        maxwait = 10
    end

    return splash:wait_for_resume(string.format([[
        function main(splash) {
          var selector = '%s';
          var maxwait = %s;
          var end = Date.now() + maxwait*1000;

          function check() {
            if(document.querySelector(selector)) {
              splash.resume('Element found');
            } else if(Date.now() >= end) {
              var err = 'Timeout waiting for element';
              splash.error(err + " " + selector);
            } else {
              setTimeout(check, 200);
            }
          }
          check();
        }]], css, maxwait))
    end

    function main(splash)
        splash:go(splash.args.url)
        wait_for_element(splash, "#fyre-comment-user")
        return {html=splash:html()}
    end


    """

    # Useful for stripping unicode and unnecessary characters
    full_pattern = re.compile('[^a-zA-Z0-9\\\/]|_')

    def __init__(self, date='', search='', datapath=''):
        # Call super to initialize the instance
        super(Spider, self).__init__()
        self.startdate = date
        self.enddate = (str(datetime.now()).split(" ")[0])
        self.searchterm = search

        # Print arguments to console for validation
        print self.startdate
        print self.enddate
        print self.searchterm
        print datapath

        self.articleCount = 0
        self.filename = "seattletimes" + '_' + self.searchterm + '_' + self.startdate

        print('filename=' + self.filename)

    # Endpoint into the class that begins the event flow once a response from the start_urls
    def parse(self, response):
        print("beginning parse")

        # Push authentication
        return scrapy.FormRequest.from_response(
                response,
                formdata={'username': 'briansc@gmail.com', 'password': 'thomas7'},
                callback=self.auth_login
                )

    # Obtain the response from the login and 
    def auth_login(self, response):

        # check login success before continuing
        print("auth_login")

        # print response.body
        if 'authentication failed' in response.body:
            self.logger.error("Login failed")
            return
        else:
            # Create new function that return list of URLs to parse
            # Use returned list of search URLs and iterate
            # for link in links:
            #       yield Request(url=link, callback=self.begin_scrapy)
            # print("Existing settings: %s" % self.settings.attributes.values())

            # OLD startURL='http://www.seattletimes.com/search-api
            #           ?query='+self.searchterm+'&page='+str(page_num)+'&perpage=1000'

            page_num = 1
            # TODO: Add flag that turns off while loop when there are no more articles (try/while)
            while page_num <= 750:
                print('page_num: ' + str(page_num))
                time.sleep(0.1)

                new_url = 'http://vendorapi.seattletimes.com/st/proxy-api/v1.0/st_search/search?' \
                          'query=' + self.searchterm + \
                          '&startdate=' + self.startdate + \
                          '&enddate=' + self.enddate + \
                          '&sortby=mostrecent&page=' + str(page_num) + '&perpage=100'

                page_num += 1

                yield scrapy.Request(
                    url=new_url,
                    callback=self.obtain_urls)

    def obtain_urls(self, response):
        # print "obtainURLs response: "
        # print response

        urls = []
        jsonresponse = json.loads(response.body_as_unicode())

        # TODO: Write jsonresponse to a file (jsonlines format)

        print('total hits: ' + str(jsonresponse['total']))

        for article in jsonresponse['hits']:
            if str(article["fields"]["url"]):
                urls.append(str(article["fields"]["url"].strip()))

        for u in urls:
            u += '#comments'
            print "Processing URL: " + u
            if u:
                #yield scrapy.Request(u, callback=self.process_request)
                yield SplashRequest(u, self.process_request,
                                    endpoint='execute',
                                    args={'lua_source': self.script}
                                    )
            else:
                print "empty url, moving on..."

    def process_request(self, response):
        print('process response request')
        #print(response.data['html'])
        r = response.data['html'].encode('utf-8')
        tree = etree.HTML(r)
        url = str(response.url)
        item = SeattletimesItem()
        item['searchIndex'] = str(self.filename) + "_" + str(self.articleCount)

        # Determine re pattern for matching against the specific keys:
        #   postIDBase64=window.SEATIMESCO.comments.info.postIDBase64
        #   window.SEATIMESCO.comments.info.postID
        #   window.SEATIMESCO.comments.info.postIDBase64
        # JavaScript link will be http://data.livefyre.com/bs3/v3.1/seattletimes.fyre.co/316317/MTAyMTk4MDM=/init
        # template will be http://data.livefyre.com/bs3/v3.1/seattletimes.fyre.co/'+self.siteID+
        #   '/'+self.postIDBase64+'=/init'

        siteID = "window.SEATIMESCO.comments.info.siteID"
        postIDBase64 = "window.SEATIMESCO.comments.info.postIDBase64"
        scriptheaderdata = tree.xpath('//script[contains(., "window.SEATIMESCO.comments.info.siteID")]')[0]

        # Collect the necessary settings to build the xhr response for the comments
        comment_settings = []
        for line in scriptheaderdata.text.split("\n"):
            line = re.sub(r"\s+", "", line, flags=re.UNICODE)
            if (siteID in line) or (postIDBase64 in line):
                comment_settings += [line]
        settings_dict = dict(line.split("=", 1) for line in comment_settings)

        # Construct the url used to retrieve the comment data
        commentjs_url = ""
        for key, value in settings_dict.iteritems():
            value = re.sub(self.full_pattern, '', value)
            settings_dict[key] = value
            commentjs_url = 'http://data.livefyre.com/bs3/v3.1/seattletimes.fyre.co/' + \
                           settings_dict[siteID] + '/' + settings_dict[postIDBase64] + '=/init'

        # Trigger the comment response using urllib2
        if commentjs_url:
            try:
                commentResponse = urllib2.urlopen(commentjs_url)
                commentJSON = json.load(commentResponse)
                # print commentJSON["headDocument"]["content"]
                print "Storing Comments Data"
                # Store the json comment blob for export as child within each story
                item['comData'] = commentJSON["headDocument"]["content"]

            except urllib2.HTTPError, e:
                print "No response: " + str(e.code) + " " + str(e.msg)

        articleid = response.xpath('//*[contains(@id, "post-")]/@id')

        if articleid:
            articleid = articleid.extract()
            articleid = articleid[0].encode('utf-8').strip()
            item['articleID'] = articleid

        article_header = response.xpath('//*[contains(@class, "article-header")]')

        if article_header:
            item['title'] = article_header.xpath('h1/text()').extract()[0].encode('utf-8').strip()
            item['date'] = article_header.xpath('//time/@datetime').extract()[0].encode('utf-8').strip()

        item['url'] = url

        author = response.xpath('//*[contains(@class, "p-author")]')
        for auth in author:
                if auth == author[0]:
                        item['author'] = remove_tags(author[0].extract()).encode('utf-8')
                elif auth == author[1]:
                        item['authorAffiliation'] = remove_tags(author[1].extract()).encode('utf-8')

        # Parse URL and extract text between / + / for category designation
        o = urlparse(response.url)

        # take the urlparse'd object and get the attribute 'path', then break that up into pieces, 
        # use the first piece for the category value
        item['category'] = o.path.split("/")[1].encode('utf-8').strip()

        for sel in response.xpath('//*[contains(@id, "article-content")]'):
            paragraphs = sel.xpath('//p').extract()
            stripped = []
            for index, para in enumerate(paragraphs):
                    stripped += str(remove_tags(para).encode('utf-8')).strip()
            # rejoin list of strings into one
            item['body'] = ''.join(stripped)

        comments = response.xpath('//*[contains(@class, "fyre-comment-article")]')

        if comments is not None:

            comment_list = []
            for comment in comments:
                comment_list.append(comment.extract().encode('utf-8'))
            item['commentStream'] = comment_list
        else:
            item['commentStream'] = ''

        self.articleCount += 1

        print item
        return item




















