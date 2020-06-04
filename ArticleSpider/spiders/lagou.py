# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['http://www.lagou.com/']

    rules = (
        Rule(LinkExtractor(allow=r'beijing-zhaopin/.*'), follow=True),
        Rule(LinkExtractor(allow=r'gongsi/\d+.html'), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html.*'), callback='parse_job', follow=True),
    )

    def parse_job(self, response):

        i = {}
        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        #item['name'] = response.xpath('//div[@id="name"]').get()
        #item['description'] = response.xpath('//div[@id="description"]').get()
        return i
