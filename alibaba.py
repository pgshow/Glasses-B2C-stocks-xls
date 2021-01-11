import time
import re
import function
import json
from selenium import webdriver
import numpy
from bs4 import BeautifulSoup


"""采集阿里英文站全店铺数据"""
def get(page1, page2):

    # 初始信息
    URL = 'https://tzwanhui.en.alibaba.com'

    """抓取开始"""
    # 禁用图片和js
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        'profile.default_content_setting_values': {
            'images': 2,  # 不加载图片
            'javascript': 2,  # 不加载JS
        }
    }
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(r"C:\Users\Administrator\AppData\Local\Google\Chrome\Application\chromedriver.exe",
                              chrome_options=chrome_options)

    products = []

    # 抓取所有分页的产品URL
    for i in range(page1, page2):
        pageUrl = URL + '/productlist-' + str(i) + '.html'
        print("当前分页：" + pageUrl)

        driver.get(pageUrl)
        res = driver.page_source
        soup = BeautifulSoup(res, 'html.parser')

        list = soup.find_all('a', {'class': 'product-image', 'style': 'width:200px;height:200px'})

        # 抓取产品页信息
        for url in list:
            products.append(URL + url['href'])

        time.sleep(1)

    # 保持数据唯一性
    products_unique = numpy.unique(products)

    products_data = []  # 所有产品的信息

    # 抓取所有产品信息
    Num = 1
    for url in products_unique:
        driver.get(url)
        res = driver.page_source
        p_soup = BeautifulSoup(res, 'html.parser')

        # 标题
        title = p_soup.find('h1', {'class': 'ma-title'})["title"]
        print(str(Num) + "." + title)
        print(url)

        # 抓取主图
        main_pics = []
        pic_html = p_soup.find_all('div', {'class': 'thumb'})
        for p in pic_html:
            # 注意有些链接会含有 https
            if re.search("http", p.img['src']):
                pic_url = p.img['src'].replace("_50x50.jpg", "")
            else:
                pic_url = ("https:" + p.img['src'].replace("_50x50.jpg", ""))
            main_pics.append(pic_url)

        print(main_pics[0])

        # 抓取款式图
        style_name_pics = []
        style_html = p_soup.find_all('span', {'class': 'sku-attr-val-frame picture-frame'})
        for s in style_html:
            try:
                style_name_pics.append([re.sub(r"\W", " ", s.img['alt']).title(),
                                        "https:" + s.img['src'].replace("_100x100.jpg", "")])  # 款式名称里面不能有特殊字符，首字母改大写
            except Exception as ex:
                print(ex)
                pass

        # 获取产品参数
        choose = (
        'Lenses Material:', 'Frame Material:', 'Lens:', 'Material:', 'Lenses Optical Attribute:', 'Style:', 'Type:')
        profile_html = p_soup.find('div', {'class': 'do-entry do-entry-separate'})
        profile_tmp = re.findall(r"attr-name J-attr-name.+>(.+)</span>[\s\S]*?class=\"ellipsis.+>(.+)<\/div>",
                                 str(profile_html))

        profile_list = []
        model_number = ""

        # 只保存需要的参数
        for item in profile_tmp:
            if item[0] in choose:
                profile_list.append(item[0] + ": " + item[1])
            elif item[0] == "Model Number:":
                model_number = item[1]

        # 详情页图
        detail_pics = []
        detail_html = p_soup.find('div', {'id': 'J-rich-text-description'})
        detail_tmp = re.findall(r"<img.+?(?=alt=).*?src=\"(.+?)\".+?>|<img.+?(?<=alt=).*?src=\"(.+?)\".+?>",
                                str(detail_html))

        for d in detail_tmp:
            detail_pics.append("https:" + "".join(d))

        # 产品数据列表字典
        products_data.append({'型号': model_number,
                              '标题': title,
                              '地址': url,
                              '均价': 0,
                              '主图': main_pics,
                              '款式': style_name_pics,
                              '详情页': detail_pics,
                              '参数': profile_list})

        Num += 1
        time.sleep(1)

    driver.close()  # 关闭浏览器

    # 数据去重后返回
    return function.list_dict_unique(products_data, "型号")
