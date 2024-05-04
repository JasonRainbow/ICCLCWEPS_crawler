import pandas as pd
import scrapy
import json
import re
from commentcrawler.items import CommentItem


class LetterBoxedCommentsSpider(scrapy.Spider):
    name = "letterboxed_comments_spider"
    base_url = "https://letterboxd.com"

    def __init__(self, keyword):
        self.keyword = keyword
        super(LetterBoxedCommentsSpider, self).__init__()

    def start_requests(self):
        url = f"{self.base_url}/search/{self.keyword.replace(' ', '+')}/"

        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        comment_page_url = self.base_url + response.xpath('//span[@class="film-title-wrapper"]/a/@href')[0].get()
        comment_page_url = comment_page_url + "reviews/by/added/"
        page_num = 3
        # print(response.text)
        for i in range(1, page_num + 1):
            url = f"{comment_page_url}page/{i}/"

            yield scrapy.Request(url, callback=self.parse_comments)

    def parse_comments(self, response):
        comments_struct_list = response.xpath('//li[@class="film-detail"]')
        for comments_struct in comments_struct_list:
            reviewer = comments_struct.xpath('.//strong[@class="name"]/text()')[0].get()
            avatar = comments_struct.xpath('.//a[contains(@class, "avatar")]/img/@src')[0].get()
            home_url = self.base_url + comments_struct.xpath('.//a[contains(@class, "avatar")]/@href')[0].get()
            try:
                release_date = comments_struct.xpath('.//span[@class="_nobr"]//text()')[0].get()
            except:
                release_date = comments_struct.xpath('.//span[@class="_nobr"]/time/@datetime')[0].get()
                print(release_date)
            release_date = str(pd.to_datetime(release_date).date())

            comment = comments_struct.xpath('string(.//div[@class="body-text -prose collapsible-text"])')[0].get().strip()
            more_btn = comments_struct.xpath('.//div[@class="collapsed-text"]')
            if more_btn:
                has_more = True
            else:
                has_more = False
            rating_ = comments_struct.xpath('.//span[contains(@class, "rating")]/text()')
            if rating_ and rating_[0].get():
                rating_ = rating_[0].get().strip()
                mp = {"★": 0, "½": 0}
                for e in rating_:
                    mp[e] += 1
                rating = mp["★"] + mp["½"] * 0.5
            else:
                rating = 0

            item = CommentItem()
            item['work_name'] = self.keyword
            item['reviewer'] = reviewer
            item["avatar"] = avatar
            item["home_url"] = home_url
            item['followers'] = 0
            item['release_date'] = release_date

            item['comment'] = comment
            item["platform"] = "Letterboxed"
            item["country"] = "美国"
            item["rating"] = rating

            more_comments_url = comments_struct.xpath('.//div[@class="body-text -prose collapsible-text"]/@data-full-text-url')[0].get()
            more_comments_url = self.base_url + more_comments_url
            likeableUid = comments_struct.xpath('.//p[@data-likeable-name="review"]/@data-likeable-uid')[0].get()

            like_cnt_url = f"https://letterboxd.com/ajax/letterboxd-metadata?likeables={likeableUid}&likeCounts={likeableUid}"

            yield scrapy.Request(like_cnt_url,
                                 meta={"item": item,
                                       "more_comments_url": more_comments_url,
                                       "has_more": has_more},
                                 method="GET", callback=self.parse_likes)

    def parse_likes(self, response):
        item = response.meta["item"]
        has_more = response.meta["has_more"]
        res_data = json.loads(response.text)
        likes = res_data["likeables"][0]["count"]
        item["likes"] = likes

        if has_more:
            more_comments_url = response.meta["more_comments_url"]
            yield scrapy.Request(more_comments_url, meta={"item": item}, callback=self.parse_more)
        else:
            yield item

    def parse_more(self, response):
        item = response.meta["item"]
        item["comment"] = response.text.strip()

        yield item


if __name__ == "__main__":
    from scrapy import cmdline
    cmdline.execute(["scrapy", "crawl", "letterboxed_comments_spider", "-a", "keyword=the wandering earth"])
