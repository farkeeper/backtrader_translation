#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/7 - 9:34
# 作者：farserver@163.com
# ====================================================
import itertools
import sys

def fun(startlevel):
    for framelevel in itertools.count(startlevel):
        try:
            # 查看函数被什么函数调用以及被第几行调用及被调用函数所在文件
            frame = sys._getframe(framelevel)
            print(frame)
        except ValueError:
            # Frame depth exceeded ... no owner ... break away
            break

if __name__ == "__main__":
    fun(100)

    print(sys._getframe().f_locals.get('__name__') == '__main__')

