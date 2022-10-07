#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/3 - 21:02
# 作者：farserver@163.com
# ====================================================

"""
未解决
"""

class Meta(type):
    """ 元类 必须显式继承 type"""
    def __new__(cls, name, bases, attr):
        """开辟内存空间
        必须有返回值，自动赋给 __init__
        所以，__init__参数必须与new一致"""
        # print("调用type的new函数创建一个meta类型的类", type(Meta).__new__(cls, name, bases, attr))
        return type(Meta).__new__(cls, name, bases, attr)

    def __init__(self, name, bases, attr):
        super().__init__(name, bases, attr)
        self.name = name
        self.bases = bases
        self.attr = attr
        self.data = None
        self.strategy = None

    def add_data(cls, data):
        cls.data = data

    def add_strategy(cls, strategy):
        cls.strategy = strategy
        print("策略添加成功", cls.strategy)

    def run(cls):
        cls.strategy.__init__(cls)

    def __call__(self):
        return self


class Cerebro(metaclass=Meta):
    """ 这是一个数据容器 """
    pass


class Strategy(metaclass=Meta):
    def __init__(self):
        print('Strategy初始化成功')
        print("strategy能使用data了")
        print(self.data)


if __name__ == "__main__":
    # list是类，为什么list()会有返回值呢？

    b = Cerebro()
    print("返回 类自己的名字", b)
    b.add_data(1234567890)
    print("添加数据", b.data)

    b.add_strategy(Strategy)

    b.run()
