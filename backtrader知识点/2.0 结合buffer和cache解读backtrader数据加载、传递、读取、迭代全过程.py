#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：结合buffer和cache解读backtrader数据加载、传递、读取、迭代全过程
# 简介：
# 时间：2022/10/5 - 18:20
# 作者：farserver@163.com
# ====================================================


































"""
bt 的数据加载过程
类 YahooFinanceCSVData 继承自 feed.CSVDataBase
在feed.CSVDataBase里：
    打开文件，定义分隔符，跳过第一行的标题（列名），删除末尾的回车符
在 YahooFinanceCSVData 里实现了_loadline方法：
    按行读取

"""
# python io模块详解
# https://docs.python.org/zh-cn/3/library/io.html
import datetime
import io
import os

"""
class io.StringIO(initial_value='', newline='\n')
一个使用内存文本缓冲的文本流。
如果 newline 为 None，则在所有平台上换行符都会被写入为 \n
当 close() 方法被调用时将会丢弃文本缓冲区
"""

# 流
# https://blog.csdn.net/ryuenkyo/article/details/81198093
"""
数据流是一串连续不断的数据的集合，就象水管里的水流，在水管的一端一点一点地供水，而在水管的另一端看到的是一股连续不断的水流。
数据写入程序可以是一段、一段地向数据流管道中写入数据，这些数据段会按先后顺序形成一个长的数据流。
对数据读取程序来说，看不到数据流在写入时的分段情况，每次可以读取其中的任意长度的数据，但只能先读取前面的数据后，再读取后面的数据。
不管写入时是将数据分多次写入，还是作为一个整体一次写入，读取时的效果都是完全一样的。
"""

import backtrader as bt
# Create a Stratey
class TestStrategy(bt.Strategy):
    print("TESTSTRAEGY")

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

    def next(self):
        print("TestStratgy-next")
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        if self.dataclose[0] < self.dataclose[-1]:
            # current close less than previous close

            if self.dataclose[-1] < self.dataclose[-2]:
                # previous close less than the previous close

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.buy()

if __name__ == "__main__":
    modpath = os.path.dirname(__file__)
    data_path = os.path.join(modpath, '../datas/yhoo-2014.txt')

    cerebro = bt.Cerebro()
    data = bt.feeds.YahooFinanceCSVData(
        dataname=data_path,
        fromdate=datetime.datetime(2014, 1, 1),
        todate=datetime.datetime(2014, 12, 1)
    )
    print("到此为止，还没有逐行取出数据")
    cerebro.adddata(data)
    cerebro.addstrategy(TestStrategy)   # 只是创建了策略类还没有实例化
    cerebro.broker.setcash(100000.0)
    # run是怎么驱动strategy的？
    cerebro.run()
    # 调用了类，类方法里面的print语句打印不出来，什么原因？
