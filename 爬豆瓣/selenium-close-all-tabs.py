# -*- coding: utf-8 -*-
import time

from selenium import webdriver


driver_path = r'D:\test\chromedriver.exe'
browser = webdriver.Chrome(executable_path=driver_path)

cwh = browser.current_window_handle
for handle in browser.window_handles:
    if handle != cwh:
        browser.switch_to_window(handle)
        browser.close()
        time.sleep(1)

browser.switch_to_window(cwh)
# browser.close()