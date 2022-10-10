#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/10 - 16:59
# 作者：farserver@163.com
# ====================================================

def findbases(kls, topclass):
    """ 查询kls类的继承关系 家谱：祖宗、祖爷爷、爷爷、爸爸
        到topclass为止，规定了老祖宗
        ：kls有两个爸爸，爸爸各有爸爸，...，最终有两个祖宗，而函数只查询topclass这一支血脉
    """
    retval = list()
    for base in kls.__bases__:  # kls的直接父类（他爸爸），不包括爷爷、祖爷爷等
        # 如果kls他爸爸是是topclass的子类
        if issubclass(base, topclass):
            retval.extend(findbases(base, topclass))  # 末尾追加 元素
            retval.append(base)  # 末尾追加 整体

    return retval
    # kls.__bases__ 返回所有直接父类（他爸爸们）坑：虽然bases是复数，但只代表他可能有好几个爸爸，查询不到他爷爷
    # extend 追加元素，append追加整体，如append([1,2,3]), extend追加的是1,2,3而append追加的是[1,2,3]
    # 函数内定义变量 retval ，累加获取元素，此法可嘉。


import backtrader as bt

if __name__ == "__main__":
    print(findbases(bt.feeds.YahooFinanceCSVData, bt.DataSeries))

    """
    python允许继承多个父类，即“多继承”，子类必须 显式 初始化 每一个 父类。
    """


    class A:
        def __init__(self):
            self.a = 1


    class B:
        def __init__(self):
            self.b = 2


    class C(A, B):
        def __init__(self):
            A.__init__(self)
            B.__init__(self)


    class D(A, B):
        def __init__(self):
            super().__init__()


    c = C()
    print("正确的多继承", c.a, c.b)

    d = D()
    print("错误的多继承", d.a, d.b)
