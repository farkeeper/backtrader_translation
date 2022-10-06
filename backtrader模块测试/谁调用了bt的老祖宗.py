#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/6 - 21:25
# 作者：farserver@163.com
# ====================================================
import backtrader as bt


class Me(metaclass=bt.MetaParams):
    pass


if __name__ == "__main__":
    metaparams = Me()
    # 调用了两次老祖宗MetaBase

    # cerebro = bt.Cerebro()
    # 调用了两次老祖宗MetaBase



