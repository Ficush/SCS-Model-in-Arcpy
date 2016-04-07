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

# 指定要计算的洪量（是否经过基流切割，及基流切割方式）：
# 0 为未经切割的原始流量数据
# 1 为用数字滤波方法切割
# 2 为用 BFI(F) 方法切割
# 3 为用时间步长（Fixed）法切割
# 4 为用时间步长（Slide）法切割
baseflood = 4

basefloodList = {
    0: " 未切割基流 ",
    1: " 数字滤波 ",
    2: " BFI(F) ",
    3: " 时间步长（Fixed） ",
    4: " 时间步长（Slide） "
}

# 文件根目录
rootFolder = "D:\\工作项目\\长汀海绵城市水文研究\\基础数据\\"

# 定义要计算的文件夹
caclulateFolder = "新数据改造前"

# 输出表格头
print " 洪水日期 | 河道有效宽度 | 水系提取阈值 | 模型效率系数 R2 | 水量守恒指数 IVF | 洪峰流量误差 Pmax | 峰现时间误差 dT | 洪水时长 "

# 定义图像保存目录
imageFolder = rootFolder + "计算结果\\汇流数据图\\" + caclulateFolder + "\\" + str(baseflood) + "\\"

for currentDate in currentDateList:

    # 定义结果 Excel 目标文件夹
    excelFilePath = rootFolder + "计算结果\\汇流数据表\\" + caclulateFolder + "\\" + currentDate + "\\"

    # 定义洪量列表
    runoffList = [(x / 3600.00) for x in FloodData.floodValue[currentDate][baseflood]]

    # 若洪量列表为空，跳过
    if len(runoffList) == 0: continue

    # 计算平均径流量
    meanRunoff = sum(runoffList) / len(runoffList)

    # 计算径流量与均值之差的平方
    Variance = sum([(value - meanRunoff) ** 2 for value in runoffList])

    # 遍历 Excel 目标文件夹
    for root, dirs, files in os.walk(excelFilePath.decode("UTF-8")):

        # 遍历 Excel 文件
        for excelFile in files:
            
            # 打开文件
            excelData  = xlrd.open_workbook(os.path.join(root,excelFile))
            excelTabel = excelData.sheets()[0]

            # 定义流量结果列表
            resultList = []

            # 获取时段长度
            rowCount = len(runoffList)

            # 按行汇总
            for row in range(rowCount):

                # 初始值
                totalValue = 0

                # 读取一行中的每个单元格
                for col in range(rowCount):

                    try:
                        # 如果单元格非空
                        if excelTabel.cell(row,col).value != "":
                            totalValue += float(excelTabel.cell(row,col).value)

                    except:

                        continue

                # 将该行汇总的流量添加至流量结果列表中
                resultList.append(totalValue / 3600)

            # 计算方差
            MSEValue = 0
            for index, value in enumerate(resultList):
                MSEValue += (value - runoffList[index]) ** 2
            SquareR = 1 - MSEValue / Variance

            # 计算水量守恒指数
            VCIValue  = sum(resultList) / sum(runoffList)

            # 计算洪量守恒指数
            MaxVolume = max(resultList) / max(runoffList)

            # 计算洪峰时间差
            Timediffenrent = abs(resultList.index(max(resultList)) - runoffList.index(max(runoffList)))

            # 输出基本信息
            width = excelFile[excelFile.find("W") + 1:excelFile.find("T")]
            threshold = excelFile[excelFile.find("T") + 1:excelFile.find(".xls")]

            # 生成 Matplotlib 图像
            resultFigure = plt.figure()

            # 设置字体为 Times New Roman，设置标题
            fontFamily = matplotlib.font_manager.FontProperties(
                fname = 'C:/Windows/Fonts/times.ttf'
            )
            fontsize = 16


            # 定义曲线
            plt.plot(range(len(resultList)), runoffList, label = 'Observed', color = 'black')
            plt.plot(range(len(resultList)), resultList, label = 'Simulated', color = 'black', linestyle = "--")

            # 设置网格、图例
            plt.grid(); plt.legend(loc = 2, prop = {'family':'Times New Roman','size': fontsize})

            # 设置坐标刻度和坐标标题
            plt.xticks(fontsize = fontsize, fontproperties = fontFamily)
            plt.yticks(fontsize = fontsize, fontproperties = fontFamily)
            plt.xlabel('Time(' + r'$h$' + ')', fontsize = fontsize, fontproperties = fontFamily)
            plt.ylabel('Discharge(' + r'$m^{3}/s$' + ')', fontsize = fontsize, fontproperties = fontFamily)

            # 保存图片
            plt.savefig(imageFolder + excelFile[:-4] + ".png" )
            plt.close("all")

            # 输出文字结果
            print currentDate + " | " + \
                width + " | " + \
                threshold + " | " + \
                str(SquareR) + " | " + \
                str(VCIValue) + " | " + \
                str(MaxVolume) + " | " + \
                str(Timediffenrent) + " | " + \
                str(len(resultList))