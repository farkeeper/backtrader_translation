#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/3 - 22:23
# 作者：farserver@163.com
# ====================================================
import six

if __name__ == "__main__":
    class A(type):
        def __new__(mcs, name, *bases, **attr):
            print("元类的new")
            obj = type.__new__(mcs, name, *bases, **attr)
            return obj

        def __init__(cls, name, *bases, **attr):
            print("元类的init的cls", cls)
            print('类调用元类的时候会把参数同时传递给new和init?')
            cls.name = 'NEW'
            cls.bases = 'FATHER'
            cls.attr = dict(a=123)

        def __call__(cls, *args, **kwargs):
            print("call的函数体")
            cls.att = '我是元类A的属性'
            return cls  # 这里应该返回什么


    class B(metaclass=A):
        def __init__(self):
            print("子类的init")
            self.att = '我是子类 B 的属性'


    class C(metaclass=A):
        def __init__(self):
            print("子类的init")
            self.name = '我是子类 C 的属性'


    class D(six.with_metaclass(A)):
        def __init__(self):
            print("子类的init")
            self.name = '我是子类 D 的属性'



    b = B()
    print(b, b.att)
    print("类的继承关系", A.mro(A), A.__mro__)

    """元类 就是上帝之手，他创造一切，
    让你有手就有手，让你有爪子就有爪子。
    让你和他长得一个样，你俩就长得一个样。
"""

    (A, B, C, D) = range(4)
    print(A, B, C, D)
