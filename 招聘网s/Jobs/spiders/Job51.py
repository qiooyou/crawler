# -*- coding: utf-8 -*-
import scrapy
import json
import requests

from Jobs.items import JobsItem 
class Job51Spider(scrapy.Spider):
    name = 'Job51'
    allowed_domains = ['search.51job.com']
    start_urls=['https://js.51jobcdn.com/in/js/2016/layer/area_array_c.js?20180319']
    # 需要爬的职位
    job='爬虫'
    # 详细连接
    F = 'https://search.51job.com/list/{0},000000,0000,00,9,99,'+job+',2,{1}.html'
    # 工作地点
    allowed_cities = ['达州','重庆']
    # allowed_cities = ['重庆','成都','北京']
    # 定义全局变量保存根据城市名查到的城市id
    global cit_num_list
    def xx(self,response):

        job_xx=JobsItem()
        job_xx["job_name"]=response.css('.tHeader div div h1').xpath('./@title').extract_first() #职位名字
        job_xx["salary"]=response.css('.tHeader div div strong').xpath('.')[0].extract().replace('<strong>','').replace('</strong>','')  #工资
        job_xx["gs_name"]=response.css('.tHeader div div p a')[0].xpath('./@title').extract_first()   #公司名字
        list_xx=response.css('.tHeader div div p')[1].xpath('./@title')[0].extract()  #
        list_xx=list_xx.split('\xa0\xa0|\xa0\xa0')  #
        num=len(list_xx)
        job_xx["site"]=list_xx[0]  #工作地点
        if num== 4:
            job_xx["work_yaoqi"]=list_xx[1]  #工作经验
        else:
            job_xx["work_yaoqi"]=list_xx[2]+','+list_xx[1]  #工作经验
        job_xx["num_pe"]=list_xx[num-2]  #找的人数
        job_xx["end_data"]=list_xx[num-1]  #时间
        job_xx["url"]=response.url #url地址
        print(job_xx)
        yield job_xx
        # import ipdb as pdb;pdb.set_trace()  #


    def get_urls(self,response):
        # 公司名字 并且由此得到一页的数据有多少条
        firm_name=response.xpath('//*[@id="resultList"]')[0]
        # import ipdb as pdb;pdb.set_trace()
        for i in range(1,len(firm_name.css(':not(.title) .el'))):

            # 得到工作的详细地址
            job_url=firm_name.css(':not(.title) .el')[i].xpath('p/span/a/@href').extract()[0]

            yield scrapy.Request(url=job_url,callback=self.xx, dont_filter=True)

            # import ipdb as pdb;pdb.set_trace()
            

        # re=scrapy.Request(url=job_url,callback=self.xx)
        # return re
        # import ipdb as pdb;pdb.set_trace()


    def parse(self, response):
        # self.get_urls(response)
        # 获取全部城市ID
        script_text=requests.get(response.url).text
        # 处理城市名 和id
        sc_json=script_text[script_text.index('=') + 1:]
        sc_json=sc_json.replace('\r\n','').replace(';','')
        script_dict = json.loads(sc_json)
        # 保存城市id
        with open('job51.json', 'wt', encoding='utf-8') as f:
             json.dump(script_dict, f, indent=4, ensure_ascii=False)
        
        # 翻转字典 吧城市名作为键
        new_dict = {v : k for k, v in script_dict.items()} 
        global cit_num_list
        cit_num_list=[]
        # 根据城市名字 取出id保存到全局变量中
        for cit in self.allowed_cities:
            try:
                cit_num_list.append(new_dict[cit])

            except Exception as e:
                print('*'*20,'城市不存在','*'*20)
                raise e
        if len(cit_num_list)==1:
            # 拼接城市url
            url=self.F.format(cit_num_list[0],'1')
        else:
            url=self.F.format('%252C'.join(cit_num_list),'1')
        
        # yield scrapy.Request(url,callback=self.get_urls)
        # 调用parse_city函数
        yield scrapy.Request(url,callback=self.parse_city)

        
        # import ipdb as pdb;pdb.set_trace()

   # 份页爬
    def parse_city(self, response):
        # 得到最大页数
        max_page=int(response.xpath('//span[contains(@class,"td")]/text()').extract_first()[:-4][1:])
        # import ipdb as pdb;pdb.set_trace()
        # 循环页数  得到url
        for item in range(1,max_page+1):
            global cit_num_list
            url=self.F.format('%252C'.join(cit_num_list),item)
            yield scrapy.Request(url,callback=self.get_urls,dont_filter=True)
