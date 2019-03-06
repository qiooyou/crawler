# -*- coding: utf-8 -*-
import io
import os
import warnings
from pprint import pprint
import json

import requests
from lxml import etree
from furl import furl


data_list = []  # 存储最终数据
url_base = 'https://maoyan.com/board/4?offset={0}'  # URL模板
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
}  # 用来伪装的HTTP请求头
# 数据更新时间
update_time = ''
for page in range(0, 10):  # 生成页码
    # 开始准备请求参数和URL
    offset = page * 10  # 生成偏移量参数
    url = url_base.format(offset)  # 构造完整URL
    print(url)
    # 开始请求数据
    resp = requests.get(url, headers=headers)  # 请求数据
    if resp.ok:  # 判断是否请求成功
        # 将得到的源码封装为lxml节点对象
        html = etree.parse(io.StringIO(resp.text), etree.HTMLParser())
        # print(html)
        # 如果更新时间未获取，则获取一次
        if not bool(update_time):
            update_time = html.xpath('.//p[@class="update-time"]/text()')
            update_time = update_time[0].strip() if bool(update_time) else None
        # 开始解析数据
        # 根据分析，所有的数据都是在 dl.board-wrapper
        dd_list = html.xpath('//dl[@class="board-wrapper"]/dd')
        if bool(dd_list):
            for dd in dd_list:
                # 用于存储单条信息
                item = {}
                # 排名信息
                rank = dd.xpath('.//i[contains(@class, "board-index")]/text()')
                item['rank'] = rank[0].strip() if bool(rank) else None
                # 封面图片信息
                cover = dd.xpath('.//img[@class="board-img"]/@data-src')
                item['cover'] = cover[0].strip() if bool(cover) else None
                # 主要信息节点
                div_main = dd.xpath('.//div[@class="board-item-main"]')
                div_main = div_main[0] if bool(div_main) else None
                if div_main is not None:
                    # 信息节点
                    div_info = div_main.xpath('.//div[@class="movie-item-info"]')
                    div_info = div_info[0] if bool(div_info) else None
                    if div_info is not None:
                        # 详细地址
                        href = div_info.xpath('.//a/@href')
                        href = href[0].strip() if bool(href) else None
                        item['href'] = furl(url_base).remove(args=True).set(path=href).url
                        # 名称
                        name = div_info.xpath('.//a/text()')
                        item['name'] = name[0].strip() if bool(name) else None
                        # 主演
                        star = div_info.xpath('.//p[@class="star"]/text()')
                        item['star'] = star[0].strip() if bool(star) else None
                        # 上映时间
                        release = div_info.xpath('.//p[@class="releasetime"]/text()')
                        item['release'] = release[0].strip() if bool(release) else None
                    else:
                        warnings.warn('很尴尬地出错了，未能取得详细信息，检查一下呗')
                    # 评分
                    score = ''.join(div_main.xpath('.//div[contains(@class, "movie-item-number")]//*/text()'))
                    item['score'] = score.strip()
                    # 汇总信息
                    data_list.append(item)
                else:
                    warnings.warn('好像哪里出错了，没有得到数据，检查一下吧')
        else:
            warnings.warn('没有得到数据, 请检查是否被反爬虫了')
    else:
        print(resp.status_code)

pprint(data_list)

# 将数据序列化到文件
save_path = os.path.join(os.getcwd(), 'maoyan-top100[{0}].json'.format(update_time))
with open(save_path, 'wt', encoding='utf-8') as fw:
    # ensure_ascii=False  Unicode字符不编码
    # indent=4  4空格缩进
    json.dump(data_list, fw, ensure_ascii=False, indent=4)
print('数据已保存到: {0}'.format(save_path))
