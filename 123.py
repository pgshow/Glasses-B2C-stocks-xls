try:
    response = requests.get(url[0], headers=headers)
    # 获取的文本实际上是图片的二进制文本
    img = response.content
    # 将他拷贝到本地文件 w 写  b 二进制  wb代表写入二进制文本
    with open(path, 'wb') as f:
        f.write(img)