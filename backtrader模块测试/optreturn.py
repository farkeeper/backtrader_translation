#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/7 - 15:35
# 作者：farserver@163.com
# ====================================================

class OptReturn(object):
    def __init__(self, params, **kwargs):  # 位置参数 关键字参数
        self.p = self.params = params
        for k, v in kwargs.items():  # 遍历字典 关键字参数以字典类型传递
            setattr(self, k, v)  # 为self设置属性值（属性可以是新增）


if __name__ == "__main__":
    params = ('name', 'Tom')
    optr = OptReturn(params)
    print(optr, dir(optr))
    print(optr.params)

