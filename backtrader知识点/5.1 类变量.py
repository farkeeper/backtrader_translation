#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/4 - 21:57
# 作者：farserver@163.com
# ====================================================

class Cerebro:
    params = (
        ('name', 'True'),
        ('open', 'True'),
        ('plot', '3')
    )


class SubCerebro(Cerebro):
    pass


if __name__ == "__main__":
    cerebro = Cerebro()
    print("所有的类属性和行为", cerebro.__dir__())

    sub = SubCerebro()
    print(sub.params)
