# 爬取GoodReads的评论
import json

import scrapy
import re
import requests
from commentcrawler.items import CommentItem
import time

payload = {
    "operationName": "getReviews",
    "query": "query getReviews($filters: BookReviewsFilterInput!, $pagination: PaginationInput) {\n  getReviews(filters: $filters, pagination: $pagination) {\n    ...BookReviewsFragment\n    __typename\n  }\n}\n\nfragment BookReviewsFragment on BookReviewsConnection {\n  totalCount\n  edges {\n    node {\n      ...ReviewCardFragment\n      __typename\n    }\n    __typename\n  }\n  pageInfo {\n    prevPageToken\n    nextPageToken\n    __typename\n  }\n  __typename\n}\n\nfragment ReviewCardFragment on Review {\n  __typename\n  id\n  creator {\n    ...ReviewerProfileFragment\n    __typename\n  }\n  recommendFor\n  updatedAt\n  createdAt\n  spoilerStatus\n  lastRevisionAt\n  text\n  rating\n  shelving {\n    shelf {\n      name\n      webUrl\n      __typename\n    }\n    taggings {\n      tag {\n        name\n        webUrl\n        __typename\n      }\n      __typename\n    }\n    webUrl\n    __typename\n  }\n  likeCount\n  viewerHasLiked\n  commentCount\n}\n\nfragment ReviewerProfileFragment on User {\n  id: legacyId\n  imageUrlSquare\n  isAuthor\n  ...SocialUserFragment\n  textReviewsCount\n  viewerRelationshipStatus {\n    isBlockedByViewer\n    __typename\n  }\n  name\n  webUrl\n  contributor {\n    id\n    works {\n      totalCount\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SocialUserFragment on User {\n  viewerRelationshipStatus {\n    isFollowing\n    isFriend\n    __typename\n  }\n  followersCount\n  __typename\n}\n",
    "variables": {
        "filters": {
            "resourceId": "",
            "resourceType": "WORK",
            # 检索最新的评论
            "sort": "NEWEST"
        },
        "pagination": {
            "limit": 30,
            # "after": ""
        }
    }
}

headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    "X-Api-Key": 'da2-xpgsdydkbregjhpr6ejzqdhuwy'
}

max_length = 4000


class GoodReadsSpider(scrapy.Spider):
    # 爬虫名称
    name = 'GoodReads_comments'
    # 允许爬取的网站域名
    # allowed_domains = ['www.goodreads.com']
    base_url = "https://www.goodreads.com"
    comments_url = "https://kxbwmqov6jgg3daaamb744ycu4.appsync-api.us-east-1.amazonaws.com/graphql"
    # 起始网址
    start_urls = []

    def __init__(self, keyword: str=None, *args, **kwargs):
        super(GoodReadsSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword

    # 检索
    def start_requests(self):
        url = f"https://www.goodreads.com/search?utf8=%E2%9C%93&query={self.keyword.replace(' ', '+')}"
        yield scrapy.Request(url=url, callback=self.parse)

    # 爬取检索到的第一项
    def parse(self, response, **kwargs):
        tr_list = response.xpath("//tr")
        tr = tr_list[0]
        detail_url = tr.xpath('.//a[@class="bookTitle"]/@href')
        if len(detail_url) > 0:
            detail_url = detail_url[0].extract()
            print(detail_url)
            yield scrapy.Request(url=self.base_url + detail_url, callback=self.parse_work_page)

    # 爬取作品评论信息  获取到workId，然后访问评论接口，迭代爬取，每次返回的数据中有nextPageToken用于下一页的查询
    def parse_work_page(self, response):
        comments_url = response.xpath('//a[@aria-label="Tap to show more reviews and ratings"]/@href')
        if len(comments_url) > 0:
            comments_url = comments_url[0].extract()
            workId = re.findall(r'"workId":"(.*?)",', comments_url, re.S)[0]
            next_page_tokens = re.findall(r'"after":"(.*?)"', comments_url, re.S)[0]
            # print(workId)
            # print(next_page_tokens)
            payload["variables"]["filters"]["resourceId"] = workId
            cnt = 0
            while True:
                res_data = requests.post(self.comments_url, data=json.dumps(payload),
                                         headers=headers, proxies={"https": "http://127.0.0.1:10809"}).text
                res_data = json.loads(res_data)
                comment_list = res_data["data"]["getReviews"]["edges"]
                for comment_struct in comment_list:
                    comment_struct = comment_struct["node"]
                    comment = comment_struct["text"]
                    like_count = comment_struct["likeCount"]
                    post_time = comment_struct["lastRevisionAt"]
                    user_name = comment_struct["creator"]["name"]
                    user_follower_count = comment_struct["creator"]["followersCount"]
                    rating = comment_struct["rating"]
                    avatar = comment_struct["creator"]["imageUrlSquare"]

                    # 保存数据
                    item = CommentItem()
                    item['work_name'] = self.keyword
                    item['reviewer'] = user_name
                    item['followers'] = user_follower_count
                    item['release_date'] = time.strftime('%Y-%m-%d', time.gmtime(post_time / 1000))
                    item['likes'] = like_count
                    item['comment'] = comment
                    item['rating'] = rating
                    item["platform"] = "GoodReads"
                    item["avatar"] = avatar
                    yield item

                    cnt += 1
                    # print(comment)
                if cnt >= max_length:
                    break
                next_page_tokens = res_data["data"]["getReviews"]["pageInfo"].get("nextPageToken")
                print(cnt)

                if not next_page_tokens:
                    break
                else:
                    payload["variables"]["pagination"]["after"] = next_page_tokens


if __name__ == "__main__":
    keyword = "The Three-Body Problem"
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'GoodReads_comments', '-a', f"keyword={keyword}"])
