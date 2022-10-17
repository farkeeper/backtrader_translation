#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/17 - 23:20
# 作者：farserver@163.com
# ====================================================

class Meta(type):
    pass


class Bases(metaclass=Meta):
    pass


class Sub(Bases):
    pass


if __name__ == "__main__":
    instance = Sub()

    print("class返回类型，类的类型是元类，实体的类型是类", Sub.__class__, instance.__class__)
    print("type返回类型，类的类型是元类，实体的类型是类", type(Sub), type(instance))
    print("bases返回基类，类的基类是爸爸类，实体是实例所以无法论基类", Sub.__bases__)

    # class 类型 ， type 类型， bases 基类(实体对象没有基类，只有类有基类)
