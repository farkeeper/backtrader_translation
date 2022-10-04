#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/4 - 18:02
# 作者：farserver@163.com
# ====================================================
import datetime

if __name__ == "__main__":
    # 当前时间
    now = datetime.datetime.now()
    # 一天后的时间
    target = now + datetime.timedelta(days=1)
    print(now, target)

    # 3天前的时间
    target = now - datetime.timedelta(days=3)
    print(now, target)
