#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/6 - 23:11
# 作者：farserver@163.com
# ====================================================

class T:
    def __init__(self):
        self.a = 'a'

    def get_b(self):
        self.b = self.a

    def get_d(self):
        """
        没有顺序要求，此时self.c还没定义
        """
        self.d = self.c

    def get_c(self):
        self.c = self.b


if __name__ == "__main__":
    pass
