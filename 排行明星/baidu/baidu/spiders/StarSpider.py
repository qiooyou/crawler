# -*- coding: utf-8 -*-
import os
import json
import time
from pprint import pprint

import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    NoSuchElementException,
    StaleElementReferenceException
)

from baidu.items import BaiduItem

def gen_browser(driver_path):
    '''实例化一个driver'''
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('disable-infobars')
    options.add_argument("--disable-plugins-discovery")
    user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36"
    options.add_argument('user-agent="{0}"'.format(user_agent))
    # ############### 专业造假 ***************************
    def send(driver, cmd, params={}):
        '''
        向调试工具发送指令
        from: https://stackoverflow.com/questions/47297877/to-set-mutationobserver-how-to-inject-javascript-before-page-loading-using-sele/47298910#47298910
        '''
        resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
        url = driver.command_executor._url + resource
        body = json.dumps({'cmd': cmd, 'params': params})
        response = driver.command_executor._request('POST', url, body)
        if response['status']:
            raise Exception(response.get('value'))
        return response.get('value')
    def add_script(driver, script):
        '''在页面加载前执行js'''
        send(driver, "Page.addScriptToEvaluateOnNewDocument", {"source": script})
    # 给 webdriver.Chrome 添加一个名为 add_script 的方法
    webdriver.Chrome.add_script = add_script # 这里（webdriver.Chrome）可能需要改，当调用不同的驱动时
    # *************** 专业造假 ###################
    browser = webdriver.Chrome(
        executable_path=driver_path,
        chrome_options=options
    )
    # ################## 辅助调试 *********************
    existed = {
        'executor_url': browser.command_executor._url,  # 浏览器可被远程连接调用的地址
        'session_id': browser.session_id  # 浏览器会话ID
    }
    # pprint(existed)
    # ********************* 辅助调试 ##################
    # ############### 专业造假 ***************************
    browser.add_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => false,
    });
    window.navigator.chrome = {
        runtime: {},
    };
    Object.defineProperty(navigator, 'languages', {
        get: () => ['zh-CN', 'zh']
    });
    Object.defineProperty(navigator, 'plugins', {
        get: () => [0, 1, 2],
    });
    """)
    # *************** 专业造假 ###################

    return browser

class StarspiderSpider(scrapy.Spider):
    name = 'StarSpider'
    allowed_domains = ['index.baidu.com']
    start_urls = ['http://index.baidu.com/v2/rank/index.html#/industryrank/star']

    def parse(self, response):
        driver_path = self.settings.get('DRIVER_PATH')
        # import ipdb; ipdb.set_trace()
        browser = gen_browser(driver_path)

        browser.get(response.url)  # 打开页面

        # 等待页面加载到可以找到元素
        try:
            # 最多等待5秒
            _element = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".tab-content"))
            )
        except TimeoutException:
            # import traceback; traceback.print_exc()
            # import ipdb; ipdb.set_trace()
            browser.quit()

        browser.find_element_by_xpath('//p[@class="more-rank"]/span[text()[contains(.,"娱乐人物")]]').click()

        time.sleep(1)


        for tab in ['周榜','周上升榜','月榜']:
            if tab == '周榜':
                browser.find_element_by_xpath('//*[text()[contains(.,"周榜")]]').click()
                time.sleep(0.5)
            elif tab == '周上升榜':
                browser.find_element_by_xpath('//*[text()[contains(.,"周上升榜")]]').click()
                time.sleep(0.5)
            else:
                browser.find_element_by_xpath('//*[text()[contains(.,"月榜")]]').click()
                time.sleep(0.5)

                
            item_count = 0
            icon_up = browser.find_elements_by_css_selector('.date-icon-up')
            if len(icon_up) > 0:
                icon_up[0].click()
                time.sleep(0.5)
                item_count = len(browser.find_elements_by_css_selector('.date-item'))

            for week in range(0, item_count):
                if week > 0:
                    # 展开周列表
                    browser.find_element_by_css_selector('.date-icon-up').click()
                    time.sleep(0.3)
                css_selector = '.date-item:nth-of-type({0})'.format(week + 1)
                # 点击某一周
                if tab == "月榜":
                    import ipdb; ipdb.set_trace()
                browser.find_elements_by_css_selector(css_selector)[0].click()
                # 等一会儿(1.5秒)，等待页面更新
                time.sleep(1.5)
                # 爬每一个周             
                bb=self.parse_week(browser)
                # import ipdb; ipdb.set_trace()
                # bb.append(tab)
                for item in bb:
                    yield item
            # browser.quit()

    def parse_week(self, browser):
        # TODO: 定义变量，收集结果
        lst=[]
        for actived in ['搜索指数','资讯指数']:
            # import ipdb; ipdb.set_trace()
            # act=browser.find_element_by_xpath('//*[text()[contains(.,"搜索指数")]]').text
            
            if actived == '搜索指数':
                browser.find_element_by_xpath('//*[text()[contains(.,"搜索指数")]]').click()
                
            else:
                browser.find_element_by_xpath('//*[text()[contains(.,"资讯指数")]]').click()
                
            
            try:
                items = browser.find_elements_by_css_selector('.tab-content .list > .list-item')
                # import ipdb; ipdb.set_trace()
                data = browser.find_elements_by_css_selector('.date-text')[0].text
                one = browser.find_elements_by_css_selector('.actived')[0].text
                for item in items:
                    # 排名
                    rank = item.find_element_by_css_selector('.content .rank').text.strip()
                    # 姓名
                    name = item.find_element_by_css_selector('.content .name').text.strip()
                    # 行指数
                    line = item.find_element_by_css_selector('.content .line-light')
                    # 行指数-真实值
                    real_value = float(line.value_of_css_property('width').replace('px', ''))
                    # 行指数-最大值元素
                    line_max = line.find_element_by_xpath('..')
                    # 最大值
                    max_value = float(line_max.value_of_css_property('width').replace('px', ''))
                    # 指数值
                    index = round(100 * real_value / max_value, 2)
                    # 指数字符串
                    index_str = str(index).rstrip('0').rstrip('.') + '%'


                    cc=BaiduItem()
                    cc['one']=one
                    cc['data']=data
                    cc['actived']=actived
                    cc['rank']=rank
                    cc['name']=name
                    cc['index_str']=index_str
                    print(index_str)
                    print('-' * 30)
                    # yield cc
                    lst.append(cc)
                    # import ipdb; ipdb.set_trace()
            except (NoSuchElementException, StaleElementReferenceException):
                import ipdb; ipdb.set_trace()
                pass
            # TODO: 返回结果
            
        return lst
