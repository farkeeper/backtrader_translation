#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/7 - 9:42
# 作者：farserver@163.com
# ====================================================

# https://zhuanlan.zhihu.com/p/51003123

# 迭代器：需要谁就才把谁放进内存，而不是一次性把所有的项都放进去
# python内置的迭代器工具
import itertools
# 迭代器分为 无限迭代器、有限迭代器、组合迭代器
# 无限迭代器 count circle repeat
# 有限迭代器 chain groupby accumulate
# 组合迭代器 product premutations

if __name__ == "__main__":
    # list是可迭代对象
    print(list.__iter__(0))
    print("查看对象的 所有 属性和方法", dir(itertools))
    for item in itertools.count(10, 2):
        if item > 100:
            break
        print(item)
