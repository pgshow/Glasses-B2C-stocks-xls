import requests
import time
import os
import function
from bs4 import BeautifulSoup

# 初始信息
URL = 'https://tzwanhui.en.alibaba.com'
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'authority': 'tzwanhui.en.alibaba.com',
    'method': 'GET',
    'path': '/productlist-7.html',
    'scheme': 'https',
}

# 抓取开始
for i in range(7,10):
    pageUrl = URL + '/productlist-' + str(i) + '.html'
    print("当前分页：" + pageUrl)
    print("----抓取页面")

    res = requests.get(pageUrl, headers = headers)
    time.sleep(1)

    soup = BeautifulSoup(res.text, 'html.parser')
    # soup = soup.select('.module-product-list')
    #
    # BeautifulSoup(soup, 'html.parser')
    #
    # print(soup.find_all('div #icbu-product-card vertical'))

    list = soup.find_all('a', {'class': 'product-image', 'style': 'width:200px;height:200px'})
    #soup.find('a', {'class': 'nav-span', 'data-bn-ipg': 'head-nav-community'})
    #print(soup.find_all('a #product-image icbu-link-normal'))

    # 抓取产品页信息
    for url in list:
        p_url = URL + url['href']
        print("    " + p_url)
        p_res = requests.get(p_url, headers=headers)

        # soup 获取数据
        p_soup = BeautifulSoup(p_res.text, 'html.parser')

        # 型号
        model_number = ""
        profile_html = p_soup.find_all('dl', {'class': 'do-entry-item'})
        for p in profile_html:
            pstr = p.get_text()
            if pstr.find("Model Number:") >= 0:
                pstr = pstr.replace("Model Number:", "").strip()
                model_number = pstr

        # 标题
        title = p_soup.find('h1', {'class': 'ma-title'})["title"]

        # 主图
        main_pics = []
        pic_html = p_soup.find_all('div', {'class': 'thumb'})
        for p in pic_html:
            main_pics.append("https:" + p.img['src'].replace("_50x50.jpg", ""))

        # 款式
        style_pics = []
        style_html = p_soup.find_all('span', {'class': 'sku-attr-val-frame picture-frame'})
        for s in style_html:
            try:
                style_pics.append(("https:" + s.img['src'].replace("_100x100.jpg", ""), s.img['alt'].replace("/", "+")))
            except Exception as ex:
                print(ex)
            pass

        # 详情页图
        detail_pics = []
        detail_html = p_soup.find_all('img', {'alt': title, 'ori-width': "790"})
        for d in detail_html:
            detail_pics.append("https:" + d['src'])

        """开始保存文件"""
        # 创建产品文件夹
        if model_number:
            dir_name = "阿里国际/" + model_number + " -- " + title.replace("/", "+")
        else:
            dir_name = "阿里国际/" + title.replace("/", "+")

        # 过滤有问题的字符
        dir_name = dir_name.replace("*", "+")

        function.mkdir(dir_name)

        f = open(dir_name+'/说明.txt', 'w')
        time.sleep(0.5)
        f.write(p_url)
        f.close()
        time.sleep(0.5)

        # 抓取主图
        function.mkdir(dir_name+"/主图")
        function.download_img(main_pics, dir_name+"/主图", headers)

        # 抓取款式
        function.mkdir(dir_name + "/款式")
        function.download_style_img(style_pics, dir_name + "/款式", headers)

        # 抓取详情页图片
        function.mkdir(dir_name + "/详情页")
        function.download_img(detail_pics, dir_name + "/详情页", headers)

        time.sleep(1)

    time.sleep(2)