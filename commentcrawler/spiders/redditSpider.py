import scrapy
import json
import pandas as pd
from commentcrawler.items import CommentItem


class RedditSpider(scrapy.Spider):
    name = "reddit_spider"
    base_url = "https://www.reddit.com"
    csrf_token = "b667b1d3c9529050b5c2d8b20f6558bf"

    def __init__(self, keyword):
        self.keyword = keyword
        super(RedditSpider, self).__init__()

    def start_requests(self):
        url = f"{self.base_url}/search/?q={self.keyword.replace(' ', '+')}&type=link&cId=2a71d5b8-7c7c-4238-8acf-2930e5a7c686&iId=0de1dd74-e419-4c09-872f-36a12bdcbb97"

        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        search_list = response.xpath('//a[@data-testid="post-title"]/@href')
        # print(search_list)
        limit = 3
        for (i, href) in enumerate(search_list, start=1):
            href = href.get()
            if i > limit:
                break
            uri = href.split("/")
            page_type = uri[-5]
            page_id = uri[-3]
            url = f"https://www.reddit.com/svc/shreddit/comments/{page_type}/t3_{page_id}?render-mode=partial&is_lit_ssr=false&sort=new"

            yield scrapy.Request(url, callback=self.parse_comments)

    def parse_comments(self, response):
        comment_struct_list = response.xpath('//shreddit-comment')
        for comment_struct in comment_struct_list:
            reviewer = comment_struct.xpath('string(./@author)')
            if reviewer and reviewer[0].get():
                reviewer = reviewer[0].get()
            else:
                reviewer = "unknown"
            home_url = comment_struct.xpath('.//faceplate-tracker[@source="post_detail"]/a/@href')
            if home_url and home_url[0].get():
                home_url = self.base_url + home_url[0].get()
            else:
                home_url = ""
            release_date = comment_struct.xpath('.//faceplate-timeago/@ts')[0].get()
            release_date = str(pd.to_datetime(release_date).date())
            likes = comment_struct.xpath('.//shreddit-comment-action-row/@score')
            if likes and likes[0].get():
                likes = likes[0].get()
            else:
                likes = 0
            try:
                comment = comment_struct.xpath('string(.//div[@id="-post-rtjson-content"])')[0].get().strip()
            except:
                continue

            avatar = comment_struct.xpath('.//faceplate-img/@src')
            if avatar and avatar[0].get():
                avatar = avatar[0].get()
            else:
                avatar = "https://styles.redditmedia.com/t5_cy6s3/styles/profileIcon_snoo1083a008-62f0-4563-8711-e16a2df760dc-headshot.png?width=64&height=64&frame=1&auto=webp&crop=64:64,smart&s=cf0f699f3d477aa5ec7fc54ba79accca027a7f2d"

            item = CommentItem()
            item['work_name'] = self.keyword
            item['reviewer'] = reviewer
            item["home_url"] = home_url
            item['followers'] = 0
            item['release_date'] = release_date
            item['likes'] = likes
            item['comment'] = comment
            item["platform"] = "Reddit"
            item["country"] = "美国"
            item["avatar"] = avatar

            # print(item)

            yield item

        next_page_reqs = response.xpath('//faceplate-partial[@method]')
        if next_page_reqs and next_page_reqs[0].get():
            for next_page_req in next_page_reqs:
                print("下一页")
                url = self.base_url + next_page_req.xpath("./@src")[0].get()
                method = next_page_req.xpath("./@method")[0].get()
                next_page_cursor = next_page_req.xpath('.//input[@name="cursor"]/@value')[0].get()
                url = f"{url}&cursor={next_page_cursor}&csrf_token={self.csrf_token}"
                yield scrapy.Request(url, method=method, callback=self.parse_comments)

        pass


if __name__ == "__main__":
    from scrapy import cmdline
    cmdline.execute(["scrapy", "crawl", "reddit_spider", "-a", "keyword=the wandering earth"])
