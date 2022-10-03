#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/3 - 21:02
# 作者：farserver@163.com
# ====================================================


class Meta(type):
    """ 这是一个元类 """

    def __new__(cls, name, bases, attr):
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

    def run(cls):
        cls.strategy()

    def __call__(self):
        # return self.name
        return self


class Cerebro(metaclass=Meta):
    """ 这是一个数据容器 """
    pass


class Strategy(metaclass=Meta):
    def __init__(self):
        # print(self.data)
        self.data = 0
        pass


if __name__ == "__main__":
    # list是类，为什么list()会有返回值呢？

    b = Cerebro()
    print("返回 类自己的名字", b)
    b.add_data(1234567890)
    print("添加数据", b.data)

    b.add_strategy(Strategy)
    b.strategy()

    b.run()
    print(b.data)
