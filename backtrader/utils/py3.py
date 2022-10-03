#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2015-2020 Daniel Rodriguez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
    """

    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    # 这可能需要一点解释：基本思想是创建一个伪元类，为同级别的的类实例，用实际的元类来替代他自己
    class metaclass(meta):
        """metaclass类继承自meta类, meta是个元类，metaclass也是个元类"""

        # 开辟内存空间
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)

    return type.__new__(metaclass, str('temporary_class'), (), {})
    # temporary_class 临时类
