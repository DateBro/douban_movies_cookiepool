import random
import time
from io import BytesIO
from PIL import Image
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from os import listdir
from os.path import abspath, dirname
import os
import cv2
import numpy as np

TEMPLATES_FOLDER = dirname(abspath(__file__)) + '/templates/'

class DoubanCookies():
    def __init__(self, username, password, browser):
        self.url = 'https://accounts.douban.com/passport/login'
        self.browser = browser
        self.wait = WebDriverWait(self.browser, 20)
        self.username = username
        self.password = password

    # 已改
    def open(self):
        """
        打开网页输入用户名密码并点击
        :return: None
        """
        self.browser.delete_all_cookies()
        self.browser.maximize_window()
        self.browser.get(self.url)

        # 先点击密码登录
        password_login_button = self.browser.find_element_by_xpath('//*[@id="account"]/div[2]/div[2]/div/div[1]/ul[1]/li[2]')
        self.webdriverwait_click(self.browser, password_login_button)

        # 先输入账号和密码
        account_input = self.browser.find_element_by_xpath('//*[@id="username"]')
        password_input = self.browser.find_element_by_xpath('//*[@id="password"]')

        account_input.send_keys(self.username)
        password_input.send_keys(self.password)

        # 找到登录按钮（豆瓣html里不是button，而是一个像button的链接）
        login_button = self.browser.find_element_by_xpath("//*[@id='account']/div[2]/div[2]/div/div[2]/div[1]/div[4]/a")
        self.webdriverwait_click(self.browser, login_button)
        time.sleep(0.2)

    @staticmethod
    def webdriverwait_click(dri, element):
        """
        显示等待 click
        :param dri: driver
        :param element:
        :return:
        """
        WebDriverWait(dri, 10, 5).until(lambda dr: element).click()

    # 已改
    def password_error(self):
        """
        判断是否密码错误
        :return:
        """
        try:
            return WebDriverWait(self.browser, 5).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#account > div.login-wrap > div.login-right > div > div.account-tabcon-start > div.account-form > div.account-form-error > span'), '用户名或密码错误'))
        except TimeoutException:
            return False

    # 已改完
    def login_successfully(self):
        """
        判断是否登录成功
        :return:
        """
        try:
            return bool(
                WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="db-global-nav"]/div/div[1]/ul/li[2]/a'))))
        except TimeoutException:
            return False

    @staticmethod
    def get_postion(chunk, canves):
        """
        判断缺口位置
        :param chunk: 缺口图片是原图
        :param canves:
        :return: 位置 x, y
        """
        otemp = chunk
        oblk = canves
        target = cv2.imread(otemp, 0)
        template = cv2.imread(oblk, 0)
        # w, h = target.shape[::-1]
        temp = 'temp.jpg'
        targ = 'targ.jpg'
        cv2.imwrite(temp, template)
        cv2.imwrite(targ, target)
        target = cv2.imread(targ)
        target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
        target = abs(255 - target)
        cv2.imwrite(targ, target)
        target = cv2.imread(targ)
        template = cv2.imread(temp)
        result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
        x, y = np.unravel_index(result.argmax(), result.shape)
        return x, y
        # # 展示圈出来的区域
        # cv2.rectangle(template, (y, x), (y + w, x + h), (7, 249, 151), 2)
        # cv2.imwrite("yuantu.jpg", template)
        # show(template)

    @staticmethod
    def get_track(distance):
        """
        模拟轨迹 假装是人在操作
        :param distance:
        :return:
        """
        # 初速度
        v = 0
        # 单位时间为0.2s来统计轨迹，轨迹即0.2内的位移
        t = 0.2
        # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
        tracks = []
        # 当前的位移
        current = 0
        # 到达mid值开始减速
        mid = distance * 7 / 8

        distance += 10  # 先滑过一点，最后再反着滑动回来
        # a = random.randint(1,3)
        while current < distance:
            if current < mid:
                # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
                a = random.randint(2, 4)  # 加速运动
            else:
                a = -random.randint(3, 5)  # 减速运动

            # 初速度
            v0 = v
            # 0.2秒时间内的位移
            s = v0 * t + 0.5 * a * (t ** 2)
            # 当前的位置
            current += s
            # 添加到轨迹列表
            tracks.append(round(s))

            # 速度已经达到v,该速度作为下次的初速度
            v = v0 + a * t

        # 反着滑动到大概准确位置
        for i in range(4):
            tracks.append(-random.randint(2, 3))
        for i in range(4):
            tracks.append(-random.randint(1, 3))
        return tracks

    # 不需要改
    def get_cookies(self):
        """
        获取Cookies
        :return:
        """
        return self.browser.get_cookies()

    @staticmethod
    def urllib_download(imgurl, imgsavepath):
        """
        下载图片
        :param imgurl: 图片url
        :param imgsavepath: 存放地址
        :return:
        """
        from urllib.request import urlretrieve
        urlretrieve(imgurl, imgsavepath)

    # 修改这里来适配豆瓣的验证码机制
    # 点击登录以后总共有 4 种可能，一是直接弹出密码错误，二是先弹出验证码，完成以后密码错误，
    # 三是验证码完成以后密码正确，四是点击之后直接成功
    def main(self):
        """
        破解入口
        :return:
        """
        self.open()

        if self.password_error():
            return {
                'status': 2,
                'content': '用户名或密码错误'
            }
        # 如果不需要验证码直接登录成功
        if self.login_successfully():
            cookies = self.get_cookies()
            return {
                'status': 1,
                'content': cookies
            }

        # 需要验证码的情况下登录
        self.login_with_auth()
        if self.login_successfully():
            cookies = self.get_cookies()
            return {
                'status': 1,
                'content': cookies
            }
        elif self.password_error():
            return {
                'status': 2,
                'content': '用户名或密码错误'
            }
        else:
            return {
                'status': 3,
                'content': '登录失败'
            }

    # 已改，试试效果
    def login_with_auth(self):
        driver = self.browser

        # 出现验证码之后
        driver.switch_to.frame(driver.find_element_by_id('tcaptcha_popup'))  # switch 到 滑块frame
        time.sleep(0.5)
        # 带缺口的大图
        bk_block = driver.find_element_by_css_selector('#slideBkg')
        web_image_width = bk_block.size
        web_image_width = web_image_width['width']
        bk_block_x = bk_block.location['x']

        # 缺口图
        slide_block = driver.find_element_by_css_selector('#slideBlock')
        slide_block_x = slide_block.location['x']

        bk_block = driver.find_element_by_css_selector('#slideBkg').get_attribute('src')       # 大图 url
        slide_block = driver.find_element_by_css_selector('#slideBlock').get_attribute('src')  # 小滑块 图片url
        slide_button = driver.find_element_by_css_selector('#tcaptcha_drag_button')

        os.makedirs('./image/', exist_ok=True)
        self.urllib_download(bk_block, './image/bkBlock.png')
        self.urllib_download(slide_block, './image/slideBlock.png')
        time.sleep(0.5)

        img_bkblock = Image.open('./image/bkBlock.png')
        real_width = img_bkblock.size[0]
        width_scale = float(real_width) / float(web_image_width)
        position = self.get_postion('./image/bkBlock.png', './image/slideBlock.png')
        real_position = position[1] / width_scale
        real_position = real_position - (slide_block_x - bk_block_x)
        track_list = self.get_track(real_position + 4)

        ActionChains(driver).click_and_hold(on_element=slide_button).perform()  # 点击鼠标左键，按住不放
        time.sleep(0.2)

        # print('第二步,拖动元素')
        for track in track_list:
            ActionChains(driver).move_by_offset(xoffset=track, yoffset=0).perform()  # 鼠标移动到距离当前位置（x,y）
            time.sleep(0.002)
        # 看一下微调的效果如何
        ActionChains(driver).move_by_offset(xoffset=-random.randint(0, 1), yoffset=0).perform()   # 微调，根据实际情况微调
        time.sleep(1)
        # print('第三步,释放鼠标')
        ActionChains(driver).release(on_element=slide_button).perform()
        time.sleep(1)

        print('滑动验证码破解成功')
        # self.after_quit()

    # 已改，后面再看看有没有必要退出浏览器，看起来不能马上就关掉这个。。。
    def after_quit(self):
        """
        关闭浏览器
        :return:
        """
        self.browser.quit()

if __name__ == '__main__':
    # 这里可能还要改一下测试的代码
    result = DoubanCookies('phone_num', 'your_password.', webdriver.Chrome()).main()
    print(result)
