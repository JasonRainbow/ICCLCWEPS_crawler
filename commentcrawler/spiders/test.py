import time

import lxml.html
import requests
import execjs  # 这个库是PyExecJS
import re
import pandas as pd


if __name__ == "__main__":

    # response = requests.post(
    #     'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes',
    #     headers={
    #         "X-S-Common": '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',
    #         "X-S": 'XYW_eyJzaWduU3ZuIjoiNTEiLCJzaWduVHlwZSI6IngxIiwiYXBwSWQiOiJ4aHMtcGMtd2ViIiwic2lnblZlcnNpb24iOiIxIiwicGF5bG9hZCI6IjQ2NjdmM2RhMTRjNjE0NmVhYzY3NTc1Zjc0MmM4ZTk3ZTg4NjhjYjg2ZDU5ODMxOGM3ZmQzNWZjZWUzMzhlNGJlMTI0NjRkY2Y0MTBiMDY3OTcyNDgwMzZlNmNiYTU3MGM5ZTNiZmRhMWZhYTFlYjkwZDc0YWEzMWI1NGM3MmNkMGQ3NGFhMzFiNTRjNzJjZGFjNDg5YjlkYThjZTVlNDhmNGFmYjlhY2ZjM2VhMjZmZTBiMjY2YTZiNGNjM2NiNWRiNTA3OTEwMTAzMDJiNTkzOGJmMDkxYWE1MzU0OGJiNGFmMzA3ZDQwZjA0NjhmMjRmNTlhNWVlZDZiNGU4ZjRjOTIyOTdkMzFkZmJlY2M1MTg0N2U3OGFjMDhmNDY2ZmUyM2FkZmU4ODAwMWExN2NhNmQ5NmVmNjZhYzc5NDIxZGJmMDNlZWMyNjVmMDAxZDJjNzNjODk3YjA1NmExMTE2NGIxYTRlZTM5ZWFiNzNkOTQzZWQ2MmJjNDA1MTExZiJ9',
    #         "X-B3-Traceid": "ca904f41e09b58b5",
    #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    #         "Origin": "https://www.xiaohongshu.com",
    #         "Cookie": "abRequestId=ffe4d787-aaab-5e7b-81f7-7842838089ee; xsecappid=xhs-pc-web; a1=18e7092947f1ol056xek6pt52s0edtxzrsxp455sj50000853945; webId=1828718153d527362a34bed686102b8f; gid=yYdW8jJjj0F8yYdW8jJj4M22Wiyl182KCdTKCMVU92JM8U28df9Cu4888Y2qj4280f84qD2J; webBuild=4.11.0; unread={%22ub%22:%22660b76d1000000001a00ffa0%22%2C%22ue%22:%22660f775d000000001a015be2%22%2C%22uc%22:49}; web_session=040069b77466cf0fca2d07a022344b31208267; acw_tc=078a87291b13880d933ae16a24c7d93fe088d1eefc8947b359ea52ab554ac4d8; websectiga=82e85efc5500b609ac1166aaf086ff8aa4261153a448ef0be5b17417e4512f28; sec_poison_id=56f912c3-5930-4aa1-8160-6de6c41f529b",
    #
    #     },
    #     data={"keyword":"长沙打卡点","page":1,"page_size":20,"search_id":"2d3bkvlqaivzyaslq9785","sort":"general","note_type":0,"ext_flags":[],"image_formats":["jpg","webp","avif"]
    #           }
    # )
    # print(response)

    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 SLBrowser/9.0.3.1311 SLBChan/25',
    #     # 'Cookie': 'll="118267"; bid=EozCmwCl2pw; __utmz=30149280.1704767567.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmz=223695111.1712020790.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _pk_id.100001.4cf6=d13ef29b6b6cf2a1.1712020796.; __yadk_uid=REi0GkJuhErbVGPfRvyjml61cOMkApeO; _vwo_uuid_v2=DE1402ACD2D6E36D861E9B6D570439143|3ccc7f23f3856b8ef8855fb174bc92ec; ct=y; __utmc=30149280; __utmc=223695111; __gads=ID=7e283fd8a0d2c28b:T=1712020809:RT=1712061629:S=ALNI_MaZBA-7ugrkNIjXHMab7dJCgV9Pcw; __gpi=UID=00000d7dd4d28e17:T=1712020809:RT=1712061629:S=ALNI_MbDut_Dd0wgBg2BofOX47HN8q1deQ; __eoi=ID=6fa14aaccd449b4e:T=1712020809:RT=1712061629:S=AA-Afjbdomk15yNBWttl4xUef5Mc; ap_v=0,6.0; _pk_ses.100001.4cf6=1; __utma=30149280.1442052059.1704767567.1712061630.1712064695.8; __utmb=30149280.0.10.1712064695; __utma=223695111.1515521444.1712020790.1712061630.1712064695.5; __utmb=223695111.0.10.1712064695',
    #     'Cookie': 'bid=5xinqXzEPI0; ll="118159"; _pk_id.100001.4cf6=640615c107c08768.1690120317.; __yadk_uid=fmFmixPwUkcV3xUg9frXAuJ3Wegme8Zr; _vwo_uuid_v2=DA007E5D334EBD2957EBC420A5BD02A8C|2913b34db4b1e15cc9755a77d84833fd; __utmv=30149280.23254; _ga=GA1.1.1001125851.1710072325; _ga_Y4GN1R87RG=GS1.1.1710072325.1.1.1710072346.0.0.0; viewed="1007305_1078244_4010136_4828612_26958958_5363767_36104107_30459512_30475767_1082349"; push_noty_num=0; push_doumail_num=0; __utmc=30149280; __utmc=223695111; __utmz=30149280.1712755494.118.31.utmcsr=cn.bing.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmz=223695111.1713428473.75.53.utmcsr=search.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/book/subject_search; FCNEC=%5B%5B%22AKsRol9VAqWJb0grXjsYX95gifPfJil-B7LrDj_FJsluc618zc6HytRQrD4-H7HwHXZ3FdMol5YciQaYb8vN5u7jvAYytCYY7vrrgvXiKIjSMPwx4_qS__UuNrmKfCx-B154F3R5z8ol9v9cNls_cAT05dYibxAupg%3D%3D%22%5D%5D; ap_v=0,6.0; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1714723371%2C%22https%3A%2F%2Fwww.douban.com%2Fsearch%3Fcat%3D1002%26q%3D%E6%B5%81%E6%B5%AA%E5%9C%B0%E7%90%832%22%5D; _pk_ses.100001.4cf6=1; __gads=ID=a9f39045710b107e-2285344453e20012:T=1689076597:RT=1714723351:S=ALNI_MYirLznxHeR9xKk0iOdVQw5i3WFeA; __gpi=UID=00000c1fcbfee3b7:T=1689076597:RT=1714723351:S=ALNI_MZDlQIkX2tudhURyxTvbqmdjX5fMQ; __eoi=ID=9eb527f720948a0c:T=1711889292:RT=1714723351:S=AA-AfjYDsFppKLe8aSgvUEakHUUW; __utma=30149280.587405364.1689076599.1713880350.1714723471.122; __utma=223695111.2049376548.1690120317.1713428473.1714723471.76; __utmb=223695111.0.10.1714723471; dbcl2="232540855:873GKibt+RY"; ck=PX-L; __utmt=1; __utmb=30149280.4.10.1714723471; frodotk_db="930af5918c714862b920e0b4a553d926"',
    #     'Host': 'movie.douban.com',
    #     'Connection': 'keep-alive',
    #     'Accept-Encoding': 'en-US,en;q=0.9'
    # }
    # res = requests.get("https://movie.douban.com/subject/35267208/comments?start=320&limit=20&sort=new_score&status=P", headers=headers)
    # print(res.text)

    from lxml import etree
    import requests

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        "Cookie": 'bid=5xinqXzEPI0; ll="118159"; _pk_id.100001.4cf6=640615c107c08768.1690120317.; __yadk_uid=fmFmixPwUkcV3xUg9frXAuJ3Wegme8Zr; _vwo_uuid_v2=DA007E5D334EBD2957EBC420A5BD02A8C|2913b34db4b1e15cc9755a77d84833fd; __utmv=30149280.23254; _ga=GA1.1.1001125851.1710072325; _ga_Y4GN1R87RG=GS1.1.1710072325.1.1.1710072346.0.0.0; viewed="1007305_1078244_4010136_4828612_26958958_5363767_36104107_30459512_30475767_1082349"; push_noty_num=0; push_doumail_num=0; __utmc=30149280; __utmc=223695111; __utmz=30149280.1712755494.118.31.utmcsr=cn.bing.com|utmccn=(referral)|utmcmd=referral|utmcct=/; FCNEC=%5B%5B%22AKsRol9VAqWJb0grXjsYX95gifPfJil-B7LrDj_FJsluc618zc6HytRQrD4-H7HwHXZ3FdMol5YciQaYb8vN5u7jvAYytCYY7vrrgvXiKIjSMPwx4_qS__UuNrmKfCx-B154F3R5z8ol9v9cNls_cAT05dYibxAupg%3D%3D%22%5D%5D; dbcl2="232540855:873GKibt+RY"; ck=PX-L; frodotk_db="930af5918c714862b920e0b4a553d926"; __gads=ID=a9f39045710b107e-2285344453e20012:T=1689076597:RT=1714726816:S=ALNI_MYirLznxHeR9xKk0iOdVQw5i3WFeA; __gpi=UID=00000c1fcbfee3b7:T=1689076597:RT=1714726816:S=ALNI_MZDlQIkX2tudhURyxTvbqmdjX5fMQ; __eoi=ID=9eb527f720948a0c:T=1711889292:RT=1714726816:S=AA-AfjYDsFppKLe8aSgvUEakHUUW; ap_v=0,6.0; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1714733229%2C%22https%3A%2F%2Flink.zhihu.com%2F%3Ftarget%3Dhttps%3A%2F%2Fmovie.douban.com%2Fsubject%2F1292052%2F%22%5D; _pk_ses.100001.4cf6=1; __utma=30149280.587405364.1689076599.1714726744.1714733462.124; __utmb=30149280.2.10.1714733462; __utma=223695111.2049376548.1690120317.1714726744.1714733472.78; __utmb=223695111.0.10.1714733472; __utmz=223695111.1714733472.78.54.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/search',
        "Connection": 'keep-alive',
        "Accept-Encoding": 'gzip, deflate, br, zstd',
        "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',

    }
    comments = {
        "user_name": [],
        "date": [],
        "comment": []
    }

    url = "https://movie.douban.com/subject/26266893/reviews?start={}"
    page = 1
    for i in range(0, 20000, 20):
        print(f"爬取第{page}页")
        page += 1
        try:
            response = requests.get(url.format(i), headers=headers)
            content = response.content.decode('UTF-8')
            # print(content)
            html = etree.HTML(content)
            # 抓取电影名
            # // *[ @ id = "content"] / div / div[2] / div[4] / div[2] / a
            comment_wrappers = html.xpath('//div[@class="main review-item"]')
            # print(comment_wrappers)
            for comment_wrapper in comment_wrappers:
                user_name = comment_wrapper.xpath('.//a[@class="name"]/text()')[0]
                comment = comment_wrapper.xpath('.//div[@class="short-content"]/text()')
                comment = "".join(comment)
                # print(lxml.etree.tostring(comment, encoding="UTF-8"))

                comment = comment.replace('(', '').replace(')', '').strip()
                date = comment_wrapper.xpath('.//span[@class="main-meta"]/@content')[0]
                comments["user_name"].append(user_name)
                comments["date"].append(date)
                comments["comment"].append(comment)
        except:
            print("爬取不到")
        time.sleep(0.1)

    df = pd.DataFrame(data=comments)
    print(df)
    df.to_excel("./流浪地球豆瓣评论.xlsx", index=False)
