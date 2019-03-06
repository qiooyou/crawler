# -*- coding: utf-8 -*-
import scrapy
from  scrapy import Selector

import dateparser
from Jobs.items import JobsItem 
class HuiboSpider(scrapy.Spider):
    name = 'huibo'
    allowed_domains = ['www.huibo.com']
    start_urls = ['http://huibo.com/']
    # 需要操作的城市名字
    allowed_cities = ["成都"]
    # 工作名字
    job='python'


    def xx(self,response):
        info=JobsItem()

        info['job_name']=response.css('.newtopTit').xpath('./h2/text()').extract_first().replace('\r\n','').split()[0]         #职位名字

        info['salary']=response.css(".newJobDtl").xpath('./p[1]/span/text()').extract_first().replace('\r\n','').split()[0]     #工资
        info['gs_name']=response.css('.newJobtop').xpath('./p/span/a/text()').extract_first()        #公司名字
        info['site']=response.css(".newJobDtl").xpath('./p[3]/span/text()').extract_first().replace('\r\n','').split()[0]      #工作地点
        info['work_yaoqi']=response.css(".newJobDtl").xpath('./p[2]/span/text()').extract_first().replace('\r\n','').split()[0]     #工作经验
        info['num_pe']=response.css(".newJobDtl").xpath('./p[4]/span/text()').extract_first().replace('\r\n','').split()[0]     #找的人数
        # if  response.url== 'http://cd.huibo.com/php/jobdcm4r42.html':
        #     import ipdb; ipdb.set_trace()
        end_num=str(len(response.css(".newJobDtl").xpath('./p')))
        data=response.css(".newJobDtl").xpath('./p['+end_num+']/span[2]/text()').extract_first().replace('\r\n','').split()[0].replace('（','').replace('）','')       #时间
        end_dat=data[:data.find('结束')]
        # dateparser得到结束时间转化为时间类型
        info['end_data']=dateparser.parse(end_dat).strftime("%Y-%m-%d") 
        info['url']=response.url 
        print(info)      #url地址
        # import ipdb; ipdb.set_trace()
        # 返回JobsItem
        yield info

    def git_job(self,response):
        # 职位集合
        e_list = response.css('.postIntro .postIntroL')
        # 遍历职位集合
        for e_item in e_list:

            item=e_item.css('.postIntroL').css('.postIntroLx')
            item_a = item.css('.name .des_title')
            # 得到单个职位的详细url
            url=item_a.xpath('./@href').extract_first()
            yield scrapy.Request(url,callback=self.xx,dont_filter=True)
            
           
    def git_page(self,response):
        # 去掉页面源码中的换行符，消除换行对通过 xpath 取 text() 的影响
        # from scrapy import Selector
        # import re
        # resp = Selector(None, re.sub(r'[\r\n]', '', response.body_as_unicode()), 'html')

        # 去掉页面源码中的换行符，消除换行对通过 xpath 取 text() 的影响
        resp = Selector(None, response.body_as_unicode().replace('\r','').replace('\n',''), 'html')
        max_pag=resp.css('.milpage')[0].xpath('./text()').extract()
        # 最大页数
        max_pag=int(max_pag[2].replace('\t','').replace('/','').split()[0])
        for pag in range(1,max_pag+1):
            # 拼接url
            url=response.url+'&params=p{0}'.format(pag)
            yield scrapy.Request(url,callback=self.git_job,dont_filter=True)
            
        
        

    def parse(self, response):
        ct_dict={}
        url= response.xpath('//dd[contains(@class,"city-twolevel")]')
        for i in range(len(url)):
            for j in range(len(url[i].xpath('./a'))):
                ct_name=url[i].xpath('./a/text()')[j].extract() 
                ct_url=url[i].xpath('./a')[j].xpath('./@href').extract_first()
                ct_dict[ct_name]=ct_url

        ct_dict['重庆']=response.url

        try:
            # job_url =ct_dict[self.allowed_cities]
            for i in self.allowed_cities:
            # http://gy.huibo.com/jobsearch/?key=PHP

                job_url=ct_dict[i]+'/jobsearch/?key={0}'.format(self.job)
                yield scrapy.Request(url=job_url,callback=self.git_page,dont_filter=True)
            
        except Exception as e:
            print('没有该城市')
            raise e

