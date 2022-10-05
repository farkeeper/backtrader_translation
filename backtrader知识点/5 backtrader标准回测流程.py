#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/4 - 21:20
# 作者：farserver@163.com
# ====================================================
import datetime
import os.path

from backtrader import OHLC

import backtrader as bt

if __name__ == "__main__":
    # 实例化引擎
    cerebro = bt.Cerebro()
    """
    # 第一步：解析Cerebro类的继承关系，确定元类
    print("赛萝卜的元类", type(bt.Cerebro))     # <class 'backtrader.metabase.MetaParams'>
    print("赛萝卜的所有父类", bt.Cerebro.__bases__)
    # 第二步：由元类MetaParams负责创建Cerebro类
    # 第三步：创建Cerebro类的一个实例cerebro
    # 在这过程中，backtrader都干了什么：
    # 好像没干什么具体的事
    """
    print("类的继承关系", bt.Cerebro.mro(), bt.Cerebro.__mro__)
    print("赛萝卜的元类", type(bt.Cerebro))
    print("赛萝卜的所有父类", bt.Cerebro.__bases__, bt.Cerebro.__class__)

    modpath = os.path.dirname(__file__)
    datapath = os.path.join(modpath, '../datas/yhoo-2003-2005.txt')
    # 加工数据饲料
    data = bt.feeds.YahooFinanceCSVData(dataname=datapath,
                                        fromdate=datetime.datetime(2005, 3, 24),
                                        todate=datetime.datetime(2005, 10, 23),
                                        )
    print(data, data.__dir__())
    # 打印出一个对象地址，可见不是简单的读取read_csv。他干了什么呢？
    # dataname是在哪里定义的，给出文件路径是如何读取文件内容的？
    # 这么复杂吗？作者是怎么掰扯清楚的？

    # # 加载数据
    # cerebro.adddata(data)
    # # 加载策略
    # cerebro.addstrategy(TestStrategy)
    # # 设置炒股资金
    # cerebro.broker.setcash(50000)
    # # 开始回测
    # cerebro.run()
    # # 绘图显示结果
    # cerebro.plot()
