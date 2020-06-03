# -*- coding: utf-8 -*-
import datetime
import json
import re
from urllib import parse

from ArticleSpider.items import ZhihuQuestionItem, ZhihuAnswerItem
from scrapy.loader import ItemLoader
from selenium.webdriver.chrome.options import Options

import scrapy
import mouse
from selenium import webdriver
import time
import pickle
import base64

from tools.chaojiying import Chaojiying_Client
from zheye import zheye
from tools import chaojiying
from selenium.webdriver.common.keys import Keys


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']
    # question的第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B*%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B*%5D.mark_infos%5B*%5D.url%3Bdata%5B*%5D.author.follower_count%2Cbadge%5B*%5D.topics&offset={2}&limit={1}&sort_by=default&platform=desktop"

    def parse(self, response):
        """
        提取出html页面中的所有url 并跟踪这些url进一步爬取
        如果提取的url中格式为 /question/xxx 就下载之后进入解析函数
        :param response:
        :return:
        """
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("http") else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                #如果提取到question相关的页面则下载后交由提取函数进行提取
                request_url = match_obj.group(1)
                yield scrapy.Request(request_url, callback=self.parse_question)
                break
            else:
                #如果不是question页面则直接进一步跟踪
                # yield scrapy.Request(url, callback=self.parse)
                pass

    def parse_question(self, response):
        #处理question页面， 从页面中提取出具体的question item
        if "QuestionHeader-title" in response.text:
            #处理新版本
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
            if match_obj:
                question_id = int(match_obj.group(2))

        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        item_loader.add_css("title", "h1.QuestionHeader-title::text")
        item_loader.add_css("content", ".QuestionHeader-detail")
        item_loader.add_value("url", response.url)
        item_loader.add_value("zhihu_id", question_id)
        item_loader.add_css("answer_num", ".List-headerText span::text")
        item_loader.add_xpath("comments_num", "//*[@class='QuestionHeader-Comment']/button/text()")
        item_loader.add_xpath("watch_user_num", "//*[@class='QuestionHeader-follow-status']/div/div/button/div/strong/text()")
        item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")
        question_item = item_loader.load_item()

        yield scrapy.Request(self.start_answer_url.format(question_id, 3, 0), callback=self.parse_answer)
        yield question_item

    def parse_answer(self, reponse):
        # 处理question的answer
        ans_json = json.loads(reponse.text)
        is_end = ans_json["paging"]["is_end"]
        next_url = ans_json["paging"]["next"]

        # 提取answer的具体字段
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["parise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()

            # yield answer_item

        if not is_end:
            yield scrapy.Request(next_url,  callback=self.parse_answer)

    def start_requests(self):
        # 本地启动chrome
        chrome_option = Options()
        chrome_option.add_argument("--disable-extensions")
        chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        browser = webdriver.Chrome(executable_path=
                                   "C:/Users/Administrator/PycharmProjects/Envs/Scripts/chromedriver.exe"
                                   , chrome_options=chrome_option)
        try:
            browser.maximize_window()
        except:
            pass
        try:
            browser.get("https://www.zhihu.com/signin")
            browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[1]/div[2]").click()
            browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
                Keys.CONTROL + "a")
            browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys("16601052213")
            browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input"
                                          ).send_keys(Keys.CONTROL + "a")
            browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input"
                                          ).send_keys("ZHUHAIOO")
            browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()
            time.sleep(1)
            login_success = False
            while not login_success:
                try:
                    notify_ele = browser.find_element_by_xpath("//*[@id='root']/div/div[2]/header/div[1]/a/svg")
                    login_success = True
                except:
                    pass
                try:
                    english_captcha_element = browser.find_element_by_xpath(
                        '//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[4]/div/span/div/img')
                except:
                    english_captcha_element = None
                try:
                    chinese_captcha_element = browser.find_element_by_xpath(
                        "//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[4]/div/div[2]/img")
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
                            mouse.move(x_relative + first_position[0],
                                       y_relative + browser_navigation_panel_height + first_position[1])
                            mouse.click()
                            time.sleep(3)
                            mouse.move(x_relative + second_position[0],
                                       y_relative + browser_navigation_panel_height + second_position[1])
                            mouse.click()

                    else:
                        last_position.append([positions[0][1], positions[0][0]])
                        first_position = [int(last_position[0][0]) / 2, int(last_position[0][1] / 2)]
                        mouse.move(x_relative + first_position[0],
                                   y_relative + browser_navigation_panel_height + first_position[1])
                        mouse.click()

                    browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
                        Keys.CONTROL + "a")
                    browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
                        "16601052213")
                    browser.find_element_by_xpath(
                        "//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input"
                        ).send_keys(Keys.CONTROL + "a")
                    browser.find_element_by_xpath(
                        "//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input"
                        ).send_keys("1qaz@4321")
                    browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()

                if english_captcha_element:
                    # 图片保存
                    base64_text = english_captcha_element.get_attribute("src")
                    code = base64_text.replace("data:image/jpg;base64,", "").replace("%0A", "")
                    fh = open("yzm_en.jpeg", "wb")
                    fh.write(base64.b64decode(code))
                    fh.close()

                    chaojiying = Chaojiying_Client('16601052213', 'ZHUHAIOO00', '905609')
                    im = open('yzm_en.jpeg', 'rb').read()
                    json_data = chaojiying.PostPic(im, 1902)
                    code = json_data["pic_str"]
                    while json_data["err_no"] != 0:
                        if code == "":
                            json_data = chaojiying.PostPic(im, 1902)
                            code = json_data["pic_str"]
                        else:
                            break

                    browser.find_element_by_xpath(
                        '//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[4]/div/div/label/input').send_keys(
                        Keys.CONTROL + "a")
                    browser.find_element_by_xpath(
                        '//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[4]/div/div/label/input').send_keys(
                        code)

                    browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
                        Keys.CONTROL + "a")
                    browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
                        "16601052213")
                    browser.find_element_by_xpath(
                        "//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input"
                        ).send_keys(Keys.CONTROL + "a")
                    browser.find_element_by_xpath(
                        "//*[@id='root']/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input"
                        ).send_keys("1qaz@4321")
                    browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()
        except:
            cookies = browser.get_cookies()
            pickle.dump(cookies, open("C:/Users/Administrator/PycharmProjects/Envs/Scripts/ArticleSpider/cookies/zhihu.cookie", "wb"))
            cookie_dict = {}
            for cookie in cookies:
                cookie_dict[cookie["name"]] = cookie["value"]

            return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]

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
