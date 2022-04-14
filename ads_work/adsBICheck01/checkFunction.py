import varGet
import biConfig
import json
import re

import collections
import random

from enum import Enum

import mitmproxy
from mitmproxy import ctx
from mitmproxy.exceptions import TlsProtocolException
from mitmproxy.proxy.protocol import TlsLayer, RawTCPLayer


smallGreen = (0.8509804, 0.91764706, 0.827451, 0)


class check:
    def __init__(self, body, name, varType):
        self.body = body
        self.name = name
        self.type = varType

    @staticmethod
    def compare_version(version1, version2):
        """
        判断v1和v2的大小，v1大返回1，v2大返回-1，相等返回0
        """
        a = version1.split('.')
        b = version2.split('.')
        c = 0
        while True:
            if c == len(a) and c == len(b):
                return 0
            if len(a) == c:
                a.append(0)
            if len(b) == c:
                b.append(0)
            if int(a[c]) > int(b[c]):
                return 1
            elif int(a[c]) < int(b[c]):
                return -1
            c = c + 1

    def isMeetConditions(self, platform, version):
        """
        param platform：期望的平台
        param version：期望的sdk版本
        return  是否满足条件
        """
        if self.body["platform"] == platform:
            # version =0, 只判断平台
            if 0 != version:
                if 1 != check.compare_version(self.body["zensdkVersion"], version):
                    return False
            else:
                return True
        return False

    def isExist(self):
        """
        return 1：存在；0：不存在；-1：不需要存在
        """
        # 调用isMeetConditions 查看是否满足存在条件
        if self.name in biConfig.varCon:
            con = biConfig.varCon[self.name]
            if isinstance(con, list):
                platform = self.body["platform"]
                if platform == "android":
                    con = con[1]
                elif platform == "ios":
                    con = con[0]
            f = self.isMeetConditions(con["platform"], con["version"])
            if not f:
                # 不满足存在条件，变量不需要存在
                return -1
        # 满足存在条件，按照'.'拆分name
        nameFlag = False
        if '.' in self.name:
            nameFlag = True
            nameList = self.name.split('.')
        if nameFlag:
            # 含有.的情况
            for x in range(0, len(nameList)):
                if nameList[x] not in self.body:
                    return 0
                self.body = self.body[nameList[x]]
            if self.body == '':
                return 0
            return 1
        else:
            # 不含有.的情况
            if self.name in self.body["parameters"]:
                return 1
            return 0

    def isType(self):
        ac_type = type(self.body["parameters"][self.name])
        obj = re.search(r'int|float|str|bool|time|json', str(ac_type))
        if obj:
            return True
        return False


class checkBi(check):
    def __init__(self, url):
        self.url = url
        self.body = None
        self.event = None

    def request(self, flow):
        if flow.request.url == self.url:
            body = json.loads(flow.request.get_text())
            self.event = body["eventName"]
            self.body = body
            self.checkIn()

    # 浅绿色color(0.8509804, 0.91764706, 0.827451, 0)
    def callSheetVar(self):
        """
        return varNameList： 变量名列表
                varTypeList： 变量类型列表
        """
        sh = biConfig.gc.open('SDK常规测试')[3]
        varNameList = []
        varTypeList = []
        # 事件名循环
        for x in range(68, 91):
            c1 = sh.cell(chr(x) + "1")
            if self.event == c1.value:
                for y in range(4, 66):
                    c2 = sh.cell(chr(x) + str(y))
                    if c2.color == smallGreen:
                        cName = sh.cell("A" + str(y)).value
                        cName = cName.replace(' ', '')
                        varNameList.append(cName)
                        cType = sh.cell("B" + str(y)).value
                        cType = cType.replace(' ', '')
                        cType = cType.split(",eg")[0].lower()
                        varTypeList.append(cType)
                break
        print(varNameList, varTypeList)
        return varNameList, varTypeList

    def checkIn(self):
        nameList, typeList = self.callSheetVar()
        if len(nameList) != len(typeList):
            print("错误：变量名和变量类型长度不一致")
            return
        for x in range(0, len(nameList)):
            b = check(self.body, nameList[x], typeList[x])
            if b.isExist() == 1:
                if b.isType():
                    print(nameList[x] + "存在，并且类型没有问题")
                else:
                    errorType = type(self.body["parameters"][nameList[x]])
                    print(self.event + nameList[x] + "类型错误", "应该为" + typeList[x], "实际为" + str(errorType))
            elif b.isExist() == 0:
                print(self.event + "     " + nameList[x] + "不存在")
            elif b.isExist() == -1:
                pass


addons = [
    checkBi(biConfig.ads_url)
]

class InterceptionResult(Enum):
    success = True
    failure = False
    skipped = None


class _TlsStrategy:
    """
    Abstract base class for interception strategies.
    """

    def __init__(self):
        # A server_address -> interception results mapping
        self.history = collections.defaultdict(lambda: collections.deque(maxlen=500))

    def should_intercept(self, server_address):
        """
        Returns:
            True, if we should attempt to intercept the connection.
            False, if we want to employ pass-through instead.
        """
        raise NotImplementedError()

    def record_success(self, server_address):
        self.history[server_address].append(InterceptionResult.success)

    def record_failure(self, server_address):
        self.history[server_address].append(InterceptionResult.failure)

    def record_skipped(self, server_address):
        self.history[server_address].append(InterceptionResult.skipped)


class ConservativeStrategy(_TlsStrategy):
    """
    Conservative Interception Strategy - only intercept if there haven't been any failed attempts
    in the history.
    """

    def should_intercept(self, server_address):
        if InterceptionResult.failure in self.history[server_address]:
            return False
        return True


class ProbabilisticStrategy(_TlsStrategy):
    """
    Fixed probability that we intercept a given connection.
    """

    def __init__(self, p):
        self.p = p
        super(ProbabilisticStrategy, self).__init__()

    def should_intercept(self, server_address):
        return random.uniform(0, 1) < self.p


class _TlsStrategy:
    """
    Abstract base class for interception strategies.
    """

    def __init__(self):
        # A server_address -> interception results mapping
        self.history = collections.defaultdict(lambda: collections.deque(maxlen=500))

    def should_intercept(self, server_address):
        """
        Returns:
            True, if we should attempt to intercept the connection.
            False, if we want to employ pass-through instead.
        """
        raise NotImplementedError()

    def record_success(self, server_address):
        self.history[server_address].append(InterceptionResult.success)

    def record_failure(self, server_address):
        self.history[server_address].append(InterceptionResult.failure)

    def record_skipped(self, server_address):
        self.history[server_address].append(InterceptionResult.skipped)


class ConservativeStrategy(_TlsStrategy):
    """
    Conservative Interception Strategy - only intercept if there haven't been any failed attempts
    in the history.
    """

    def should_intercept(self, server_address):
        if InterceptionResult.failure in self.history[server_address]:
            return False
        return True


class ProbabilisticStrategy(_TlsStrategy):
    """
    Fixed probability that we intercept a given connection.
    """

    def __init__(self, p):
        self.p = p
        super(ProbabilisticStrategy, self).__init__()

    def should_intercept(self, server_address):
        return random.uniform(0, 1) < self.p


class TlsFeedback(TlsLayer):
    """
    Monkey-patch _establish_tls_with_client to get feedback if TLS could be established
    successfully on the client connection (which may fail due to cert pinning).
    """

    def _establish_tls_with_client(self):
        server_address = self.server_conn.address

        try:
            super(TlsFeedback, self)._establish_tls_with_client()
        except TlsProtocolException as e:
            tls_strategy.record_failure(server_address)
            raise e
        else:
            tls_strategy.record_success(server_address)


# inline script hooks below.

tls_strategy = None


def load(l):
    l.add_option(
        "tlsstrat", int, 0, "TLS passthrough strategy (0-100)",
    )


def configure(updated):
    global tls_strategy
    if ctx.options.tlsstrat > 0:
        tls_strategy = ProbabilisticStrategy(float(ctx.options.tlsstrat) / 100.0)
    else:
        tls_strategy = ConservativeStrategy()


def next_layer(next_layer):
    """
    This hook does the actual magic - if the next layer is planned to be a TLS layer,
    we check if we want to enter pass-through mode instead.
    """
    if isinstance(next_layer, TlsLayer) and next_layer._client_tls:
        server_address = next_layer.server_conn.address

        if tls_strategy.should_intercept(server_address):
            # We try to intercept.
            # Monkey-Patch the layer to get feedback from the TLSLayer if interception worked.
            next_layer.__class__ = TlsFeedback
        else:
            # We don't intercept - reply with a pass-through layer and add a "skipped" entry.
            mitmproxy.ctx.log("TLS passthrough for %s" % repr(next_layer.server_conn.address), "info")
            next_layer_replacement = RawTCPLayer(next_layer.ctx, ignore=True)
            next_layer.reply.send(next_layer_replacement)
            tls_strategy.record_skipped(server_address)