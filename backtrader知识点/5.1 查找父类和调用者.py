#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/10 - 16:59
# 作者：farserver@163.com
# ====================================================

def findbases_(kls, topclass):
    lst = list()
    for base in kls.__bases__:
        print("父类之---", base)
        if issubclass(base, topclass):
            print("—— %s 的父类 %s 是 %s 的子类" % (kls, base, topclass))
            lst.append(base)
        else:
            print("mmmmmmmmmmmm", base)
    return lst

def findbases(kls, topclass):
    """ kls的所有父类中,谁是topclass的子类 """
    retval = list()
    for base in kls.__bases__:      # 所有父类
        if issubclass(base, topclass):  # 如果base是topclass的子类
            # print("%s 的父类 %s 是 %s 的子类" % (kls, base, topclass))
            retval.extend(findbases(base, topclass))  # 末尾追加 元素
            retval.append(base)  # 末尾追加 整体

    return retval

import backtrader as bt

if __name__ == "__main__":
    print(findbases_(bt.feeds.YahooFinanceCSVData, bt.DataSeries))
    print(findbases(bt.feeds.YahooFinanceCSVData, bt.DataSeries))
