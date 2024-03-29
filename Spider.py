#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import re
import requests
import sys
import traceback
from datetime import datetime
from datetime import timedelta
from lxml import etree


class Weibo:
    cookie = {"Cookie": "SCF=AsmXMrcy1hmpnFKFDKV_ejn7E7HjeoBhG4OoBcaEFKDmsRu6pb64fVDlB5JdD7aaz2vEl87oWd0OvBrfb6XfY00.; _T_WM=b9cfffdcb2a759cc75bcd6b5f16a58bf; MLOGIN=1; M_WEIBOCN_PARAMS=uicode%3D20000174%26featurecode%3D20000320%26fid%3Dhotword; SUB=_2A253-6KNDeRhGeBL7lEY8irKzD6IHXVVB87FrDV6PUJbkdAKLRj3kW1NRxT0B4IUCrUBmx2jcr_nEqnJcSTn0ps5; SUHB=0oU4oDCb4cSQ0-; SSOLoginState=1526715103"}  # 将your cookie替换成自己的cookie

    # Weibo类初始化
    def __init__(self, user_id, filter=0):
        self.user_id = user_id  # 用户id，即需要我们输入的数字，如昵称为“Dear-迪丽热巴”的id为1669879400
        self.filter = filter  # 取值范围为0、1，程序默认值为0，代表要爬取用户的全部微博，1代表只爬取用户的原创微博
        self.username = ''  # 用户名，如“Dear-迪丽热巴”
        self.weibo_num = 0  # 用户全部微博数
        self.weibo_num2 = 0  # 爬取到的微博数
        self.following = 0  # 用户关注数
        self.followers = 0  # 用户粉丝数
        self.weibo_content = []  # 微博内容
        self.publish_time = []  # 微博发布时间
        self.up_num = []  # 微博对应的点赞数
        self.retweet_num = []  # 微博对应的转发数
        self.comment_num = []  # 微博对应的评论数

    # 获取用户昵称
    def get_username(self):
        try:
            url = "https://weibo.cn/%d/info" % (self.user_id)
            html = requests.get(url, cookies=self.cookie).content
            selector = etree.HTML(html)
            username = selector.xpath("//title/text()")[0]
            self.username = username[:-3]
            print(u"用户名: " + self.username)
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    # 获取用户微博数、关注数、粉丝数
    def get_user_info(self):
        try:
            url = "https://weibo.cn/u/%d?filter=%d&page=1" % (
                self.user_id, self.filter)
            html = requests.get(url, cookies=self.cookie).content
            selector = etree.HTML(html)
            pattern = r"\d+\.?\d*"

            # 微博数
            str_wb = selector.xpath(
                "//div[@class='tip2']/span[@class='tc']/text()")[0]
            guid = re.findall(pattern, str_wb, re.S | re.M)
            for value in guid:
                num_wb = int(value)
                break
            self.weibo_num = num_wb
            print(u"微博数: " + str(self.weibo_num))

            # 关注数
            str_gz = selector.xpath("//div[@class='tip2']/a/text()")[0]
            guid = re.findall(pattern, str_gz, re.M)
            self.following = int(guid[0])
            print(u"关注数: " + str(self.following))

            # 粉丝数
            str_fs = selector.xpath("//div[@class='tip2']/a/text()")[1]
            guid = re.findall(pattern, str_fs, re.M)
            self.followers = int(guid[0])
            print(u"粉丝数: " + str(self.followers))

        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    # 获取"长微博"全部文字内容
    def get_long_weibo(self, weibo_link):
        try:
            html = requests.get(weibo_link, cookies=self.cookie).content
            selector = etree.HTML(html)
            info = selector.xpath("//div[@class='c']")[1]
            wb_content = info.xpath("div/span[@class='ctt']")[0].xpath(
                "string(.)").encode(sys.stdout.encoding, "ignore").decode(
                sys.stdout.encoding)
            return wb_content
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    # 获取用户微博内容及对应的发布时间、点赞数、转发数、评论数
    def get_weibo_info(self):
        try:
            url = "https://weibo.cn/u/%d?filter=%d&page=1" % (
                self.user_id, self.filter)
            html = requests.get(url, cookies=self.cookie).content
            selector = etree.HTML(html)
            if selector.xpath("//input[@name='mp']") == []:
                page_num = 1
            else:
                page_num = (int)(selector.xpath(
                    "//input[@name='mp']")[0].attrib["value"])
            pattern = r"\d+\.?\d*"
            for page in range(1, page_num + 1):
                url2 = "https://weibo.cn/u/%d?filter=%d&page=%d" % (
                    self.user_id, self.filter, page)
                html2 = requests.get(url2, cookies=self.cookie).content
                selector2 = etree.HTML(html2)
                info = selector2.xpath("//div[@class='c']")
                is_empty = info[0].xpath("div/span[@class='ctt']")
                if is_empty:
                    for i in range(0, len(info) - 2):
                        # 微博内容
                        str_t = info[i].xpath("div/span[@class='ctt']")
                        weibo_content = str_t[0].xpath("string(.)").encode(
                            sys.stdout.encoding, "ignore").decode(
                            sys.stdout.encoding)
                        weibo_content = weibo_content[:-1]
                        weibo_id = info[i].xpath("@id")[0][2:]
                        a_link = info[i].xpath(
                            "div/span[@class='ctt']/a/@href")
                        if a_link:
                            if a_link[-1] == "/comment/" + weibo_id:
                                weibo_link = "https://weibo.cn" + a_link[-1]
                                wb_content = self.get_long_weibo(weibo_link)
                                if wb_content:
                                    weibo_content = wb_content
                        self.weibo_content.append(weibo_content)
                        print(u"微博内容：" + weibo_content)

                        # 微博发布时间
                        str_time = info[i].xpath("div/span[@class='ct']")
                        str_time = str_time[0].xpath("string(.)").encode(
                            sys.stdout.encoding, "ignore").decode(
                            sys.stdout.encoding)
                        publish_time = str_time.split(u'来自')[0]
                        if u"刚刚" in publish_time:
                            publish_time = datetime.now().strftime(
                                '%Y-%m-%d %H:%M')
                        elif u"分钟" in publish_time:
                            minute = publish_time[:publish_time.find(u"分钟")]
                            minute = timedelta(minutes=int(minute))
                            publish_time = (
                                datetime.now() - minute).strftime(
                                "%Y-%m-%d %H:%M")
                        elif u"今天" in publish_time:
                            today = datetime.now().strftime("%Y-%m-%d")
                            time = publish_time[3:]
                            publish_time = today + " " + time
                        elif u"月" in publish_time:
                            year = datetime.now().strftime("%Y")
                            month = publish_time[0:2]
                            day = publish_time[3:5]
                            time = publish_time[7:12]
                            publish_time = (
                                year + "-" + month + "-" + day + " " + time)
                        else:
                            publish_time = publish_time[:16]
                        self.publish_time.append(publish_time)
                        print(u"微博发布时间：" + publish_time)

                        str_footer = info[i].xpath("div")[-1]
                        str_footer = str_footer.xpath("string(.)").encode(
                            sys.stdout.encoding, "ignore").decode(sys.stdout.encoding)
                        str_footer = str_footer[str_footer.rfind(u'赞'):]
                        guid = re.findall(pattern, str_footer, re.M)

                        # 点赞数
                        up_num = int(guid[0])
                        self.up_num.append(up_num)
                        print(u"点赞数: " + str(up_num))

                        # 转发数
                        retweet_num = int(guid[1])
                        self.retweet_num.append(retweet_num)
                        print(u"转发数: " + str(retweet_num))

                        # 评论数
                        comment_num = int(guid[2])
                        self.comment_num.append(comment_num)
                        print(u"评论数: " + str(comment_num))

                        self.weibo_num2 += 1

            if not self.filter:
                print(u"共" + str(self.weibo_num2) + u"条微博")
            else:
                print (u"共" + str(self.weibo_num) + u"条微博，其中" +
                       str(self.weibo_num2) + u"条为原创微博"
                       )
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    # 将爬取的信息写入文件
    def write_txt(self):
        try:
            if self.filter:
                result_header = u"\n\n原创微博内容：\n"
            else:
                result_header = u"\n\n微博内容：\n"
            result = (u"用户信息\n用户昵称：" + self.username +
                      u"\n用户id：" + str(self.user_id) +
                      u"\n微博数：" + str(self.weibo_num) +
                      u"\n关注数：" + str(self.following) +
                      u"\n粉丝数：" + str(self.followers) +
                      result_header
                      )
            for i in range(1, self.weibo_num2 + 1):
                text = (str(i) + ":" + self.weibo_content[i - 1] + "\n" +
                        u"发布时间：" + self.publish_time[i - 1] + "\n" +
                        u"点赞数：" + str(self.up_num[i - 1]) +
                        u"	 转发数：" + str(self.retweet_num[i - 1]) +
                        u"	 评论数：" + str(self.comment_num[i - 1]) + "\n\n"
                        )
                result = result + text
            file_dir = os.path.split(os.path.realpath(__file__))[
                0] + os.sep + "weibo"
            if not os.path.isdir(file_dir):
                os.mkdir(file_dir)
            file_path = file_dir + os.sep + "%d" % self.user_id + ".txt"
            f = open(file_path, "wb")
            f.write(result.encode(sys.stdout.encoding))
            f.close()
            print(u"微博写入文件完毕，保存路径:")
            print(file_path)
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    # 运行爬虫
    def start(self):
        try:
            self.get_username()
            self.get_user_info()
            self.get_weibo_info()
            self.write_txt()
            print(u"信息抓取完毕")
            print("===========================================================================")
        except Exception as e:
            print("Error: ", e)


def main():
    try:
        # 使用实例,输入一个用户id，所有信息都会存储在wb实例中
        user_id = 3890184351  # 可以改成任意合法的用户id（爬虫的微博id除外）
        filter = 1  # 值为0表示爬取全部微博（原创微博+转发微博），值为1表示只爬取原创微博
        wb = Weibo(user_id, filter)  # 调用Weibo类，创建微博实例wb
        wb.start()  # 爬取微博信息
        print(u"用户名：" + wb.username)
        print(u"全部微博数：" + str(wb.weibo_num))
        print(u"关注数：" + str(wb.following))
        print(u"粉丝数：" + str(wb.followers))
        if wb.weibo_content:
            print(u"最新/置顶 微博为：" + wb.weibo_content[0])
            print(u"最新/置顶 微博发布时间：" + wb.publish_time[0])
            print(u"最新/置顶 微博获得赞数：" + str(wb.up_num[0]))
            print(u"最新/置顶 微博获得转发数：" + str(wb.retweet_num[0]))
            print(u"最新/置顶 微博获得评论数：" + str(wb.comment_num[0]))
    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()


if __name__ == "__main__":
    main()
