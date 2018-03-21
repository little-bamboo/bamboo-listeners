from scrapy.spiders import Spider, Request
from scrapy.utils.markup import remove_tags
import json

from datetime import datetime, date

from sbnation.items import SBNationArticle

from sqlalchemy import create_engine


class SBNationArticlesSpider(Spider):
    name = "sbnation-articles"

    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
         Chrome/48.0.2564.116 Safari/537.36'
    }

    def __init__(self, domain='', mysqlauth='../../config/mysqlauth.json'):
        # Call super to initialize the instance
        super(Spider, self).__init__()

        self.domain = domain
        self.current_year = datetime.now().year
        self.search_to_year = datetime.now().year
        self.search_to_month = datetime.now().month

        mysql_auth = json.loads(open(mysqlauth, 'r').read())
        self.user = mysql_auth['user']
        self.password = mysql_auth['password']
        self.database = mysql_auth['database']
        self.host = mysql_auth['host']
        self.port = mysql_auth['port']
        self.table_name = "sbn_articles"

    def get_current_articles(self):

        # Get table column for articleid and commentjsurl

        print ("reading articles table for comment URL list")
        engine = create_engine('mysql+mysqlconnector://' +
                               self.user + ':' +
                               self.password + '@' +
                               self.host + ':' +
                               self.port + '/' +
                               self.database)
        conn = engine.connect()

        # Add 'LIMIT 200' to query for testing
        url_article_list = conn.execute(
            "SELECT url FROM " + self.table_name + "  WHERE search_index='" + self.domain +
            "' AND created_on > NOW() - INTERVAL 30 DAY").fetchall()

        article_list = [x[0] for x in url_article_list]
        return article_list

    def start_requests(self):

        # Build a list of URLs using the search URL and paginating through results
        try:
            while self.current_year >= self.search_to_year:
                current_month = 12
                while current_month >= self.search_to_month:
                    url = 'https://www.' + str(self.domain) + '.com/archives/' + str(self.current_year) + '/' + str(
                        current_month)
                    print "URL: {0}".format(url)
                    yield Request(url=url, headers=self.headers, callback=self.parse)
                    # print "Current Month: {0} Current Year: {1}".format(current_month, self.current_year)
                    current_month -= 1
                self.current_year -= 1
        except Exception, e:
            print "Out of Date Range Error: {0}".format(e)

    def parse(self, response):

        article_links = response.xpath('//h2[contains(@class, "c-entry-box--compact__title")]/a/@href').extract()

        existing_articles = self.get_current_articles()

        articles = set(article_links) - set(existing_articles)

        for article in articles:
            yield Request(url=article, headers=self.headers, callback=self.parse_article)

        

    def parse_article(self, response):
        item = SBNationArticle()

        title = response.css('title').extract()
        if title:
            item['title'] = remove_tags(title[0]).encode('utf-8').strip()
        else:
            item['title'] = 'No Title Found'

        body = response.css('div.c-entry-content').extract()
        if body:
            item['body'] = body[0].encode('utf-8').strip()
        else:
            item['body'] = 'No body text found'

        article_id = response.css('body ::attr(data-entry-id)').extract()
        if article_id:
            item['article_id'] = article_id[0]
        else:
            item['article_id'] = ''

        article_url = response.url
        if article_url:
            item['url'] = article_url
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
                item['created_on'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        except Exception, e:
            # print"Error datetime conversion: {0}".format(e)
            item['created_on'] = datetime.now().strftime("%Y-%m-%d %H:%M")

        categories = response.css('li.c-entry-group-labels__item a span::text').extract()

        if categories:
            item['categories'] = ','.join(categories).encode('utf-8')
        else:
            item['categories'] = ''

        search_index = self.domain
        if search_index:
            item['search_index'] = search_index
        else:
            item['search_index'] = ''

        cdata_id = response.css('div.c-entry-stat--comment ::attr(data-cdata)').extract()

        if cdata_id:
            # Convert cdataId to a json object, store objects into item
            cdata = json.loads(cdata_id[0])
            item['comment_num'] = cdata['comment_count']
            item['recommended_num'] = cdata['recommended_count']
        else:
            item['comment_num'] = 0
            item['recommended_num'] = 0

        author = response.css('span.c-byline__item a::text').extract()

        if author:
            item['author'] = remove_tags(author[0]).encode('utf-8').strip()
        else:
            item['author'] = 'No Author'

        return item
