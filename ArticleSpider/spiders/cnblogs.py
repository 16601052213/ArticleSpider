# -*- coding: utf-8 -*-
import json
import re
from urllib import parse
from pydispatch import dispatcher

import scrapy
from ArticleSpider.utils import common
from scrapy import Request, signals
from scrapy.loader import ItemLoader

from ArticleSpider.items import CnblogsArticleItem, ArticleItemLoader
from selenium import webdriver


class CnblogsSpider(scrapy.Spider):
    name = 'cnblogs'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['http://news.cnblogs.com/']

    def __init__(self):
        self.browser = webdriver.Chrome(executable_path="C:/Users/Administrator/PycharmProjects/Envs/Scripts/chromedriver.exe")
        super(CnblogsSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    # def spider_closed(self, spider):
    #     #当爬虫退出的时候关闭chrome
    #     print ("spider closed")
    #     self.browser.quit()

    def parse(self, response):
        post_nodes = response.css('div#news_list .news_block')
        for post_node in post_nodes:
            image_url = post_node.css('.entry_summary a img::attr(src)').extract_first("")
            image_url = parse.urljoin(response.url, image_url)
            post_url = post_node.css('h2 a::attr(href)').extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url},
                          callback=self.parse_detail)
            break
        # 提取下一页并交给scarpy进行下载
        next_url = response.xpath("//a[contains(text(), 'Next >')]/@href").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url),
                          callback=self.parse)

    def parse_detail(self, response):
        match_re_id = re.match(".*?(\d+)", response.url)
        if match_re_id:
            post_id = match_re_id.group(1)

            # article_item = CnblogsArticleItem()
            # title = response.css("#news_title a::text").extract_first("")
            # create_time = response.css("#news_info .time::text").extract_first("")
            # match_re_time = re.match(".*?(\d+.*)", create_time)
            # if match_re_time:
            #     create_time = match_re_time.group(1)
            # content = response.css("#news_content").extract()[0]
            # tag_list = response.css(".news_tags a::text").extract()
            # tags = ",".join(tag_list)

            #
            # article_item["title"] = title
            # article_item["create_time"] = create_time
            # article_item["content"] = content
            # article_item["tags"] = tags
            # article_item["url"] = response.url
            # if response.meta.get("front_image_url", ""):
            #     article_item["front_image_url"] = [response.meta.get("front_image_url", "")]
            # else:
            #     article_item["front_image_url"] = []

            item_loader = ArticleItemLoader(item=CnblogsArticleItem(), response=response)
            item_loader.add_css("title", "#news_title a::text")
            item_loader.add_css("content", "#news_content")
            item_loader.add_css("tags", ".news_tags a::text")
            item_loader.add_css("create_time", "#news_info .time::text")
            item_loader.add_value("url", response.url)
            if response.meta.get("front_image_url", []):
                item_loader.add_value("front_image_url", response.meta.get("front_image_url", []))

            yield Request(url=parse.urljoin(response.url, "/NewsAjax/GetAjaxNewsInfo?contentId={}".format(post_id)),
                          meta={"article_item": item_loader, "url": response.url}, callback=self.parse_nums)

    def parse_nums(self, response):

        j_data = json.loads(response.text)
        item_loader = response.meta.get("article_item", "")

        item_loader.add_value("praise_nums", j_data["DiggCount"])
        item_loader.add_value("fav_nums", j_data["TotalView"])
        item_loader.add_value("comment_nums", j_data["CommentCount"])
        item_loader.add_value("url_object_id", common.get_md5(response.meta.get("url", "")))

        # praise_nums = j_data["DiggCount"]
        # fav_nums = j_data["TotalView"]
        # comment_nums = j_data["CommentCount"]
        #
        # article_item["praise_nums"] = praise_nums
        # article_item["fav_nums"] = fav_nums
        # article_item["comment_nums"] = comment_nums
        # article_item["url_object_id"] = common.get_md5(article_item["url"])
        article_item = item_loader.load_item()

        yield article_item
