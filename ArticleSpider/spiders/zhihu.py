# -*- coding: utf-8 -*-
import scrapy
import mouse
from selenium import webdriver
import time
import pickle
import base64
from zheye import zheye
from tools.yundama_requests import YDMHttp
from selenium.webdriver.common.keys import Keys


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']

    def parse(self, response):
        pass

    def start_requests(self):
        # 本地启动chrome
        from selenium.webdriver.chrome.options import Options
        chrome_option = Options()
        chrome_option.add_argument("--disable-extensions")
        chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        browser = webdriver.Chrome(executable_path=
                                   "C:/Users/issuser/PycharmProjects/Envs/Scripts/chromedriver.exe"
                                   , chrome_options=chrome_option)
        try:
            browser.maximize_window()
        except:
            pass
        browser.get("https://www.zhihu.com/signin")
        browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[1]/div[2]").click()
        browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(Keys.CONTROL + "a")
        browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys("16601052213")
        browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input"
                                      ).send_keys(Keys.CONTROL + "a")
        browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input"
                                      ).send_keys("ZHUHAIOO")
        browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()
        time.sleep(3)
        login_success = False
        while not login_success:
            try:
                notify_ele = browser.find_element_by_xpath("//*[@id='root']/div/div[2]/header/div[1]/a/svg")
                login_success = True
            except:
                pass
            try:
                english_captcha_element = browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[4]/div/span/div/img')
            except:
                english_captcha_element = None
            try:
                chinese_captcha_element = browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[4]/div/div[2]/img")
            except:
                chinese_captcha_element = None
            if chinese_captcha_element:
                # 图片位置坐标x和y
                ele_position = chinese_captcha_element.location
                x_relative = ele_position["x"]
                y_relative = ele_position["y"]
                # 浏览器上部的y的坐标
                browser_navigation_panel_height = 70
                # 图片保存
                base64_text = chinese_captcha_element.get_attribute("src")
                code = base64_text.replace("data:image/jpg;base64,", "").replace("%0A", "")
                fh = open("yzm_cn.jpeg", "wb")
                fh.write(base64.b64decode(code))
                fh.close()

                z = zheye()
                positions = z.Recognize('yzm_cn.jpeg')
                last_position = []
                if len(positions) == 2:
                    # 如果第一个元素的x坐标大于第二个元素的x坐标，则第二个元素是第一个倒立文字
                    if positions[0][1] > positions[1][1]:
                        # 所以列表里放文字的时候返过来放，先放第二个元素的xy，再放第一个元素的xy,后面的是x，前面的是y
                        last_position.append([positions[1][1], positions[1][0]])
                        last_position.append([positions[0][1], positions[0][0]])
                    else:
                        last_position.append([positions[0][1], positions[0][0]])
                        last_position.append([positions[1][1], positions[1][0]])
                        # 浏览器中的图片实际要比
                        first_position = [int(last_position[0][0]) / 2, int(last_position[0][1] / 2)]
                        second_position = [int(last_position[1][0]) / 2, int(last_position[1][1] / 2)]
                        mouse.move(x_relative + first_position[0], y_relative + browser_navigation_panel_height + first_position[1])
                        mouse.click()
                        time.sleep(3)
                        mouse.move(x_relative + second_position[0], y_relative + browser_navigation_panel_height + second_position[1])
                        mouse.click()

                else:
                    last_position.append([positions[0][1], positions[0][0]])
                    first_position = [int(last_position[0][0]) / 2, int(last_position[0][1] / 2)]
                    mouse.move(x_relative + first_position[0],
                               y_relative + browser_navigation_panel_height + first_position[1])
                    mouse.click()

                browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(Keys.CONTROL + "a")
                browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys("16601052213")
                browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input"
                                              ).send_keys(Keys.CONTROL + "a")
                browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input"
                                              ).send_keys("ZHUHAIOO00")
                browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()

            if english_captcha_element:
                # 图片保存
                base64_text = english_captcha_element.get_attribute("src")
                code = base64_text.replace("data:image/jpg;base64,", "").replace("%0A", "")
                fh = open("yzm_en.jpeg", "wb")
                fh.write(base64.b64decode(code))
                fh.close()

                yundama = YDMHttp("da_ge_dal", "dageda", 3129, "40d5ad41c047179fc797631e3b9c3025")
                code = yundama.decode("yzm_en.jpeg", 5000, 60)
                while True:
                    if code == "":
                        code = yundama.decode("yzm_en.jpeg", 5000, 60)
                    else:
                        break
                browser.find_element_by_css_selector('//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[4]/div/span/div/img').send_keys(
                    Keys.CONTROL + "a")
                browser.find_element_by_css_selector('//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[4]/div/span/div/img').send_keys(
                    code)

                browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(Keys.CONTROL + "a")
                browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys("16601052213")
                browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input"
                                              ).send_keys(Keys.CONTROL + "a")
                browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input"
                                              ).send_keys("ZHUHAIOO00")
                browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()

        time.sleep(5)

    # def start_requests(self):
    #     # 本地启动chrome
    #     from selenium.webdriver.chrome.options import Options
    #     chrome_option = Options()
    #     chrome_option.add_argument("--disable-extensions")
    #     chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    #
    #     browser = webdriver.Chrome(executable_path=
    #                                "C:/Users/issuser/PycharmProjects/Envs/Scripts/chromedriver.exe"
    #                                , chrome_options=chrome_option)
    #     # browser.get("https://www.zhihu.com/signin")
    #     #
    #     # browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[1]/div[2]").click()
    #     # browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(Keys.CONTROL + "a")
    #     # browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys("16601052213")
    #     # browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input"
    #     #                               ).send_keys(Keys.CONTROL + "a")
    #     # browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input"
    #     #                               ).send_keys("ZHUHAIOO00")
    #     # browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()
    #
    #     browser.get("https://www.zhihu.com/")
    #
    #     cookies = pickle.load(open("C:/Users/issuser/PycharmProjects/ArticleSpider/cookies/zhihu.cookie", "rb"))
    #     cookie_dict = {}
    #     for cookie in cookies:
    #         cookie_dict[cookie["name"]] = cookie["value"]
    #     return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]
    #
    #     # cookies = browser.get_cookies()
    #     # pickle.dump(cookies, open("C:/Users/issuser/PycharmProjects/ArticleSpider/cookies/zhihu.cookie", "wb"))
    #     # cookie_dict = {}
    #     # for cookie in cookies:
    #     #     cookie_dict[cookie["name"]] = cookie["value"]
    #     #
    #     # return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]
