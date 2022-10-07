#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/7 - 11:39
# 作者：farserver@163.com
# ====================================================
import itertools
import sys

if __name__ == "__main__":
    print("sys包的所有属性和方法", dir(sys))
    print("sys._getframe 的所有属性和方法", dir(sys._getframe))

    for i in itertools.count(1, 1):
        try:
            frame = sys._getframe(i)
        except ValueError:
            break

        self_ = frame.f_locals.get('self', None)
        print(self_)
        if skip is not self_:
            if self_ is not owned and isinstance(self_, cls):
                return self_

        # '_obj' in metaclasses
        obj_ = frame.f_locals.get('_obj', None)
        if skip is not obj_:
            if obj_ is not owned and isinstance(obj_, cls):
                return obj_
