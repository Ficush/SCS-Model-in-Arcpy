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

# 定义要计算的文件夹
caclulateFolder = "新数据改造前"

# 定义栅格单元大小
rasterCellSize  = 45

# 定义河道曼宁糙率
riverRoughness = 0.04

# 定义最大汇流量（按栅格个数累积）
maxAccumulate = 180758

# 定义有效河道宽度列表
widthList = [3,4,5,6,7,8,10,12,15,20,25,30]

# 定义河道提取阈值列表
thresholdList = [0.002,0.0025,0.003,0.004,0.0045,0.005,0.0055,0.006]

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
