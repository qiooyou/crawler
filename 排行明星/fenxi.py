# -*- coding: utf-8 -*-
import os
import json
import time
from pprint import pprint

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


def gen_browser(driver_path, is_headless=False):
    '''实例化一个driver'''
    options = webdriver.ChromeOptions()
    if is_headless:
        options.add_argument("--headless")
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


# folder = os.path.dirname(os.path.abspath(__file__))
folder = os.getcwd()
driver_path = os.path.join(folder, 'chromedriver.exe')
print(driver_path)
browser = gen_browser(driver_path)
browser.get('http://index.baidu.com/v2/rank/index.html#/industryrank/star')

def get_tab(browser, tab_name, bang_name, date_text):
    tab_data = []
    item_list = browser.find_elements_by_css_selector('.tab-content ul.list > .list-item')
    for item in item_list:
        # 排名
        try:
            rank = item.find_element_by_css_selector('.rank').text.strip()
        except NoSuchElementException as ex:
            import ipdb; ipdb.set_trace()
            pass
        # 姓名
        name = item.find_element_by_css_selector('.name').text.strip()
        # 排名值
        value = item.find_element_by_css_selector('.value').text.strip()
        # 趋势
        trend = None
        if len(item.find_elements_by_css_selector('.trend-down')) > 0:
            trend = 'down'  # 上升
        elif len(item.find_elements_by_css_selector('.trend-up')) > 0:
            trend = 'up'  # 下降
        else:
            if bang_name != '周上升榜':
                trend = 'fair'  # 持平
        # 指数条
        line = item.find_element_by_css_selector('.line-light')
        # 指数条-CSS宽度值
        line_width = float(line.value_of_css_property('width').replace('px', ''))
        # 指数条的父级元素
        line_parent = line.find_element_by_xpath('..')
        # 指数条的父级元素-CSS宽度值
        parent_width = float(line_parent.value_of_css_property('width').replace('px', ''))
        # 指数(保留2位小数)
        index = round(100 * line_width / parent_width, 2)
        # 指数转为字符串形式(%)
        index_str = str(index) + '%'
        # 调试打印
        print(rank, name, value, trend, index_str, tab_name, bang_name, date_text)
        tab_item = {
            'rank': rank,
            'name': name,
            'value': value,
            'trend': trend,
            'index_str': index_str,
            'tab_name': tab_name,
            'bang_name': bang_name,
            'date_text': date_text
        }
        tab_data.append(tab_item)
    return tab_data

def get_bang(browser, bang_name):
    all_tab = []
    date_count = len(browser.find_elements_by_css_selector('.selected-layer-date .date-item'))
    for date_index in range(1, date_count + 1):
        # 如果箭头向下(有这样的class: date-icon-up)，说明没有展开，需要点击一下，让它展开可见
        date_icons = browser.find_elements_by_css_selector('.date-icon-up')
        if len(date_icons) > 0:
            # 点击周列表，可以将其展开
            date_icons[0].click()
            time.sleep(0.1)
        # 某一个周的CSS选择器
        css_selector = '.selected-layer-date .date-item:nth-of-type({0})'.format(date_index)
        # 选择某一个周
        date_item = browser.find_element_by_css_selector(css_selector)
        print(date_item.text)  # 显示周内容
        # 点击找到的周，会刷新页面数据
        date_item.click()
        time.sleep(0.55)
        # 切换到-搜索指数
        browser.find_element_by_xpath('//li[text()[contains(., "搜索指数")]]').click()
        time.sleep(0.1)
        tab_data = get_tab(browser, '搜索指数', bang_name, date_item.text)
        all_tab.extend(tab_data)
        # 切换到-资讯指数
        browser.find_element_by_xpath('//li[text()[contains(., "资讯指数")]]').click()
        time.sleep(0.1)
        tab_data = get_tab(browser, '资讯指数', bang_name, date_item.text)
        all_tab.extend(tab_data)
    return all_tab

def parse():
    global browser
    all_data = []
    for bang_name in ['周榜', '周上升榜', '月榜']:
        bang_selector = '//li[text()[contains(., "{0}")]]'.format(bang_name)
        browser.find_element_by_xpath(bang_selector).click()
        print(bang_name)
        time.sleep(0.35)
        bang_data = get_bang(browser, bang_name)
        all_data.extend(bang_data)
    pprint(all_data)
    print(len(all_data))
    '''
    for item in all_data:
        yield item
    '''

parse()
