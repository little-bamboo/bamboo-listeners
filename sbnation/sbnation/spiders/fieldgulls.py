import scrapy
from scrapy.utils.markup import remove_tags
import json
import re
import urllib2

from datetime import datetime, date

from sbnation.items import SBNationArticle

class FieldGullsSpider(scrapy.Spider):
    name = "fieldgulls"

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

    def stringReplace(self, string):
        return re.sub(self.full_pattern, '', string)

    def start_requests(self):

        # Build a list of URLs using the search URL and paginating through results
        search_term = 'seahawks'
        url = 'http://www.fieldgulls.com/search?order=date&q=' + search_term
        yield scrapy.Request(url=url,headers=self.headers, callback=self.parse_search)

    def parse_search(self, response):

        articleLinks = response.xpath('//div[contains(@class, "c-entry-box--compact--article")]/a/@href').extract()

        for article in articleLinks:
            yield scrapy.Request(url=article,headers=self.headers, callback=self.parse_article)

        nextPage = response.xpath('//a[contains(@class, "c-pagination__next")]/@href').extract()

        try:
            nextLink = 'http://www.fieldgulls.com' + str(nextPage[0])
            print "nextLink: " + nextLink
            yield scrapy.Request(url=nextLink,headers=self.headers, callback=self.parse_search)
        except Exception, e:
            print "Error: {0}".format(e)


    def parse_article(self, response):
        item = SBNationArticle()

        title = response.css('h1.c-page-title').extract()
        if title:
            item['title'] = remove_tags(title[0].encode('utf-8').strip())
        else:
            item['title'] = 'No Title Found'

        body = response.css('div.c-entry-content').extract()
        if body:
            item['body'] = body[0].encode('utf-8').strip()
        else:
            item['body'] = 'No body text found'

        articleID = response.css('body ::attr(data-entry-id)').extract()
        if articleID:
            item['articleID'] = articleID[0]
        else:
            item['articleID'] = ''

        articleURL = response.url
        if articleURL:
            item['url'] = articleURL
        else:
            item['url'] = ''

        try:
            raw_date = response.css('time::text')[0].extract().strip()
            if raw_date:
                new_date = raw_date.split(' ')
                del new_date[-1]
                # Sample: Sep 12, 2017,  8:00am PDT
                item['created_on'] = datetime.strptime(' '.join(new_date), '%b %d, %Y, %I:%M%p')
            else:
                item['created_on'] = date.today().strftime('%Y-%m-%d')
        except Exception, e:
            print"Error datetime conversion: {0}".format(e)

        categories = response.css('li.c-entry-group-labels__item a span::text').extract()

        if categories:
            item['categories'] = ','.join(categories)
        else:
            item['categories'] = ''

        search_index = response.request.headers.get('Referer', None).split('=')[-1]
        if search_index:
            item['searchIndex'] = search_index
        else:
            item['searchIndex'] = ''

        cdataId = response.css('div.c-entry-stat--comment ::attr(data-cdata)').extract()

        if cdataId:
            # Convert cdataId to a json object, store objects into item
            cdata = json.loads(cdataId[0])
            item['commentNum'] = cdata['comment_count']
            item['recommendedNum'] = cdata['recommended_count']
        else:
            item['commentNum'] = ''
            item['recommendedNum'] = ''

        author = response.css('span.c-byline__item a::text').extract()

        if author:
            item['author'] = remove_tags(author[0].encode('utf-8'))
        else:
            item['author'] = 'No Author'

        if 'articleID' in item:
            articleId = str(item['articleID'])
            commentjsURL = 'http://www.fieldgulls.com/comments/load_comments/' + articleId
        else:
            commentjsURL = ""

        return item
