#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/4 - 21:20
# 作者：farserver@163.com
# ====================================================
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

    """

    # # 加工数据饲料
    # data = bt.feeds.YahooFinanceCSVData(dataname=,
    #                                     fromdate=,
    #                                     todate=,
    #                                     )
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
