import json
import mitmproxy.http

def check_order():
    fp = open("/sdk/ads_work/sdk/Request.json", 'r')
    list_info = fp.readlines()
    list_d = []
    for x in list_info:
        x = json.loads(x)
        list_d.append(x)
    if len(list_d) >=3:
        if 'show' in list_d[-1]["eventName"]:
            assert 'closed' in list_d[-2]["eventName"], 'closed后面不是show'
            print('show 测试完成')
        elif 'open' in list_d[-1]["eventName"]:
            assert 'show' in list_d[-2]["eventName"], 'show后面不是open'
            print('open 测试完成')
        elif 'closed' in list_d[-1]["eventName"]:
            assert 'open' in list_d[-2]["eventName"], 'open后面不是closed'
            print('closed 测试完成')
            check_userinfo(list_d)
            chece_videoinfo(list_d)

def chece_videoinfo(list_info):
    assert list_info[-1]["adunit"] == list_info[-2]["adunit"] == list_info[-3]["adunit"], 'adunit不统一'
    print('adunit 测试完成')
    assert list_info[-1]["creativeId"] == list_info[-2]["creativeId"] == list_info[-3]["creativeId"], 'creativeId不统一'
    print('creativeid 测试完成')

def check_userinfo(list_info):
    assert list_info[-1]["advertisingId"] == list_info[-2]["advertisingId"] ==list_info[-3]["advertisingId"]==list_info[-4]["advertisingId"],'advertisingId不统一'
    print('advertisingId 测试完成')
    assert list_info[-1]["adjustId"] == list_info[-2]["adjustId"] ==list_info[-3]["adjustId"]==list_info[-4]["adjustId"], 'adjustId不统一'
    print('adjustId 测试完成')
    assert list_info[-1]["userId"] == list_info[-2]["userId"] ==list_info[-3]["userId"]==list_info[-4]["userId"],'userId不统一'
    print('userId 测试完成')

if __name__ == '__main__':
    check_order()