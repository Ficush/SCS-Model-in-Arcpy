# -*- coding: utf-8 -*-

# 导入模块
import os
import math
import sys
import xlrd

# 导入制图模块
import matplotlib
import matplotlib.pyplot as plt
import numpy

# 导入数据
import FloodData

# 定义要计算的洪水日期
currentDateList = [
    "Y2012M04D23",
    "Y2012M05D01",
    "Y2012M05D14",
    "Y2012M06D10",
    "Y2012M08D03",
    "Y2013M08D22",
    "Y2015M05D19",
    "Y2015M05D26",
    "Y2015M07D03"
]

# 文件根目录
rootFolder = "D:\\工作项目\\长汀海绵城市水文研究\\基础数据\\"

# 要对比的基准文件夹
baseFolder = "新数据改造前"

# 要对比的目标文件夹
caclulateFolder = "新数据改造后"

# 定义图像保存目录
imageFolder = rootFolder + "计算结果\\汇流数据图\\改造对比\\" + caclulateFolder + "\\"

print " 洪水场次 | 河道宽度 | 水系提取阈值 | 改造前洪峰流量 | 改造后洪峰流量 | 改造前总流量 | 改造后总流量 "

for currentDate in currentDateList:

    # 定义要对比的目标 Excel 目标文件夹
    caclulateFilePath = rootFolder + "计算结果\\汇流数据表\\" + caclulateFolder + "\\" + currentDate + "\\"
    
    # 定义要对比的基准 Excel 目标文件夹
    baseFilePath = rootFolder + "计算结果\\汇流数据表\\" + baseFolder + "\\" + currentDate + "\\"

    # 定义洪量列表
    runoffList = FloodData.floodValue[currentDate][0]

    # 若洪量列表为空，跳过
    if len(runoffList) == 0: continue

    # 遍历要对比的 Excel 目标文件夹
    for root, dirs, files in os.walk(caclulateFilePath.decode("UTF-8")):

        # 遍历 Excel 文件
        for excelFile in files:
            
            # 打开文件
            caclulateExcelData  = xlrd.open_workbook(os.path.join(root,excelFile))
            caclulateExcelTabel = caclulateExcelData.sheets()[0]

            # 打开对应的基准文件
            baseExcelData  = xlrd.open_workbook(os.path.join(str(root).replace(caclulateFolder,baseFolder),excelFile))
            baseExcelTabel = baseExcelData.sheets()[0]

            # 定义流量结果列表
            caclulateResultList = []
            baseResultList = []

            # 获取时段长度
            rowCount = len(runoffList)

            # 按行汇总
            for row in range(rowCount):

                # 初始值
                caclulateTotalValue = 0
                baseTotalValue = 0

                # 读取一行中的每个单元格
                for col in range(rowCount):

                    try:
                        # 如果单元格非空
                        if caclulateExcelTabel.cell(row,col).value != "":
                            caclulateTotalValue += float(caclulateExcelTabel.cell(row,col).value)
                        
                        if baseExcelTabel.cell(row,col).value != "":
                            baseTotalValue += float(baseExcelTabel.cell(row,col).value)

                    except:

                        continue

                # 将该行汇总的流量添加至流量结果列表中
                caclulateResultList.append(caclulateTotalValue)
                baseResultList.append(baseTotalValue)

            # 输出基本信息
            width = excelFile[excelFile.find("W") + 1:excelFile.find("T")]
            threshold = excelFile[excelFile.find("T") + 1:excelFile.find(".xls")]

            # 生成 Matplotlib 图像
            resultFigure = plt.figure()            

            # 定义曲线
            plt.plot(range(len(runoffList)), baseResultList, label = 'Before', color = 'red')
            plt.plot(range(len(runoffList)), caclulateResultList, label = 'After', color = 'blue')

            # 设置网格、图例，并保存图片
            plt.grid(); plt.legend(loc = 2)
            plt.savefig(imageFolder + excelFile[:-4] + ".png" )
            plt.close("all")

            # 输出文字结果
            print currentDate + " | " + \
                width + " | " + \
                threshold + " | " + \
                str(max(baseResultList)/3600) + " | " + \
                str(max(caclulateResultList)/3600) + " | " + \
                str(sum(baseResultList)) + " | " + \
                str(sum(caclulateResultList))