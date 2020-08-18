# -*- coding: utf-8 -*-
"""
Created on Sun Aug 16 10:41:08 2020

@author: fly
"""

import numpy as np
import pandas as pd
import time
import re
import datetime
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.font_manager import *  # 如果想在图上显示中文，需导入这个包
import xlwt
import wordcloud  # 词云
import imageio
import jieba  # 中文分词


class WechatAnalysis:
    def __init__(self, data_frame, name):
        self.data_frame = data_frame
        self.wechat_name = name
        self.chat_time, self.chat_content = self.get_time_and_content()
        self.font_path = r'C:\Windows\Fonts\MSYH.TTC'  # 微软雅黑

    def get_time_and_content(self):
        # 把聊天内容和时间取出
        chat = self.data_frame
        chat_time = []
        chat_content = []
        for i in range(len(chat) - 1):
            content = chat[i:i + 1]
            if content['talker'].values[0] == self.wechat_name:
                t = content['createTime'].values[0] // 1000  # 除以1000用以剔除后三位0
                c = content['content'].values[0]
                chat_time.append(t)
                chat_content.append(c)
        return chat_time, chat_content

    def get_time_hist(self, time_flag=0):
        """
        :param time_flag: 0 hour, 1 year day, 2 month
        :return:
        """
        # 画小时核密度分布图
        str_list = ['小时', '天', '月']
        data_list = [self.to_struct_time(t)[time_flag] for t in self.chat_time]  # 得到数据列表
        max_indx = np.argmax(np.bincount(data_list))  # 出现次数最多的数据
        max_num = np.bincount(data_list)[max_indx]  # 出现次数
        print('\n.......................\n开始画图\n.......................')
        myfont = FontProperties(fname=r'C:\Windows\Fonts\MSYH.TTC', size=22)  # 标题字体样式
        myfont2 = FontProperties(fname=r'C:\Windows\Fonts\MSYH.TTC', size=18)  # 横纵坐标字体样式
        myfont3 = FontProperties(fname=r'C:\Windows\Fonts\FZSTK.TTF', size=18)  # 标注字体
        sns.set_style('darkgrid')  # 设置图片为深色背景且有网格线
        if time_flag == 0:
            sns.distplot(data_list, 24, color='lightcoral')
            plt.xticks(np.arange(0, 25, 1.0), fontsize=15)
            plt.ylabel('聊天概率', fontproperties=myfont2)
        elif time_flag == 1:
            sns.distplot(data_list, 365, kde=False, color='lightcoral')
            plt.xticks(np.arange(1, 366, 30), fontsize=15)
            plt.ylabel('消息条数', fontproperties=myfont2)
            plt.annotate("这%s我们发了%d条消息！" % (str_list[time_flag], max_num),
                         xy=(max_indx,max_num), fontproperties=myfont3)
        elif time_flag == 2:
            sns.distplot(data_list, 12, kde=False, color='lightcoral')
            plt.xticks(np.arange(0, 12, 1.0), fontsize=15)
            plt.ylabel('消息条数', fontproperties=myfont2)
            plt.annotate("这%s我们发了%d条消息！" % (str_list[time_flag], max_num),
                         xy=(max_indx, max_num), fontproperties=myfont3)

        plt.yticks(fontsize=15)
        plt.title('聊天时间分布', fontproperties=myfont)
        plt.xlabel('时间段/' + str_list[time_flag], fontproperties=myfont2)

        fig = plt.gcf()
        fig.set_size_inches(15, 8)
        fig.savefig('chat_time.png', dpi=100)
        plt.show()
        print('\n.......................\n画图结束\n.......................')

    def get_hour_slice(self):
        hour_set = [self.to_struct_time(t)[0] for t in self.chat_time]
        print('\n.......................\n开始聊天时段统计\n.......................')
        time_slice = [0, 0, 0, 0, 0, 0]
        deep_night = []
        for i in range(len(hour_set)):
            if 0 <= hour_set[i] < 6:
                time_slice[0] += 1
                deep_night.append([self.chat_time[i], self.chat_content[i]])
            elif 6 <= hour_set[i] < 10:
                time_slice[1] += 1
            elif 10 <= hour_set[i] < 14:
                time_slice[2] += 1
            elif 14 <= hour_set[i] < 18:
                time_slice[3] += 1
            elif 18 <= hour_set[i] < 22:
                time_slice[4] += 1
            else:
                time_slice[5] += 1
        labels = ['凌晨0点至6点', '6点至10点', '10点至14点',
                  '14点至18点', '18点至22点', '22点至次日凌晨0点']
        time_distribution = {
            labels[0]: time_slice[0],
            labels[1]: time_slice[1],
            labels[2]: time_slice[2],
            labels[3]: time_slice[3],
            labels[4]: time_slice[4],
            labels[5]: time_slice[5]
        }
        for label in labels:
            print("{ name: '%s': %d}, \n" % (label, time_distribution[label]))

        ''' 深夜聊天记录 '''
        wbk = xlwt.Workbook()
        sheet = wbk.add_sheet('late')
        for i in range(len(deep_night)):
            sheet.write(i, 0, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(deep_night[i][0])))
            sheet.write(i, 1, deep_night[i][1])
        wbk.save('聊得很晚.xls')
        print('\n.......................\n聊天时段统计结束\n.......................')

    def get_word_cloud(self, chinese_slice=False, stopwords=None, image_out_name=None):
        """
        :param chinese_slice:  Whether Use jieba to slice the sentences.
        :param stopwords: a set include some words to exclude.
        :return:
        """
        font_path = self.font_path
        if image_out_name is None:
            image_out_name = 'word-heart.png'
        if chinese_slice:
            text = ",".join(self.chat_content)
            text_list = jieba.lcut(text)
            text = " ".join(text_list)
            image_out_name = 'zh-'.__add__(image_out_name)
        else:
            text = " ".join(self.chat_content)
        mk = imageio.imread("heart.png")

        # 构建并配置词云对象w，注意要加scale参数，提高清晰度
        w = wordcloud.WordCloud(width=1000,
                                height=700,
                                background_color='white',
                                font_path=font_path,
                                mask=mk,
                                scale=2,
                                stopwords=stopwords,
                                contour_width=1,
                                contour_color='red')
        # 将string变量传入w的generate()方法，给词云输入文字
        w.generate(text)
        # 展示图片
        # 根据原始背景图片的色调进行上色
        image_colors = wordcloud.ImageColorGenerator(mk)
        plt.imshow(w.recolor(color_func=image_colors))
        # 根据原始黑白色调进行上色
        # plt.imshow(wc.recolor(color_func=grey_color_func, random_state=3), interpolation='bilinear') #生成黑白词云图
        # 根据函数原始设置进行上色
        # plt.imshow(wc)

        # 隐藏图像坐标轴
        plt.axis("off")
        plt.show()

        # 将词云图片导出到当前文件夹
        w.to_file(image_out_name)

    def get_word_statistic(self):
        ''' 字符统计 '''
        chat_content = self.chat_content
        chat_time = self.chat_time

        print('\n..........\n开始字符统计\n............\n')
        start = datetime.datetime.now()
        pattern_love = '.*?(爱).*?'
        pattern_morning = '.*?(早).*?'
        pattern_night = '.*?(晚安).*?'
        pattern_miss = '.*?(想你).*?'
        pattern_set = [pattern_love, pattern_morning, pattern_night,
                       pattern_miss, '.*?(在干嘛).*?', '.*?(嘻嘻).*?']
        statistic = list(np.zeros(len(pattern_set), dtype=np.int))
        for i in range(len(chat_content)):
            for j in range(len(pattern_set)):
                length = len(re.findall(pattern_set[j], str(chat_content[i])))
                statistic[j] += length

        print("在%d个日日夜夜里" % ((max(chat_time) - min(chat_time)) // (3600*24)))
        for i, pattern in enumerate(pattern_set):
            print("我们说了%d次 %s" % (statistic[i], pattern.strip('.*?()')))

        end = datetime.datetime.now()
        print('\n..........\n字符统计结束,用时: {}\n............\n'.format(end - start))


    @staticmethod
    def to_struct_time(t):
        struct_time = time.localtime(t)  # 将时间戳转换为struct_time元组
        hour = round((struct_time[3] + struct_time[4] / 60), 2)
        month = struct_time.tm_mon
        yday = struct_time.tm_yday
        return hour, yday, month


if __name__ == '__main__':
    myGirl = '微信UID !!!'
    csv_path = '你导出的csv文件'

    chat = pd.read_csv(csv_path, sep=',', encoding='utf-8', usecols=[6,7,8])
    # createTime  talker    content‘ dtype: float, string,string

    Wechat = WechatAnalysis(chat, myGirl)
    # Get the hour distribution
    Wechat.get_time_hist()
    Wechat.get_hour_slice()

    # Get word cloud
    plt.figure(2)
    Wechat.get_word_cloud()  # Not slice the chinese words
    plt.figure(3)
    Wechat.get_word_cloud(stopwords={'嘻嘻', '嗯嗯', '嗯呢', '这样子', '这样子呀', '捂脸'})
    Wechat.get_word_statistic()

