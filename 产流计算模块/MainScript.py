# -*- coding: utf-8 -*-

# 导入模块
import arcpy
import FloodData

# 检查许可
arcpy.CheckOutExtension("spatial")

# 需要计算产流的洪水日期列表
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

# 是否计算克里金、1：计算，0：跳过
doKriging = 0

# 文件根目录
rootFolder = "D:\\工作项目\\长汀海绵城市水文研究\\基础数据\\"

# 定义要计算的文件夹
caclulateFolder = "新数据不改造竹林"

# 定义栅格单元大小
rasterCellSize  = 45

# 定义逐小时产流的计算方式，若为真则允许有负值（保持产流总量的一致）
allowNegativeValue = True

floodList = FloodData.floodList
floodSoilType = FloodData.floodSoilType

# 循环开始
for currentDate in currentDateList:

    # 获取降雨列表
    filedList = floodList[currentDate]

    # 获取土壤湿度
    SoilHumidity = floodSoilType[currentDate]

    # 输入雨量站数据和流域范围
    InputPoint = rootFolder + "基本要素\\雨量站数据\\雨量站点.gdb\\" + currentDate
    FlowRange = rootFolder + "基本要素\\观音桥流域范围\\观音桥上游流域.shp"
    extentFeature = arcpy.Describe(FlowRange)

    OutputCellSize = rasterCellSize

    # 定义克里金插值方法
    KrigingMethod = "Spherical #"

    # 如果要计算克里金降雨插值
    if doKriging != 0:

        # 本循环对逐小时累积降雨进行克里金插值
        for filed in filedList:

            try:

                arcpy.env.extent = extentFeature.extent

                # 中间栅格
                MiddleRaster1 = "C:\\Users\\Ficush\\Documents\\ArcGIS\\Default.gdb\\" + filed + "A"
                MiddleRaster2 = "C:\\Users\\Ficush\\Documents\\ArcGIS\\Default.gdb\\" + filed + "B"

                # 输出栅格目录
                OutputRaster = rootFolder + "产流分析\\" + caclulateFolder + "\\降雨及产流\\" + currentDate + "\\Raster_P_Total\\Raster_P_Total_" + filed + ".tif"

                # Process: 克里金法
                arcpy.gp.Kriging_sa(InputPoint, filed, MiddleRaster1, KrigingMethod, OutputCellSize, "VARIABLE 12", None)

                # Process: 栅格计算器，去除负值
                outCon = arcpy.sa.Con(MiddleRaster1, 0, MiddleRaster1, "VALUE <= 0")
                outCon.save(MiddleRaster2)

                # Process: 按流域范围的掩膜提取
                arcpy.gp.ExtractByMask_sa(MiddleRaster2, FlowRange, OutputRaster)

                # 删除中间栅格
                arcpy.Delete_management(MiddleRaster1)
                arcpy.Delete_management(MiddleRaster2)

                printMessage = str(currentDate) + " | Kriging Succeed: " + str(filed)
                arcpy.AddMessage(printMessage)

            except Exception as e:

                printMessage = str(currentDate) + " | Kriging Fail: " + str(filed)
                arcpy.AddMessage(printMessage)
                arcpy.AddMessage(str(e))

    #  本循环计算逐小时的累积产流量  
    for filed in filedList:
    
        try:

            # 输入降雨栅格和对应土壤湿度的潜在入渗量栅格
            Raster_P = arcpy.Raster(rootFolder + "产流分析\\" + caclulateFolder + "\\降雨及产流\\" + currentDate + "\\Raster_P_Total\\Raster_P_Total_" + filed + ".tif")
            Raster_S = arcpy.Raster(rootFolder + "产流分析\\" + caclulateFolder + "\\潜在入渗量\\Raster_" + SoilHumidity + "_45m.tif")

            # 输出栅格目录
            OutputRaster = rootFolder + "产流分析\\" + caclulateFolder + "\\降雨及产流\\" + currentDate + "\\Raster_Q_Total\\Raster_Q_Total_" + filed + ".tif"

            # 计算产流
            Raster_Q = arcpy.sa.Con(Raster_P >= (0.2 * Raster_S),arcpy.sa.Con(Raster_P + Raster_S >0,((Raster_P - 0.2 * Raster_S) ** 2)/ (Raster_P + 0.2 * Raster_S),0),0)
            Raster_Q.save(OutputRaster)

            printMessage = str(currentDate) + " | Calculate Total Q Succeed: " + str(filed)
            arcpy.AddMessage(printMessage)

        except Exception as e:

            printMessage = str(currentDate) + " | Calculate Total Q Fail: " + str(filed)
            arcpy.AddMessage(printMessage)
            arcpy.AddMessage(str(e))

    # 本循环通过前后相减计算逐小时净产流量（未经去除负值处理）
    for index, filed in enumerate(filedList):

        try:

            # 不是第一小时，该时段净产流量等于该小时产流累积量减去前一小时产流累积量
            if index != 0:
            
                Raster_First = arcpy.Raster(rootFolder + "产流分析\\" + caclulateFolder + "\\降雨及产流\\" + currentDate + "\\Raster_Q_Total\\Raster_Q_Total_" + filedList[index-1] + ".tif")
                Raster_Sencond = arcpy.Raster(rootFolder + "产流分析\\" + caclulateFolder + "\\降雨及产流\\" + currentDate + "\\Raster_Q_Total\\Raster_Q_Total_" + filedList[index] + ".tif")
                
                # 逐小时产流的计算方式，参见脚本开头关于参数 allowNegativeValue 的说明
                if allowNegativeValue:
                    Raster_Outcome = Raster_Sencond - Raster_First
                else:
                    Raster_Outcome = arcpy.sa.Con(Raster_Sencond >= Raster_First, Raster_Sencond - Raster_First, 0)

            # 是第一小时，该时段净产流量等于该小时产流累积量
            else:

                Raster_Outcome = arcpy.Raster(rootFolder + "产流分析\\" + caclulateFolder + "\\降雨及产流\\" + currentDate + "\\Raster_Q_Total\\Raster_Q_Total_" + filedList[index] + ".tif")

            # 保存栅格            
            OutputRaster = rootFolder + "产流分析\\" + caclulateFolder + "\\降雨及产流\\" + currentDate + "\\Raster_Q_Timeline\\Raster_Q_" + filedList[index] + ".tif"
            Raster_Outcome.save(OutputRaster)

            printMessage = str(currentDate) + " | Calculate Q Succeed: " + str(filed)
            arcpy.AddMessage(printMessage)

        except Exception as e:

            printMessage = str(currentDate) + " | Calculate Q Fail: " + str(filed)
            arcpy.AddMessage(printMessage)
            arcpy.AddMessage(str(e))
