#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：bt对内存缓冲区的读写，按行读入怎么按列生成的line
# 简介：
# 时间：2022/10/7 - 21:19
# 作者：farserver@163.com
# ====================================================
import os

import psutil as psutil


def get_memory_info():
    """ 查看内存使用情况 """
    memory = psutil.virtual_memory()
    total = float(memory.total) / 1024 / 1024 / 1024
    used = float(memory.used) / 1024 / 1024 / 1024
    free = float(memory.free) / 1024 / 1024 / 1024
    print("内存尺寸 %.2f G, 已使用 %.2f G, 剩余 %.2f G" % (total, used, free))

    # 查看内存占用情况
    pid = os.getpid()
    p = psutil.Process(pid)
    info = p.memory_full_info()
    return info.uss / 1024 / 1024 / 1024


if __name__ == "__main__":
    print(get_memory_info())
