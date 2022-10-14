#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/14 - 21:06
# 作者：farserver@163.com
# ====================================================
class Meta(type):
    """元类
    类是元类创建的，元类必须显式继承type
    """

    def __new__(mcs, name, bases, attrs):
        """开辟一块内存空间，用来存储即将创建的（空对象）类
        （通过调用type<本类的元类>的new来完成，包含4个参数 调用者 类名 类的父类 类的属性和行为）
        返回值传递给__init__
        """
        _obj = type.__new__(mcs, name, bases, attrs)
        return _obj

    def __init__(cls, *bases, **attrs):
        """ 为刚才创建的空对象进行赋值 """
        print("空对象self包含的属性和行为", dir(cls))
        cls.attr = 987
        cls.newvar = 852
        setattr(cls, 'old', 444)    # 更改属性值或新增属性
        print("给 通过这个元类创建的类 添加属性name之后的属性和行为", dir(cls))


class A(metaclass=Meta):
    attr = 123

    def __init__(self):
        self.name = 1


if __name__ == "__main__":
    a = A()
    print(a.name, A.attr, A.newvar, A.old, A.a)
    # 元类给类增加了类变量 newattr
