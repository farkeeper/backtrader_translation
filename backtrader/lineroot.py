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
'''

.. module:: lineroot

Definition of the base class LineRoot and base classes LineSingle/LineMultiple
to define interfaces and hierarchy for the real operational classes

.. moduleauthor:: Daniel Rodriguez

'''
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import operator

from .utils.py3 import range, with_metaclass

from . import metabase

"""
mro()：类的继承关系
"""
class MetaLineRoot(metabase.MetaParams):
    '''
    Once the object is created (effectively pre-init) the "owner" of this
    class is sought
    一旦对象被创建（实际上是预初始化），就会查询这个类的所有者
    '''

    def donew(cls, *args, **kwargs):
        _obj, args, kwargs = super(MetaLineRoot, cls).donew(*args, **kwargs)

        # Find the owner and store it
        # startlevel = 4 ... to skip intermediate call stacks
        # 查找所有者并存储 开始级别=4 跳过中间的堆栈
        ownerskip = kwargs.pop('_ownerskip', None)
        _obj._owner = metabase.findowner(_obj,
                                         _obj._OwnerCls or LineMultiple,
                                         skip=ownerskip)

        # Parameter values have now been set before __init__
        # 在 __init__ 之前前 参数值已被设置
        return _obj, args, kwargs


class LineRoot(with_metaclass(MetaLineRoot, object)):
    '''
    Defines a common base and interfaces for Single and Multiple
    LineXXX instances
    为 单线 和多线 定义一个通用接口 基础类

        Period management
        Iteration management
        Operation (dual/single operand) Management
        Rich Comparison operator definition
    '''
    _OwnerCls = None
    _minperiod = 1
    _opstage = 1

    IndType, StratType, ObsType = range(3)

    def _stage1(self):
        self._opstage = 1

    def _stage2(self):
        self._opstage = 2

    def _operation(self, other, operation, r=False, intify=False):
        if self._opstage == 1:
            return self._operation_stage1(
                other, operation, r=r, intify=intify)

        return self._operation_stage2(other, operation, r=r)

    def _operationown(self, operation):
        if self._opstage == 1:
            return self._operationown_stage1(operation)

        return self._operationown_stage2(operation)

    def qbuffer(self, savemem=0):
        """Change the lines to implement a minimum size qbuffer scheme
        更改lines使之适应缓冲区大小"""
        raise NotImplementedError
    # 这里没有用abc.abstractmethod
    # 抛出 未实现错误 很好的提示作用

    def minbuffer(self, size):
        """Receive notification of how large the buffer must at least be
        接收缓冲区最小尺寸的通知
        """
        raise NotImplementedError

    def setminperiod(self, minperiod):
        '''
        Direct minperiod manipulation. It could be used for example
        by a strategy
        to not wait for all indicators to produce a value
        直接指定最小周期。可以用于策略
        而不必等所有指标都生成值
        '''
        self._minperiod = minperiod

    def updateminperiod(self, minperiod):
        '''
        Update the minperiod if needed. The minperiod will have been
        calculated elsewhere
        如果需要的话更新最小周期。
        最小周期将被计算
        如果self的更大必须接管
        and has to take over if greater that self's
        '''
        self._minperiod = max(self._minperiod, minperiod)

    def addminperiod(self, minperiod):
        '''
        Add a minperiod to own ... to be defined by subclasses
        为所有者添加一个最小周期，将在子类定义
        '''
        raise NotImplementedError

    def incminperiod(self, minperiod):
        '''
        Increment the minperiod with no considerations
        自增加最小周期 无需考虑
        '''
        raise NotImplementedError

    def prenext(self):
        '''
        It will be called during the "minperiod" phase of an iteration.
        将在 迭代‘最小周期’阶段 被调用
        '''
        pass

    def nextstart(self):
        '''
        It will be called when the minperiod phase is over for the 1st
        post-minperiod value. Only called once and defaults to automatically
        calling next
        第一个 ‘最小周期’阶段 结束时将被调用
        仅被调用一次，默认会自动调用下一轮
        '''
        self.next()

    def next(self):
        '''
        Called to calculate values when the minperiod is over
        当最小周期结束时 将被调用 来计算值
        '''
        pass

    def preonce(self, start, end):
        '''
        It will be called during the "minperiod" phase of a "once" iteration
        '''
        pass

    def oncestart(self, start, end):
        '''
        It will be called when the minperiod phase is over for the 1st
        post-minperiod value

        Only called once and defaults to automatically calling once
        '''
        self.once(start, end)

    def once(self, start, end):
        '''
        Called to calculate values at "once" when the minperiod is over
        '''
        pass

    # Arithmetic operators
    def _makeoperation(self, other, operation, r=False, _ownerskip=None):
        raise NotImplementedError

    def _makeoperationown(self, operation, _ownerskip=None):
        raise NotImplementedError

    def _operationown_stage1(self, operation):
        '''
        Operation with single operand which is "self"
        '''
        return self._makeoperationown(operation, _ownerskip=self)

    def _roperation(self, other, operation, intify=False):
        '''
        Relies on self._operation to and passes "r" True to define a
        reverse operation
        '''
        return self._operation(other, operation, r=True, intify=intify)

    def _operation_stage1(self, other, operation, r=False, intify=False):
        '''
        Two operands' operation. Scanning of other happens to understand
        if other must be directly an operand or rather a subitem thereof
        '''
        if isinstance(other, LineMultiple):
            other = other.lines[0]

        return self._makeoperation(other, operation, r, self)

    def _operation_stage2(self, other, operation, r=False):
        '''
        Rich Comparison operators. Scans other and returns either an
        operation with other directly or a subitem from other
        '''
        if isinstance(other, LineRoot):
            other = other[0]

        # operation(float, other) ... expecting other to be a float
        if r:
            return operation(other, self[0])

        return operation(self[0], other)

    def _operationown_stage2(self, operation):
        return operation(self[0])

    def __add__(self, other):
        return self._operation(other, operator.__add__)

    def __radd__(self, other):
        return self._roperation(other, operator.__add__)

    def __sub__(self, other):
        return self._operation(other, operator.__sub__)

    def __rsub__(self, other):
        return self._roperation(other, operator.__sub__)

    def __mul__(self, other):
        return self._operation(other, operator.__mul__)

    def __rmul__(self, other):
        return self._roperation(other, operator.__mul__)

    def __div__(self, other):
        return self._operation(other, operator.__div__)

    def __rdiv__(self, other):
        return self._roperation(other, operator.__div__)

    def __floordiv__(self, other):
        return self._operation(other, operator.__floordiv__)

    def __rfloordiv__(self, other):
        return self._roperation(other, operator.__floordiv__)

    def __truediv__(self, other):
        return self._operation(other, operator.__truediv__)

    def __rtruediv__(self, other):
        return self._roperation(other, operator.__truediv__)

    def __pow__(self, other):
        return self._operation(other, operator.__pow__)

    def __rpow__(self, other):
        return self._roperation(other, operator.__pow__)

    def __abs__(self):
        return self._operationown(operator.__abs__)

    def __neg__(self):
        return self._operationown(operator.__neg__)

    def __lt__(self, other):
        return self._operation(other, operator.__lt__)

    def __gt__(self, other):
        return self._operation(other, operator.__gt__)

    def __le__(self, other):
        return self._operation(other, operator.__le__)

    def __ge__(self, other):
        return self._operation(other, operator.__ge__)

    def __eq__(self, other):
        return self._operation(other, operator.__eq__)

    def __ne__(self, other):
        return self._operation(other, operator.__ne__)

    def __nonzero__(self):
        return self._operationown(bool)

    __bool__ = __nonzero__

    # Python 3 forces explicit implementation of hash if
    # the class has redefined __eq__
    __hash__ = object.__hash__


class LineMultiple(LineRoot):
    '''
    Base class for LineXXX instances that hold more than one line
    '''
    def reset(self):
        self._stage1()
        self.lines.reset()

    def _stage1(self):
        super(LineMultiple, self)._stage1()
        for line in self.lines:
            line._stage1()

    def _stage2(self):
        super(LineMultiple, self)._stage2()
        for line in self.lines:
            line._stage2()

    def addminperiod(self, minperiod):
        '''
        The passed minperiod is fed to the lines
        '''
        # pass it down to the lines
        for line in self.lines:
            line.addminperiod(minperiod)

    def incminperiod(self, minperiod):
        '''
        The passed minperiod is fed to the lines
        '''
        # pass it down to the lines
        for line in self.lines:
            line.incminperiod(minperiod)

    def _makeoperation(self, other, operation, r=False, _ownerskip=None):
        return self.lines[0]._makeoperation(other, operation, r, _ownerskip)

    def _makeoperationown(self, operation, _ownerskip=None):
        return self.lines[0]._makeoperationown(operation, _ownerskip)

    def qbuffer(self, savemem=0):
        for line in self.lines:
            line.qbuffer(savemem=1)

    def minbuffer(self, size):
        for line in self.lines:
            line.minbuffer(size)


class LineSingle(LineRoot):
    '''
    Base class for LineXXX instances that hold a single line
    '''
    def addminperiod(self, minperiod):
        '''
        Add the minperiod (substracting the overlapping 1 minimum period)
        '''
        self._minperiod += minperiod - 1

    def incminperiod(self, minperiod):
        '''
        Increment the minperiod with no considerations
        '''
        self._minperiod += minperiod
