# -*- coding: utf-8 -*-
# -------------------------------------------
# 本文件用于分区统计各汇流时间的水量
# -------------------------------------------

# 导入模块
import arcpy
import os
import xlwt

# 导入数据
import FloodData

# 检查许可
arcpy.CheckOutExtension("spatial")

# 从配置中导入数据
floodList = FloodData.floodList

# 定义有效河道宽度列表
widthList = [5,10,15,20,25,30]

# 定义河道提取阈值列表
thresholdList = [0.003,0.004,0.0045,0.005,0.0055,0.006,0.007,0.008]

# 定义栅格单元大小
rasterCellSize  = 45

# 定义要计算的洪水日期
currentDateList = [
    "Y2015M05D19"
]

# 文件根目录
rootFolder = "D:\\工作项目\\长汀海绵城市水文研究\\基础数据\\"

# 定义要计算的文件夹
caclulateFolder = "新数据改造前"

# 输入重分类后的汇流时间栅格目录
reclassFolder = rootFolder + "汇流分析\\" + caclulateFolder + "\\时间成本栅格\\汇流时间\\"

# 输入保存表格的目录
resultDatabase = rootFolder + "汇流分析\\" + caclulateFolder + "\\时间成本栅格\\数据库.gdb\\"

# 对于每个洪水日期
for currentDate in currentDateList:

    # 输入存储 Excel 表的目录
    excelFolder = rootFolder + "计算结果\\汇流数据表\\" + caclulateFolder + "\\" + currentDate + "\\"

    # 如果该目录不存在，则创建
    if not os.path.exists(excelFolder.decode("UTF-8")):
        os.mkdir(excelFolder.decode("UTF-8"))

    # 河道宽度循环开始
    for width in widthList:

        # 提取阈值循环开始
        for threshold in thresholdList:

            # 定义循环名称
            circleName = "W" + str(width) + "T" + str(threshold)

            # 逐小时计算
            for index, filed in enumerate(floodList[currentDate]):

                try:

                    # 输入产流数据目录
                    valueFolder = rootFolder + "产流分析\\" + caclulateFolder + "\\降雨及产流\\" + currentDate + "\\Raster_Q_Timeline\\Raster_Q_"

                    # 获取栅格路径
                    timeRaster = reclassFolder + currentDate + "_" + circleName + "_Reclass.tif"
                    valueRaster = valueFolder + filed + ".tif"
                    resultTable = resultDatabase + filed + circleName.replace(".","_") 

                    # 如果输出的表在数据库中已存在，则删除旧表
                    if arcpy.Exists(resultTable):
                        arcpy.Delete_management(resultTable)

                    # 按区域统计属性
                    arcpy.gp.ZonalStatisticsAsTable_sa(timeRaster, "Value", valueRaster, resultTable, "DATA", "SUM")

                    printMessage = circleName + " | Zonal Succeed! : " + str(filed)
                    arcpy.AddMessage(printMessage)

                except Exception as e:

                    printMessage = circleName + " | Zonal Fail! : " + str(filed) + "|" + str(e)
                    arcpy.AddMessage(printMessage)

            # 分区统计结束
            
            # 将结果写入 Excel 表中
            resultExcel = excelFolder + currentDate + "_" + circleName + ".xls"
            dataExcel = xlwt.Workbook(encoding = 'utf-8')
            dataSheet = dataExcel.add_sheet(currentDate)

            # 逐小时计算
            for index, filed in enumerate(floodList[currentDate]):

                try:

                    objectTable = resultDatabase + filed + circleName.replace(".","_") 

                    # 读取分区统计结果
                    with arcpy.da.UpdateCursor(objectTable,["VALUE","SUM"]) as rows:

                        # 按行读取
                        for row in rows:

                            timeValue = row[0]
                            flowValue = float(row[1]) * rasterCellSize * rasterCellSize / 1000

                            # 如果时间不大
                            if timeValue <= 255:
                                # 将结果写入 Excel 中
                                dataSheet.write(timeValue + index - 1, index, flowValue)

                    # 保存文件
                    dataExcel.save(resultExcel.decode("UTF-8"))

                    printMessage = circleName + " | Write Data to Excel Succeed! : " + str(filed)
                    arcpy.AddMessage(printMessage)

                except Exception as e:

                    printMessage = circleName + " | Write Data to Excel Fail! : " + str(filed) + "|" + str(e)
                    arcpy.AddMessage(printMessage)

