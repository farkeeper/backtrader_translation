#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/4 - 19:29
# 作者：farserver@163.com
# ====================================================
class A:
    def __init__(self):
        self.name = 'Tom'
        self.age = 18
        self.gun = 'AK47'

if __name__ == "__main__":
    a = A()
    print("对象（类实例）是否拥有name属性", hasattr(a, 'name'))

    # 给对象设置属性值，给对象增加属性并赋值
    setattr(a, 'name', 'JACK')
    
    print("获取对象的属性值", getattr(a, 'name'))
    print("获取对象的属性值，如果没有则返回None", getattr(a, 'language', 'None'))


