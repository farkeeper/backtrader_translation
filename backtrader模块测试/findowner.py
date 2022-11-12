#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/11/12 - 23:41
# 作者：farserver@163.com
# ====================================================
import itertools
import sys


def findowner(startlevel=0, skip=None):
    for framlevel in itertools.count(startlevel):
        try:
            frame = sys._getframe(framlevel)
        except:
            break
        print(frame)


def fun(a):
    findowner()


if __name__ == "__main__":
    fun(1)
