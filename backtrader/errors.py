#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################

###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__all__ = ['BacktraderError', 'StrategySkipError']


class BacktraderError(Exception):
    """ Base exception for all other exceptions
        所有异常类的基类
    """
    pass


class StrategySkipError(BacktraderError):
    """Requests the platform to skip this strategy for backtesting. To be
    raised during the initialization (``__init__``) phase of the instance
    请求平台跳过此策略
    在实例的初始化阶段抛出异常"""
    pass


class ModuleImportError(BacktraderError):
    """Raised if a class requests a module to be present to work and it cannot
    be imported
    模块导入异常 类
    如果一个类需要一个模块才能工作但是这个模块却不能导入 则抛出 模块导入异常
    """

    def __init__(self, message, *args):
        super(ModuleImportError, self).__init__(message)
        self.args = args


class FromModuleImportError(ModuleImportError):
    """Raised if a class requests a module to be present to work and it cannot
    be imported"""

    def __init__(self, message, *args):
        super(FromModuleImportError, self).__init__(message, *args)


if __name__ == "__main__":
    module_import_error = ModuleImportError("模块导入异常啊哥们", 12345, 67890)
    print("为什么不打印message却能打印可变参数呢", module_import_error)
