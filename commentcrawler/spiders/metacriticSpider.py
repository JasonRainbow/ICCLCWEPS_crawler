import scrapy
import json
import re
from commentcrawler.items import CommentItem


class MetacriticSpider(scrapy.Spider):
    name = "metacritic_spider"
    base_url = "https://www.metacritic.com"

    def __init__(self, keyword):
        self.keyword = keyword
        super(MetacriticSpider, self).__init__()

    def start_requests(self):
        url = f"{self.base_url}/search/{self.keyword.replace(' ', '%20')}"

        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        search_list = response.xpath('//div[contains(@class, "g-grid-container u-grid-columns")]/a/@href')

        if search_list and search_list[0].get():
            uri = search_list[0].get()
            if uri.split("/")[-3] != "movie":
                return
            url = self.base_url + uri + "user-reviews"
            yield scrapy.Request(url, callback=self.parse_comments)

    def parse_comments(self, response):
        movie_name = response.url.split("/")[-3]
        total = re.findall("total:(\\d+)", response.text)[0]
        total = int(total)
        apiKey = re.findall("apiKey=(.*?)&", response.text)[0]

        for i in range(0, total, 50):
            url = f"https://internal-prod.apigee.fandom.net/v1/xapi/reviews/metacritic/user/movies/{movie_name}/web?apiKey={apiKey}&offset={i}&limit=50&filterBySentiment=all&sort=date&componentName=user-reviews&componentDisplayName=user%20Reviews&componentType=ReviewList"

            yield scrapy.Request(url, callback=self.parse_comments2)

    def parse_comments2(self, response):
        res_data = json.loads(response.text)
        items = res_data["data"]["items"]

        for comment_struct in items:
            reviewer = comment_struct["author"]
            home_url = f"{self.base_url}/user/{reviewer}/"
            release_date = comment_struct["date"]
            likes = 0
            comment = comment_struct["quote"]
            rating = comment_struct["score"]

            item = CommentItem()
            item['work_name'] = self.keyword
            item['reviewer'] = reviewer
            item["home_url"] = home_url
            item['followers'] = 0
            item['release_date'] = release_date
            item['likes'] = likes
            item['comment'] = comment
            item["platform"] = "Metacritic"
            item["country"] = "美国"
            item["rating"] = rating

            yield item
        pass


if __name__ == "__main__":
    from scrapy import cmdline
    cmdline.execute(["scrapy", "crawl", "metacritic_spider", "-a", "keyword=The Irishman"])
