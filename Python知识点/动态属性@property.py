#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/6 - 22:47
# 作者：farserver@163.com
# ====================================================
import datetime
import time


class Student:
    def __init__(self, name, birthday):
        self.name = name
        year, month, day = birthday
        self.birthday = datetime.datetime(year, month, day)

    @property
    def age(self):
        return datetime.datetime.now() - self.birthday


if __name__ == "__main__":
    zhangsan = Student("张三", (2009, 10, 9))
    time.sleep(1)
    print(zhangsan.age)

    # https://www.cnblogs.com/wagyuze/p/10622561.html

