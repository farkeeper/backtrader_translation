#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/5 - 17:20
# 作者：farserver@163.com
# ====================================================
import collections
import io
import os
import sys

if __name__ == "__main__":
    modpath = os.path.dirname(__file__)
    data_path = os.path.join(modpath, '../datas/yhoo-2003-2005.txt')

    file = io.open(data_path, 'r')
    file.readline()
    # print(file)
    dq = collections.deque()    # 创建 双向队列 对象
    for line in file:
        dq.appendleft(line)
    print(dq)

    f = io.StringIO(newline=None)
    f.writelines(dq)
    f.seek(0)
    f.close()
    print(f)
    print("大小", sys.getsizeof(f))
