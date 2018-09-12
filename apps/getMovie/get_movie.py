import requests
from lxml import etree
import pymysql
import random
import threading
import time
import logging
from queue import Queue
import re


class MovieSpider():
    def __init__(self):
        self.file_object = open("amazon.txt", 'a')
        self.file_object.write("asin, state\n")

    def randHeader(self):
        head_connection = ['Keep-Alive', 'close']
        head_accept = ['text/html, application/xhtml+xml, */*']
        head_accept_language = ['zh-CN,fr-FR;q=0.5', 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3']
        head_user_agent = ['Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
                           'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; rv:11.0) like Gecko)',
                           'Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1',
                           'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070309 Firefox/2.0.0.3',
                           'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12',
                           'Opera/9.27 (Windows NT 5.2; U; zh-cn)',
                           'Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en) Opera 8.0',
                           'Opera/8.0 (Macintosh; PPC Mac OS X; U; en)',
                           'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.12) Gecko/20080219 Firefox/2.0.0.12 Navigator/9.0.0.6',
                           'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0)',
                           'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)',
                           'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E)',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Maxthon/4.0.6.2000 Chrome/26.0.1410.43 Safari/537.1 ',
                           'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E; QQBrowser/7.3.9825.400)',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0 ',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.92 Safari/537.1 LBBROWSER',
                           'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; BIDUBrowser 2.x)',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/3.0 Safari/536.11']

        header = {
            'Connection': head_connection[0],
            'Accept': head_accept[0],
            'Accept-Language': head_accept_language[1],
            'User-Agent': head_user_agent[random.randrange(0, len(head_user_agent))]
        }
        return header

    def make_url(self, movie_type, movie_num, movie_or_tv, page=1):
        # http://www.ygdy8.net/html/gndy/china/list_4_2.html
        page = page
        if movie_type and movie_num:
            url = "http://www.dytt8.net/html/" + movie_or_tv + "/"
            url += movie_type + "/"
            url += "list_%s" % (str(movie_num))
            url += "_%s" % (str(page))
            url += ".html"
            return url

    def getDataById(self, page=2):
        # if self.findFromDB(query_id=queryId):  # 在一个方法体内调用另一个方法
        #     return
        # url = self.make_url(movie_type, movie_num, movie_or_tv, page=page)  # 获取单页的电影列表链接
        # req = requests.get(url=url, headers=self.randHeader()).text  # 得到单页电影列表的html主体
        # html = etree.HTML(req)  # 把主体转换成可以xpath的格式
        # movie_url_list = html.xpath("//tr[2]/td[2]/b/a[2]/@href")  # 得到进入电影详情的 链接列表（每页的）
        # print("test1", movie_url_list, url)

        url = "https://www.dy2018.com/html/gndy/dyzz/index.html"  # 首页
        url2 = "https://www.dy2018.com/html/gndy/dyzz/index_%d.html" % page  # 第二页
        try:
            ret = requests.get(url=url2, headers=self.randHeader()).text
        except:
            ret = None
        if ret:
            html = etree.HTML(ret)
            movie_url_list = html.xpath("//tr[2]/td[2]/b/a/@href")  # 爬取每页的电影列表的url

            print("test1")
            for movie_url in movie_url_list:
                movie_url = "https://www.dy2018.com" + movie_url  # 电影详情的链接

                try:
                    ret2 = requests.get(url=movie_url, headers=self.randHeader())
                except:
                    continue
                ret2.encoding = "GBK"
                ret2 = ret2.text
                html = etree.HTML(ret2)

                try:
                    download_url = html.xpath("//*[@id='Zoom']/table[1]/tbody/tr/td//a/text()")  # 电影的下载链接
                except:
                    continue
                try:
                    movie_image_url = html.xpath("//p[1]/img/@src")  # 电影的封面图片链接
                except:
                    movie_image_url = ""
                try:
                    movie_image2_url = html.xpath("//div/img/@src")  # 电影的内容介绍图片链接
                except:
                    movie_image2_url = ""
                try:
                    movie_score = float(html.xpath("//div[2]/ul/div[1]/span[1]/strong/text()")[0])  # 电影评分
                except:
                    movie_score = 0
                # movie_type = html.xpath("//div[2]/ul/div[1]/span[2]/a/text()")  # 电影类型
                # movie_release_time = html.xpath("//div[6]/div[2]/ul/div[1]/span[3]/text()")  # 发布时间
                try:
                    movie_detail_info = html.xpath("//p[position()>2 and position()<20]/text()")  # 电影详细信息
                except:
                    movie_detail_info = ""
                try:
                    movie_index_name = html.xpath("//div[2]/div[6]/div[1]/h1/text()")  # 电影页面名称
                except:
                    movie_index_name = ""
                try:
                    translate = movie_detail_info[0]
                except:
                    continue
                try:
                    movie_name = movie_detail_info[1]
                except:
                    movie_name = ""
                try:
                    release_time = movie_detail_info[2]
                except:
                    release_time = 0
                try:
                    area = movie_detail_info[2]  # movie_detail_info[3]
                except:
                    area = ""
                try:
                    movie_type2 = movie_detail_info[3]  # movie_detail_info[4]
                except:
                    movie_type2 = ""
                try:
                    language = movie_detail_info[4]  # movie_detail_info[5]
                except:
                    language = ""
                try:
                    subtitle = movie_detail_info[5]  # movie_detail_info[6]
                except:
                    subtitle = ""
                try:
                    release_detail_time = movie_detail_info[6]  # movie_detail_info[7]  # 需要正则去掉中文，再转成时间戳
                except:
                    release_detail_time = ""
                # size = ''
                # time_long = movie_detail_info[12]  # movie_detail_info[13]
                # director = movie_detail_info[13]  # movie_detail_info[14]
                # performer = movie_detail_info[15]
                if not translate:
                    translate = ""
                if not movie_image_url:
                    movie_image_url = ""
                if not movie_image2_url:
                    movie_image2_url = ""
                if not movie_score:
                    movie_score = 8
                if not area:
                    area = ''
                if not language:
                    language = ""
                if not release_detail_time:
                    release_detail_time = ""
                if not download_url:
                    download_url = "暂无该资源"
                if not movie_index_name:
                    movie_index_name = ""
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>this file has exit", translate)
                if self.findFromDB(title_1=translate):
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>this file has exit", translate)

                    continue
                self.insertIntoDB(title_1=translate, image_url_1=movie_image_url,
                                  image_url_2=movie_image2_url, score=movie_score, show_time=release_time,
                                  area=area,
                                  type=movie_type2, language=language, subtitle=subtitle,
                                  release_time=release_detail_time, download_url=download_url,
                                  remark=movie_index_name)
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>success", translate)

    def findFromDB(self, title_1):
        db = pymysql.connect(host='45.63.51.252', user='root', passwd='123456', db='zoro', port=3306, charset='utf8')
        cursor = db.cursor()
        sql = ' select * from common_movie where title_1 = %s '
        cursor.execute(sql, (title_1))
        db.commit()
        cursor.close()
        db.close()
        return cursor.fetchone() is not None

    def insertIntoDB(self, title_1, image_url_1, image_url_2, score, show_time, area,
                     type, language, subtitle, release_time, download_url, remark):
        now = time.time()
        db = pymysql.connect(host='45.63.51.252', user='root', passwd='123456', db='zoro', port=3306, charset='utf8')
        cursor = db.cursor()
        sql = " insert into common_movie(title_1,image_url_1, image_url_2, score,show_time,area,type,language,subtitle,release_time,download_url,remark,create_time)  values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, (
            title_1, image_url_1, image_url_2, score, show_time, area, type, language,
            subtitle, release_time, download_url, remark, now))
        db.commit()
        cursor.close()
        db.close()


class ThreadCrawl(threading.Thread):  # ThreadCrawl类继承了Threading.Thread类

    def __init__(self, queue):  # 子类特有属性， queue
        FORMAT = time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()) + "[AmazonSpider]-----%(message)s------"
        logging.basicConfig(level=logging.INFO, format=FORMAT)
        threading.Thread.__init__(self)
        self.queue = queue
        self.spider = MovieSpider()  # 子类特有属性spider， 并初始化，将实例用作属性

    def run(self):
        while True:
            success = True
            item = self.queue.get()  # 调用队列对象的get()方法从队头删除并返回一个项目item
            try:
                self.spider.getDataById(item)  # 调用实例spider的方法getDataById(item)
            except:
                success = False
            if not success:
                self.queue.put(item)
            logging.info("now queue size is: %d" % self.queue.qsize())  # 队列对象qsize()方法，返回队列的大小
            self.queue.task_done()  # 队列对象在完成一项工作后，向任务已经完成的队列发送一个信号


class AmazonSpiderJob():
    def __init__(self, size, qs):
        self.size = size  # 将形参size的值存储到属性变量size中
        self.qs = qs

    def work(self):
        toSpiderQueue = Queue()  # 创建一个Queue队列对象
        for i in range(self.size):
            t = ThreadCrawl(toSpiderQueue)  # 将实例用到一个类的方法中
            t.setDaemon(True)
            t.start()
        for q in self.qs:
            toSpiderQueue.put(q)  # 调用队列对象的put()方法，在对尾插入一个项目item
        toSpiderQueue.join()  # 队列对象，等到队列为空，再执行别的操作


#
# class GetMovieInfo(object):
#     def __init__(self):
#         self.xpath_pattern_1 = "//div/ul/li[position()>2 and position()<11]/a/@href"  # 获取首页数据 获得每个分类的链接
#         self.xpath_pattern_2 = "//tr[2]/td[2]/b/a[2]/@href"  # 每个分类里面 获得每个电影的详情链接
#         self.xpath_pattern_3 = "//span/table/tbody/tr/td/a/@href"  # 爬取详细电影下载链接的规则
#         self.xpath_pattern_4 = "//span/p[1]/text()"  # 爬取电影主体信息
#         self.index_url = "http://www.dytt8.net/"  #
#
#         # 连接数据库
#         # self.db = pymysql.connect(host="45.63.51.252", user="root",
#         #                           password="123456", db="zoro", port=3306)
#         #
#         # # 开启游标
#         # self.cur = self.db.cursor()
#
#     def get_response(self, url):
#         response = requests.get(url=url)
#         response = response.text
#         html = etree.HTML(response)
#         return html
#
#     def deal_data(self, url, xpath_pattern):
#         html = self.get_response(url=url)
#         data = html.xpath(xpath_pattern)
#         return data
#
#     def save_to_db(self):
#         pass
#
#     def run(self):
#         # # 第一层是首页中的分类的链接
#         # movie_url_list = self.deal_data(url=self.index_url, xpath_pattern=self.xpath_pattern_1)
#         # for article_url in movie_url_list:
#         #     url = self.index_url + article_url
#         #     print(url)
#         #
#         #     # 第二层各个电影的连接
#         #     movie_url_list = self.deal_data(url=url, xpath_pattern=self.xpath_pattern_2)
#         #     for movie_url in movie_url_list:
#         #
#         #         self.deal_data(url=movie_url, xpath_pattern=self.xpath_pattern_3)
#         #
#         #         print(movie_url)
#         #
#         #         # 第三层电影详情
#
#         # http://www.ygdy8.net/html/gndy/china/list_4_2.html
#         # http://www.ygdy8.net/html/gndy/oumei/list_7_1.html
#         self.deal_data()
#
#
# movie_obj = GetMovieInfo()
# movie_obj.run()
def run():
    print("start spider====")
    movie_obj = MovieSpider()
    for i in range(2, 301):
        print(i)
        movie_obj.getDataById(page=i)
    print("finish spider")
