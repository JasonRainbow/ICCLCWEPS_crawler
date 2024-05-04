import re

import scrapy
from commentcrawler.items import CommentItem
import pandas as pd


class IMDbSpider(scrapy.Spider):
    # 爬虫名
    name = "IMDbSpider"
    # 网站基础URL
    base_url = "https://www.imdb.com"

    def __init__(self, keyword):
        self.keyword = keyword
        super(IMDbSpider, self).__init__()

    # 爬虫起始函数
    def start_requests(self):
        url = f"https://www.imdb.com/find/?q=the%20wandering%20earth&ref_=nv_sr_sm"

        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        movie_hrefs = response.xpath('//section[@data-testid="find-results-section-title"]//a[@class="ipc-metadata-list-summary-item__t"]/@href')
        if len(movie_hrefs) == 0:
            return
        movie_href = self.base_url + movie_hrefs[0].get()

        yield scrapy.Request(movie_href, callback=self.parse_movie_page)

    cnt_num = 0
    limit_num = 200

    def parse_movie_page(self, response):
        reviews_url = response.xpath('//div[@data-testid="reviews-header"]//a/@href')[0].get()
        reviews_url = self.base_url + reviews_url + "&sort=submissionDate&dir=desc&ratingFilter=0"

        yield scrapy.Request(reviews_url,
                             meta={"reviews_url": reviews_url},
                             callback=self.parse_comments)

    def parse_comments(self, response: scrapy.http.Response):

        comment_struct_list = response.xpath('//div[@class="review-container"]')
        for comment_struct in comment_struct_list:
            try:
                reviewer = comment_struct.xpath('string(.//span[@class="display-name-link"])')[0].get()
                home_url = self.base_url + comment_struct.xpath('.//span[@class="display-name-link"]/a/@href')[0].get()
                release_date = comment_struct.xpath('string(.//span[@class="review-date"])')[0].get()
                release_date = str(pd.to_datetime(release_date).date())
                likes = comment_struct.xpath('.//div[@class="actions text-muted"]/text()')[0].get().strip()
                likes = int(re.findall("^\\d+", likes)[0])
                comment = comment_struct.xpath('string(.//div[@class="text show-more__control"])')[0].get().strip()
                rating = comment_struct.xpath('string(.//span[@class="rating-other-user-rating"])')
                if rating:
                    rating = rating[0].get().strip()
                    if rating:
                        rating = int(rating.split("/")[0])
                    else:
                        rating = 0
                else:
                    rating = 0

                item = CommentItem()
                item['work_name'] = self.keyword
                item['reviewer'] = reviewer
                item["home_url"] = home_url
                item['followers'] = 0
                item['release_date'] = release_date
                item['likes'] = likes
                item['comment'] = comment
                item["platform"] = "IMDb"
                item["country"] = "未知"
                item["rating"] = rating

                yield item

                self.cnt_num += 1
            except:
                # print(comment_struct.get())
                continue

        if self.cnt_num > self.limit_num:
            return
        load_more_info = response.xpath('//div[@class="load-more-data"]/@data-key')
        if load_more_info:
            load_more_info = load_more_info[0].get()
            next_page_url = f'{response.meta["reviews_url"].split("?")[0]}/_ajax?sort=submissionDate&dir=desc&ratingFilter=0&ref_=undefined&paginationKey={load_more_info}'

            yield scrapy.Request(next_page_url,
                                 meta={"reviews_url": response.meta["reviews_url"]},
                                 callback=self.parse_comments)


if __name__ == "__main__":
    from scrapy import cmdline

    cmdline.execute(["scrapy", "crawl", "IMDbSpider", "-a", "keyword=the wandering earth"])
