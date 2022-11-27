#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/11/27 - 10:12
# 作者：farserver@163.com
# ====================================================

class A():
    code = 1

    def __init__(self):
        self.age = 18

    def fun(self):
        return 2


if __name__ == "__main__":
    a = A()
    print(a.__dict__)
    print(dir(a))
    print(a.__class__)
