import pandas as pd
import scrapy
import json
import re
from commentcrawler.items import ProfessionalReview


class TheVergeReviewsSpider(scrapy.Spider):
    name = "theverge_reviews_spider"
    base_url = "https://www.theverge.com"

    def __init__(self, keyword):
        self.keyword = keyword
        super(TheVergeReviewsSpider, self).__init__()

    def start_requests(self):
        url = f"{self.base_url}/api/search?q={self.keyword.replace(' ', '%20')}&page=0"

        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        res_data = json.loads(response.text)
        article_links = res_data["items"]
        for link in article_links:
            yield scrapy.Request(link["link"], callback=self.parse_review)

    def parse_review(self, response):
        # print(response.url)
        try:
            contents = response.xpath('//div[@class="duet--article--article-body-component"]')
            # print(contents)
            if not contents or not contents[0].get():
                return
            content = ""
            for e in contents:
                content += e.xpath('string(.//*)')[0].get().strip() + "\n"
            content = content.strip()
            # print(content)
            title = response.xpath('//h1/text()')[0].get()
            report_date = response.xpath('//article[@id="content"]//time/@datetime')[0].get()
            report_date = str(pd.to_datetime(report_date).date())
            reviewer = response.xpath('//p[@class="duet--article--article-byline max-w-[550px] font-polysans text-12 leading-120"]//a[@class="hover:shadow-underline-inherit"]/text()')[0].get()
            home_url = response.xpath('//p[@class="duet--article--article-byline max-w-[550px] font-polysans text-12 leading-120"]//a[@class="hover:shadow-underline-inherit"]/@href')[0].get()
            home_url = self.base_url + home_url

            item = ProfessionalReview()
            item["work_name"] = self.keyword
            item["title"] = title
            item["report_date"] = report_date
            item["reviewer"] = reviewer
            item["home_url"] = home_url
            item["content"] = content
            item["platform"] = "The Verge"
            item["country"] = "美国"

            yield item
        except:
            pass


if __name__ == "__main__":
    from scrapy import cmdline
    cmdline.execute(["scrapy", "crawl", "theverge_reviews_spider", "-a", "keyword=the wandering earth"])
