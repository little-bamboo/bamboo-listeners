import scrapy

from ford_reddit.items import FordRedditItem

class RedditSpider(scrapy.Spider):
    """docstring for RedditSpider"""
    name = "reddit"
    allowed_domains = ["https://www.reddit.com"]
    start_urls = ["https://www.reddit.com/r/Ford/"]

    def parse(self, response):
        print "response: ",response.xpath('//*[contains(@class, "thing")]').extract()

        for sel in response.xpath('//*[contains(@class, "thing")]'):

            print "sel: " , str(sel)
            print "sel.xpath: ", str(sel.xpath)

            title = "title: ", sel.xpath('a')
            link = "link: ", sel.xpath('a/@href').extract()
            desc = "desc: ", sel.xpath('p')

            print title, link, desc

            if len(title) > 0:
                item = FordRedditItem()
                item['title'] = title[0]
                item['link'] = link[0]
                print item



