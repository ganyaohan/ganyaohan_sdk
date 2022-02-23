class SDKupdate:
    def __init__(self, list):
        self.list = list
        self.channel = ['Fyber', 'Google', 'IronSource', 'Vungle', 'AdColony', 'InMobi', 'Nend', 'Mintegral', 'Verizon',
                        'Facebook', 'Maio', 'Unity', 'Smaato', 'ByteDance', 'AppLovin']  # 'Chartboost',
        self.version_list = [['0' for i in range(2)] for i in range(len(self.channel))]

    # 输入一个版本号返回，当前版本号所有渠道sdk和adapter的版本号
    def update(self, version):
        # 找到version
        index = 0
        while version not in self.list[index]:
            index += 1
        # 开始向后做SDK检索
        version_count = len(self.channel)
        txt_count = len(self.list)
        n = index  # index 打点
        count = -1  # 位数打点
        for i in self.channel:
            count += 1  # 起始为0
            while index < txt_count:
                # 判断该行的内容是不是寻找的渠道升级
                s = self.list[index]
                if ('>' in s) and ((i in s) or (i.lower() in s)):
                    if len(s.split('>')[1]) > 8:
                        str = s.split('>')[1][0:9]
                    else:
                        str = s.split('>')[1]
                    if 'Adapter' in s:
                        self.version_list[count][1] = str
                    else:  # if ('SDK' in s) or ('sdk' in s):
                        self.version_list[count][0] = str
                    if (self.version_list[count][0] != '0') and (self.version_list[count][1] != '0'):
                        index = n  # 回头找下一个渠道
                        break
                index += 1
            if index == txt_count:
                index = n
        # 清空applovin adapter的值
        self.version_list[-1][1] = '0'

        # 格式输出
        print('channel\t\t\t\tSDK\t\t\t\tadapter')
        for i in range(0, version_count):
            print('{channel}\t\t\t\t{sdk}\t\t\t\t{adap}'.format(channel=self.channel[i],
                                                                sdk=self.version_list[i][0].strip('\n'),
                                                                adap=self.version_list[i][1].strip('\n')))
        return

    # 输入一大一小两个版本号，返回两个版本之间的更新内容，左开右闭
    def between(self, small, big):

        # 确定大小版本号的行数
        big_index = 0
        while big not in self.list[big_index]:
            big_index += 1
        small_index = big_index
        while small not in self.list[small_index]:
            small_index += 1
        # 取两个版本之间的差别
        diff_list = []
        index = big_index
        while index < small_index:
            diff_list.append(self.list[index])
            index += 1
        # 删除版本号那一行
        i = 0
        while i < len(diff_list):
            s = diff_list[i]
            if ('[' in s) and (']' in s):
                s = diff_list.pop(i)
                i -= 1
            elif (len(s) <= 8) and (s.count('.')):
                s = diff_list.pop(i)
                i -= 1
            elif ('ZenSDK' in s) and (s.count('.')):
                s = diff_list.pop(i)
                i -= 1
            elif 'SDK Update' in s:
                s = diff_list.pop(i)
                i -= 1
            elif 'SDK 更新' in s:
                s = diff_list.pop(i)
                i -= 1
            elif len(s) <= 3:
                s = diff_list.pop(i)
                i -= 1
            i += 1

        # 去掉相同的渠道的更新内容
        # 先把更新的相关取出来
        update_list = []
        for i in range(big_index, small_index):
            if '>' in self.list[i]:
                update_list.append(self.list[i])

        # 进行android格式的判断
        ver_android = [0 for i in self.channel]
        for i in update_list:
            if ('com.applovin.mediation:' in i) and ('Updated' in i):
                for x in range(0, len(self.channel)):
                    if self.channel[x] in i:
                        if ver_android[x] != 0:
                            index = update_list.index(i)
                            s = update_list.pop(index)
                        else:
                            ver_android[x] = 1
        # 还可以做进一步升级取出两个版本之间的update version

        # 进行ios的格式判断
        update_list.sort()
        i = -1
        while i > -(len(update_list) - 1):
            if update_list[i].split(':')[0] == update_list[i - 1].split(':')[0]:
                s = update_list.pop(i)
                i += 1
            i -= 1

        # 最后输出去掉换行符
        for i in update_list:
            print(i.strip('\n'))

        for i in diff_list:
            if '>' in i:
                continue
            print(i.strip('\n'))


if __name__ == '__main__':
    isIos = input('是否是ios的log，输入是否是y/n')
    filename = ''
    if isIos == 'y':
        filename = "changelog_ios.txt"
    if isIos == 'n':
        filename = "changelog_android.txt"
    with open(filename, "r") as f:
        data = f.readlines()
        for line in data:
            line = line.strip('\n')
    a = SDKupdate(data)
    # version1 = input()
    # a.update(version1)
    version2 = input('请输入较小的版本号')
    version3 = input('请输入较大的版本号')
    a.between(version2, version3)
