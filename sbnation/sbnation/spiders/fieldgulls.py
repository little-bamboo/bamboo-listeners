import scrapy

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

    def start_requests(self):
        urls = ['http://www.fieldgulls.com/2016/12/8/13876732/seattle-seahawks-earl-thomas-iii-kam-chancellor-pete-carroll-richard-sherman-legion-of-boom-safety']
        for url in urls:
            yield scrapy.Request(url=url,headers=self.headers, callback=self.parse)

    def parse(self, response):

        print response.css('h1.c-page-title').extract()
        #print response.xpath('/html/body/section/section/div[2]/div[1]/div[1]').extract()
        print response.css('span.c-entry-stat__comment-data').extract()[1]
        print response.text


# http://www.fieldgulls.com/comments/load_comments/13640773?t=1481258642995
#headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}


# First is start url - search url?
# Second, store urls you want to search in a list
# Pass list to iterable and yield returns


# http://www.fieldgulls.com/comments/load_comments/13640773?t=14812605 46345