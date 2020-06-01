# -*- coding: utf-8 -*-
import scrapy
from selenium import  webdriver
import time

from selenium.webdriver.common.keys import Keys


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']

    def start_requests(self):
        # 本地启动chrome
        from selenium.webdriver.chrome.options import Options
        chrome_option = Options()
        chrome_option.add_argument("--disable-extensions")
        chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        browser = webdriver.Chrome(executable_path=
                                   "C:/Users/Administrator/PycharmProjects/Envs/Scripts/chromedriver.exe"
                                   , chrome_options=chrome_option)
        browser.get("https://www.zhihu.com/signin")

        browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[1]/div[2]").click()
        browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(Keys.CONTROL + "a")
        browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys("16601052213")
        browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys("16601052213")
        browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input"
                                      ).send_keys(Keys.CONTROL + "a")
        browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input"
                                      ).send_keys("ZHUHAIOO00")
        browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()
        time.sleep(60)
