#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：元类 负责创建类，自定义元类 可以 控制 类的创建过程
# 简介：
# 时间：2022/10/4 - 12:48
# 作者：farserver@163.com
# ====================================================

# 类的创建过程（注意 不是 类的实例化过程）
# 第一步：解析继承关系
# 第二步：确定元类
# 第三步：元类开始一步一步创建类:
#   __new__ 开辟空间
#   __init__ 初始化类的属性

class Meta(type):
    """自定义元类，由他负责创建类"""

    def __new__(cls, *args, **kwargs):
        print("new")
        """为将要创建的类开辟空间，返回值传给 __ini__函数 作为参数"""
        return type.__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        """为已经成功创建的空类，赋初始值"""
        self.data = 123


class MClass(metaclass=Meta):
    """自定义类 ，该类 由 自定义元类Meta负责创建
    如果不给出元类，自定义类 默认是由 type 负责创建的
    该类的创建过程：解析继承关系，确定元类，由元类创建这个类"""
    pass


# print(MClass, id(MClass))
# print(MClass.data)

# 类的实例化过程
# 调用类体内的__call__函数 进行实例化
# call函数会先调用new 再调用init
m = MClass()
print(m, m.data)

# 实例化 的 整体过程：
# 第一步：解析类的继承关系，确定该类的元类，由元类创建 该类
# 第二步：调用类内的call函数，初始化赋值，完成实例化

if __name__ == "__main__":
    pass
