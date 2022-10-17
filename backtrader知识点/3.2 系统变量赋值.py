#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/15 - 22:04
# 作者：farserver@163.com
# ====================================================
from six import with_metaclass


class Meta(type):
    """元类控制类的生成过程"""

    def __new__(mcs, *args, **kwargs):
        """开辟空间，创建空对象"""
        return type.__new__(mcs, *args, **kwargs)

    def __init__(cls, *args, **kwargs):
        cls.__name__ = "B"  # 子类更名为 B
        cls.data = 12345  # 子类添加data属性 data是类变量，不是实例属性
        for dct in kwargs:
            print(dct)


class A(metaclass=Meta):
    pass


class C(A):
    def __init__(self):
        self.data = 5


class D(object, metaclass=Meta):
    """基类object，元类Meta"""
    pass


if __name__ == "__main__":
    print(A.__name__)
    print(A.data)

    c = C()
    print(C.__name__)
    print(C.data, c.data)
