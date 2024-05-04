import pandas as pd
import os
from commentcrawler.items import CommentItem, ProfessionalReview, WorkMetrics


class DataPipeline(object):
    work_name = None
    platform = None
    item_type = "normal_comment"

    def __init__(self):
        self.data = None

    # 处理数据
    def process_item(self, item, spider):
        if self.work_name is None:
            self.work_name = item['work_name']
            # 记录爬取的数据类型
            if type(item) == CommentItem:
                self.item_type = "normal_comment"
            elif type(item) == ProfessionalReview:
                self.item_type = "professional_review"
            elif type(item) == WorkMetrics:
                self.item_type = "work_metrics"
        if self.platform is None:
            self.platform = item['platform']
        if self.data is None:
            self.data = dict()
            for key in item:
                self.data[key] = []

        for key in item:
            self.data[key].append(item[key])

        return item

    # 爬虫结束时，会调用这个方法
    def close_spider(self, spider):
        if self.work_name is None:
            return
        # 目录不存在 -> 创建目录
        data_dir = os.path.dirname(__file__) + "/storage/data/"
        if not os.path.isdir(data_dir):
            os.makedirs(data_dir)

        # 保存文件
        df = pd.DataFrame(data=self.data)
        # print(df)
        # print(self.item_type)
        df.to_excel(f"{data_dir}{self.platform}-{self.work_name}-{self.item_type}.xlsx", index=False)
