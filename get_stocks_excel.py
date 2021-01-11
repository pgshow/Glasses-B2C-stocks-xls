import xlrd
import xlsxwriter

"""整理仓库数据"""
data = xlrd.open_workbook('仓库编号.xls')

sheet = data.sheets()[0]

row_num = sheet.nrows  # 总行数
col_num = sheet.ncols  # 总列数

"""通过算法整理数据"""
data_tmp = []
data_tmp.append({
    '型号': sheet.row_values(1)[1],
    '款式': [sheet.row_values(1)[2] + " : " + sheet.row_values(1)[4]],
})

for i in range(2, row_num):
    k = 0
    d = sheet.row_values(i)

    for item in data_tmp:
        if d[1] != item["型号"]:
            k += 1
        else:
            item["款式"].append(d[2] + " : " + d[4])
            break
        if k == len(data_tmp):
            data_tmp.append({
                '型号': d[1],
                '款式': [d[2] + " : " + d[4]],
            })

"""保存数据到excel"""
# 新建一个表文件
workbook = xlsxwriter.Workbook("仓库_整理_new.xlsx")
# 新建一个表
worksheet = workbook.add_worksheet('new')

cell_format = workbook.add_format({
    'text_wrap': 1,
})

# 定义表头
title = [u'型号', u'款式']

# 写前数据格式
data = []
for item in data_tmp:
    data.append([
        item['型号'],
        "\n".join(item['款式'])
    ])

# 写入数据
for row_num, row_data in enumerate(data):
    worksheet.write_row(row_num + 1, 0, row_data, cell_format)  # 写入数据

print("仓库_整理_new.xlsx 生成完成")
workbook.close()