# coding=utf-8
"""
爬取Pixiv右栏推荐
"""
import re
#import time
import json
import queue
from threading import Lock, Thread
import requests
import AddHeaders
from selenium import webdriver
from pyvirtualdisplay import Display

class PSpider(object):
    """
    main
    """
    visited = []
    grabbers = []
    writers = []
    lockOfPos = Lock()
    dataQueue = queue.Queue()
    pidQueue = queue.Queue()
    rec = re.compile(r'<a href="/member_illust.php\?mode=medium&amp;illust_id=(\d*)&amp;uarea=recommend_on_member_illust"')
    origi = re.compile(r'data-src="(https://i.pximg.net/img-original.*)"\sclass="original-image"')
    ifmulti = re.compile(r'(\d)P')
    picname = re.compile(r'「(.*)」/「(.*)」')
    makebig = re.compile(r'mode=medium')
    urlid = re.compile(r'.*id=(.*)')
    def __init__(self):
        with open('option.json', 'r') as optionFile:
            option = json.load(optionFile)
            self.logpath = option['logpath']
            self.savepath = option['savepath']
            self.pidQueue.put(option['startpid'])
            self.Cookie = option['cookie']
        #self.pidlist.append(startid)

        with open(self.logpath,'r') as f:
            self.visited = f.read().split()
        for i in range(3):
            g = Thread(target=self.grab)
            self.grabbers.append(g)
            g.start()
        for j in range(3):
            w = Thread(target=self.write)
            self.writers.append(w)
            w.start()
        for i in range(3):
            self.grabbers[i].join()
        for j in range(3):
            self.writers[i].join()

        with open(self.logpath,'w') as f:
            for id in self.visited:
                f.write(id)
                f.write('\n')
            f.close()

    def __del__(self):
        pass
    def grab(self):
        """get original image, update pid list."""
        driver = webdriver.Chrome(chrome_options=AddHeaders.co)
        while 1:
            pid = self.pidQueue.get()
            url = 'http://www.pixiv.net/member_illust.php?mode=medium&illust_id='+pid
            pos = self.ifvisit(pid)
            if pos == -2:
                driver.get(url)
                for recommendId in self.rec.findall(driver.page_source):
                    self.pidQueue.put(recommendId)
                #self.pidlist+=self.rec.findall(self.driver.page_source)
                continue

            driver.get(url)

            multipic = driver.find_element_by_xpath("//div[@id='wrapper']/div[1]/div[1]/div/section[1]/ul/li[2]").get_attribute('innerHTML')
            multimatch = self.ifmulti.search(multipic)
            #write参数生成
            if multimatch:
                pages = int(multimatch.group(1))
                for page in range(pages):
                    purl = re.sub(self.makebig, "mode=manga_big", url) + "&page="+str(page)
                    driver.get(purl)
                    uri = driver.find_element_by_xpath('/html/body/img').get_attribute('src')
                    tempname = self.picname.findall(driver.title)
                    filename = self.savepath+tempname[0][0].replace('/','-')+' '+tempname[0][1].replace('/','-')+'['+str(page)+']'
                    self.dataQueue.put((filename, url, uri))
                    print(filename)
            else:
                uri = self.origi.findall(driver.page_source)[0]
                tempname = self.picname.findall(driver.title)
                filename = self.savepath+tempname[0][0].replace('/','-')+' '+tempname[0][1].replace('/','-')
                self.dataQueue.put((filename, url, uri))
                print(filename)

            for recommendId in self.rec.findall(driver.page_source):
                self.pidQueue.put(recommendId)
            #self.pidlist += self.rec.findall(self.driver.page_source)
            with self.lockOfPos:
                self.visited.insert(pos+1, pid)

    def write(self):
        while 1:
            filename, url, uri = self.dataQueue.get()
            print('Write process has got data.')
            req = requests.Session()
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
                "Cookie": self.Cookie,
                "referer": url,
            }
            origipic = req.get(uri,headers=headers)
            picflie = open(filename+'.'+self.pic_type(uri), 'wb')
            picflie.write(origipic.content)
            picflie.close()
            print('Write done!')
            self.dataQueue.task_done()
    def ifvisit(self, id):
        """ever visited, return -2, else return insert pos"""
        l, r = -1, len(self.visited)
        while l+1 != r:
            mid = (l + r) // 2
            if self.visited[mid] == id:
                print(mid)
                return -2
            else:
                if id<self.visited[mid]:
                    r = mid
                else:
                    l = mid
        return l

    def pic_type(self, real_url):
        """type of image"""
        p_type = re.search(re.compile('png', re.S), real_url)
        if p_type is None:
            return 'jpg'
        else:
            return 'png'

    def log(self, text):
        """log"""
        log = open(self.savepath+'plog.txt', 'w')
        log.write(text)
        log.close()

"""def setProxy(driver)
    driver.get('chrome-extension://padekgcemlokbadohgkifijomclgjgif/options.html#/io')
    time.sleep(2)
    driver.screenshot()
    driver.driver.find_element_by_xpath('/html/body/div[1]/main/section[2]/div/div/input').send_keys('http://127.0.0.1/OmegaOptions.bak')
    driver.driver.find_element_by_xpath('/html/body/div[1]/main/section[2]/div/div/span/button/span[1]').click()
    time.sleep(1)
    driver.driver.find_element_by_xpath('/html/body/div[1]/main/section[2]/div/div/span/button/span[1]').click()
    time.sleep(1)
"""

display = Display(visible=0, size=(1024, 768))
#display.start()
urlh = 'http://httpbin.org/headers'
driver = PSpider()
#setProxy(driver)

#display.stop()
