#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/3 - 22:23
# 作者：farserver@163.com
# ====================================================


if __name__ == "__main__":
    class A(type):
        def __new__(cls, name, bases, attr):
            print("new")
            return type.__new__(cls, name, bases, attr)

        def __init__(self, name, bases, attr):
            print('init')
            self.data = 1234567890
            self.name = name

        def __call__(self):
            print("call")
            """call使类可以被调用"""
            self.name = '类改名了'
            return self


    class B(metaclass=A):
        pass

    class C(metaclass=A):
        pass


    b = B()
    print(b.name)
    c = C()
    print(c.name)

    print("类的继承关系", A.mro(A), A.__mro__)

    """元类 就是上帝之手，他创造一切，
    让你有手就有手，让你有爪子就有爪子。
    让你和他长得一个样，你俩就长得一个样。
    让A的数据B也能用，B就能用，所以，backtrader的cerebro有了data属性值，Stragegy能用这个data"""

    (A,B,C,D) = range(4)
    print(A,B,C,D)
