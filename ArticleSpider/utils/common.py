# -*- coding: utf-8 -*-
__author__ = 'zhuhai'
__date__ = '2020/5/31 17:26'

import hashlib
import re


def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)

    return m.hexdigest()


def extract_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums


def delete_douhao(num):
    # 传入一个字符串将数字中的","去掉，提纯数字
    while 1:
        mm = re.search("\d,\d", num)
        if mm:
            mm = mm.group()
            num = num.replace(mm, mm.replace(",", ""))
        else:
            break
    return int(num)
