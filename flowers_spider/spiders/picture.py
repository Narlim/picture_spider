# -*- coding: utf-8 -*-
import scrapy
import json

from scrapy import Request
from scrapy_splash import SplashRequest
from scrapy.loader import ItemLoader
from flowers_spider.items import FlowersSpiderItem

class PictureSpider(scrapy.Spider):
    name = 'picture'
    allowed_domains = ['huaban.com']
    
    start_urls = ['https://huaban.com/favorite/beauty/?k457pe8h&max=2839114681&limit=20&wfl=1',]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                'Accept': 'application/json', 'X-Request': 'JSON', 'X-Requested-With': 'XMLHttpRequest'}

    
    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse, headers=self.headers)
    
    def parse(self, response):
        result_json = json.loads(response.text) 
        pins = result_json['pins']
        pin_list = [pins[pin_id]['pin_id'] for pin_id in range(len(pins))]
        last_pin = pin_list[-1]
        for pin_id in pin_list:
            absolute_url = f'https://huaban.com/pins/{pin_id}/'
            yield SplashRequest(url=absolute_url, callback=self.pic_parse)
        if last_pin:
            next_url = f'https://huaban.com/favorite/beauty/?k457pe8h&max={last_pin}&limit=20&wfl=1'
            yield Request(next_url, headers=self.headers, callback=self.parse)


    def pic_parse(self, response):
        l = ItemLoader(item=FlowersSpiderItem(), response=response)
        pic_url_div = response.xpath('//div[@class="image-holder"]')
        image_urls = 'https:' + pic_url_div.xpath('.//img/@src').extract_first()
        
        l.add_value('image_urls', image_urls)

        return l.load_item()