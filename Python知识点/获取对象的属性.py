#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/11/27 - 9:53
# 作者：farserver@163.com
# ====================================================
import sys


def fun():
    frame = sys._getframe(0)
    print(frame.f_locals.get('age', None))
    print('yes')
    return


class A:
    age = 12

    def __init__(self):
        self.name = 'tom'
        fun()


if __name__ == "__main__":
    a = A()
