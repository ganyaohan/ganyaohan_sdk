import json
import pygsheets
import datetime
import pandas as pd
import mitmproxy.http
import xlwt
import xlsxwriter

'''
按照timestamp（事件发生时间）顺序对事件进行排序插入
1.核对一个广告的show、open、closed顺序
2.核对观看广告的ID，大概有和玩家相关的advertisingId,adjustId,userId,和广告相关的adUnitId,creativeId,adunit
https://ads-bi-beta.zenkube
待解决：

'''

# authorization
gc = pygsheets.authorize(
    service_file='/sdk/ads_work/sdk/yaohan-329808-1038d761d603.json')
# 找到文件
sh = gc.open('SDK常规测试')
# 选择第三个表格
wks = sh[2]

list_info = []
list_dailyrevenue = []
list_order = ['show', 'open', 'closed']
list_type = ["banner", "interstitial", "rewardedVideo"]
list_id = ['adunit', 'creativeId', 'advertisingId', 'adjustId', 'userId']
list_network = ['AppLovin', 'Facebook', 'AdColony', 'Mintegral', 'Pangle', 'Vungle', 'Google AdMob', 'Fyber',
                'IronSource', 'Unity Ads', 'InMobi', 'Verizon', 'Smaato', 'Tapjoy', 'Chartboost', 'Verve',
                'Google Ad Manager']


def request(flow):
    if flow.request.url == "https://ads-bi-beta.zenkube.com/ads":
        body = json.loads(flow.request.get_text())
        if "revenue_paid" in body["eventName"]:
            request_revenue(body)
        else:
            for x in list_order:
                # 如果是需要操作的事件
                if x in body["eventName"]:
                    info = {
                        "timestamp": body["timestamp"],
                        "eventName": body["eventName"],
                        "networkName": body["parameters"]["mediationInfo"]["networkName"],
                        "adjustId": body["adjustId"],
                        "advertisingId": body["advertisingId"],
                        "userId": body["userId"],
                        "adunit": body["parameters"]["adunit"],
                        "creativeId": body["parameters"]["mediationInfo"]["creativeId"],
                    }
                    if 'banner' not in info["eventName"]:
                        list_info.append(info)
                        list_info.sort(key=takeTimestampe)
                        print(list_info)
                        check_order()
                    break


def takeTimestampe(elem):
    return elem["timestamp"]

def request_revenue(body: json):
    dailyRevenue = {
        "revenue": body["parameters"]["revenue"],
        "eventName": body["eventName"],
        "timestamp": body["timestamp"],
        "networkName": body["parameters"]["mediationInfo"]["networkName"],
        "adunit": body["parameters"]["adunit"],
        "banner": body["invalids"]["dailyRevenue"]["banner"],
        "rewardedVideo": body["invalids"]["dailyRevenue"]["rewardedVideo"],
        "interstitial": body["invalids"]["dailyRevenue"]["interstitial"]
    }
    list_dailyrevenue.append(dailyRevenue)
    list_dailyrevenue.sort(key=takeTimestampe)
    if len(list_dailyrevenue) >= 3:
        daily_revenue()


# 检查加的值和类型、检查过utc零点有没有清零
def daily_revenue():
    timestamp_utc0 = '00:00:00 +0000'
    for x in range(-3, -1):
        revenue_a = list_dailyrevenue[x]
        revenue_b = list_dailyrevenue[x+1]
        timestamp_a = revenue_a["timestamp"].split(' ')[1]
        timestamp_b = revenue_b["timestamp"].split(' ')[1]
        # 等于零可能就没有这个字段了！
        # 首次启动没有字段哪个看了哪个有。。。。补字段吗
        if timestamp_a > timestamp_b > timestamp_utc0:
            for ad_type in list_type:
                if revenue_b[ad_type] != 0:
                    save_error(ad_type + "过utc0但是未清零", [revenue_a, revenue_b])
        else:
            for ad_type in list_type:
                if ad_type in revenue_b["eventName"]:
                    if revenue_a[ad_type] + revenue_b["revenue"] != revenue_b[ad_type]:
                        save_error(ad_type + "revenue错误", [revenue_a, revenue_b])


def check_order():
        global list_info
        if len(list_info) == len(list_order):
            for i in range(0, len(list_order)):
                if list_order[i] not in list_info[i]["eventName"]:
                    print('顺序错误')
                    save_error('广告事件顺序错误',list_info)

            check_idinfo()
            # 保存广告渠道并清空list
            save_network()
            list_info = []

        elif len(list_info) > len(list_order):
            list_info = []


def check_idinfo():
    global list_info
    global list_id
    for id in list_id:
        for num in range(1, len(list_info)):
            if list_info[num - 1][id] != list_info[num][id]:
                print(id + '错误')
                save_error(id + '错误', list_info)
                break


def save_error(err_message, list_error):
    fp = open("/sdk/ads_work/sdk/Save Error.txt", 'a+')
    fp.write(err_message + '\n')
    for x in list_error:
        fp.write(str(x) + '\n')


def save_network():
    # 根据渠道找到写入位置的行数
    network = list_info[0]["networkName"]
    index_network = list_network.index(network)

    # 根据事件判断是iv 还是rv
    if 'interstitial' in list_info[0]["eventName"]:
        column_video = 'B'
    else:
        column_video = 'C'

    # 生成pygsheets的位置
    cell_network = column_video + str(index_network + 2)
    wks.cell(cell_network).set_text_format('bold', True).value = '已经找到'
