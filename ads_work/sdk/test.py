import json
import pygsheets
import pandas as pd
import mitmproxy.http
import xlwt
import xlsxwriter

# authorization
gc = pygsheets.authorize(
    service_file='/sdk/ads_work/sdk/yaohan-329808-1038d761d603.json')

list_network = ['AppLovin', 'Facebook', 'AdColony', 'Mintegral', 'Pangle', 'Vungle', 'Google AdMob', 'Fyber',
                'IronSource', 'Unity Ads', 'InMobi', 'Verizon', 'Smaato', 'Tapjoy', 'Chartboost', 'Verve',
                'Google ad manage']
list_info = []
info = {"eventName": 'interstitial_closed',
        "networkName": 'Facebook'}
list_info.append(info)

network = list_info[0]["networkName"]
index_network = list_network.index(network)

# 根据事件判断是iv 还是rv
if 'interstitial' in list_info[0]["eventName"]:
    column_video = 'B'
else:
    column_video = 'C'
# 找到文件
sh = gc.open('SDK常规测试')
# 选择第三个表格
wks = sh[2]

# 生成pygsheets的位置
cell_network = column_video + str(index_network + 2)

wks.cell(cell_network).set_text_format('bold', True).value = '已经找到'

wks.cell(cell_network).color(1.0,0,1.0,1.0)
