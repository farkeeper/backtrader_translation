#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：元类 负责创建类，自定义元类 可以 控制 类的创建过程
# 简介：
# 时间：2022/10/4 - 12:48
# 作者：farserver@163.com
# ====================================================
# 类名后面的()可以理解成 调用运算
# 任何类里面都有一个隐藏的__new__函数，负责分配一个内存地址
"""
类的创建过程：
class B(object, metaclass=A)执行流程：
    1、有()先执行()内的运算（四则运算也是如此），即 ‘object, metaclass=A’ 这行代码，A也可以是函数（包含name，bases，attrs）
        解析继承关系（默认继承objcet），继承父类的属性和方法。
        确定元类，由元类创建类对象。
            内置函数执行顺序：
            __new__     开辟内存空间（内存地址），创建一个实例（类是元类的具体对象（实例））对象，传递给init作为第一个参数
            __init__    初始化函数。
    2、类（这个对象）已创建完成。

类的创建到实例化全过程：
    1、执行()调用动作：
        元类有call函数，他的实例类才可以被调用
    2、运行()内的代码
        解析继承关系，继承父类的属性方法。
        确定元类，由元类生成类。
            执行元类的 __new__ 创建空对象实例
            执行元类的 __init__ 初始化类对象
        类已创建，并完成初始化。
    3、执行类体内的 __new__ 创建实例对象（python已内置，不要以为没有）
        __init__ 构造函数进行初始化
注意区分 类的创建 和 类的实例化， 区分类对象和实例对象， 区分类属性和实例属性
"""


class Meta(type):
    """自定义元类必须显式继承type
    """

    def __new__(mcs, name, bases, attrs):
        """ 创建一个空对象
            为将要创建的类（对象 _cls）开辟空间(调用type的new函数来完成)，将这个内存地址传递给init作为第一个参数"""
        _cls = type.__new__(mcs, name, bases, attrs)
        return _cls

    def __init__(cls, name, bases, attrs):
        """初始化函数 给刚刚创建的空对象的属性行为等赋值"""
        # 让类名大写
        cls.__name__ = cls.__name__.upper()
        # 元类是控制类的，所以能够控制类属性这一级别
        # 但控制不到实例属性这一级别
        cls.cattr = 987

    def __call__(self, *args, **kwargs):
        print("元类内的call")
        return type.__call__(self, *args, **kwargs)


class MClass(metaclass=Meta):
    """自定义类 ，该类 由 自定义元类Meta负责创建
    如果不给出元类，自定义类 默认是由 type 负责创建的
    该类的创建过程：解析继承关系，确定元类，调用元类的函数创建这个类
    先调用new后调用init"""
    cattr = '123'

    def __init__(self):
        print("自定义类的初始化")
        self.data = 123


print("以下是正文")
m = MClass()
print("类内也有new函数（python内置了），不要以为没有", dir(MClass))
print("打印出一个内存地址（指针）:对象")
print(m)
# python一切皆对象，一切皆指针，一切皆内存地址，常量、变量、函数、类、元类、就连所有代码也是个对象
# 只要是对象就一定包括：属性和行为
# 对象就是个内存地址
print(MClass.__name__)
print(MClass.cattr)
