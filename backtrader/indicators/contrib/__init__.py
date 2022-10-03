#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################

###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)



import backtrader as bt

# from . import vortex as vortex
from backtrader.indicators.contrib import vortex    # 上句为什么不行

for name in vortex.__all__:
    setattr(bt.indicators, name, getattr(vortex, name))

# vortex:涡流、漩涡

"""
setattr() 设置对象的属性值
对象即类的实例，类是类型，是抽象的，实例是实体。
如：
    动物 是 类，听得见，看不着
    狗 是 类，
    这只狗，是实例，是唯一的实体。
"""

if __name__ == "__main__":
    class A:
        def __init__(self, name):
            self.name = name

    a = A('Tom')
    print("实例a具备name属性，实例a的name值是:", a.name)

    # 设置属性值
    setattr(a, 'age', '18')     # 注意：age 是 字符串 类型
    print("实例啊设置一个新属性age，age的值是：", a.age)

    # 设置的属性值可以是原来类 没有 的属性
    # 也就是说 setattr()函数可以给类增加属性

    # getattr()获取属性值
    print("获取 a实例的name属性 的 值", getattr(a, 'name'))

    # 给实例a设置一个新属性say
    setattr(a, 'say', 'True')
    print("两种方式都可以获取属性值", getattr(a, 'say'), a.say)
