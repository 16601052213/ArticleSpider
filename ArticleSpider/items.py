# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Identity, MapCompose, Join


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ArticleItemLoader(ItemLoader):
    """
    将ItemLoader默认存的值改为str类型
    """
    default_output_processor = TakeFirst()


def date_convert(value):
    match_re_time = re.match(".*?(\d+.*)", value)
    if match_re_time:
        return match_re_time.group(1)
    else:
        return "1970-07-01"


class CnblogsArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_time = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=Identity()
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    fav_nums = scrapy.Field()
    tags = scrapy.Field(
        output_processor=Join(",")
    )
    content = scrapy.Field()
