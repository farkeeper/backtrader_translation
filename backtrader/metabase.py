#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# 元基类模块：祖宗类
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
    """ 查询kls类的继承关系 返回家谱：祖宗、祖爷爷、爷爷、爸爸
        如果kls有多个爸爸（多继承），爸爸各有爸爸，...，最终有多个祖宗，而函数只查询topclass这一支血脉
        blood lineage 血缘关系
    """
    retval = list()
    for base in kls.__bases__:      # kls的直接父类（他爸爸），不包括爷爷、祖爷爷等
        # 如果kls他爸爸是是topclass的子类 就一只往上辈查
        if issubclass(base, topclass):
            retval.extend(findbases(base, topclass))  # 末尾追加 元素
            retval.append(base)  # 末尾追加 整体

    return retval
    # kls.__bases__ 返回所有直接父类（他爸爸们）
    # 坑：虽然bases是复数，但只查询爸爸辈（可能有多个），查询不到爷爷辈
    # extend 追加元素，append追加整体，如append([1,2,3]), extend追加的是1,2,3而append追加的是[1,2,3]
    # 函数内定义变量 retval ，累加获取元素，此法可嘉。

# type 不考虑继承关系 ， isinstance 考虑继承关系, 如ABCDE5个类，e=E(), e也是A的实例
def findowner(owned, cls, startlevel=2, skip=None):
    # 本函数不会被用来处理数据，所以一般会在类和元类中调用，用于查找是哪个类调用的
    """ 调用本函数的类或元类（如果是cls的实例）# isinstance 考虑继承关系, 如ABCDE5个类，e=E(), e也是A的实例
    owned:
    cls:
    startlevel:从第几级开始查
    skip:跳过谁
    """
    # skip this frame and the caller's -> start at 2
    # 跳过本框框和直接调用者 - 从2级开始
    # 无限迭代器 从startlevel开始，默认步长为1，从无限迭代器里挨个取出
    for framelevel in itertools.count(startlevel):
        # 查找本函数被谁调用过，跳过第一级（直接调用的函数），第2级、3、4、5....直至抛出异常
        try:
            frame = sys._getframe(framelevel)
        except ValueError:
            # 抛出异常时停止循环
            break

        # 返回frame的 self或者obj （实例或者对象）
        # 'self' in regular code    正常代码中的self
        # self是 类 这个对象(有地址有名字有父类有属性有行为)，哪个类调用了，self就是谁，self是个指针，是个内存地址
        # 结合__new__方法理解：new创建一个类（这个类是空的，就是个内存地址，地址里有类名 父类 属性 三个空变量）
        # 类创建的实例如果是cls的实例
        self_ = frame.f_locals.get('self', None)
        if skip is not self_:   # 如果不跳过这一级
            # 如果调用本函数的类不是owned并且调用本函数的类是cls的实例
            if self_ is not owned and isinstance(self_, cls):
                return self_

        # '_obj' in metaclasses ： 元类里面的 _obj
        # 调用本函数的元类创建的对象如果是cls类的实例
        obj_ = frame.f_locals.get('_obj', None)
        if skip is not obj_:
            if obj_ is not owned and isinstance(obj_, cls):
                return obj_

    return None

"""
findbases 和 findowner 用来查找实例的父类和调用者
在bt里，通过这两个函数就能把父子关系捋出来
"""

"""
__call__()函数 使 类名 可以像函数一样被调用，必须有返回值
类名后面加(),就像个函数一样。
可见类的返回值从__call__而来
如:
    class A:
        def __call__():
            pass
            
    就可以 A() 
"""


class MetaBase(type):
    print("MetaBase")
    """
    元基类：backtrader所有类的老祖宗
    由名字猜想元类 MetaBase 是所有元类的基类
    元类 必须显式继承type
    backtrader可能有很多元类，这些元类负责创建不同的类，但这些元类都继承自 基类MetaBase
    像：
        MetaBase是玉帝，玉帝手下有很多神仙，这些都是元类，元类负责创建类。
        神仙负责创建不同的类(型)，动物类、人类、植物类、建筑类；   狗类、鸡类、菊花类、学生类、商品房类
        不同的类有好多好多的实体。 张三家的那只老母狗、李四、这棵野菊花、去年春天和美女一起开过房的那幢酒店
    """

    # 类的实例化会首先运行()内的代码，元类有call函数，才可以调用。
    # 创建类对象时，会自动调用 元类的 __call__ 函数，返回一个元类的实例对象（类）

    # 接下来的5个 类行为（函数） 都是给 call函数 准备的
    # 类是由 该类（或者父类）设定的 元类 负责创建的：

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
        （）可以看出 调用运算
        谁调用谁就是cls，谁(metaclass=MetaBase)， 谁就是cls
        """
        print("看谁调用了bt的老祖宗元基类MetaBase", __file__)
        cls, args, kwargs = cls.doprenew(*args, **kwargs)
        _obj, args, kwargs = cls.donew(*args, **kwargs)
        _obj, args, kwargs = cls.dopreinit(_obj, *args, **kwargs)
        _obj, args, kwargs = cls.doinit(_obj, *args, **kwargs)
        _obj, args, kwargs = cls.dopostinit(_obj, *args, **kwargs)
        return _obj  # 一切皆对象

    # python 一切皆对象，一切皆指针
    # 面向过程 --> 面向对象 --> 面向Github
    """
    元基类MetaBase老祖宗，未实现new函数，应让 子类 实现
    """


class AutoInfoClass(object):
    _getpairsbase = classmethod(lambda cls: OrderedDict())  # lambda 参数:表达式，返回一个函数对象（函数的地址）
    _getpairs = classmethod(lambda cls: OrderedDict())  # OrderedDict 有序字典
    _getrecurse = classmethod(lambda cls: False)
    # _getpairsbase用于提取所有bases(父类)中的相关属性
    # _getpairs用于提取父类和当前类定义中的所有相关属性
    # @classmethod 类方法装饰器，可 通过类名直接调用
    # 以上代码等价于：
    # @classmethod
    # def _getpairsbase(cls):
    #       return OrderedDict()

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

    @classmethod  # 类方法，类不用实例化，就可以调用该方法，如 AutoInfoClass._getkwargsdefault(cls)
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
        # 调用父类的new函数，创建一个空对象（内存地址）
        obj = super(AutoInfoClass, cls).__new__(cls, *args, **kwargs)

        if cls._getrecurse():
            for infoname in obj._getkeys():
                recursecls = getattr(cls, infoname)
                setattr(obj, infoname, recursecls())
        # 返回这个对象 赋值给__init__的self
        return obj


class MetaParams(MetaBase):
    print("MetaParams类")
    """
    参数类的元类
    继承自元类的类也是元类"""

    def __new__(meta, name, bases, dct):
        # Remove params from class definition to avoid inheritance
        # (and hence "repetition")
        # 从类的定义中删除params以避免被继承或者因此重复
        newparams = dct.pop('params', ())  # 取出params，如果没有则返回空元组

        packs = 'packages'
        newpackages = tuple(dct.pop(packs, ()))  # remove before creation

        fpacks = 'frompackages'
        fnewpackages = tuple(dct.pop(fpacks, ()))  # remove before creation

        # Create the new class - this pulls predefined "params"
        # 创建新类 - 提取预定义的‘params’
        cls = super(MetaParams, meta).__new__(meta, name, bases, dct)
        # python3可以直接用super().__new__(cls, bases, attr)

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
    pass
    # stub to allow easy subclassing without metaclasses
    # 没有元类的情况下轻松子类化？


class ItemCollection(object):
    """
    封装了 一个可以通过 index和name 访问具体项 的 数据结构对象
    Holds a collection of items that can be reached by
      - Index
      - Name (if set in the append operation)
    """

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

    # list.index(x) 返回对象x的索引
