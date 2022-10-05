#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：backtrader内存缓冲区数据加载过程
# 简介：我是潘哥
# 时间：2022/10/5 - 17:32
# 作者：farserver@163.com
# ====================================================

import collections
import io
import os
import time

import pandas as pd

if __name__ == "__main__":
    # 数据文件路径
    modpath = os.path.dirname(__file__)
    data_path = os.path.join(modpath, '../datas/yhoo-2003-2005.txt')

    start = time.time()
    # 流 读取文件内容
    file = io.open(data_path, 'r')
    file.readline()
    # print(file)

    # 创建 双向队列 对象， 逆向写入
    dq = collections.deque()
    for line in file:
        dq.appendleft(line)
    # print(dq)

    # 写入到内存缓冲区
    f = io.StringIO(newline=None)
    f.writelines(dq)
    f.seek(0)  # 把指针移动到开头  f.tell()查看指针位置
    # print(f)
    # print(f.getvalue())
    file.close()
    print(time.time() - start)  # 接近0.0秒

    start = time.time()
    df = pd.read_csv(data_path)
    print(time.time() - start)  # 慢 8 倍

    #
    # class DataFeeds:
    #     def __init__(self):
    #         # 数据文件路径
    #         modpath = os.path.dirname(__file__)
    #         data_path = os.path.join(modpath, '../datas/yhoo-2003-2005.txt')
    #
    #         # 流 读取文件内容
    #         file = io.open(data_path, 'r')
    #         file.readline()
    #         # print(file)
    #
    #         # 创建 双向队列 对象， 逆向写入
    #         dq = collections.deque()
    #         for line in file:
    #             dq.appendleft(line)
    #         # print(dq)
    #
    #         # 写入到缓存
    #         f = io.StringIO(newline=None)
    #         f.writelines(dq)
    #         f.seek(0)  # 把光标移动到开头
    #         # print(f)
    #         # print(f.getvalue())
    #         file.close()
    #         self.data = f
    #
    # start = time.time()
    # feeds = DataFeeds()
    # # print(feeds.data)
    # # print(feeds.data.getvalue())
    # print(time.time() - start)

    start = time.time()
    with open(data_path, 'r') as f:
        f.readline()

        dq = collections.deque()
        for line in f:
            dq.appendleft(line)

    ff = io.StringIO(newline=None)
    ff.writelines(dq)
    ff.seek(0)
    # print(ff.getvalue())
    print(time.time() - start)
