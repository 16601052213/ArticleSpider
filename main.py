# -*- coding: utf-8 -*-
__author__ = 'zhuhai'
__date__ = '2020/5/31 0:12'
from scrapy.cmdline import execute
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 博客园
# execute(["scrapy", "crawl", "cnblogs"])

# 知乎
execute(["scrapy", "crawl", "zhihu"])
