#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# with_metaclass(meta, *bases) 到底是个什么，有什么作用
# 实际就是：指明元类 等同于 metaclass = meta
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import itertools
import sys

PY2 = sys.version_info.major == 2

if PY2:
    try:
        import _winreg as winreg
    except ImportError:
        winreg = None

    MAXINT = sys.maxint
    MININT = -sys.maxint - 1

    MAXFLOAT = sys.float_info.max
    MINFLOAT = sys.float_info.min

    string_types = str, unicode
    integer_types = int, long

    filter = itertools.ifilter
    map = itertools.imap
    range = xrange
    zip = itertools.izip
    long = long

    cmp = cmp

    bytes = bytes
    bstr = bytes

    from io import StringIO

    from urllib2 import urlopen, ProxyHandler, build_opener, install_opener
    from urllib import quote as urlquote


    def iterkeys(d):
        return d.iterkeys()


    def itervalues(d):
        return d.itervalues()


    def iteritems(d):
        return d.iteritems()


    def keys(d):
        return d.keys()


    def values(d):
        return d.values()


    def items(d):
        return d.items()


    import Queue as queue

else:
    try:
        import winreg
    except ImportError:
        winreg = None

    MAXINT = sys.maxsize
    MININT = -sys.maxsize - 1

    MAXFLOAT = sys.float_info.max
    MINFLOAT = sys.float_info.min

    string_types = str,
    integer_types = int,

    filter = filter
    map = map
    range = range
    zip = zip
    long = int


    def cmp(a, b):
        return (a > b) - (a < b)


    def bytes(x):
        return x.encode('utf-8')


    def bstr(x):
        return str(x)


    from io import StringIO

    from urllib.request import (urlopen, ProxyHandler, build_opener,
                                install_opener)
    from urllib.parse import quote as urlquote


    def iterkeys(d):
        return iter(d.keys())


    def itervalues(d):
        return iter(d.values())


    def iteritems(d):
        return iter(d.items())


    def keys(d):
        return list(d.keys())


    def values(d):
        return list(d.values())


    def items(d):
        return list(d.items())


    import queue as queue


# This is from Armin Ronacher from Flash simplified later by six
def with_metaclass(meta, *bases):
    """Create a base class with a metaclass.
    使用元类创建一个基类 ： 使用元类meta创建一个 临时 基类
        创建一个基类，这个基类是临时的，这个基类是由元类meta创建的。
    创建一个伪元类
    """

    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    # 这可能需要一点解释：基本思想是为同级别的的类实例创建一个伪元类，用实际的元类来替代他自己
    class metaclass(meta):
        """metaclass类继承自meta类, meta是个元类，metaclass也是个元类"""

        # 开辟内存空间
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)

    return type.__new__(metaclass, str('temporary_class'), (), {})
    # 使用元类meta创建一个元类metaclass（基类是bases）
    # 调用type类的__new__函数，创建一个metaclass类型的对象，命名为temporary_class
    # 作为一个基类

    # Cerebro类继承自temporary_class类
    # Cerebro类未指明元类，所以调用父类temporary_class类的元类meta（即MetaParams）来生成类
    # __new__函数中运行代码MetaParams(name, bases, d)来生成cerebro，

    """
    函数输出type.new(metaclass, str('temporary_class'), (), {})，是以metaclass为类型的类，暂命名为 return_class
cerebro类继承return_class
在生成类cerebro过程中，由于cerebro代码定义中为指名元类，所以调用父类return_class的类型metaclass来生成类
metaclass执行__new__函数来生成cerebro类
__new__函数中运行代码MetaParams(name, bases, d)来生成cerebro，MetaParams继承父类MetaBase，在MetaParams和MetaBase中均未指定元类，所以MetaParams的类型是type，所以MetaParams会调用内部定义的__new__函数来生成对象
测试可知道，type(cerebro) = MetaParams
测试可知道，运行cerebro()代码，作为MetaParams实例的cerebro继承MetaParams的父类MetaBase的实例方法__call__方法
    """
