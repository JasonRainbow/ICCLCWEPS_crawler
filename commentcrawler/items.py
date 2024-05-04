# Define here the models for your scraped items
import scrapy


# 普通评论
class CommentItem(scrapy.Item):
    # 作品名称
    work_name = scrapy.Field()
    # 评论者
    reviewer = scrapy.Field()
    home_url = scrapy.Field()
    # 评论者头像
    avatar = scrapy.Field()
    # 评论人的粉丝数
    followers = scrapy.Field()
    # 评论时间
    release_date = scrapy.Field()
    # 喜爱数
    likes = scrapy.Field()
    # 评论内容
    comment = scrapy.Field()
    # 翻译后的评论
    translated_comment = scrapy.Field()
    # 评分
    rating = scrapy.Field()
    # 所属平台
    platform = scrapy.Field()
    # 所属国家
    country = scrapy.Field()


# 专业评论
class ProfessionalReview(scrapy.Item):
    # 作品名称
    work_name = scrapy.Field()
    # 标题
    title = scrapy.Field()
    # 发布时间
    report_date = scrapy.Field()
    # 评论人
    reviewer = scrapy.Field()
    # 评论人的主页
    home_url = scrapy.Field()
    # 评论内容
    content = scrapy.Field()
    # 所属平台
    platform = scrapy.Field()
    # 所属国家
    country = scrapy.Field()


# 作品指标
class WorkMetrics(scrapy.Item):
    # 作品名称
    work_name = scrapy.Field()
    # 所属平台
    platform = scrapy.Field()
    # 评论数
    comment_count = scrapy.Field()
    # 评分
    rating = scrapy.Field()
    # 播放量
    view_count = scrapy.Field()
    # 点赞数
    like_count = scrapy.Field()
