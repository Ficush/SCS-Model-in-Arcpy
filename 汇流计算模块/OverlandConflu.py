# -*- coding: utf-8 -*-
# -------------------------------------------
# 本文件用于计算坡面栅格汇流时间成本
# -------------------------------------------

# 导入模块
import arcpy

# 导入数据
import FloodData

floodList = FloodData.floodList

# 检查许可
arcpy.CheckOutExtension("spatial")

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
caclulateFolder = "新数据不改造竹林"

# 输入糙率栅格
overlandRoughness = arcpy.Raster(rootFolder + "汇流分析\\" + caclulateFolder + "\\土地利用糙率栅格\\糙率栅格.tif")

# 输入坡度栅格
slopeRaster = arcpy.Raster(rootFolder + "汇流分析\\" + caclulateFolder + "\\百分比坡度栅格\\坡度非零化.tif")

# 定义栅格大小
rasterCellSize = 45

# 定义净雨强度目录
rainfallFolder = rootFolder + "汇流分析\\" + caclulateFolder + "\\平均净雨强度\\"

# 定义坡面时间成本保存目录
overlandFolder = rootFolder + "汇流分析\\" + caclulateFolder + "\\时间成本栅格\\坡面时间成本\\"

# 定义流向栅格
inFlowDirRaster = rootFolder + "汇流分析\\" + caclulateFolder + "\\水文流向栅格\\流向.tif"

# 定义累积流量栅格目录
flowAccumulatePath = rootFolder + "汇流分析\\" + caclulateFolder + "\\累积流量栅格\\累积流量目录\\"

# 循环计算逐次洪水的平均净雨强度
for currentDate in currentDateList:

    # 获取降雨列表
    filedList = floodList[currentDate]

    # 获取最后一个小时的累积降雨量
    totalRainfallRaster = arcpy.Raster(rootFolder + "产流分析\\" + caclulateFolder + "\\降雨及产流\\" + currentDate + "\\Raster_Q_Total\\Raster_Q_Total_" + filedList[-1] + ".tif")

    # 计算平均净雨强度（单位：米每秒）
    avgRainfallRaster = totalRainfallRaster / (len(filedList) * 1000 * 3600)

    rainfallRaster = rainfallFolder + currentDate + ".tif"

    # 如净雨强度目录已有该文件，删除
    if arcpy.Exists(rainfallRaster):
        arcpy.Delete_management(rainfallRaster)

    # 保存到净雨强度目录
    avgRainfallRaster.save(rainfallRaster)

    print currentDate + " Rainfall Succeed! "

# 循环计算逐次洪水的累积流量
for currentDate in currentDateList:

    # 获取净雨强度
    rainfallRaster = rainfallFolder + currentDate + ".tif"
   
    # 如累积流量目录已有待输出文件，删除
    accRaster = flowAccumulatePath + currentDate + ".tif"

    if arcpy.Exists(accRaster):
        arcpy.Delete_management(accRaster)

    # 生成累积流量栅格
    arcpy.gp.FlowAccumulation_sa(inFlowDirRaster, accRaster, rainfallRaster, "FLOAT")


    print currentDate + " Accumulate Succeed! "

# 循环计算逐次洪水的坡面流速
for currentDate in currentDateList:

    rainfallRaster = arcpy.Raster(rainfallFolder + currentDate + ".tif")

    overlandTimecost = (
        (overlandRoughness ** 0.6)
        )/(
        (rainfallRaster ** 0.4) * (slopeRaster ** 0.3) * (rasterCellSize ** 0.4)
    )

    overlandTimecost.save(overlandFolder + currentDate + ".tif")

    print currentDate + " Overland Succeed! "
