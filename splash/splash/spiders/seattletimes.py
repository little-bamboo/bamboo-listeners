# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest


class SeattletimesSpider(scrapy.Spider):
    name = "seattletimes"
    allowed_domains = ["seattletimes.com"]
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
        return {png=splash:html()}
    end


    """
    
    def parse(self, response):

        # Push authentication
        return scrapy.FormRequest.from_response(
            response,
            formdata={'username': 'briansc@gmail.com', 'password': 'thomas7'},
            callback=self.process_request
        )

    def process_request(self, response):

        url = 'http://www.seattletimes.com/seattle-news/environment/rare-ice-circle-spinning-in-middle-fork-snoqualmie-river-mesmerizes-then-breaks-apart/#comments'
        yield SplashRequest(url, self.parse_result,
                            endpoint='execute',
                            args={'lua_source': self.script}
                            )

    def parse_result(self, response):
        comments = response.xpath('//*[contains(@class, "fyre-comment-article")]')
        print(comments)

