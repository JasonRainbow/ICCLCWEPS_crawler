import scrapy
import json
import re
from jsonsearch import JsonSearch
import datetime
from dateutil.relativedelta import relativedelta

from commentcrawler.items import CommentItem, WorkMetrics


headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    "Accept": '*/*',
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": 'gzip, deflate, br, zstd',
    "Connection": 'keep-alive',
    # 这个请求头很重要，没有这个请求返回的json数据格式不太一样
    "X-Goog-Visitor-Id": 'CgtWZ3FGekdPcGRfYyjv3bawBjIKCgJISxIEGgAgGg%3D%3D'
}

payload = {"context": {
    "client": {"hl": "en", "gl": "US", "remoteHost": "219.78.134.102", "deviceMake": "", "deviceModel": "",
               "visitorData": "CgtLdHl1S2M5QUloVSiajLawBjIKCgJTRxIEGgAgJQ%3D%3D",
               "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36,gzip(gfe)",
               "clientName": "WEB", "clientVersion": "2.20240401.05.00", "osName": "Windows", "osVersion": "10.0",
               "originalUrl": "https://www.youtube.com/results?search_query=the+wandering+earth",
               "screenPixelDensity": 1, "platform": "DESKTOP", "clientFormFactor": "UNKNOWN_FORM_FACTOR",
               "configInfo": {
                   "appInstallData": "CJ-ws7AGEOPKsAUQo7uwBRCfybAFEIiHsAUQvZmwBRC4qrAFEI3MsAUQzN-uBRDd6P4SENbWsAUQ86GwBRCmmrAFEJaZ_xIQz86wBRCD368FEIjjrwUQ57qvBRCWlbAFEL75rwUQvPmvBRC3768FENnJrwUQ1KGvBRDGubAFEPywsAUQ7rOwBRDViLAFEPjSsAUQ_rKwBRDQjbAFELersAUQ4fKvBRDgw7AFEKKSsAUQls2wBRCQsrAFEParsAUQ4tSuBRD8hbAFEO6irwUQ6-j-EhDvzbAFEMrDsAUQieiuBRDEw7AFEKKBsAUQ26-vBRDT4a8FEM-osAUQl4OwBRC9tq4FENfprwUQpcL-EhCe0LAFEIO_sAUQu9KvBRChw7AFEOrDrwUQyMOwBRDGw7AFEKiasAUQ2NGwBRCPxLAFEMzDsAUQyfevBRC9irAFEJ2msAUQmvCvBRClu7AFENyCsAUQ9KuwBRDrk64FELfq_hIQk82wBRCh_bciEL-f_xIQgaSwBRDhyrAFEL3DsAUQkv23IhC2yrAFEJaP_xIqKENBTVNHUlVTb0wyd0ROSGtCckx4OWd2MnB3YkwxQVM3eG9zTkhRYz0%3D"},
               "screenDensityFloat": 1.25, "userInterfaceTheme": "USER_INTERFACE_THEME_LIGHT",
               "timeZone": "Asia/Shanghai", "browserName": "Chrome", "browserVersion": "123.0.0.0",
               "acceptHeader": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
               "deviceExperimentId": "ChxOek0xTXpRNE9Ua3hPVGsyT0RVeE5EQTFOQT09EJ-ws7AGGJ-ws7AG",
               "screenWidthPoints": 792, "screenHeightPoints": 742, "utcOffsetMinutes": 480,
               "connectionType": "CONN_CELLULAR_4G", "memoryTotalKbytes": "8000000",
               "mainAppWebInfo": {"graftUrl": "https://www.youtube.com/results?search_query=the+wandering+earth",
                                  "pwaInstallabilityStatus": "PWA_INSTALLABILITY_STATUS_CAN_BE_INSTALLED",
                                  "webDisplayMode": "WEB_DISPLAY_MODE_BROWSER", "isWebNativeShareAvailable": True}},
    "user": {"lockedSafetyMode": False},
    "request": {"useSsl": True, "internalExperimentFlags": [], "consistencyTokenJars": []},
    "clickTracking": {"clickTrackingParams": "CAEQt6kLGAIiEwj_3evnl6WFAxXZUg8CHXXLAQQ="}, "adSignalsInfo": {
        "params": [{"key": "dt", "value": "1712117796240"}, {"key": "flash", "value": "0"},
                   {"key": "frm", "value": "0"}, {"key": "u_tz", "value": "480"}, {"key": "u_his", "value": "3"},
                   {"key": "u_h", "value": "864"}, {"key": "u_w", "value": "1536"}, {"key": "u_ah", "value": "864"},
                   {"key": "u_aw", "value": "1536"}, {"key": "u_cd", "value": "24"}, {"key": "bc", "value": "31"},
                   {"key": "bih", "value": "742"}, {"key": "biw", "value": "775"},
                   {"key": "brdim", "value": "0,0,0,0,1536,0,1536,864,792,742"}, {"key": "vis", "value": "1"},
                   {"key": "wgl", "value": "true"}, {"key": "ca_type", "value": "image"}],
        "bid": "ANyPxKppdoR2vLkv39YNJI13WdpWpmPnH7Xp_BOOyLfe9aUTshmiVRIwmPGDSJbpa6cFxJS_x-3CrIfdloBpqnbsJ0xxjHBLGg"}
},
    "continuation": "EqwDEhN0aGUgd2FuZGVyaW5nIGVhcnRoGpQDU0NpQ0FRdEJWV2hFT1ZkUmNtUm5SWUlCQzJkRU5uWm1jMWhFUkdFd2dnRUxiSGw0ZEhBeWNYcENRVTJDQVF0bU1UWTVUa0Z1YUhaMlk0SUJDMGcyWVRaNlYyOTNUemhGZ2dFTGJHTjRSbU5zZGt0d1QwbUNBUXRwV2xsQmJuRTBkbTlLTUlJQkMwZHRWMEZDVFhoeU4xcEpnZ0VMUTNSZlJuVTVielpCWXpDQ0FRczJSelpYUXpjeGFrczRUWUlCQzNjMFZWTkJNRVl6YlRCcmdnRUxObXREVGxCRk5VMTFORTJDQVF0SmVuaFNVMkZ2WkMxck5JSUJDMmg2UTBwNFJtUmxNa3hOZ2dFTGJHMUlkSGxxTXpOaGFrbUNBUXRxTVVZeVpsZDVUMnRoYTRJQkMxcEZZM0JLVjBjNFZ6VnpnZ0VMYkdaeUxYTnVUSHBpY1hlQ0FRdFdPR3hUVW5OVVdXTkRZNElCQzBSbmRURnplVkZRTVRJMHNnRUdDZ1FJTHhBRDZnRUVDQVFRUFElM0QlM0QYgeDoGCILc2VhcmNoLWZlZWQ%3D"
}


# 爬取指标
class YoutubeMetricsSpider(scrapy.Spider):
    name = "youtube_metrics_spider"
    base_url = "https://www.youtube.com/"

    def __init__(self, keyword, **kwargs):
        self.keyword = keyword
        super(YoutubeMetricsSpider, self).__init__(**kwargs)

    def start_requests(self):
        url = f"https://www.youtube.com/results?search_query={self.keyword.replace(' ', '+')}"
        # url = "https://www.youtube.com/youtubei/v1/search?prettyPrint=false"

        yield scrapy.Request(url, headers=headers, callback=self.parse)

    def parse(self, response, **kwargs):
        # print(response)
        # 设置爬取的视频数量限制
        limit = 4
        # 获取视频id
        ytInitialData = re.findall('var ytInitialData = (.*?);</script>', response.text)[0]

        ytInitialData = JsonSearch(ytInitialData, mode="s")
        contents = ytInitialData.search_first_value("itemSectionRenderer")["contents"]

        videoIds = []
        for item in contents:
            if item.get("shelfRenderer"):
                if item["shelfRenderer"]["title"]["simpleText"] == "People also watched":
                    videoRenderers = JsonSearch(item, mode="j").search_all_value("videoRenderer")
                    for videoRender in videoRenderers:
                        videoId = JsonSearch(videoRender, mode="j").search_first_value("videoId")
                        if videoId:
                            videoIds.append(videoId)
            else:
                videoId = JsonSearch(item, mode="j").search_first_value("videoId")
                if videoId:
                    videoIds.append(videoId)

        # print(videoIds)
        for (idx, video_id) in enumerate(videoIds, start=1):
            if idx > limit:
                break
            print(video_id)
            url = f"https://www.youtube.com/watch?v={video_id}"
            yield scrapy.Request(url, headers=headers, meta={"url": url}, callback=self.parse_video)

    def parse_video(self, response):
        # print(response.text)
        view_count = re.findall('"viewCount":{"simpleText":"(.*?) views"}', response.text, re.S)[0]
        view_count = int(view_count.replace(",", ""))
        like_count = re.findall('"iconName":"LIKE","title":"(.*?)"', response.text, re.S)[0]
        if "K" in like_count:
            like_count = float(like_count.replace("K", "")) * 1000
        else:
            like_count = int(like_count)
        comment_count = re.findall('"commentCount":{"simpleText":"(.*?)"', response.text, re.S)[0]
        if "K" in comment_count:
            comment_count = float(comment_count.replace("K", "")) * 1000
        else:
            comment_count = int(comment_count)
        # print(view_count, like_count, comment_count)
        item = WorkMetrics()
        item["work_name"] = self.keyword
        item["platform"] = "Youtube"
        item["comment_count"] = comment_count
        item["view_count"] = view_count
        item["like_count"] = like_count
        yield item


# 爬取评论
class YoutubeSpider(YoutubeMetricsSpider):
    name = "youtube_comments_spider"
    base_url = "https://www.youtube.com/"
    comments_url = "https://www.youtube.com/youtubei/v1/next?prettyPrint=false"

    def parse_video(self, response):
        # 视频的第一页评论列表token存在于html网页中
        next_page_token = re.findall('"continuationCommand":{"token":"(.*?)"', response.text)[0]
        video_url = response.meta["url"]
        payload["continuation"] = next_page_token
        payload["context"]["client"]["mainAppWebInfo"]["graftUrl"] = video_url
        payload["context"]["client"]["originalUrl"] = video_url

        print(next_page_token)
        yield scrapy.Request(self.comments_url, method="POST",
                             body=json.dumps(payload),
                             meta={"payload": payload, "scrapy_type": "first_page"},
                             headers=headers,
                             callback=self.parse_comments)

    cnt_num = 0
    limit_num = 400

    def parse_comments(self, response):
        json_data = json.loads(response.text)
        json_search_data = JsonSearch(json_data, mode="j")

        # print(json_data["frameworkUpdates"])

        scrapy_type = response.meta["scrapy_type"]

        if scrapy_type == "first_page":
            subMenuItems = json_search_data.search_first_value("subMenuItems")
            next_page_token = JsonSearch(subMenuItems[1], mode="j").search_first_value("token")
        else:
            try:
                next_page_token = json_data["onResponseReceivedEndpoints"][-1]
                next_page_token = JsonSearch(next_page_token, mode="j").search_first_value("continuationItems")
                next_page_token = next_page_token[-1]
                next_page_token = JsonSearch(next_page_token, mode="j").search_first_value("token")
            except:
                return

        if self.cnt_num <= self.limit_num:
            new_payload = response.meta["payload"]
            new_payload["continuation"] = next_page_token
            yield scrapy.Request(self.comments_url,
                                 method="POST",
                                 body=json.dumps(new_payload),
                                 meta={"payload": new_payload, "scrapy_type": "follow_page"},
                                 headers=headers,
                                 callback=self.parse_comments)

        # 解析评论信息
        item_gen = self.parse_comment_data(json_search_data)
        for item in item_gen:
            self.cnt_num += 1
            # print(item)
            yield item

        # 爬取回复的评论
        if scrapy_type != "replies":
            reply_tokens = json_search_data.search_all_value("commentRepliesRenderer")
            if self.cnt_num > self.limit_num:
                return
            for reply_token in reply_tokens:
                token = JsonSearch(reply_token, mode="j").search_first_value("token")
                new_payload = response.meta["payload"]
                new_payload["continuation"] = token
                yield scrapy.Request(self.comments_url,
                                     method="POST",
                                     body=json.dumps(new_payload),
                                     meta={"payload": new_payload, "scrapy_type": "replies"},
                                     headers=headers,
                                     callback=self.parse_comments)

    def parse_comment_data(self, data: JsonSearch):
        comment_struct_list = data.search_all_value("commentEntityPayload")
        for comment_struct in comment_struct_list:
            reviewer = comment_struct["author"]["displayName"]
            release_date = self.parse_date(comment_struct["properties"]["publishedTime"])
            likes = self.parse_like_count(comment_struct["toolbar"]["likeCountLiked"])
            comment = comment_struct["properties"]["content"]["content"]
            avatar = comment_struct["author"]["avatarThumbnailUrl"]
            home_url = self.base_url + reviewer

            item = CommentItem()
            item['work_name'] = self.keyword
            item['reviewer'] = reviewer
            item["home_url"] = home_url
            item['followers'] = 0
            item['release_date'] = release_date
            item['likes'] = likes
            item['comment'] = comment
            item["platform"] = "Youtube"
            item["country"] = "未知"
            item["avatar"] = avatar

            yield item
        pass

    @classmethod
    def parse_date(cls, date_str):

        m_date = datetime.date.today()
        if "day" in date_str:
            day = int(re.findall("^\\d+", date_str)[0])
            m_date = m_date - relativedelta(days=day)
        elif "week" in date_str:
            week = int(re.findall("^\\d+", date_str)[0])
            m_date = m_date - relativedelta(weeks=week)
        elif "month" in date_str:
            month = int(re.findall("^\\d+", date_str)[0])
            m_date = m_date - relativedelta(months=month)
        elif "year" in date_str:
            year = int(re.findall("^\\d+", date_str)[0])
            m_date = m_date - relativedelta(years=year)

        return m_date.strftime("%Y-%m-%d")

    @classmethod
    def parse_like_count(cls, s: str):
        if "K" in s:
            return float(s.replace("K", "")) * 1000
        else:
            return int(s)


if __name__ == "__main__":
    from scrapy import cmdline

    # cmdline.execute(["scrapy", "crawl", "youtube_comments_spider", "-a", "keyword=西游记"])
    cmdline.execute(["scrapy", "crawl", "youtube_metrics_spider", "-a", "keyword=the wandering earth"])
