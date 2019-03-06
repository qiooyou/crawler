# -*- coding: utf-8 -*-
import scrapy
import json
import xlwt
from xlrd import open_workbook
from xlutils.copy import copy
class LianjiaSpider(scrapy.Spider):
    name = 'Lianjia'
    allowed_domains = ['lianjia.com']
    start_urls = ['https://www.lianjia.com/city/']
    site=['达州']
    global adds_url
    adds_url={}
    workbook = xlwt.Workbook(encoding = 'ascii')
    worksheet = workbook.add_sheet('orksheet')
    worksheet.write(0, 0, label = '总价(万)')
    worksheet.write(0, 1, label = '单价')
    worksheet.write(0, 2, label = '面积')
    workbook.save('test.xls')

    def parse_yemian(self, response):
        len_pag=len(response.xpath('//div[contains(@class,"totalPrice")]/span/text()'))
        for i in range(len_pag):
            totalPrice=response.xpath('//div[contains(@class,"totalPrice")]/span/text()')[i].extract()#万 总价
            unitPrice=response.xpath('//div[contains(@class,"unitPrice")]/span/text()')[i].extract()#单价
            acreage=response.xpath('//div[contains(@class,"address")]/div')[i].extract().split('|')[2].strip()#面积
            print(totalPrice,unitPrice,acreage)
            r_xls = open_workbook("test.xls") # 读取excel文件
            row = r_xls.sheets()[0].nrows # 获取已有的行数
            excel = copy(r_xls) # 将xlrd的对象转化为xlwt的对象
            table = excel.get_sheet(0) # 获取要操作的sheet

            #对excel表追加一行内容
            table.write(row, 0, totalPrice) #括号内分别为行数、列数、内容
            table.write(row, 1, unitPrice)
            table.write(row, 2, acreage)

            excel.save("test.xls") # 保存并覆盖文件
        
    def parse_xx(self, response):
        urll=response.url
        max_page=json.loads(response.css('.contentBottom > div.page-box.fr > div').xpath('./@page-data')[0].extract())['totalPage']
        # import ipdb;ipdb.set_trace()
        if bool(max_page):
            for i in range(1,max_page+1):
                url=urll+'pg{0}'.format(i)
                yield scrapy.Request(url=url,callback=self.parse_yemian,dont_filter=True)
   
        
        

    def parse(self, response):
        max_a=response.css('.city_list_ul >li >div.city_list >div >ul>li >a')
        global adds_url
        for i in range(len(max_a)):
            adds=max_a.xpath('./text()')[i].extract()
            href=max_a.xpath('./@href')[i].extract()
            
            adds_url[adds]=href
        try:
            for di in self.site:
                # import ipdb;ipdb.set_trace()
                url=adds_url[di]+'ershoufang/'

                yield scrapy.Request(url=url,callback=self.parse_xx,dont_filter=True)
        except :
            print('*-'*20,'没有该地方')
            
        # import ipdb;ipdb.set_trace()
