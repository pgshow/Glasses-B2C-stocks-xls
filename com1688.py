import time
import re
import function
import json
from selenium import webdriver
import numpy
from bs4 import BeautifulSoup


"""采集1688中文全店铺数据"""
def get(page1, page2):
    # 初始信息
    URL = 'https://wdeyewear.1688.com'

    # 储存 cookie
    # function.login_cookie()

    """抓取开始"""
    # 禁用图片和js
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        'profile.default_content_setting_values': {
            'images': 2,  # 不加载图片
            'javascript':  2,  # 不加载JS
        }
    }
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(r"C:\Users\Administrator\AppData\Local\Google\Chrome\Application\chromedriver.exe",
                              chrome_options=chrome_options)

    # 先写入cookie
    # driver.get("https://wdeyewear.1688.com/")
    # with open("1688_cookies.txt", "r") as fp:
    #     cookies = json.load(fp)
    #     for cookie in cookies:
    #         driver.add_cookie(cookie)

    products = []

    # 抓取所有分页的产品URL
    for i in range(page1, page2):
        pageUrl = URL + '/page/offerlist.htm?pageNum=' + str(i)
        print("当前分页：" + pageUrl)

        driver.get(pageUrl)
        res = driver.page_source
        soup = BeautifulSoup(res, 'html.parser')

        list = soup.find_all('a', {'class': 'title-link'})

        # 抓取产品页信息
        for url in list:
            products.append(url['href'])

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

        # 获取标题
        title = p_soup.find('h1', {'class': 'd-title'}).get_text()
        print(str(Num) + "." + title)
        print(url)

        # 抓取主图
        pic_html = p_soup.find('div', {'class': 'tab-content-container'})
        main_pics = re.findall(r"<img.+?src=\"(.+?)\"", str(pic_html).replace(".60x60", ""))

        print(main_pics[0])

        # 抓取款式图
        style_html = p_soup.find('div', {'data-widget-name': 'offerdetail_ditto_purchasing'})
        style_name_pics = re.findall(r"<img alt=\"(.+?)\".+?src=\"(.+?.jpg)\"", str(style_html).replace(".32x32", ""))

        # 如果款式不是图片展示还得抓取文字
        if not style_name_pics:
            style_pics_tmp = re.findall(r"{\"name\":\"(.+?)\"|{\"skuName\":\"(.+?)\"", str(style_html))
            for item in style_pics_tmp:
                style_name_pics.append(("".join(item), "无图"))

        # 获取产品参数
        choose = ('产品类别', '材质', '是否偏光', '镜片材料', '风格', '镜架材料', '款式', '抗UV等级')
        profile_html = p_soup.find('div', {'id': 'mod-detail-attributes'})
        profile_tmp = re.findall(r"<td class=\"de-feature\">(.*)</td>\s*<td class=\"de-value\">(.*)</td>", str(profile_html))

        model_number_tmp = []
        profile_list = []

        # 只保存需要的参数
        for item in profile_tmp:
            if item[0] in choose:
                profile_list.append(item[0] + ": " + item[1])
            elif item[0] == "货号" or item[0] == "型号":
                model_number_tmp.append(item[1])
        try:
            model_number = model_number_tmp[0] if model_number_tmp[0] else model_number_tmp[1]
        except:
            model_number = "".join(model_number_tmp)
            if not model_number:
                model_number = "无型号"

        # 获取价格
        price_html = p_soup.find('tr', {'class': 'price'})

        # 两种价格情况（各等级批发价，以及款式不同价格不同）
        if str(price_html).find("--") != -1:
            # 以款式定价，取两头平均数
            prices_list = re.findall(r">([0-9.]+)<", str(price_html))
            price = (float(min(prices_list)) + float(max(prices_list)))/2

        else:
            # 以数量定价，取最小数
            prices_list = re.findall(r">([0-9.]+)<", str(price_html))
            price = float(min(prices_list))

        # 详情页图
        detail_pics = []
        detail_html = p_soup.find('div', {'data-widget-name': 'offerdetail_w1190_description'})
        content_url = re.findall(r"contentUrl\":\"(.+?)\"", str(detail_html))

        # 详情页内容在一个单独的页面里面
        driver.get(content_url[0])
        c_res = driver.page_source
        detail_pics_tmp = re.findall(r"src=\\\"(https://.+?.jpg)\\\"", c_res)

        for item in detail_pics_tmp:
            if not re.search(r"\d{3}x\d{3}", item):  # 去掉小图片
                detail_pics.append(item)

        # 产品数据列表字典
        products_data.append({'型号': model_number,
                              '标题': title,
                              '地址': url,
                              '均价': price,
                              '主图': main_pics,
                              '款式': style_name_pics,
                              '详情页': detail_pics,
                              '参数': profile_list})

        Num += 1
        time.sleep(1)

    driver.close()  # 关闭浏览器

    # 数据去重后返回
    return function.list_dict_unique(products_data, "型号")
