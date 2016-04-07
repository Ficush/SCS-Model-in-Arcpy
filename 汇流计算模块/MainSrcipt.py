# -*- coding: utf-8 -*-
# -------------------------------------------
# 本文件用于计算河流时间成本及总的汇流时间
# -------------------------------------------

# 导入模块
import arcpy
import xlwt
import os
import FloodData

# 检查许可
arcpy.CheckOutExtension("spatial")

# 从配置中导入数据
reclassFunction = FloodData.ReclassFunction
floodList = FloodData.floodList

# 需要计算汇流的洪水日期列表
# currentDateList = [
#     "Y2012M06D10",
#     "Y2012M08D03",
#     "Y2015M05D19",
#     "Y2015M05D26"
# ]

currentDateList = [
    "Y2012M04D23",
    "Y2012M05D01",
    "Y2013M08D22",
    "Y2015M07D03"
]

# 文件根目录
rootFolder = "D:\\工作项目\\长汀海绵城市水文研究\\基础数据\\"

# 定义要计算的文件夹
caclulateFolderList = ["新数据改造后", "新数据不改造竹林"]

# 定义栅格单元大小
rasterCellSize  = 45

# 定义河道曼宁糙率
riverRoughness = 0.04

# 定义最大汇流量（按栅格个数累积）
maxAccumulate = 180758

# 定义有效河道宽度列表
widthList = [8]

# 定义河道提取阈值列表
thresholdList = [0.002]

# 循环要计算的文件夹
for caclulateFolder in caclulateFolderList:

    # 输入原始累积流量栅格（按栅格个数累积）
    flowAccumulate = arcpy.Raster(rootFolder + "汇流分析\\" + caclulateFolder + "\\累积流量栅格\\简单累积流量.tif")

    # 定义累积流量栅格目录
    flowAccumulatePath = rootFolder + "汇流分析\\" + caclulateFolder + "\\累积流量栅格\\累积流量目录\\"

    # 输入流向栅格
    flowDirection = arcpy.Raster(rootFolder + "汇流分析\\" + caclulateFolder + "\\水文流向栅格\\流向.tif")

    # 输入坡度栅格
    slopeRaster = arcpy.Raster(rootFolder + "汇流分析\\" + caclulateFolder + "\\百分比坡度栅格\\坡度非零化.tif")

    # 定义坡面汇流时间成本目录
    overlandFolder = rootFolder + "汇流分析\\" + caclulateFolder + "\\时间成本栅格\\坡面时间成本\\"

    # 定义汇流时间成本目录
    timeCostFolder = rootFolder + "汇流分析\\" + caclulateFolder + "\\时间成本栅格\\总时间成本\\"

    # 定义汇流时间目录
    flowTimeFolder = rootFolder + "汇流分析\\" + caclulateFolder + "\\时间成本栅格\\汇流时间\\"

    # 计算每次洪水的时间成本
    for currentDate in currentDateList:

        # 不同河道宽度取值，循环开始
        for width in widthList:

            # 不同提取阈值取值，循环开始
            for threshold in thresholdList:

                # 定义循环名称
                circleName = "W" + str(width) + "T" + str(threshold)

                try:

                    # 输入基准坡面汇流时间成本栅格
                    overlandTimeCost = arcpy.Raster(overlandFolder + currentDate + ".tif")

                    # 输入汇流累积量
                    currentFlowAccumulate = arcpy.Raster(flowAccumulatePath + currentDate + ".tif")
                    
                    # 计算提取阈值对应的栅格阈值
                    riverThreshold = maxAccumulate * threshold

                    # 提取河道及其累积流量
                    riverFlowAccumulate = arcpy.sa.Con(flowAccumulate > riverThreshold, currentFlowAccumulate)

                    # 计算河道时间成本
                    riverTimeCost = (
                        (riverRoughness ** 0.6) * (width ** 0.4)
                        )/(
                        ((riverFlowAccumulate * rasterCellSize * rasterCellSize) ** 0.4) * (slopeRaster ** 0.4)
                    )
                    print currentDate + " | " + circleName + " | Timecost of River | Succeed! "

                    # 利用栅格镶嵌工具计算总时间成本
                    arcpy.MosaicToNewRaster_management(
                        input_rasters = [overlandTimeCost, riverTimeCost],
                        output_location = timeCostFolder,
                        raster_dataset_name_with_extension = currentDate + "_" + circleName + "_TimeCost.tif",
                        coordinate_system_for_the_raster = "#",
                        pixel_type = "32_BIT_FLOAT",
                        cellsize = "#",
                        number_of_bands = "1",
                        mosaic_method = "MINIMUM",
                        mosaic_colormap_mode = "FIRST"
                    )

                    print currentDate + " | " + circleName + " | Mosaic Timecost | Succeed! "

                    # 生成的总时间成本的路径
                    totalTimecost = timeCostFolder + currentDate + "_" + circleName + "_TimeCost.tif"

                    # 利用水流长度工具计算汇流时间
                    arcpy.gp.FlowLength_sa(flowDirection, flowTimeFolder + currentDate + "_" + circleName + "_FlowLength.tif", "DOWNSTREAM", totalTimecost)

                    print currentDate + " | " + circleName + " | FlowLength | Succeed! "

                    # 对汇流时间进行重分类
                    arcpy.gp.Reclassify_sa(
                        flowTimeFolder + currentDate + "_" + circleName + "_FlowLength.tif",
                        "Value",
                        reclassFunction,
                        flowTimeFolder + currentDate + "_" + circleName + "_Reclass.tif"
                    )

                    print currentDate + " | " + circleName + " | FlowLength Reclass | Succeed! "

                except Exception as e:

                    print currentDate + " | " + circleName + "Fail: "  + str(e)
                    continue

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