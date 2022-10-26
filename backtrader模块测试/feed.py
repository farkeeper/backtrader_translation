#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/19 - 20:58
# 作者：farserver@163.com
# ====================================================
import os.path

import backtrader as bt

if __name__ == "__main__":
    modpath = os.path.dirname(__file__)
    datapath = os.path.join(modpath, "../datas/600848.his")
    data = bt.feeds.YahooFinanceCSVData(dataname=datapath,
                                        fromdate='2020-02-02',
                                        todate='2021-02-02',
                                        )
    print(data)
