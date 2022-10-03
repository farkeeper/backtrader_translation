#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/3 - 20:33
# 作者：farserver@163.com
# ====================================================
import collections


# collections.Counter
# 统计出现的次数。  split()分割字符串
# print(collections.Counter("hello hello world hello nihao".split()))
def findbases(kls, topclass):
    """ 查找kls的所有父类 到topclass为止 """
    retval = list()
    for base in kls.__bases__:
        if issubclass(base, topclass):      # 如果base是topclass的子类
            retval.extend(findbases(base, topclass))        # 末尾追加 元素
            retval.append(base)  # 末尾追加 整体

    return retval

if __name__ == "__main__":
    class A:
        pass


    class B(A):
        pass


    class C(B):
        pass


    class D(C):
        pass


    # print(findbases(D, B))


    class A(type):
        def __call__(self):
            """call会截断new和init？会先于new和init运行？不会吧"""
            return 123

    class B(metaclass=A):
        pass

    b = B()
    print(b)
