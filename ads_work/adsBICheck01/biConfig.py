import pygsheets

ads_url = "https://ads-bi-beta.zenkube.com/ads"

gc = pygsheets.authorize(
    service_file='/Users/yaohan.gan/PycharmProjects/MITM/adsBICheck/yaohan-329808-1038d761d603.json')

test_body = {
    "ts": "2022-04-13 16:06:39",
    "eventName": "banner_revenue_paid",
    "abtestVersion": 1,
    "adgroupId": 2,
    "adjustId": "602eeb2e6119b9c0a6454a3ba4113cad",
    "advertisingId": "ad4290ac-90ca-4b08-ad8c-c0e40ad4a243",
    "country": "FR",
    "deviceModel": "amber",
    "isProduction": True,
    "language": "fr",
    "packageName": "com.wordgame.wordconnect.fr",
    "parameters": {
        "adType": "banner",
        "adunit": "3f8e58b1c3d1084f",
        "dailyRevenueBefore": 0.0800309042195435,
        "ecpm": 0,
        "isBidding": False,
        "isSmartSeg": False,
        "partner": "applovinMax",
        "revenue": 0.005,
        "showTime": 1649836928156,
        "slot": "default",
        "uuid": "8f911f66-4b98-480f-ba4d-d649c9986aff",
        "currentRevenue": 0.001
    },
    "platform": "android",
    "platformVersion": "30",
    "versionCode": "99",
    "versionName": "5.412.239",
    "zensdkVersion": "3.17.23",
    "geoCountry": "FR",
    "ip": "93.23.106.164",
    "androidId": "a977c9f752f9bebd",
    "brand": "Xiaomi",
    "manufacturer": "Xiaomi",
    "model": "21081111RG",
    "timestamp": "2022-04-13T08:06:38.789Z",
    "userId": "s1NM1MMnc",
    "isLimitAdTracking": False,
    "timeIntervalSince1970": 1649837198789
}

varCon = {
    "mediationInfo.provider": {
        "platform": "ios",
        "version": "0"
    },
    "mediationInfo.networkName": {
        "platform": "ios",
        "version": "0"
    },
    "mediationInfo.adUnitId": {
        "platform": "ios",
        "version": "0"
    },
    "mediationInfo.creativeId": {
        "platform": "ios",
        "version": "0"
    },
    "mediationInfo.revenue": {
        "platform": "ios",
        "version": "0"
    },
    "dailyRevenueMap": [
        {
            "platform": "ios",
            "version": "4.8.3",
        },
        {
            "platform": "android",
            "version": "5.4.0",
        }]
}
