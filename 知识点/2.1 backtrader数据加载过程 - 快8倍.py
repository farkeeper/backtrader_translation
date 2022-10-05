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
    f.seek(0)   # 把光标移动到开头
    # print(f)
    # print(f.getvalue())
    print(time.time() - start)      # 接近0.0秒
    file.close()

    start = time.time()
    df = pd.read_csv(data_path)
    print(time.time() - start)      # 慢 8 倍


