import time
import alibaba
import com1688
import function

if __name__ == '__main__':
    print("1.制作阿里中文站表格   2.制作阿里英文站表格   3.采集1688图片   4.采集Alibaba图片")

    c = input("请输入你的命令:")

    if c is "1":
        data = com1688.get(1, 33)  # 从1页至n页
        function.excel(data, '1688产品总表.xlsx')
    elif c is "2":
        data = alibaba.get(1, 11)  # 从1页至n页
        function.excel(data, 'Alibaba产品总表.xlsx')
    elif c is "3":
        data = com1688.get(1, 33)  # 从1页至n页
        function.download_img(data)
    else:
        print("输入有误")
