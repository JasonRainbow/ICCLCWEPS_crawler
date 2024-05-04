import json
import math
import time
from typing import Any
import re

import scrapy
from scrapy.http import Response
from commentcrawler.items import CommentItem, WorkMetrics


headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    "Accept": '*/*',
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": 'gzip, deflate, br, zstd',
    "Connection": 'keep-alive',
    "Cookie": 'session-id=136-4771805-0070566; session-id-time=2082787201l; i18n-prefs=USD; lc-main=zh_CN; ubid-main=133-5602420-4480853; av-timezone=Asia/Shanghai; skin=noskin; sp-cdn="L5Z9:CN"; aws_lang=cn; session-token=oByC4inRQXcTkcNKObG5AN95KoRhYhq/Dmk6HoiR45ZmbzuOmTBNuA60bTIC/gohP1RgSZPfqiSD/a/eLw3Km2/XsnPZyrpY947siLxahjvJtLxeD+w/EM4itmJVk33wnzneal8rVMRRm9TJHTlUqvZqLfXbePsSnTQOrNzSiuwy5p/WGpn/jb5/fK28R7/ko7GgMAKCwuRF0LmyKkA/2NSPl+h3IgZNoweI5/wWABNCvzOjfqWKaXMeeuxP9AvUOrL8v8lGambNulNXMzTWemyvb0tW2lF1soz7yPYfPIKkX13ggrHhPmHbIOLUZqnRulwdDKkf2odeNfDjMCVqGGD9G7Dfo1ce; csm-hit=tb:21HV13HCEBNSZCBDNHSA+s-21HV13HCEBNSZCBDNHSA|1711992483300&t:1711992483300&adb:adblk_no',
    "TE": 'Trailers',
}


class AmazonCommentsSpider(scrapy.Spider):
    name = 'amazon'
    base_url = "https://www.amazon.com"
    comments_url = None

    def __init__(self, keyword, **kwargs: Any):
        self.keyword = keyword
        # print(keyword)
        super().__init__(**kwargs)

    def parse(self, response, **kwargs):
        pass

    def start_requests(self):
        keyword = self.keyword.replace(" ", "+")
        url = f"https://www.amazon.com/s?k={keyword}&__mk_zh_CN=%E4%BA%9A%E9%A9%AC%E9%80%8A%E7%BD%91%E7%AB%99&crid=17VKPNMIJ42YR&sprefix={keyword}%2Caps%2C396&ref=nb_sb_noss_1"

        yield scrapy.Request(url,
                             headers=headers,
                             callback=self.parse_search)

    # 解析搜索界面
    def parse_search(self, response: Response, **kwargs: Any) -> Any:
        # print(response)
        # 提取搜索结果中的第一个链接
        detail_url = response.xpath('//div[@data-cy="title-recipe"]//a/@href')[0].extract()
        detail_url = self.base_url + detail_url
        # print(detail_url)

        yield scrapy.Request(detail_url, headers=headers, callback=self.parse_work_detail)

    # 解析商品详情页面
    def parse_work_detail(self, response):
        self.comments_url = response.xpath('//a[@data-hook="see-all-reviews-link-foot"]/@href')[0].extract()
        self.comments_url = self.base_url + self.comments_url + "&sortBy=recent"
        # print(self.comments_url)

        yield scrapy.Request(self.comments_url, headers=headers, callback=self.parse_comments)

    cnt_page = 1
    total_pages = None

    # 解析评论列表界面
    def parse_comments(self, response: Response):
        if self.total_pages is None:
            try:
                # 获取总评论数，进而计算总页数
                num_info = response.xpath('//div[@data-hook="cr-filter-info-review-rating-count"]/text()')[0].extract()
                self.total_pages = math.ceil(int(re.findall(", (.*?) 带评论", num_info, re.S)[0]) / 10)
                print("总页数：", self.total_pages)
            except:
                return

        # 评论块所在的区域
        comment_wrappers = response.xpath('//div[@data-hook="review"]')

        for comment_wrapper in comment_wrappers:
            extra_info = comment_wrapper.xpath('.//span[@data-hook="review-date"]//text()')[0].extract()
            if "审核" in extra_info:
                extra_info = extra_info.split(" ")
                # 评论发布的日期
                release_date = time.strptime(extra_info[0], "%Y年%m月%d日")
                release_date = time.strftime("%Y-%m-%d", release_date)

                # 评论所属国家
                country = re.findall("在(.*?)审核", extra_info[1])[0]
            else:
                # print(extra_info)
                # 评论所属国家
                country = re.findall("评论地点：(.*?)，", extra_info)[0]
                # 评论时间
                release_date = re.findall("时间：(.*?)$", extra_info)[0]
                release_date = time.strptime(release_date, "%Y年%m月%d日")
                release_date = time.strftime("%Y-%m-%d", release_date)

            # 评论内容
            comment = comment_wrapper.xpath('string(.//span[@data-hook="review-body"])')[0].get().strip()

            reviewer = comment_wrapper.xpath('string(.//span[@class="a-profile-name"])')[0].extract().strip()

            likes = comment_wrapper.xpath('string(.//span[@data-hook="helpful-vote-statement"])')[0].extract().strip()
            if likes:
                likes = int(re.findall("\\d+", likes)[0])
            else:
                likes = 0
            rating = comment_wrapper.xpath('string(.//i[contains(@data-hook, "review-star-rating")])')[0].get().strip()
            if rating:
                rating = float(re.findall("(.*?) 颗星", rating)[0])
            else:
                rating = 0
            avatar = comment_wrapper.xpath('.//div[@class="a-profile-avatar"]/img/@data-src')[0].get()

            item = CommentItem()
            item['work_name'] = self.keyword
            item['reviewer'] = reviewer
            item['followers'] = 0
            item['release_date'] = release_date
            item['likes'] = likes
            item['comment'] = comment
            item['rating'] = rating
            item["platform"] = "Amazon"
            item["country"] = country
            item["avatar"] = avatar

            yield item

        self.cnt_page += 1
        if self.cnt_page <= self.total_pages:
            url = self.comments_url + f"&pageNumber={self.cnt_page}"
            yield scrapy.Request(url, headers=headers, callback=self.parse_comments)


# 爬取指标
class AmazonMetricsSpider(scrapy.Spider):
    name = "amazon_metrics_spider"
    base_url = "https://www.amazon.com"

    def __init__(self, keyword, **kwargs: Any):
        self.keyword = keyword
        # print(keyword)
        super().__init__(**kwargs)

    def parse(self, response, **kwargs):
        pass

    def start_requests(self):
        keyword = self.keyword.replace(" ", "+")
        url = f"https://www.amazon.com/s?k={keyword}&__mk_zh_CN=%E4%BA%9A%E9%A9%AC%E9%80%8A%E7%BD%91%E7%AB%99&crid=17VKPNMIJ42YR&sprefix={keyword}%2Caps%2C396&ref=nb_sb_noss_1"

        yield scrapy.Request(url,
                             headers=headers,
                             callback=self.parse_search)

    def parse_search(self, response):
        detail_url = response.xpath('//div[@data-cy="title-recipe"]//a/@href')[0].extract()

        token = detail_url.split("/")[-2]
        detail_url = f"{self.base_url}/-/zh/product-reviews/{token}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews"

        yield scrapy.Request(detail_url, headers=headers, callback=self.parse_work_detail)

    def parse_work_detail(self, response):
        num_info = response.xpath('//div[@data-hook="cr-filter-info-review-rating-count"]/text()')[0].extract()
        # print(num_info)
        total_comments = int(re.findall(", (.*?) 带评论", num_info, re.S)[0])
        # print("总评论数：", total_comments)
        avg_rating = response.xpath('//span[@data-hook="rating-out-of-text"]/text()')[0].get()
        avg_rating = float(re.findall("^(.*?)星，共", avg_rating, re.S)[0])
        # print("评分", avg_rating)
        item = WorkMetrics()
        item["work_name"] = self.keyword
        item["platform"] = "Amazon"
        item["comment_count"] = total_comments
        item["rating"] = avg_rating
        yield item


if __name__ == "__main__":
    from scrapy import cmdline
    # cmdline.execute(["scrapy", "crawl", "amazon", "-a", "keyword=三体"])
    cmdline.execute(["scrapy", "crawl", "amazon_metrics_spider", "-a", "keyword=the wandering earth"])
