# -*- coding: utf-8 -*-
__author__ = 'zhuhai'
__date__ = '2020/5/31 17:26'

import hashlib


def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)

    return m.hexdigest()
