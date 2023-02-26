#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# ##############################################################################
# 将有用的模块导入到__init__模块里，此后可通过backtrader.模块名调用
# 有__init__模块的文件夹，叫 包，.py结尾的文件叫模块
# 如果把包看作一个类，那么，__init__就像类的初始化函数，__init__内的代码就像类的属性，被导入的模块就像函数的具体实现
# __init__ 就是包的初始化， __init__ 内的各种类、函数、常(变)量，就是包的属性
# 类.属性名 可以调用类的属性，包.属性名 就可以调用该包的各种属性（模块、类、函数、常(变)量）
# ##############################################################################
"""
    把有用的模块导入到 __init__模块里
    以后用 backtrader.模块名 就能调用该模块了
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

# 从同级模块中导入变量
from .version import __version__, __btversion__

from .errors import *
from . import errors as errors

from .utils import num2date, date2num, time2num, num2time

from .linebuffer import *
from .functions import *

from .order import *
from .comminfo import *
from .trade import *
from .position import *

from .store import Store

from . import broker as broker
from .broker import *

from .lineseries import *

from .dataseries import *
from .feed import *
from .resamplerfilter import *

from .lineiterator import *
from .indicator import *
from .analyzer import *
from .observer import *
from .sizer import *
from .sizers import SizerFix  # old sizer for compatibility
from .strategy import *

from .writer import *

from .signal import *

from .cerebro import *
from .timer import *
from .flt import *

# 导入同级别的包
from . import utils as utils

from . import feeds as feeds
from . import indicators as indicators
from . import indicators as ind
from . import studies as studies
from . import strategies as strategies
from . import strategies as strats
from . import observers as observers
from . import observers as obs
from . import analyzers as analyzers
from . import commissions as commissions
from . import commissions as comms
from . import filters as filters
from . import signals as signals
from . import sizers as sizers
from . import stores as stores
from . import brokers as brokers
from . import timer as timer

from . import talib as talib

# Load contributed indicators and studies
# 负荷贡献指标和研究？
# 加载指标和研究
import backtrader.indicators.contrib
import backtrader.studies.contrib
