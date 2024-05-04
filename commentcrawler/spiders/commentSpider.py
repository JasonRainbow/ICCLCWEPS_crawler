# 获取豆瓣读书Top250的评论

import scrapy
from bs4 import BeautifulSoup
from commentcrawler.items import CommentItem


headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    "Cookie": 'bid=5xinqXzEPI0; __utmc=30149280; ll="118159"; __utmv=30149280.23254; Hm_lvt_6d4a8cfea88fa457c3127e14fb5fabc2=1710072310; talionnav_show_app="0"; Hm_lpvt_6d4a8cfea88fa457c3127e14fb5fabc2=1710072342; _ga=GA1.1.1001125851.1710072325; _ga_Y4GN1R87RG=GS1.1.1710072325.1.1.1710072346.0.0.0; viewed="1007305_1078244_4010136_4828612_26958958_5363767_36104107_30459512_30475767_1082349"; dbcl2="232540855:246If3UiLZs"; ck=tPT3; __utmz=30149280.1711387329.108.28.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; push_noty_num=0; push_doumail_num=0; __gads=ID=a9f39045710b107e-2285344453e20012:T=1689076597:RT=1711889292:S=ALNI_MYirLznxHeR9xKk0iOdVQw5i3WFeA; __gpi=UID=00000c1fcbfee3b7:T=1689076597:RT=1711889292:S=ALNI_MZDlQIkX2tudhURyxTvbqmdjX5fMQ; __eoi=ID=9eb527f720948a0c:T=1711889292:RT=1711889292:S=AA-AfjYDsFppKLe8aSgvUEakHUUW; frodotk_db="97d3c1f5497a64cdc77b45dfdc6f2e67"; ap_v=0,6.0; __utma=30149280.587405364.1689076599.1711889286.1712027565.110; __utmt=1; __utmb=30149280.6.10.1712027565',
    # "Host": 'm.douban.com',
    # "Origin": 'https://www.douban.com',
    # "Referer": 'https://www.douban.com/search?source=suggest&q=%E6%B5%81%E6%B5%AA%E5%9C%B0%E7%90%83',
    # "Connection": 'keep-alive'
}


class CommonSpider(scrapy.Spider):
    # 爬虫名称
    name = 'comment'
    # 允许爬取的网站域名
    allowed_domains = ['book.douban.com']
    # 起始网址
    start_urls = []
    # 获取前2页书籍的评论
    for x in range(2):
        url = "https://book.douban.com/top250?start={}".format(25*x)
        start_urls.append(url)

    # def start_requests(self):
    #     url = "https://m.douban.com/rexxar/api/v2/search?q=%E6%B5%81%E6%B5%AA%E5%9C%B0%E7%90%83&type=&loc_id=&start=0&count=10&sort=relevance&ck=tPT3"
    #
    #     yield scrapy.Request(url, headers=headers, callback=self.parse_douban)
    #
    # def parse_douban(self, response):
    #     print(response)
    #     print(response.text)

    # 解析起始网址
    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'html.parser')
        pl2_list = soup.find_all("tr", class_='item')
        for pl2 in pl2_list:
            # 书籍链接
            book_link = pl2.find("a")['href']
            # 评论链接
            common_link = book_link + "comments/"

            yield scrapy.Request(common_link, headers=headers, callback=self.common_parse)

    # 解析评论
    def common_parse(self, response):
        # print(response.text)
        soup = BeautifulSoup(response.text, 'html.parser')
        # 书籍名称
        bookname = soup.find_all("p", class_='pl2 side-bar-link')[0].find("a").text

        li_list = soup.find_all('li', class_='comment-item')
        for li in li_list:
            common_info = li.find(class_='comment-info')
            # 评论人
            common_id = common_info.find("a").text
            # 评论时间
            common_date = common_info.find(class_="comment-time").text
            # 指数
            common_vote_num = li.find(class_='vote-count').text
            # 评论内容
            common_content = li.find(class_='comment-content').find("span").text

            item = CommentItem()
            item['work_name'] = bookname
            item['platform'] = "豆瓣图书"
            item['reviewer'] = common_id
            item['release_date'] = common_date
            item['likes'] = common_vote_num
            item['comment'] = common_content

            yield item


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'comment'])
