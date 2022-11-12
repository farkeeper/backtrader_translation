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


def findbases(cls, topclass):
    """查询cls类的topclass这一支的所有父类"""
    retval = list()  # 定义列表，用于存放父类名字。
    for base in cls.__bases__:
        print(base)
        if issubclass(base, topclass):
            retval.extend(findbases(base, topclass))
            retval.append(base)
    return retval


class M:
    pass


class X:
    pass


class Y(M):
    pass


class A(object):
    pass


class B(A):
    pass


class C(B):
    pass


class D(C, X):
    pass


class E(D, Y):
    pass


if __name__ == "__main__":
    print(findbases(E, M))
