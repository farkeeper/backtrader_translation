#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/10 - 17:52
# 作者：farserver@163.com
# ====================================================
import six


def findowner(owned, cls, startlevel=2, skip=None):
    """ 查找调用者 """
    # skip this frame and the caller's -> start at 2
    # 跳过本框框和直接调用者 - 从2级开始
    # 无限迭代器 从startlevel开始，步长为1，从无限迭代器里挨个取出
    for framelevel in itertools.count(startlevel):
        try:
            # 查看函数被什么函数调用以及被第几行调用及被调用函数所在文件
            frame = sys._getframe(framelevel)
        except ValueError:
            # Frame depth exceeded ... no owner ... break away
            break

        # 'self' in regular code    正常代码中的self
        self_ = frame.f_locals.get('self', None)
        if skip is not self_:
            if self_ is not owned and isinstance(self_, cls):
                return self_

        # '_obj' in metaclasses
        obj_ = frame.f_locals.get('_obj', None)
        if skip is not obj_:
            if obj_ is not owned and isinstance(obj_, cls):
                return obj_

    return None


import backtrader as bt
import itertools
import sys

if __name__ == "__main__":

    def findowner(owned, cls, startlevel=2, skip=None):
        """本函数被谁调用过
        owned:
        cls:
        startlevel:从第几级开始查
        skip:跳过谁
        """
        # skip this frame and the caller's -> start at 2
        # 跳过本框框和直接调用者 - 从2级开始
        # 无限迭代器 从startlevel开始，默认步长为1，从无限迭代器里挨个取出
        for framelevel in itertools.count(startlevel):
            # 查找本函数被谁调用过，跳过第一级（直接调用的函数），第2级、3、4、5....直至抛出异常
            try:
                frame = sys._getframe(framelevel)
                print("frame", frame)
            except ValueError:
                # 抛出异常时停止循环
                break

            # 'self' in regular code    代码中的self
            # self是 类 这个对象(有地址有名字有父类有属性有行为)，哪个类调用了，self就是谁，self是个指针，是个内存地址
            # 结合__new__方法理解：new创建一个类（这个类是空的，就是个内存地址，地址里有类名 父类 属性 三个空变量）
            self_ = frame.f_locals.get('self', None)
            if skip is not self_:  # 如果不跳过这一级
                # 如果调用者不是owned并且调用者是cls的实例
                if isinstance(self_, cls):
                    print(self_, "调用啦")
                    return self_

            # '_obj' in metaclasses ： 元类里面的obj
            obj_ = frame.f_locals.get('_obj', None)
            if skip is not obj_:
                if isinstance(obj_, cls):
                    return obj_

        return None


    """本元类创建的对象如果是cls的实例 则返回这个对象"""
    """本类"""


    class A:
        def __init__(self):
            self.name = 'A'


    a = A()
    x = a
    y = x


    class B(A):
        def __init__(self):
            self.name = a
            x = findowner(a, A)


    b = B()


    class C(B):
        def __init__(self):
            self.name = b
            x = findowner(b, B)


    c = C()


    class D(C):
        def __init__(self):
            self.name = 5
            b = B()
            c = C()


    d = D()
