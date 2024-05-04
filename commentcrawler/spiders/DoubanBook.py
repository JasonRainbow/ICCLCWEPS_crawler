import scrapy
import requests
from datetime import datetime
from lxml import etree
from commentcrawler.items import CommentItem

payload = {
    "start": 0,
    "limit": 20,
    "sort": 'time',
    'status': 'P',
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 SLBrowser/9.0.3.1311 SLBChan/25',
    'Cookie': 'll="118267"; bid=EozCmwCl2pw; __utmz=30149280.1704767567.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmz=223695111.1712020790.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _pk_id.100001.4cf6=d13ef29b6b6cf2a1.1712020796.; __yadk_uid=REi0GkJuhErbVGPfRvyjml61cOMkApeO; _vwo_uuid_v2=DE1402ACD2D6E36D861E9B6D570439143|3ccc7f23f3856b8ef8855fb174bc92ec; ct=y; __utmc=30149280; __utmc=223695111; __gads=ID=7e283fd8a0d2c28b:T=1712020809:RT=1712061629:S=ALNI_MaZBA-7ugrkNIjXHMab7dJCgV9Pcw; __gpi=UID=00000d7dd4d28e17:T=1712020809:RT=1712061629:S=ALNI_MbDut_Dd0wgBg2BofOX47HN8q1deQ; __eoi=ID=6fa14aaccd449b4e:T=1712020809:RT=1712061629:S=AA-Afjbdomk15yNBWttl4xUef5Mc; ap_v=0,6.0; _pk_ses.100001.4cf6=1; __utma=30149280.1442052059.1704767567.1712061630.1712064695.8; __utmb=30149280.0.10.1712064695; __utma=223695111.1515521444.1712020790.1712061630.1712064695.5; __utmb=223695111.0.10.1712064695',

}

class DoubanbookSpider(scrapy.Spider):
    name = 'DoubanBook_comments'
    # allowed_domains = ['www.douban.com']
    # start_urls = ['http://www.douban.com/']
    hot_page_num = 10  # 设置热门评论爬取的页数 每页20条评论
    new_page_num = 11  # 设置最新评论爬取的页数 每页20条评论
    cnt = 0  # 爬取评论的总数量

    def __init__(self, keyword: str = None, *args, **kwargs):
        super(DoubanbookSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword

    # 发起书籍搜索请求
    def start_requests(self):
        url = f"https://www.douban.com/search?cat=1001&q={self.keyword}"
        yield scrapy.Request(url=url, callback=self.parse_book_search)

    # 解析书籍搜索结果页面 获取书籍详情链接
    def parse_book_search(self, response):
        res_divs = response.xpath("//div[@class='result']")
        if len(res_divs) > 0:
            first_div = res_divs[0]
            book_url = first_div.xpath(".//a[@class='nbg']/@href").extract_first()
            print(book_url)
            # 发起进入书籍详情页面请求
            yield scrapy.Request(url=book_url, callback=self.parse_book_info)

    # 解析书籍详情页面 获取书籍短评页面链接
    def parse_book_info(self, response):
        # 获取显示短评的页面链接
        short_comments_div = response.xpath("//div[@id='comments-section']")
        short_comments_span = short_comments_div.xpath(".//span[@class='pl']")
        short_comments_url = short_comments_span.xpath(".//a/@href").extract_first()
        print(short_comments_url)
        # 请求爬取书籍短最新与热门评论
        yield scrapy.Request(url=short_comments_url, callback=self.parse_new_and_hot_comments)

    # 爬取最新和热门评论
    def parse_new_and_hot_comments(self, response):
        baseurl = response.url
        # 爬取最新评论数据
        payload["sort"] = 'time'
        for i in range(self.new_page_num):
            payload["start"] = 20 * i
            res_data = requests.get(url=baseurl, params=payload, headers=headers)  # 该部分需设置参数 添加头
            res_html = etree.HTML(res_data.text)  # 将其转为可解析的html文档
            comment_item_list = res_html.xpath("//li[@class='comment-item']")
            self.cnt += len(comment_item_list)
            print(self.cnt)
            # 保存数据
            for comment_item in comment_item_list:
                item = self.get_Comment_Item(comment_item)
                yield item
            # 检查是否有下一页 若有则继续下一页数据爬取 没有则结束最新评论数据爬取
            next_page = res_html.xpath("//a[@data-page='next']")
            if not next_page:
                break

        # 爬取热门评论数据
        payload["sort"] = 'score'
        for i in range(self.hot_page_num):
            payload["start"] = 20 * i
            res_data = requests.get(url=baseurl, params=payload, headers=headers)  # 该部分需设置参数 添加头
            res_html = etree.HTML(res_data.text)  # 将其转为可解析的html文档
            comment_item_list = res_html.xpath("//li[@class='comment-item']")
            self.cnt += len(comment_item_list)
            print(self.cnt)
            # 保存数据
            for comment_item in comment_item_list:
                item = self.get_Comment_Item(comment_item)
                yield item
            # 检查是否有下一页 若有则继续下一页数据爬取 没有则结束最新评论数据爬取
            next_page = res_html.xpath("//a[@data-page='next']")
            if not next_page:
                break

    # 根据评论数据生成相应item
    def get_Comment_Item(self, comment_item):
        avatar_div = comment_item.xpath(".//div[@class='avatar']")[0]
        avatar_url = avatar_div.xpath(".//a/@href")[0]  # 用户头像链接
        comment_div = comment_item.xpath(".//div[@class='comment']")[0]
        comment_vote = comment_div.xpath(".//span[@class='vote-count']/text()")[0]  # 有用数（点赞数）
        comment_info_span = comment_div.xpath(".//span[@class='comment-info']")[0]
        user_name = comment_info_span.xpath(".//a/text()")[0]  # 用户昵称
        rating_desc = comment_info_span.xpath(".//span[@title]/@title")[0] \
            if len(comment_info_span.xpath(".//span[@title]/@title")) > 0 else ''
        rating = self.judge_rating(rating_desc)  # 用户评分
        comment_raw_date = comment_info_span.xpath(".//a[@class='comment-time']/text()")[0]
        # 将日期转成YYYY-mm-dd的模式
        comment_formatted_date = datetime.strptime(comment_raw_date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")  # 发布时间
        comment_content = comment_div.xpath(".//span[@class='short']/text()")[0]  # 评论内容

        # 保存每条评论数据
        item = CommentItem()
        item["work_name"] = self.keyword
        item["reviewer"] = user_name
        item["avatar"] = avatar_url
        item["followers"] = 0
        item["release_date"] = comment_formatted_date
        item["likes"] = comment_vote
        item["comment"] = comment_content
        item["translated_comment"] = comment_content  # 并未翻译
        item["rating"] = rating
        item["platform"] = "豆瓣"
        item["country"] = "中国"
        return item

    # 判断用户对作品的评分 "力荐"->5  "推荐"->4  "还行"->3  "较差"->2  "很差"->1
    def judge_rating(self, rating):
        if rating == '力荐':
            return 5
        elif rating == '推荐':
            return 4
        elif rating == '还行':
            return 3
        elif rating == '较差':
            return 2
        elif rating == '很差':
            return 1
        else:
            return 0


if __name__ == "__main__":
    keyword = "三体"
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'DoubanBook_comments', '-a', f"keyword={keyword}"])
