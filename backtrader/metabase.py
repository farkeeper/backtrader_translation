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

from collections import OrderedDict
import itertools
import sys

import backtrader as bt
from .utils.py3 import zip, string_types, with_metaclass


def findbases(kls, topclass):
    """ 查找kls的所有父类 到topclass为止 """
    retval = list()
    for base in kls.__bases__:
        if issubclass(base, topclass):      # 如果base是topclass的子类
            retval.extend(findbases(base, topclass))        # 末尾追加 元素
            retval.append(base)  # 末尾追加 整体

    return retval
    # kls.__bases__ 返回所有基类
    # 函数内部如果只 append,每次迭代都将会清空retval，无法获取所有父类
    # 函数内定义变量 retval ，累加获取元素，此法可取。
    # 迭代法可以吗？

def findowner(owned, cls, startlevel=2, skip=None):
    # skip this frame and the caller's -> start at 2
    for framelevel in itertools.count(startlevel):
        try:
            frame = sys._getframe(framelevel)
        except ValueError:
            # Frame depth exceeded ... no owner ... break away
            break

        # 'self' in regular code
        self_ = frame.f_locals.get('self', None)
        if skip is not self_:
            if self_ is not owned and isinstance(self_, cls):
                return self_

        # '_obj' in metaclasses
        obj_ = frame.f_locals.get('_obj', None)
        if skip is not obj_:
            if obj_ is not owned and isinstance(obj_, cls):
                return obj_

    return None

"""
__call__()函数 使 类名 可以像函数一样被调用，有返回值
类名后面加(),就像个函数一样。
可见类的返回值从__call__而来
如:
    class A:
        def __call__():
            pass
            
    就可以 A() 
"""
class MetaBase(type):
    """
    元基类：backtrader所有类的老祖宗
    元类 必须显式继承type
    由名字猜想元类 MetaBase 是所有元类的基类
    backtrader可能有很多元类，这些元类负责创建不同的类，但这些元类都继承自 基类MetaBase
    像：
        MetaBase是玉帝，玉帝手下有很多神仙，这些都是元类，元类负责创建类。
        神仙负责创建不同的类(型)，动物类、人类、植物类、建筑类；   狗类、鸡类、菊花类、学生类、商品房类
        不同的类有好多好多的实体。 张三家的那只老母狗、李四、这棵野菊花、去年春天和美女一起开过房的那幢酒店
    """

    # 接下来的5个 类行为（函数） 都是给 call函数 准备的
    # 类是由 该类（或者父类）设定的 元类 负责创建的：metaclass=元类名，会自动调用 元类的 __call__ 函数
    # 类是由 元类的 __call__ 函数，控制创建过程 的

    def doprenew(cls, *args, **kwargs):
        return cls, args, kwargs

    def donew(cls, *args, **kwargs):
        _obj = cls.__new__(cls, *args, **kwargs)
        return _obj, args, kwargs

    def dopreinit(cls, _obj, *args, **kwargs):
        return _obj, args, kwargs

    def doinit(cls, _obj, *args, **kwargs):
        _obj.__init__(*args, **kwargs)
        return _obj, args, kwargs

    def dopostinit(cls, _obj, *args, **kwargs):
        return _obj, args, kwargs

    def __call__(cls, *args, **kwargs):
        """call函数使 类 可调用，如 类名()
        谁调用谁就是cls，谁(metaclass=MetaBase)， 谁就是cls
        """
        print("看谁调用了bt的老祖宗元基类MetaBase", __file__)
        cls, args, kwargs = cls.doprenew(*args, **kwargs)
        _obj, args, kwargs = cls.donew(*args, **kwargs)
        _obj, args, kwargs = cls.dopreinit(_obj, *args, **kwargs)
        _obj, args, kwargs = cls.doinit(_obj, *args, **kwargs)
        _obj, args, kwargs = cls.dopostinit(_obj, *args, **kwargs)
        return _obj     # 一切皆对象

    # python 一切皆对象，一切皆指针
    # 面向过程 --> 面向对象 --> 面向Github
    """
    元基类MetaBase老祖宗，未实现new函数，应让 子类实现
    """


class AutoInfoClass(object):
    _getpairsbase = classmethod(lambda cls: OrderedDict())
    _getpairs = classmethod(lambda cls: OrderedDict())
    _getrecurse = classmethod(lambda cls: False)

    @classmethod
    def _derive(cls, name, info, otherbases, recurse=False):
        # collect the 3 set of infos
        # info = OrderedDict(info)
        baseinfo = cls._getpairs().copy()
        obasesinfo = OrderedDict()
        for obase in otherbases:
            if isinstance(obase, (tuple, dict)):
                obasesinfo.update(obase)
            else:
                obasesinfo.update(obase._getpairs())

        # update the info of this class (base) with that from the other bases
        baseinfo.update(obasesinfo)

        # The info of the new class is a copy of the full base info
        # plus and update from parameter
        clsinfo = baseinfo.copy()
        clsinfo.update(info)

        # The new items to update/set are those from the otherbase plus the new
        info2add = obasesinfo.copy()
        info2add.update(info)

        clsmodule = sys.modules[cls.__module__]
        newclsname = str(cls.__name__ + '_' + name)  # str - Python 2/3 compat

        # This loop makes sure that if the name has already been defined, a new
        # unique name is found. A collision example is in the plotlines names
        # definitions of bt.indicators.MACD and bt.talib.MACD. Both end up
        # definining a MACD_pl_macd and this makes it impossible for the pickle
        # module to send results over a multiprocessing channel
        namecounter = 1
        while hasattr(clsmodule, newclsname):
            newclsname += str(namecounter)
            namecounter += 1

        newcls = type(newclsname, (cls,), {})
        setattr(clsmodule, newclsname, newcls)

        setattr(newcls, '_getpairsbase',
                classmethod(lambda cls: baseinfo.copy()))
        setattr(newcls, '_getpairs', classmethod(lambda cls: clsinfo.copy()))
        setattr(newcls, '_getrecurse', classmethod(lambda cls: recurse))

        for infoname, infoval in info2add.items():
            if recurse:
                recursecls = getattr(newcls, infoname, AutoInfoClass)
                infoval = recursecls._derive(name + '_' + infoname,
                                             infoval,
                                             [])

            setattr(newcls, infoname, infoval)

        return newcls

    def isdefault(self, pname):
        return self._get(pname) == self._getkwargsdefault()[pname]

    def notdefault(self, pname):
        return self._get(pname) != self._getkwargsdefault()[pname]

    def _get(self, name, default=None):
        return getattr(self, name, default)

    @classmethod    # 类方法，类不用实例化，就可以调用该方法，如 AutoInfoClass()._getkwargsdefault(cls)
    def _getkwargsdefault(cls):
        return cls._getpairs()

    @classmethod
    def _getkeys(cls):
        return cls._getpairs().keys()

    @classmethod
    def _getdefaults(cls):
        return list(cls._getpairs().values())

    @classmethod
    def _getitems(cls):
        return cls._getpairs().items()

    @classmethod
    def _gettuple(cls):
        return tuple(cls._getpairs().items())

    def _getkwargs(self, skip_=False):
        l = [
            (x, getattr(self, x))
            for x in self._getkeys() if not skip_ or not x.startswith('_')]
        return OrderedDict(l)

    def _getvalues(self):
        return [getattr(self, x) for x in self._getkeys()]

    def __new__(cls, *args, **kwargs):
        obj = super(AutoInfoClass, cls).__new__(cls, *args, **kwargs)

        if cls._getrecurse():
            for infoname in obj._getkeys():
                recursecls = getattr(cls, infoname)
                setattr(obj, infoname, recursecls())

        return obj


class MetaParams(MetaBase):
    """
    参数类的元类
    继承自元类的类也是元类"""
    def __new__(meta, name, bases, dct):
        # Remove params from class definition to avoid inheritance
        # (and hence "repetition")
        # 从类的定义中删除params以避免被继承或者因此重复
        newparams = dct.pop('params', ())   # 取出params，如果没有则返回空元组

        packs = 'packages'
        newpackages = tuple(dct.pop(packs, ()))  # remove before creation

        fpacks = 'frompackages'
        fnewpackages = tuple(dct.pop(fpacks, ()))  # remove before creation

        # Create the new class - this pulls predefined "params"
        # 创建新类 - 提取预定义的‘params’
        cls = super(MetaParams, meta).__new__(meta, name, bases, dct)

        # Pulls the param class out of it - default is the empty class
        # 提取 param 类 - 默认是空类
        # 从cls中获取params属性值，如果没有params属性则返回AutoInfoClass
        params = getattr(cls, 'params', AutoInfoClass)

        # Pulls the packages class out of it - default is the empty class
        packages = tuple(getattr(cls, packs, ()))
        fpackages = tuple(getattr(cls, fpacks, ()))

        # get extra (to the right) base classes which have a param attribute
        morebasesparams = [x.params for x in bases[1:] if hasattr(x, 'params')]

        # Get extra packages, add them to the packages and put all in the class
        for y in [x.packages for x in bases[1:] if hasattr(x, packs)]:
            packages += tuple(y)

        for y in [x.frompackages for x in bases[1:] if hasattr(x, fpacks)]:
            fpackages += tuple(y)

        cls.packages = packages + newpackages
        cls.frompackages = fpackages + fnewpackages

        # Subclass and store the newly derived params class
        # 子类 并 储存新派生的params类
        cls.params = params._derive(name, newparams, morebasesparams)

        return cls

    def donew(cls, *args, **kwargs):
        clsmod = sys.modules[cls.__module__]
        # import specified packages
        for p in cls.packages:
            if isinstance(p, (tuple, list)):
                p, palias = p
            else:
                palias = p

            pmod = __import__(p)

            plevels = p.split('.')
            if p == palias and len(plevels) > 1:  # 'os.path' not aliased
                setattr(clsmod, pmod.__name__, pmod)  # set 'os' in module

            else:  # aliased and/or dots
                for plevel in plevels[1:]:  # recurse down the mod
                    pmod = getattr(pmod, plevel)

                setattr(clsmod, palias, pmod)

        # import from specified packages - the 2nd part is a string or iterable
        for p, frompackage in cls.frompackages:
            if isinstance(frompackage, string_types):
                frompackage = (frompackage,)  # make it a tuple

            for fp in frompackage:
                if isinstance(fp, (tuple, list)):
                    fp, falias = fp
                else:
                    fp, falias = fp, fp  # assumed is string

                # complain "not string" without fp (unicode vs bytes)
                pmod = __import__(p, fromlist=[str(fp)])
                pattr = getattr(pmod, fp)
                setattr(clsmod, falias, pattr)
                for basecls in cls.__bases__:
                    setattr(sys.modules[basecls.__module__], falias, pattr)

        # Create params and set the values from the kwargs
        # 创建params，并通过 kwargs字典 给他赋值
        params = cls.params()
        for pname, pdef in cls.params._getitems():
            setattr(params, pname, kwargs.pop(pname, pdef))
        # pop 取出，弹出。返回值为取出的值，原数据被删除。

        # Create the object and set the params in place
        _obj, args, kwargs = super(MetaParams, cls).donew(*args, **kwargs)
        _obj.params = params
        _obj.p = params  # shorter alias

        # Parameter values have now been set before __init__
        # 在初始化之前参数值已被设置完毕
        return _obj, args, kwargs


class ParamsBase(with_metaclass(MetaParams, object)):
    pass  # stub to allow easy subclassing without metaclasses


class ItemCollection(object):
    '''
    Holds a collection of items that can be reached by

      - Index
      - Name (if set in the append operation)
    '''
    def __init__(self):
        self._items = list()
        self._names = list()

    def __len__(self):
        return len(self._items)

    def append(self, item, name=None):
        setattr(self, name, item)
        self._items.append(item)
        if name:
            self._names.append(name)

    def __getitem__(self, key):
        return self._items[key]

    def getnames(self):
        return self._names

    def getitems(self):
        return zip(self._names, self._items)

    def getbyname(self, name):
        idx = self._names.index(name)
        return self._items[idx]

