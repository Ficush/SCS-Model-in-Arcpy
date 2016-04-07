# -*- coding: utf-8 -*-

# 导入模块
import arcpy

# 导入数据
import FloodData

# 检查许可
arcpy.CheckOutExtension("spatial")

# 需要计算产流的洪水日期列表
currentDateList = [
    "Y2012M06D10"
]

floodList = FloodData.floodList

# 文件根目录
rootFolder = "D:\\工作项目\\长汀海绵城市水文研究\\基础数据\\"

# 逐次洪水循环
for currentDate in currentDateList:

    # 定义输入的雨量站点数据
    pointData = rootFolder + "基本要素\\雨量站数据\\雨量站点.gdb\\" + currentDate
    
    # 逐小时循环
    for index, filed in enumerate(floodList[currentDate]):

        try:

            # 当不是第一个时段时，对其进行累加，累积降雨量等于前一时段累积降雨加本时段降雨
            if index != 0:
                expression = "!" + filed + "! + !" + floodList[currentDate][index-1] + "!"
                arcpy.CalculateField_management(pointData, filed, expression, "PYTHON_9.3")

            printMessage = "Succeed: " + str(filed)
            arcpy.AddMessage(printMessage)

        except Exception as e:

            printMessage = "Fail: " + str(filed)
            arcpy.AddMessage(printMessage)
            arcpy.AddMessage(str(e))
