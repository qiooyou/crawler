# -*- coding: utf-8 -*-
import re
from pprint import pprint

'''
参考:
Python爬虫学习（4）: python中re模块中的向后引用以及零宽断言
https://www.cnblogs.com/linux-wangkun/p/5978462.html
'''

# info.text()
# data_str = '作者\n:\n[美]埃里克·马瑟斯\n出版社:\n人民邮电出版社\n副标题:\n从入门到实践\n原作名:\nPython Crash Course\n译者\n:\n袁国忠\n出版年:\n2016-7-1\n页数:\n459\n定价:\nCNY 89.00\n装帧:\n平装\n丛书:\n图灵程序设计丛书\nISBN:\n9787115428028'

# info.text(squash_space=False).strip()
data_str = '作者\n:\n        \n        \n        \n[美]埃里克·马瑟斯\n\n    \n\n\n\n\n    \n    \n  \n    \n出版社:\n 人民邮电出版社\n\n\n\n    \n    \n  \n\n    \n    \n  \n    \n副标题:\n 从入门到实践\n\n\n\n    \n    \n  \n    \n原作名:\n Python Crash Course\n\n\n\n    \n    \n  \n    \n\n      \n 译者\n:\n        \n        \n        \n袁国忠\n\n    \n\n\n\n\n    \n    \n  \n    \n出版年:\n 2016-7-1\n\n\n\n    \n    \n  \n    \n页数:\n 459\n\n\n\n    \n    \n  \n    \n定价:\n CNY 89.00\n\n\n\n    \n    \n  \n    \n装帧:\n 平装\n\n\n\n    \n    \n  \n    \n丛书:\n\xa0\n图灵程序设计丛书\n\n\n\n\n    \n    \n  \n    \n      \n      \nISBN:\n 9787115428028'

print(repr(data_str))
print()

# 分割行
split_result = re.split(r'(?<!\:)[\s\n]+(?!\:)', data_str)
pprint(split_result)

# 处理特殊行，一致化
split_result = list(map(
    lambda item: re.sub(r'[\s\n]s+(?=\:)', '', item),
    split_result
))
pprint(split_result)

# 分割每一行的名称值数据
split_result = dict(map(
    lambda item: re.split(r'\:[\s\n]+', item),
    split_result
))
pprint(split_result)
