import scrapy
import requests
import json
from datetime import datetime
from commentcrawler.items import CommentItem


headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}
payload = {
    'after': "",
    'pageCount': 20,
}

class RottentomatoesSpider(scrapy.Spider):
    name = 'RottentomatoesSpider'
    base_url = "https://www.rottentomatoes.com"
    start_urls = []
    cnt = 0

    def __init__(self, keyword: str=None, *args, **kwargs):
        super(RottentomatoesSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword

    # 发起作品搜索请求
    def start_requests(self):
        url = f"https://www.rottentomatoes.com/search?search={self.keyword.replace(' ', '_')}"
        yield scrapy.Request(url=url, callback=self.parse_work_search)

    # 解析作品搜索页面 获取作品网址
    def parse_work_search(self, response):
        search_result = response.xpath("//search-page-result[@type='movie']")
        work_urls = search_result.xpath(".//a[@data-qa='info-name']/@href")
        # 判断有无该作品 若有则匹配结果中的第一个作品连接
        if len(work_urls) > 0:
            work_url = work_urls.extract_first()
            # 发起该作品的用户评论页面请求 回调用户评论页面解析方法
            yield scrapy.Request(url=work_url + '/reviews?type=user', callback=self.parse_work_comments_page)

    # 解析作品用户评论页面 爬取评论用户名称、用户评分、评论日期、评论内容
    def parse_work_comments_page(self, response):
        # 获取最初页面json响应数据的请求url
        inital_page_url = self.base_url + response.xpath("//load-more-manager/@endpoint").extract_first()
        res_data = requests.get(url=inital_page_url, headers=headers, proxies={"https": "http://127.0.0.1:10809"}).text
        res_data = json.loads(res_data)  # 将响应数据转为json格式数据
        # 获取当前页评论信息
        comment_list = res_data["reviews"] if 'reviews' in res_data else []
        # 保存当前页评论数据
        for comment in comment_list:
            item = CommentItem()
            item["work_name"] = self.keyword
            item["reviewer"] = comment["userDisplayName"] if 'userDisplayName' in comment else ''
            item["avatar"] = ""
            item["followers"] = 0
            comment_date = comment["creationDate"]
            date_object = datetime.strptime(comment_date, "%b %d, %Y")
            formatted_comment_date = date_object.strftime("%Y-%m-%d")
            item["release_date"] = formatted_comment_date
            item["likes"] = 0
            item["comment"] = comment["quote"]
            item["translated_comment"] = comment["quote"]  # 并未翻译 用的原文
            item["rating"] = comment["rating"] if 'rating' in comment else '无'
            item["platform"] = "烂番茄"
            item["country"] = "未知"
            self.cnt += 1
            yield item
        print(self.cnt)

        # 获取下一页的token 若存在下一页则持续爬取下一页评论数据 直至爬完最后一页的评论数据
        if 'endCursor' in res_data["pageInfo"]:
            next_page_token = res_data["pageInfo"]["endCursor"]
            # 更改请求参数after值
            payload["after"] = next_page_token
            while True:
                res_data = requests.get(url=inital_page_url, params=payload,
                                        headers=headers, proxies={"https": "http://127.0.0.1:10809"}).text
                res_data = json.loads(res_data)  # 将响应数据转为json格式数据
                # 获取每页评论信息
                comment_list = res_data["reviews"] if 'reviews' in res_data else []
                # 保存当前页评论数据
                for comment in comment_list:
                    item = CommentItem()
                    item["work_name"] = self.keyword
                    item["reviewer"] = comment["userDisplayName"] if 'userDisplayName' in comment else ''
                    item["avatar"] = ''
                    item["followers"] = 0
                    comment_date = comment["creationDate"]
                    date_object = datetime.strptime(comment_date, "%b %d, %Y")
                    formatted_comment_date = date_object.strftime("%Y-%m-%d")
                    item["release_date"] = formatted_comment_date
                    item["likes"] = 0
                    item["comment"] = comment["quote"]
                    item["translated_comment"] = comment["quote"]  # 并未翻译 用的原文
                    item["rating"] = comment["rating"] if 'rating' in comment else '无'
                    item["platform"] = "烂番茄"
                    item["country"] = "未知"

                    self.cnt += 1
                    yield item
                print(self.cnt)

                # 判断当前页是否有下一页 若没有（无endCursor键）则退出循环 有则继续爬取下一页评论数据
                if 'endCursor' in res_data["pageInfo"]:
                    # 获取下一页的token
                    next_page_token = res_data["pageInfo"]["endCursor"]
                    payload["after"] = next_page_token  # 更改请求参数after值
                else:
                    break


if __name__ == "__main__":
    keyword = "The Wandering Earth II"
    from scrapy import cmdline
    cmdline.execute(['scrapy', 'crawl', 'RottentomatoesSpider', '-a', f"keyword={keyword}"])
