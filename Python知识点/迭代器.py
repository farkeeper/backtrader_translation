#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ====================================================
# 名称：
# 简介：
# 时间：2022/10/6 - 20:09
# 作者：farserver@163.com
# ====================================================
import os.path

if __name__ == "__main__":
    # modpath = os.path.dirname(__file__)
    # datapath = os.path.join(modpath, '../datas/orcl-1995-2014.txt')
    #
    # with open(datapath, 'r') as f:
    #     obj = f.readline()
    #     print(obj, type(obj))
    #
    #     obj = f.readline()
    #     print(obj, type(obj))
    #
    #     obj = f.readline()
    #     print(obj, type(obj))
    #
    #     obj = f.readline()
    #     print(obj, type(obj))
    #
    #     print(f.__next__())
    #     print(f.__next__())
    #     print(f.__next__())

    class ITE:
        def __init__(self, data):
            self.data = data

        def __iter__(self):
            return self

        def __next__(self):
            if self.data > 100:
                raise (StopIteration)
            item = self.data
            self.data += 1
            return item


    ite = ITE(1)
    for i in ite:
        print(i)


    class ITE:
        def __init__(self, lst):
            self.lst = lst
            self.key = 0

        def __getitem__(self, key):
            return self.lst[key]

        def __next__(self):
            item = self.lst[self.key]
            self.key += 1
            return item


    ite = ITE(['a', 'b', 'c'])
    for i in ite:
        print(i)

    # 迭代器使用场景：数列数据量巨大
    # 斐波那契数列：每个数都是前两个数之和 0，1，1，2，3，5，8，13，21，34
    class FibIterator:
        def __init__(self, stop):
            self.num1 = 0   # 第一个数
            self.num2 = 1   # 第二个数
            self.key = 0    # 当前指针
            self.stop = stop    # 终点

        def __iter__(self):
            return self

        def __next__(self):
            if self.key > self.stop:
                raise StopIteration
            # 当前项 当前状态
            item = self.num1 + self.num2
            self.num1 = self.num2
            self.num2 = item
            self.key += 1   # 指向下一项
            return item
    fib = FibIterator(15)
    for i in fib:
        print(i)

    """
    1.迭代器的应用场景
        1).如果数列的数据规模巨大
        2).数列有规律，但是依靠列表推导式描述不出来


    2.数学中有个著名的斐波那契数列（Fibonacci），
    数列中第⼀个数0，第⼆个数1，其后的每⼀个数都可由前两个数相加得到：
    如下：
    0,    1,    1,   2,    3,    5,   8,    13,    21,   34,    ...

    现在我们想要通过for...in...循环来遍历迭代斐波那契数列中的前n个数。
    那么这个斐波那契数列我们就可以⽤迭代器来实现，
    每次迭代都通过数学计算来⽣成下⼀个数。

    """
    from collections.abc import Iterable, Iterator


    class FibIterator(object):
        """
            fib数列迭代器
        """

        # 初始化方法
        def __init__(self, count):
            # 斐波拉契数列中的前两个数
            self.num1 = 0
            self.num2 = 1

            # 用来保存迭代的总次数
            self.count = count
            # 用来记录迭代次数(计数器)
            self.i = 0

        # 实现__iter__表示FibIterator是一个可迭代对象
        # 返回对象自己。是一个可迭代对象
        def __iter__(self):
            return self

        # 实现__next__方法，是FibIterator定义为迭代器对象的重要条件之一
        def __next__(self):
            # 判断是否迭代结束，如果没有到达迭代次数，则返回数据
            # self.count 需要迭代的次数
            # self.i已迭代次数
            if self.i < self.count:

                item = self.num1
                # 计算num1, num2的值，方便下次迭代返回
                # 这里运用的是序列的封包与解包，不会的可以看我以前的文章（元组）
                self.num1, self.num2 = self.num2, self.num1 + self.num2

                # 执行一次next方法，计数器+1
                self.i += 1
                # 返回新获得的数，
                # 也就是前两个数求和的第三个数
                return item
            else:
                # 到达了迭代次数，抛出异常
                raise StopIteration


    # 创建一个fib数列迭代器对象
    fibIter = FibIterator(15)

    # fibIter对象是一个迭代器
    print(isinstance(fibIter, Iterable))  # True
    print(isinstance(fibIter, Iterator))  # True

    # 转换为列表查看fib对象内容
    # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]
    print(list(fibIter))

    # 遍历，因为self.key已指向末尾，所以打印不出来 如果注释掉print(list(fibIter))就能打印出来了
    for li in fibIter:
        print("遍历", li)

    # 重置一下
    fibIter.i = 0
    fibIter.num1 = 0
    fibIter.num2 = 1
    for li in fibIter:
        print("遍历", li)
