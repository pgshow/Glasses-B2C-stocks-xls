#coding=utf-8
from selenium import webdriver
import imghdr
import json
import requests
import time
import os
import xlsxwriter
from io import BytesIO
from retrying import retry

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'zh-CN,zh;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'method': 'GET',
    'scheme': 'https',
}

'''
图片下载
@:param url_info ('http://img.xixik.net/custom/section/country-flag/xixik-cdaca66ba3839767.png','北马里亚纳群岛)
'''
def download_img(urls, dir_name, headers):
    i = 0
    for url in urls:
        i += 1

        # 保存路径
        path = dir_name + "/" + str(i) + ".jpg"

        isExists = os.path.exists(path)
        if isExists:
            print("----------- %s 图片存在" % (i))
            break

        time.sleep(1)

        print("----------- 正在下载图片 %s"%(url))
        # 这是一个图片的url
        try:
            response = requests.get(url, headers=headers)
            # 获取的文本实际上是图片的二进制文本
            img = response.content
            # 将他拷贝到本地文件 w 写  b 二进制  wb代表写入二进制文本
            with open(path, 'wb') as f:
                f.write(img)
        except Exception as ex:
            print(ex)
            pass


def download_style_img(urls, dir_name, headers):
    if not urls:
        return
    for url in urls:

        # 保存路径
        path = dir_name + "/" + url[1] + ".jpg"
        isExists = os.path.exists(path)

        if isExists:
            print("----------- %s 图片存在"%(url[1]))
            break

        time.sleep(1)

        print("----------- 正在下载图片 %s"%(url[0]))
        # 这是一个图片的url
        try:
            response = requests.get(url[0], headers=headers)
            # 获取的文本实际上是图片的二进制文本
            img = response.content
            # 将他拷贝到本地文件 w 写  b 二进制  wb代表写入二进制文本
            with open(path, 'wb') as f:
                f.write(img)
        except Exception as ex:
            print(ex)
            pass


def mkdir(path):
    # 引入模块
    import os

    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)

    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)

        print(path + ' 创建成功')
        time.sleep(0.5)
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print(path + ' 目录已存在')
        return False


"""获取阿里巴巴cookie"""
def login_cookie():
    driver = webdriver.Chrome(r"C:\Users\Administrator\AppData\Local\Google\Chrome\Application\chromedriver.exe")
    driver.get("https://wdeyewear.1688.com/")
    print("请先登录阿里巴巴")

    for i in range(1, 2):
        print(i)
        time.sleep(1)

    cookies = driver.get_cookies()
    with open("1688_cookies.txt", "w") as fp:
        json.dump(cookies, fp)

    driver.close()


@retry(wait_fixed=2000)
def save_excel(workbook):
    print("正在保存文件，请注意不要占用")
    workbook.close()


def excel(d, file_name):
    # 新建一个表文件
    workbook = xlsxwriter.Workbook(file_name)
    # 新建一个表
    worksheet = workbook.add_worksheet('new')
    worksheet.set_row(0, 155)
    worksheet.set_column(0, 1, 25)

    # 定义表头
    title = [u'图片', u'型号', u'标题', u'地址', u'均价', u'款式', u'参数']

    # 格式所有数据
    data = []
    i = 0
    for item in d:

        styles = []  # 款式的元祖数据转换成列表，并忽略url
        for s in item["款式"]:
            styles.append(s[0])

        data.append(
            [
                item["型号"],
                item["标题"],
                item["地址"],
                item["均价"],
                "\n".join(styles),
                "\n".join(item["参数"])
            ]
        )
        i += 1

    # 定义标题样式
    bold = workbook.add_format({
        'bold': 1,
        'align': 'center',
    })
    cell_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': 1,
    })

    # 内容的换行
    # cell_format = workbook.add_format()
    # cell_format.set_text_wrap()

    worksheet.write_row('A1', title, bold)

    # 写入数据
    for row_num, row_data in enumerate(data):
        worksheet.write_row(row_num + 1, 1, row_data, cell_format)  # 写入数据

    row = 2
    for item in d:
        # 写入图片
        url = item["主图"][0].replace(".jpg", ".200x200.jpg")
        response = requests.get(str(url), headers=headers)

        pic_data = response.content
        # 只写入有效的图片格式
        if imghdr.what('', pic_data):
            image_data = BytesIO(pic_data)
            print("正在写入图片：" + url)
            worksheet.insert_image(
                "A" + str(row),
                url,
                {'image_data': image_data, 'x_scale': 0.7, 'y_scale': 0.07}
            )
        row += 1
        time.sleep(0.2)

    #save_excel(worksheet)
    try:
        workbook.close()
    except:
        pass

    print("Excel保存完毕")


"""整理填充字典的列表-用于产品数据唯一性"""
def list_dict_unique(list, key):
    tmp = []
    tmp.append(list[0])

    for d in list:
        k = 0
        for item in tmp:
            if d[key] != item[key]:
                k += 1
            else:
                break
            if k == len(tmp):
                tmp.append(d)
    return tmp
