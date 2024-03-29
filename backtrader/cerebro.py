#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
# 模块名称
# 模块功能
# 应用场景
# 涉及知识
# 待解问题
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime
import collections

import itertools
import multiprocessing  # 多进程 https://zhuanlan.zhihu.com/p/136995403
# ProcessPoolExecutor 和 ThreadPoolExecutor 更简单

import backtrader as bt
from .utils.py3 import (map, range, zip, with_metaclass, string_types,
                        integer_types)

from . import linebuffer
from . import indicator
from .brokers import BackBroker
from .metabase import MetaParams
from . import observers
from .writer import WriterFile
from .utils import OrderedDict, tzparse, num2date, date2num
from .strategy import Strategy, SignalStrategy
from .tradingcal import (TradingCalendarBase, TradingCalendar,
                         PandasMarketCalendar)
from .timer import Timer


# Defined here to make it pickable. Ideally it could be defined inside Cerebro
# 在这里定义以期他可以被拾取，理想状态下他可以在Cerebro内部定义

class OptReturn(object):
    def __init__(self, params, **kwargs):  # 位置参数 关键字参数
        self.p = self.params = params
        for k, v in kwargs.items():  # 遍历字典键值对 关键字参数以字典类型传递
            setattr(self, k, v)  # 为类实例设置属性值（属性可以是新增）

# object是所有类的基类、超类，一切皆对象。
"""
    赛萝卜运行机制：
        加载系统变量
        实例化策略
        执行策略
"""


class Cerebro(with_metaclass(MetaParams, object)):
    '''
    赛萝卜：backtrader的大脑、发动机、回测引擎
    Params:
    参数：
      - ``preload`` (default: ``True``)
        预加载：默认值 是
        Whether to preload the different ``data feeds`` passed to cerebro for
        the Strategies
        是否把传递给 cerebro的 ’数据饲料‘ 预加载 给 策略
        是否为策略预加载‘数据源’传递给cerebro

      - ``runonce`` (default: ``True``)
        矢量化运行：是
        Run ``Indicators`` in vectorized mode to speed up the entire system.
        Strategies and Observers will always be run on an event based basis
        以向量化模式运行’Indicators'指标库以加速整个系统。
        策略和观察者将一直基于事件运行

      - ``live`` (default: ``False``)
        实时模式：否
        If no data has reported itself as *live* (via the data's ``islive``
        method but the end user still want to run in ``live`` mode, this
        parameter can be set to true
        如果没有数据报告为“live”（通过数据的“islive”方法）但最终用户仍希望在“实时”模式下运行，
        这个参数可以设置为true

        This will simultaneously deactivate ``preload`` and ``runonce``. It
        will have no effect on memory saving schemes.
        这将同时停止'preload'和‘runonce’。这对节省内存没有影响（效果？）

        Run ``Indicators`` in vectorized mode to speed up the entire system.
        Strategies and Observers will always be run on an event based basis
        以矢量化模式运行’Indicators'指标库以加速整个系统。
        策略和观察者将一直基于标准运行

      - ``maxcpus`` (default: None -> all available cores)
        最大CPU核心数：默认，所有可用的内核
         How many cores to use simultaneously for optimization
        多少内核并行 优化

      - ``stdstats`` (default: ``True``)
        标准模式
        If True default Observers will be added: Broker (Cash and Value),
        Trades and BuySell
        若为True，默认的观察者将被添加：经纪人、交易、买卖

      - ``oldbuysell`` (default: ``False``)

        If ``stdstats`` is ``True`` and observers are getting automatically
        added, this switch controls the main behavior of the ``BuySell``
        observer
        如果``stdstats``为``True``，并且自动添加观察者，则此开关控制``BuySell``观察者的主要行为

        - ``False``: use the modern behavior in which the buy / sell signals
          are plotted below / above the low / high prices respectively to avoid
          cluttering the plot

        - ``True``: use the deprecated behavior in which the buy / sell signals
          are plotted where the average price of the order executions for the
          given moment in time is. This will of course be on top of an OHLC bar
          or on a Line on Cloe bar, difficulting the recognition of the plot.

      - ``oldtrades`` (default: ``False``)

        If ``stdstats`` is ``True`` and observers are getting automatically
        added, this switch controls the main behavior of the ``Trades``
        observer
        如果’stdstats‘为’True'并且观察者自动获取添加的话，本开关控制‘Trades’观察者的主要行为

        - ``False``: use the modern behavior in which trades for all datas are
          plotted with different markers

        - ``True``: use the old Trades observer which plots the trades with the
          same markers, differentiating only if they are positive or negative

      - ``exactbars`` (default: ``False``)

        With the default value each and every value stored in a line is kept in
        memory

        Possible values:
          - ``True`` or ``1``: all "lines" objects reduce memory usage to the
            automatically calculated minimum period.

            If a Simple Moving Average has a period of 30, the underlying data
            will have always a running buffer of 30 bars to allow the
            calculation of the Simple Moving Average

            - This setting will deactivate ``preload`` and ``runonce``
            - Using this setting also deactivates **plotting**

          - ``-1``: datafreeds and indicators/operations at strategy level will
            keep all data in memory.

            For example: a ``RSI`` internally uses the indicator ``UpDay`` to
            make calculations. This subindicator will not keep all data in
            memory

            - This allows to keep ``plotting`` and ``preloading`` active.

            - ``runonce`` will be deactivated

          - ``-2``: data feeds and indicators kept as attributes of the
            strategy will keep all points in memory.

            For example: a ``RSI`` internally uses the indicator ``UpDay`` to
            make calculations. This subindicator will not keep all data in
            memory

            If in the ``__init__`` something like
            ``a = self.data.close - self.data.high`` is defined, then ``a``
            will not keep all data in memory

            - This allows to keep ``plotting`` and ``preloading`` active.

            - ``runonce`` will be deactivated

      - ``objcache`` (default: ``False``)

        Experimental option to implement a cache of lines objects and reduce
        the amount of them. Example from UltimateOscillator::

          bp = self.data.close - TrueLow(self.data)
          tr = TrueRange(self.data)  # -> creates another TrueLow(self.data)

        If this is ``True`` the 2nd ``TrueLow(self.data)`` inside ``TrueRange``
        matches the signature of the one in the ``bp`` calculation. It will be
        reused.

        Corner cases may happen in which this drives a line object off its
        minimum period and breaks things and it is therefore disabled.

      - ``writer`` (default: ``False``)

        If set to ``True`` a default WriterFile will be created which will
        print to stdout. It will be added to the strategy (in addition to any
        other writers added by the user code)

      - ``tradehistory`` (default: ``False``)

        If set to ``True``, it will activate update event logging in each trade
        for all strategies. This can also be accomplished on a per strategy
        basis with the strategy method ``set_tradehistory``

      - ``optdatas`` (default: ``True``)
        优化数据：是
        If ``True`` and optimizing (and the system can ``preload`` and use
        ``runonce``, data preloading will be done only once in the main process
        to save time and resources.
        若为‘True’ 将优化（系统将预加载且使用矢量化，预加载数据将只运行一次，目的是在主进程中节约时间和资源

        The tests show an approximate ``20%`` speed-up moving from a sample
        execution in ``83`` seconds to ``66``
        测试表明：可以提高20%的性能

      - ``optreturn`` (default: ``True``)
        优化返回结果 <本页定义了Optreturn类>
        If ``True`` the optimization results will not be full ``Strategy``
        objects (and all *datas*, *indicators*, *observers* ...) but and object
        with the following attributes (same as in ``Strategy``):
        若为‘True’，
        优化结果将不是完整的'Strategy‘对象（以及所有的数据 指标 观察者）
        而是具备以下 与’Strategy‘相同属性的对象

          - ``params`` (or ``p``) the strategy had for the execution    执行策略
          - ``analyzers`` the strategy has executed 分析员

        In most occassions, only the *analyzers* and with which *params* are
        the things needed to evaluate a the performance of a strategy. If
        detailed analysis of the generated values for (for example)
        *indicators* is needed, turn this off
        在多数情况下，只有 分析员 和 参数 是评估策略性能所必须的。
        如果需要详细的分析结果（例如 指标），请关闭此项

        The tests show a ``13% - 15%`` improvement in execution time. Combined
        with ``optdatas`` the total gain increases to a total speed-up of
        ``32%`` in an optimization run.
        测试表明，执行时间提升了 13%-15%。与 ’optdatas‘联合使用将有效提升32%的加速

      - ``oldsync`` (default: ``False``)

        Starting with release 1.9.0.99 the synchronization of multiple datas
        (same or different timeframes) has been changed to allow datas of
        different lengths.

        If the old behavior with data0 as the master of the system is wished,
        set this parameter to true

      - ``tz`` (default: ``None``)
      时区：默认使用 世界统一时间

        Adds a global timezone for strategies. The argument ``tz`` can be
        为策略添加全球时区。‘tz’参数可取类型：

          - ``None``: in this case the datetime displayed by strategies will be
            in UTC, which has been always the standard behavior
            ‘None’：策略显式的日期时间将是 世界统一时间 ，这是标配

          - ``pytz`` instance. It will be used as such to convert UTC times to
            the chosen timezone
            ‘pytz’实例。他将世界标准时区转换为所选时区

          - ``string``. Instantiating a ``pytz`` instance will be attempted.
            `string`：尝试实例化‘pytz’实例

          - ``integer``. Use, for the strategy, the same timezone as the
            corresponding ``data`` in the ``self.datas`` iterable (``0`` would
            use the timezone from ``data0``)
            对于策略，使用与self.datas中的data相同的时区

      - ``cheat_on_open`` (default: ``False``)

        The ``next_open`` method of strategies will be called. This happens
        before ``next`` and before the broker has had a chance to evaluate
        orders. The indicators have not yet been recalculated. This allows
        issuing an orde which takes into account the indicators of the previous
        day but uses the ``open`` price for stake calculations

        For cheat_on_open order execution, it is also necessary to make the
        call ``cerebro.broker.set_coo(True)`` or instantite a broker with
        ``BackBroker(coo=True)`` (where *coo* stands for cheat-on-open) or set
        the ``broker_coo`` parameter to ``True``. Cerebro will do it
        automatically unless disabled below.

      - ``broker_coo`` (default: ``True``)

        This will automatically invoke the ``set_coo`` method of the broker
        with ``True`` to activate ``cheat_on_open`` execution. Will only do it
        if ``cheat_on_open`` is also ``True``
        自动调用‘set_coo’方法，为‘True’将激活‘cheat_on_open’执行。

      - ``quicknotify`` (default: ``False``)

        Broker notifications are delivered right before the delivery of the
        *next* prices. For backtesting this has no implications, but with live
        brokers a notification can take place long before the bar is
        delivered. When set to ``True`` notifications will be delivered as soon
        as possible (see ``qcheck`` in live feeds)

        Set to ``False`` for compatibility. May be changed to ``True``

    '''
    # params是在哪里定义的？metabase模块的 MetaParams(MetaBase)：参数类的元类
    # 定义类成员：
    params = (
        ('preload', True),  # 是否把 数据饲料 预加载给 策略 ：是
        ('runonce', True),  # 矢量化运行 ： 是
        ('maxcpus', None),  # 最大核心数 ：默认 所有核心一块干
        ('stdstats', True),  # 标准模式：是
        ('oldbuysell', False),
        ('oldtrades', False),
        ('lookahead', 0),
        ('exactbars', False),
        ('optdatas', True),  # 优化数据
        ('optreturn', True),  # 优化返回结果
        ('objcache', False),
        ('live', False),  # 实时模式：否
        ('writer', False),
        ('tradehistory', False),
        ('oldsync', False),
        ('tz', None),  # 时区 默认使用世界统一时间
        ('cheat_on_open', False),
        ('broker_coo', True),
        ('quicknotify', False),
    )

    # 构造函数
    def __init__(self):
        """初始化函数 类实例初始化（实体，具体的对象）时会给对象（实体）赋初始值 """
        # 以下是实例属性
        self._dolive = False
        self._doreplay = False
        self._dooptimize = False
        self.stores = list()
        self.feeds = list()  # 饲料
        self.datas = list()  # 数据
        self.datasbyname = collections.OrderedDict()
        self.strats = list()  # 策略
        self.optcbs = list()  # holds a list of callbacks for opt strategies 保存 策略的回调列表
        self.observers = list()  # 观察者
        self.analyzers = list()  # 分析员
        self.indicators = list()  # 指标
        self.sizers = dict()
        self.writers = list()
        self.storecbs = list()
        self.datacbs = list()
        self.signals = list()  # 信号
        self._signal_strat = (None, None, None)
        self._signal_concurrent = False
        self._signal_accumulate = False

        self._dataid = itertools.count(1)

        self._broker = BackBroker()  # 私有成员 经纪人
        self._broker.cerebro = self

        self._tradingcal = None  # TradingCalendar()

        self._pretimers = list()
        self._ohistory = list()
        self._fhistory = None

    @staticmethod  # 静态方法 不用实例化就能使用 类名.函数名() 调用 和@classmethod差不多 https://blog.csdn.net/EMIvv/article/details/122482756
    def iterize(iterable):
        '''Handy function which turns things into things that can be iterated upon
        including iterables
        灵活函数，把东西转换为可迭代的，包括iterables
        '''
        niterable = list()  # 定义一个数组
        for elem in iterable:
            if isinstance(elem, string_types):  # 如果 elem 是 字符串类型 （的实例）
                elem = (elem,)  # 转换成元组
            elif not isinstance(elem, collections.Iterable):  # 如果不是 类型
                elem = (elem,)  # 也转换成元组

            niterable.append(elem)  # 末尾追加 元素

        return niterable

    # 只要不是 collections.Iterable 类型 就转换成 元组

    def set_fund_history(self, fund):
        '''
        Add a history of orders to be directly executed in the broker for
        performance evaluation
        在经纪人 中 添加一份 直接执行的历史订单， 以进行绩效评估

          - ``fund``: is an iterable (ex: list, tuple, iterator, generator)
          fund：是可迭代类型（如：数组、元组、迭代器、生成器）
            in which each element will be also an iterable (with length) with
            the following sub-elements (2 formats are possible)
            其中每个元素都是可迭代的（有长度），包含以下子元素（可能有两种格式）

            ``[datetime, share_value, net asset value]``
            [datetime, 价值，净值]

            **Note**: it must be sorted (or produce sorted elements) by
              datetime ascending
            注意：必须按 日期时间 升序排列（或者生成排序的元素）

            where:

              - ``datetime`` is a python ``date/datetime`` instance or a string
                with format YYYY-MM-DD[THH:MM:SS[.us]] where the elements in
                brackets are optional
                ‘datetime’是python的‘date’或'datetime'类型，
                或者 YYYY-MM-DD[THH:MM:SS[.us]] 格式的字符串，括号内的元素是可选的

              - ``share_value`` is an float/integer     浮点数或整数
              - ``net_asset_value`` is a float/integer
        '''
        self._fhistory = fund

    def add_order_history(self, orders, notify=True):
        '''
        Add a history of orders to be directly executed in the broker for
        performance evaluation
        在经纪人 中 添加一份 直接执行的历史订单， 以进行绩效评估

          - ``orders``: is an iterable (ex: list, tuple, iterator, generator)
            in which each element will be also an iterable (with length) with
            the following sub-elements (2 formats are possible)

            ``[datetime, size, price]`` or ``[datetime, size, price, data]``

            **Note**: it must be sorted (or produce sorted elements) by
              datetime ascending

            where:

              - ``datetime`` is a python ``date/datetime`` instance or a string
                with format YYYY-MM-DD[THH:MM:SS[.us]] where the elements in
                brackets are optional
              - ``size`` is an integer (positive to *buy*, negative to *sell*)
              - ``price`` is a float/integer
              - ``data`` if present can take any of the following values

                - *None* - The 1st data feed will be used as target
                - *integer* - The data with that index (insertion order in
                  **Cerebro**) will be used
                - *string* - a data with that name, assigned for example with
                  ``cerebro.addata(data, name=value)``, will be the target

          - ``notify`` (default: *True*)

            If ``True`` the 1st strategy inserted in the system will be
            notified of the artificial orders created following the information
            from each order in ``orders``

        **Note**: Implicit in the description is the need to add a data feed
          which is the target of the orders. This is for example needed by
          analyzers which track for example the returns
        '''
        self._ohistory.append((orders, notify))

    def notify_timer(self, timer, when, *args, **kwargs):
        '''Receives a timer notification where ``timer`` is the timer which was
        returned by ``add_timer``, and ``when`` is the calling time. ``args``
        and ``kwargs`` are any additional arguments passed to ``add_timer``

        The actual ``when`` time can be later, but the system may have not be
        able to call the timer before. This value is the timer value and no the
        system time.
        '''
        pass

    def _add_timer(self, owner, when,
                   offset=datetime.timedelta(), repeat=datetime.timedelta(),
                   weekdays=[], weekcarry=False,
                   monthdays=[], monthcarry=True,
                   allow=None,
                   tzdata=None, strats=False, cheat=False,
                   *args, **kwargs):
        '''Internal method to really create the timer (not started yet) which
        can be called by cerebro instances or other objects which can access
        cerebro'''

        timer = Timer(
            tid=len(self._pretimers),
            owner=owner, strats=strats,
            when=when, offset=offset, repeat=repeat,
            weekdays=weekdays, weekcarry=weekcarry,
            monthdays=monthdays, monthcarry=monthcarry,
            allow=allow,
            tzdata=tzdata, cheat=cheat,
            *args, **kwargs
        )

        self._pretimers.append(timer)
        return timer

    def add_timer(self, when,
                  offset=datetime.timedelta(), repeat=datetime.timedelta(),
                  weekdays=[], weekcarry=False,
                  monthdays=[], monthcarry=True,
                  allow=None,
                  tzdata=None, strats=False, cheat=False,
                  *args, **kwargs):
        '''
        Schedules a timer to invoke ``notify_timer``

        Arguments:

          - ``when``: can be

            - ``datetime.time`` instance (see below ``tzdata``)
            - ``bt.timer.SESSION_START`` to reference a session start
            - ``bt.timer.SESSION_END`` to reference a session end

         - ``offset`` which must be a ``datetime.timedelta`` instance

           Used to offset the value ``when``. It has a meaningful use in
           combination with ``SESSION_START`` and ``SESSION_END``, to indicated
           things like a timer being called ``15 minutes`` after the session
           start.

          - ``repeat`` which must be a ``datetime.timedelta`` instance

            Indicates if after a 1st call, further calls will be scheduled
            within the same session at the scheduled ``repeat`` delta

            Once the timer goes over the end of the session it is reset to the
            original value for ``when``

          - ``weekdays``: a **sorted** iterable with integers indicating on
            which days (iso codes, Monday is 1, Sunday is 7) the timers can
            be actually invoked

            If not specified, the timer will be active on all days

          - ``weekcarry`` (default: ``False``). If ``True`` and the weekday was
            not seen (ex: trading holiday), the timer will be executed on the
            next day (even if in a new week)

          - ``monthdays``: a **sorted** iterable with integers indicating on
            which days of the month a timer has to be executed. For example
            always on day *15* of the month

            If not specified, the timer will be active on all days

          - ``monthcarry`` (default: ``True``). If the day was not seen
            (weekend, trading holiday), the timer will be executed on the next
            available day.

          - ``allow`` (default: ``None``). A callback which receives a
            `datetime.date`` instance and returns ``True`` if the date is
            allowed for timers or else returns ``False``

          - ``tzdata`` which can be either ``None`` (default), a ``pytz``
            instance or a ``data feed`` instance.

            ``None``: ``when`` is interpreted at face value (which translates
            to handling it as if it where UTC even if it's not)

            ``pytz`` instance: ``when`` will be interpreted as being specified
            in the local time specified by the timezone instance.

            ``data feed`` instance: ``when`` will be interpreted as being
            specified in the local time specified by the ``tz`` parameter of
            the data feed instance.

            **Note**: If ``when`` is either ``SESSION_START`` or
              ``SESSION_END`` and ``tzdata`` is ``None``, the 1st *data feed*
              in the system (aka ``self.data0``) will be used as the reference
              to find out the session times.

          - ``strats`` (default: ``False``) call also the ``notify_timer`` of
            strategies

          - ``cheat`` (default ``False``) if ``True`` the timer will be called
            before the broker has a chance to evaluate the orders. This opens
            the chance to issue orders based on opening price for example right
            before the session starts
          - ``*args``: any extra args will be passed to ``notify_timer``

          - ``**kwargs``: any extra kwargs will be passed to ``notify_timer``

        Return Value:

          - The created timer

        '''
        return self._add_timer(
            owner=self, when=when, offset=offset, repeat=repeat,
            weekdays=weekdays, weekcarry=weekcarry,
            monthdays=monthdays, monthcarry=monthcarry,
            allow=allow,
            tzdata=tzdata, strats=strats, cheat=cheat,
            *args, **kwargs)

    def addtz(self, tz):
        '''
        This can also be done with the parameter ``tz``
        添加时区，本操作也可以在 param 里设置
        Adds a global timezone for strategies. The argument ``tz`` can be

          - ``None``: in this case the datetime displayed by strategies will be
            in UTC, which has been always the standard behavior

          - ``pytz`` instance. It will be used as such to convert UTC times to
            the chosen timezone

          - ``string``. Instantiating a ``pytz`` instance will be attempted.

          - ``integer``. Use, for the strategy, the same timezone as the
            corresponding ``data`` in the ``self.datas`` iterable (``0`` would
            use the timezone from ``data0``)

        '''
        self.p.tz = tz

    def addcalendar(self, cal):
        '''Adds a global trading calendar to the system. Individual data feeds
        may have separate calendars which override the global one
        给系统添加全球交易日历。
        个别的 数据饲料 可以具有覆盖全球日历的 单独日历

        ``cal`` can be an instance of ``TradingCalendar`` a string or an
        instance of ``pandas_market_calendars``. A string will be will be
        instantiated as a ``PandasMarketCalendar`` (which needs the module
        ``pandas_market_calendar`` installed in the system.

        If a subclass of `TradingCalendarBase` is passed (not an instance) it
        will be instantiated
        '''
        if isinstance(cal, string_types):
            cal = PandasMarketCalendar(calendar=cal)
        elif hasattr(cal, 'valid_days'):
            cal = PandasMarketCalendar(calendar=cal)

        else:
            try:
                if issubclass(cal, TradingCalendarBase):
                    cal = cal()
            except TypeError:  # already an instance
                pass

        self._tradingcal = cal

    def add_signal(self, sigtype, sigcls, *sigargs, **sigkwargs):
        '''Adds a signal to the system which will be later added to a
        ``SignalStrategy``
        给系统添加 signal信号，此信号将被添加给 信号策略 ‘SignalStrategy’
        '''
        self.signals.append((sigtype, sigcls, sigargs, sigkwargs))

    def signal_strategy(self, stratcls, *args, **kwargs):
        '''Adds a SignalStrategy subclass which can accept signals
        添加可以接受信号的 信号策略子类'''
        self._signal_strat = (stratcls, args, kwargs)

    def signal_concurrent(self, onoff):
        '''If signals are added to the system and the ``concurrent`` value is
        set to True, concurrent orders will be allowed'''
        self._signal_concurrent = onoff

    def signal_accumulate(self, onoff):
        '''If signals are added to the system and the ``accumulate`` value is
        set to True, entering the market when already in the market, will be
        allowed to increase a position'''
        self._signal_accumulate = onoff

    def addstore(self, store):
        '''Adds an ``Store`` instance to the if not already present
        添加一个 目前还不存在的 ‘Store’实例
        '''
        if store not in self.stores:  # 如果stores里没有store
            self.stores.append(store)  # stores追加store（整体） extend是（打碎）追加元素

    def addwriter(self, wrtcls, *args, **kwargs):
        '''Adds an ``Writer`` class to the mix. Instantiation will be done at
        ``run`` time in cerebro
        添加 ‘Writer’类，将在cerebro的run运行的时候 实例化
        '''
        self.writers.append((wrtcls, args, kwargs))

    def addsizer(self, sizercls, *args, **kwargs):
        '''Adds a ``Sizer`` class (and args) which is the default sizer for any
        strategy added to cerebro
        添加到大脑的任何策略的默认 大小计算器
        '''
        self.sizers[None] = (sizercls, args, kwargs)

    def addsizer_byidx(self, idx, sizercls, *args, **kwargs):
        '''Adds a ``Sizer`` class by idx. This idx is a reference compatible to
        the one returned by ``addstrategy``. Only the strategy referenced by
        ``idx`` will receive this size
        '''
        self.sizers[idx] = (sizercls, args, kwargs)

    def addindicator(self, indcls, *args, **kwargs):
        '''
        Adds an ``Indicator`` class to the mix. Instantiation will be done at
        ``run`` time in the passed strategies
        添加指标类。实例化将在添加策略后执行run的时候进行
        '''
        self.indicators.append((indcls, args, kwargs))

    def addanalyzer(self, ancls, *args, **kwargs):
        '''
        Adds an ``Analyzer`` class to the mix. Instantiation will be done at
        ``run`` time
        '''
        self.analyzers.append((ancls, args, kwargs))

    def addobserver(self, obscls, *args, **kwargs):
        '''
        Adds an ``Observer`` class to the mix. Instantiation will be done at
        ``run`` time
        添加‘Observer’类，run的时候进行实例化
        '''
        self.observers.append((False, obscls, args, kwargs))

    def addobservermulti(self, obscls, *args, **kwargs):
        '''
        Adds an ``Observer`` class to the mix. Instantiation will be done at
        ``run`` time

        It will be added once per "data" in the system. A use case is a
        buy/sell observer which observes individual datas.

        A counter-example is the CashValue, which observes system-wide values
        '''
        self.observers.append((True, obscls, args, kwargs))

    def addstorecb(self, callback):
        '''Adds a callback to get messages which would be handled by the
        notify_store method

        The signature of the callback must support the following:

          - callback(msg, \*args, \*\*kwargs)

        The actual ``msg``, ``*args`` and ``**kwargs`` received are
        implementation defined (depend entirely on the *data/broker/store*) but
        in general one should expect them to be *printable* to allow for
        reception and experimentation.
        '''
        self.storecbs.append(callback)

    def _notify_store(self, msg, *args, **kwargs):
        for callback in self.storecbs:
            callback(msg, *args, **kwargs)

        self.notify_store(msg, *args, **kwargs)

    def notify_store(self, msg, *args, **kwargs):
        '''Receive store notifications in cerebro
        接收、储存 通知

        This method can be overridden in ``Cerebro`` subclasses
        此方法可以在‘Cerebro’类中被重写

        The actual ``msg``, ``*args`` and ``**kwargs`` received are
        implementation defined (depend entirely on the *data/broker/store*) but
        in general one should expect them to be *printable* to allow for
        reception and experimentation.
        实际收到的``msg``、``*args``和``*kwargs``是被定义的工具（完全取决于*data/broker/store*），
        但一般来说，人们应该期望它们是可打印的，以便接收和实验。
        '''
        pass

    def _storenotify(self):
        for store in self.stores:
            for notif in store.get_notifications():
                msg, args, kwargs = notif

                self._notify_store(msg, *args, **kwargs)
                for strat in self.runningstrats:
                    strat.notify_store(msg, *args, **kwargs)

    def adddatacb(self, callback):
        '''Adds a callback to get messages which would be handled by the
        notify_data method

        The signature of the callback must support the following:

          - callback(data, status, \*args, \*\*kwargs)

        The actual ``*args`` and ``**kwargs`` received are implementation
        defined (depend entirely on the *data/broker/store*) but in general one
        should expect them to be *printable* to allow for reception and
        experimentation.
        '''
        self.datacbs.append(callback)

    def _datanotify(self):
        for data in self.datas:
            for notif in data.get_notifications():
                status, args, kwargs = notif
                self._notify_data(data, status, *args, **kwargs)
                for strat in self.runningstrats:
                    strat.notify_data(data, status, *args, **kwargs)

    def _notify_data(self, data, status, *args, **kwargs):
        for callback in self.datacbs:
            callback(data, status, *args, **kwargs)

        self.notify_data(data, status, *args, **kwargs)

    def notify_data(self, data, status, *args, **kwargs):
        '''Receive data notifications in cerebro

        This method can be overridden in ``Cerebro`` subclasses

        The actual ``*args`` and ``**kwargs`` received are
        implementation defined (depend entirely on the *data/broker/store*) but
        in general one should expect them to be *printable* to allow for
        reception and experimentation.
        '''
        pass

    def adddata(self, data, name=None):
        '''
        Adds a ``Data Feed`` instance to the mix.
        添加一个数据饲料类的 实例 到组合中，名字默认为空

        If ``name`` is not None it will be put into ``data._name`` which is
        meant for decoration/plotting purposes.
        如果‘name’非空，他将被赋值给‘data._name’，装饰在绘图画面上。

        # 函数体 ：
        next（迭代器[，默认值]）
        从迭代器返回下一项。如果给定默认值，并且迭代器已用完，则返回它，而不引发StopIteration。
        '''
        # 给‘数据饲料’（类的实例）命名
        if name is not None:
            data._name = name

        data._id = next(self._dataid)
        data.setenvironment(self)

        # cerebro的数据表列表里追加一个数据 并能通过名字调用
        self.datas.append(data)  # 类实例的datas属性添加data元素
        self.datasbyname[data._name] = data

        # 饲料里添加一个饲料？
        # data是实例，是数据饲料类的实例
        feed = data.getfeed()  # 把抽象基类里的feed赋值给cerebro的feed
        if feed and feed not in self.feeds:
            self.feeds.append(feed)

        if data.islive():
            self._dolive = True

        return data

    def chaindata(self, *args, **kwargs):
        '''
        Chains several data feeds into one

        If ``name`` is passed as named argument and is not None it will be put
        into ``data._name`` which is meant for decoration/plotting purposes.

        If ``None``, then the name of the 1st data will be used
        '''
        dname = kwargs.pop('name', None)
        if dname is None:
            dname = args[0]._dataname
        d = bt.feeds.Chainer(dataname=dname, *args)
        self.adddata(d, name=dname)

        return d

    def rolloverdata(self, *args, **kwargs):
        '''Chains several data feeds into one

        If ``name`` is passed as named argument and is not None it will be put
        into ``data._name`` which is meant for decoration/plotting purposes.

        If ``None``, then the name of the 1st data will be used

        Any other kwargs will be passed to the RollOver class

        '''
        dname = kwargs.pop('name', None)
        if dname is None:
            dname = args[0]._dataname
        d = bt.feeds.RollOver(dataname=dname, *args, **kwargs)
        self.adddata(d, name=dname)

        return d

    def replaydata(self, dataname, name=None, **kwargs):
        '''
        Adds a ``Data Feed`` to be replayed by the system

        If ``name`` is not None it will be put into ``data._name`` which is
        meant for decoration/plotting purposes.

        Any other kwargs like ``timeframe``, ``compression``, ``todate`` which
        are supported by the replay filter will be passed transparently
        '''
        if any(dataname is x for x in self.datas):
            dataname = dataname.clone()

        dataname.replay(**kwargs)
        self.adddata(dataname, name=name)
        self._doreplay = True

        return dataname

    def resampledata(self, dataname, name=None, **kwargs):
        '''
        Adds a ``Data Feed`` to be resample by the system

        If ``name`` is not None it will be put into ``data._name`` which is
        meant for decoration/plotting purposes.

        Any other kwargs like ``timeframe``, ``compression``, ``todate`` which
        are supported by the resample filter will be passed transparently
        '''
        if any(dataname is x for x in self.datas):
            dataname = dataname.clone()

        dataname.resample(**kwargs)
        self.adddata(dataname, name=name)
        self._doreplay = True

        return dataname

    def optcallback(self, cb):
        '''
        Adds a *callback* to the list of callbacks that will be called with the
        optimizations when each of the strategies has been run

        The signature: cb(strategy)
        '''
        self.optcbs.append(cb)

    def optstrategy(self, strategy, *args, **kwargs):
        '''
        Adds a ``Strategy`` class to the mix for optimization. Instantiation
        will happen during ``run`` time.

        args and kwargs MUST BE iterables which hold the values to check.

        Example: if a Strategy accepts a parameter ``period``, for optimization
        purposes the call to ``optstrategy`` looks like:

          - cerebro.optstrategy(MyStrategy, period=(15, 25))

        This will execute an optimization for values 15 and 25. Whereas

          - cerebro.optstrategy(MyStrategy, period=range(15, 25))

        will execute MyStrategy with ``period`` values 15 -> 25 (25 not
        included, because ranges are semi-open in Python)

        If a parameter is passed but shall not be optimized the call looks
        like:

          - cerebro.optstrategy(MyStrategy, period=(15,))

        Notice that ``period`` is still passed as an iterable ... of just 1
        element

        ``backtrader`` will anyhow try to identify situations like:

          - cerebro.optstrategy(MyStrategy, period=15)

        and will create an internal pseudo-iterable if possible
        '''
        self._dooptimize = True
        args = self.iterize(args)
        optargs = itertools.product(*args)

        optkeys = list(kwargs)

        vals = self.iterize(kwargs.values())
        optvals = itertools.product(*vals)

        okwargs1 = map(zip, itertools.repeat(optkeys), optvals)

        optkwargs = map(dict, okwargs1)

        it = itertools.product([strategy], optargs, optkwargs)
        self.strats.append(it)

    def addstrategy(self, strategy, *args, **kwargs):
        '''
        Adds a ``Strategy`` class to the mix for a single pass run.
        Instantiation will happen during ``run`` time.
        添加一个 策略类。
        实例化将在 run执行时进行

        args and kwargs will be passed to the strategy as they are during
        instantiation.
        在实例化期间，args和kwargs将被传递给策略

        Returns the index with which addition of other objects (like sizers)
        can be referenced
        返回可以添加其他对象的索引
        '''
        self.strats.append([(strategy, args, kwargs)])
        return len(self.strats) - 1

    def setbroker(self, broker):
        '''
        Sets a specific ``broker`` instance for this strategy, replacing the
        one inherited from cerebro.
        为该策略设置一个特定的‘broker’实例，替代从cerebor继承的那个
        '''
        self._broker = broker
        broker.cerebro = self
        return broker

    def getbroker(self):
        '''
        Returns the broker instance.
        返回broker实例
        This is also available as a ``property`` by the name ``broker``
        '''
        return self._broker

    broker = property(getbroker, setbroker)

    def plot(self, plotter=None, numfigs=1, iplot=True, start=None, end=None,
             width=16, height=9, dpi=300, tight=True, use=None,
             **kwargs):
        '''
        Plots the strategies inside cerebro
        绘制策略

        If ``plotter`` is None a default ``Plot`` instance is created and
        ``kwargs`` are passed to it during instantiation.

        ``numfigs`` split the plot in the indicated number of charts reducing
        chart density if wished

        ``iplot``: if ``True`` and running in a ``notebook`` the charts will be
        displayed inline

        ``use``: set it to the name of the desired matplotlib backend. It will
        take precedence over ``iplot``

        ``start``: An index to the datetime line array of the strategy or a
        ``datetime.date``, ``datetime.datetime`` instance indicating the start
        of the plot

        ``end``: An index to the datetime line array of the strategy or a
        ``datetime.date``, ``datetime.datetime`` instance indicating the end
        of the plot

        ``width``: in inches of the saved figure

        ``height``: in inches of the saved figure

        ``dpi``: quality in dots per inches of the saved figure

        ``tight``: only save actual content and not the frame of the figure
        '''
        if self._exactbars > 0:
            return

        if not plotter:
            from . import plot
            if self.p.oldsync:
                plotter = plot.Plot_OldSync(**kwargs)
            else:
                plotter = plot.Plot(**kwargs)

        # pfillers = {self.datas[i]: self._plotfillers[i]
        # for i, x in enumerate(self._plotfillers)}

        # pfillers2 = {self.datas[i]: self._plotfillers2[i]
        # for i, x in enumerate(self._plotfillers2)}

        figs = []
        for stratlist in self.runstrats:
            for si, strat in enumerate(stratlist):
                rfig = plotter.plot(strat, figid=si * 100,
                                    numfigs=numfigs, iplot=iplot,
                                    start=start, end=end, use=use)
                # pfillers=pfillers2)

                figs.append(rfig)

            plotter.show()

        return figs

    def __call__(self, iterstrat):
        '''
        Used during optimization to pass the cerebro over the multiprocesing
        module without complains
        用于：在无损情况下优化使用多处理模块
        '''

        predata = self.p.optdatas and self._dopreload and self._dorunonce
        return self.runstrategies(iterstrat, predata=predata)

    def __getstate__(self):
        '''
        Used during optimization to prevent optimization result `runstrats`
        from being pickled to subprocesses
        用于：在优化期间防止优化结果“runstrats”被子流程拾取
        '''

        rv = vars(self).copy()
        if 'runstrats' in rv:
            del (rv['runstrats'])
        return rv

    def runstop(self):
        """If invoked from inside a strategy or anywhere else, including other
        threads the execution will stop as soon as possible.
        如果被调用，无论是策略内部还是其他任何地方，包括 所有执行的线程 将立即结束"""
        self._event_stop = True  # signal a stop has been requested

    def run(self, **kwargs):
        '''The core method to perform backtesting. Any ``kwargs`` passed to it
        will affect the value of the standard parameters ``Cerebro`` was
        instantiated with.
        执行回测的核心方法：
        所有传递进来的参数都会影响到Cerebro的实例的执行结果

        If ``cerebro`` has not datas the method will immediately bail out.
        如果 cerebro无数据，本方法将立刻退出

        It has different return values:
        不同的返回结果：

          - For No Optimization: a list contanining instances of the Strategy
            classes added with ``addstrategy``
            无优化：包含通过addstrategy添加进来的策略类实例 的列表

          - For Optimization: a list of lists which contain instances of the
            Strategy classes added with ``addstrategy``
            优化：一个 包含通过addstrategy添加进来的策略类实例 的列表 的列表
        '''
        self._event_stop = False  # Stop is requested

        # 如果没有数据则返回空列表
        if not self.datas:
            return []  # nothing can be run

        # 第一步 设置参数属性值
        pkeys = self.params._getkeys()
        for key, val in kwargs.items():
            if key in pkeys:
                setattr(self.params, key, val)

        # Manage activate/deactivate object cache
        # 缓存管理 管理激活的和停用的对象缓存
        linebuffer.LineActions.cleancache()  # clean cache      # MetaLineActions类
        indicator.Indicator.cleancache()  # clean cache

        linebuffer.LineActions.usecache(self.p.objcache)
        indicator.Indicator.usecache(self.p.objcache)

        self._dorunonce = self.p.runonce  # 矢量化
        self._dopreload = self.p.preload  # 预加载
        self._exactbars = int(self.p.exactbars)  # 正在执行的当前bar

        if self._exactbars:
            self._dorunonce = False  # something is saving memory, no runonce
            self._dopreload = self._dopreload and self._exactbars < 1

        self._doreplay = self._doreplay or any(x.replaying for x in self.datas)
        if self._doreplay:
            # preloading is not supported with replay. full timeframe bars
            # are constructed in realtime
            self._dopreload = False

        if self._dolive or self.p.live:
            # in this case both preload and runonce must be off
            self._dorunonce = False
            self._dopreload = False

        self.runwriters = list()

        # Add the system default writer if requested
        # 设置一个默认的记录员
        if self.p.writer is True:
            wr = WriterFile()
            self.runwriters.append(wr)

        # Instantiate any other writers
        # 实例化其他记录员
        for wrcls, wrargs, wrkwargs in self.writers:
            wr = wrcls(*wrargs, **wrkwargs)
            self.runwriters.append(wr)

        # Write down if any writer wants the full csv output
        # csv记下所有记录
        self.writers_csv = any(map(lambda x: x.p.csv, self.runwriters))

        self.runstrats = list()

        if self.signals:  # allow processing of signals 允许处理信号
            signalst, sargs, skwargs = self._signal_strat
            if signalst is None:
                # Try to see if the 1st regular strategy is a signal strategy
                try:
                    signalst, sargs, skwargs = self.strats.pop(0)
                except IndexError:
                    pass  # Nothing there
                else:
                    if not isinstance(signalst, SignalStrategy):
                        # no signal ... reinsert at the beginning
                        self.strats.insert(0, (signalst, sargs, skwargs))
                        signalst = None  # flag as not presetn

            if signalst is None:  # recheck
                # Still None, create a default one
                signalst, sargs, skwargs = SignalStrategy, tuple(), dict()

            # Add the signal strategy
            self.addstrategy(signalst,
                             _accumulate=self._signal_accumulate,
                             _concurrent=self._signal_concurrent,
                             signals=self.signals,
                             *sargs,
                             **skwargs)

        # 添加策略
        if not self.strats:  # Datas are present, add a strategy
            self.addstrategy(Strategy)
        # 第二步 调用 实例化策略 函数
        iterstrats = itertools.product(*self.strats)  # 组合式迭代器 策略迭代器
        if not self._dooptimize or self.p.maxcpus == 1:
            # If no optimmization is wished ... or 1 core is to be used
            # let's skip process "spawning"
            # 如果不希望优化 或者 使用单核心计算机，就跳过多进程
            for iterstrat in iterstrats:
                runstrat = self.runstrategies(iterstrat)
                self.runstrats.append(runstrat)
                if self._dooptimize:
                    for cb in self.optcbs:
                        cb(runstrat)  # callback receives finished strategy
        else:
            # 如果优化、预加载、矢量化
            if self.p.optdatas and self._dopreload and self._dorunonce:
                """ # 循环提取数据 """
                for data in self.datas:
                    data.reset()
                    if self._exactbars < 1:  # datas can be full length
                        data.extend(size=self.params.lookahead)

                    # print("data._start()在这里准备调用CSVDataBase类方法_start()")
                    data._start()  # 在这里调用了CSVDataBase类方法_start()
                    if self._dopreload:
                        data.preload()

            # 多进程 干嘛这是
            # pool.imap()一旦生成就会开始，返回迭代器格式，缓存在内存里
            print("多进程 干嘛这是")
            pool = multiprocessing.Pool(self.p.maxcpus or None)  # maxcpus进程数
            for r in pool.imap(self, iterstrats):
                self.runstrats.append(r)
                for cb in self.optcbs:
                    cb(r)  # callback receives finished strategy 回调接收到的已完成策略
                    # 回调就是个指针，指针就是地址

            pool.close()  # 必须关闭

            if self.p.optdatas and self._dopreload and self._dorunonce:
                for data in self.datas:
                    data.stop()

        if not self._dooptimize:
            # avoid a list of list for regular cases    # 避免
            return self.runstrats[0]

        return self.runstrats

    def _init_stcount(self):
        self.stcount = itertools.count(0)

    def _next_stid(self):
        return next(self.stcount)

    def runstrategies(self, iterstrat, predata=False):
        print("runstrategies")
        '''
        Internal method invoked by ``run``` to run a set of strategies
        通过run()调用的内部方法：执行策略
        '''
        self._init_stcount()

        # store feed broker启动start方法，broker设置相关history

        self.runningstrats = runstrats = list()
        for store in self.stores:
            store.start()

        if self.p.cheat_on_open and self.p.broker_coo:
            # try to activate in broker
            if hasattr(self._broker, 'set_coo'):
                self._broker.set_coo(True)

        if self._fhistory is not None:
            self._broker.set_fund_history(self._fhistory)

        for orders, onotify in self._ohistory:
            self._broker.add_order_history(orders, onotify)

        self._broker.start()

        for feed in self.feeds:
            feed.start()

        if self.writers_csv:
            wheaders = list()
            for data in self.datas:
                if data.csv:
                    wheaders.extend(data.getwriterheaders())

            for writer in self.runwriters:
                if writer.p.csv:
                    writer.addheaders(wheaders)

        # self._plotfillers = [list() for d in self.datas]
        # self._plotfillers2 = [list() for d in self.datas]

        # data视情况进行重置 重启 预加载数据

        if not predata:
            for data in self.datas:
                data.reset()
                if self._exactbars < 1:  # datas can be full length
                    data.extend(size=self.params.lookahead)
                data._start()
                if self._dopreload:
                    data.preload()

        # 将datas作为参数实例化策略 并设置相关属性 包括tz qbuffer
        for stratcls, sargs, skwargs in iterstrat:
            sargs = self.datas + list(sargs)
            try:
                strat = stratcls(*sargs, **skwargs)
            except bt.errors.StrategySkipError:
                continue  # do not add strategy to the mix

            if self.p.oldsync:
                strat._oldsync = True  # tell strategy to use old clock update
            if self.p.tradehistory:
                strat.set_tradehistory()
            runstrats.append(strat)

        tz = self.p.tz
        if isinstance(tz, integer_types):
            tz = self.datas[tz]._tz
        else:
            tz = tzparse(tz)

        # 给策略添加其他角色 observer indicator analyzer sizer writer

        if runstrats:
            # loop separated for clarity
            defaultsizer = self.sizers.get(None, (None, None, None))
            for idx, strat in enumerate(runstrats):
                if self.p.stdstats:
                    strat._addobserver(False, observers.Broker)
                    if self.p.oldbuysell:
                        strat._addobserver(True, observers.BuySell)
                    else:
                        strat._addobserver(True, observers.BuySell,
                                           barplot=True)

                    if self.p.oldtrades or len(self.datas) == 1:
                        strat._addobserver(False, observers.Trades)
                    else:
                        strat._addobserver(False, observers.DataTrades)

                for multi, obscls, obsargs, obskwargs in self.observers:
                    strat._addobserver(multi, obscls, *obsargs, **obskwargs)

                for indcls, indargs, indkwargs in self.indicators:
                    strat._addindicator(indcls, *indargs, **indkwargs)

                for ancls, anargs, ankwargs in self.analyzers:
                    strat._addanalyzer(ancls, *anargs, **ankwargs)

                sizer, sargs, skwargs = self.sizers.get(idx, defaultsizer)
                if sizer is not None:
                    strat._addsizer(sizer, *sargs, **skwargs)

                strat._settz(tz)

                # 策略启动
                strat._start()

                # 如果写入csv，日志器写入策略表头
                for writer in self.runwriters:
                    if writer.p.csv:
                        writer.addheaders(strat.getwriterheaders())

            if not predata:
                for strat in runstrats:
                    strat.qbuffer(self._exactbars, replaying=self._doreplay)

            # 启动日志器
            for writer in self.runwriters:
                writer.start()

            # 用data[0]启动timer并添加至相关的cerebro._timers
            # Prepare timers
            self._timers = []
            self._timerscheat = []
            for timer in self._pretimers:
                # preprocess tzdata if needed
                timer.start(self.datas[0])

                if timer.params.cheat:
                    self._timerscheat.append(timer)
                else:
                    self._timers.append(timer)

            # 进一步进入策略逻辑 _runnext(runstrats)
            if self._dopreload and self._dorunonce:
                if self.p.oldsync:
                    self._runonce_old(runstrats)
                else:
                    self._runonce(runstrats)
            else:
                if self.p.oldsync:
                    self._runnext_old(runstrats)
                else:
                    self._runnext(runstrats)

            for strat in runstrats:
                strat._stop()

        self._broker.stop()

        if not predata:
            for data in self.datas:
                data.stop()

        for feed in self.feeds:
            feed.stop()

        for store in self.stores:
            store.stop()

        self.stop_writers(runstrats)

        # 如果是优化模型 封装参数信息及analyzer信息并返回
        if self._dooptimize and self.p.optreturn:
            # Results can be optimized
            results = list()
            for strat in runstrats:
                for a in strat.analyzers:
                    a.strategy = None
                    a._parent = None
                    for attrname in dir(a):
                        if attrname.startswith('data'):
                            setattr(a, attrname, None)

                oreturn = OptReturn(strat.params, analyzers=strat.analyzers, strategycls=type(strat))
                results.append(oreturn)

            return results

        return runstrats

    def stop_writers(self, runstrats):
        cerebroinfo = OrderedDict()
        datainfos = OrderedDict()

        for i, data in enumerate(self.datas):
            datainfos['Data%d' % i] = data.getwriterinfo()

        cerebroinfo['Datas'] = datainfos

        stratinfos = dict()
        for strat in runstrats:
            stname = strat.__class__.__name__
            stratinfos[stname] = strat.getwriterinfo()

        cerebroinfo['Strategies'] = stratinfos

        for writer in self.runwriters:
            writer.writedict(dict(Cerebro=cerebroinfo))
            writer.stop()

    def _brokernotify(self):
        '''
        Internal method which kicks the broker and delivers any broker
        notification to the strategy
        '''
        self._broker.next()
        while True:
            order = self._broker.get_notification()
            if order is None:
                break

            owner = order.owner
            if owner is None:
                owner = self.runningstrats[0]  # default

            owner._addnotification(order, quicknotify=self.p.quicknotify)

    def _runnext_old(self, runstrats):
        '''
        Actual implementation of run in full next mode. All objects have its
        ``next`` method invoke on each data arrival
        '''
        data0 = self.datas[0]
        d0ret = True
        while d0ret or d0ret is None:
            lastret = False
            # Notify anything from the store even before moving datas
            # because datas may not move due to an error reported by the store
            self._storenotify()
            if self._event_stop:  # stop if requested
                return
            self._datanotify()
            if self._event_stop:  # stop if requested
                return

            d0ret = data0.next()
            if d0ret:
                for data in self.datas[1:]:
                    if not data.next(datamaster=data0):  # no delivery
                        data._check(forcedata=data0)  # check forcing output
                        data.next(datamaster=data0)  # retry

            elif d0ret is None:
                # meant for things like live feeds which may not produce a bar
                # at the moment but need the loop to run for notifications and
                # getting resample and others to produce timely bars
                data0._check()
                for data in self.datas[1:]:
                    data._check()
            else:
                lastret = data0._last()
                for data in self.datas[1:]:
                    lastret += data._last(datamaster=data0)

                if not lastret:
                    # Only go extra round if something was changed by "lasts"
                    break

            # Datas may have generated a new notification after next
            self._datanotify()
            if self._event_stop:  # stop if requested
                return

            self._brokernotify()
            if self._event_stop:  # stop if requested
                return

            if d0ret or lastret:  # bars produced by data or filters
                for strat in runstrats:
                    strat._next()
                    if self._event_stop:  # stop if requested
                        return

                    self._next_writers(runstrats)

        # Last notification chance before stopping
        self._datanotify()
        if self._event_stop:  # stop if requested
            return
        self._storenotify()
        if self._event_stop:  # stop if requested
            return

    def _runonce_old(self, runstrats):
        '''
        Actual implementation of run in vector mode.
        Strategies are still invoked on a pseudo-event mode in which ``next``
        is called for each data arrival
        '''
        for strat in runstrats:
            strat._once()

        # The default once for strategies does nothing and therefore
        # has not moved forward all datas/indicators/observers that
        # were homed before calling once, Hence no "need" to do it
        # here again, because pointers are at 0
        data0 = self.datas[0]
        datas = self.datas[1:]
        for i in range(data0.buflen()):
            data0.advance()
            for data in datas:
                data.advance(datamaster=data0)

            self._brokernotify()
            if self._event_stop:  # stop if requested
                return

            for strat in runstrats:
                # data0.datetime[0] for compat. w/ new strategy's oncepost
                strat._oncepost(data0.datetime[0])
                if self._event_stop:  # stop if requested
                    return

                self._next_writers(runstrats)

    def _next_writers(self, runstrats):
        if not self.runwriters:
            return

        if self.writers_csv:
            wvalues = list()
            for data in self.datas:
                if data.csv:
                    wvalues.extend(data.getwritervalues())

            for strat in runstrats:
                wvalues.extend(strat.getwritervalues())

            for writer in self.runwriters:
                if writer.p.csv:
                    writer.addvalues(wvalues)

                    writer.next()

    def _disable_runonce(self):
        '''API for lineiterators to disable runonce (see HeikinAshi)'''
        self._dorunonce = False

    def _runnext(self, runstrats):
        '''
        Actual implementation of run in full next mode. All objects have its
        ``next`` method invoke on each data arrival
        '''
        datas = sorted(self.datas,
                       key=lambda x: (x._timeframe, x._compression))
        datas1 = datas[1:]
        data0 = datas[0]
        d0ret = True

        rs = [i for i, x in enumerate(datas) if x.resampling]
        rp = [i for i, x in enumerate(datas) if x.replaying]
        rsonly = [i for i, x in enumerate(datas)
                  if x.resampling and not x.replaying]
        onlyresample = len(datas) == len(rsonly)
        noresample = not rsonly

        clonecount = sum(d._clone for d in datas)
        ldatas = len(datas)
        ldatas_noclones = ldatas - clonecount
        lastqcheck = False
        dt0 = date2num(datetime.datetime.max) - 2  # default at max
        while d0ret or d0ret is None:
            # if any has live data in the buffer, no data will wait anything
            newqcheck = not any(d.haslivedata() for d in datas)
            if not newqcheck:
                # If no data has reached the live status or all, wait for
                # the next incoming data
                livecount = sum(d._laststatus == d.LIVE for d in datas)
                newqcheck = not livecount or livecount == ldatas_noclones

            lastret = False
            # Notify anything from the store even before moving datas
            # because datas may not move due to an error reported by the store
            self._storenotify()
            if self._event_stop:  # stop if requested
                return
            self._datanotify()
            if self._event_stop:  # stop if requested
                return

            # record starting time and tell feeds to discount the elapsed time
            # from the qcheck value
            drets = []
            qstart = datetime.datetime.utcnow()
            for d in datas:
                qlapse = datetime.datetime.utcnow() - qstart
                d.do_qcheck(newqcheck, qlapse.total_seconds())
                drets.append(d.next(ticks=False))

            d0ret = any((dret for dret in drets))
            if not d0ret and any((dret is None for dret in drets)):
                d0ret = None

            if d0ret:
                dts = []
                for i, ret in enumerate(drets):
                    dts.append(datas[i].datetime[0] if ret else None)

                # Get index to minimum datetime
                if onlyresample or noresample:
                    dt0 = min((d for d in dts if d is not None))
                else:
                    dt0 = min((d for i, d in enumerate(dts)
                               if d is not None and i not in rsonly))

                dmaster = datas[dts.index(dt0)]  # and timemaster
                self._dtmaster = dmaster.num2date(dt0)
                self._udtmaster = num2date(dt0)

                # slen = len(runstrats[0])
                # Try to get something for those that didn't return
                for i, ret in enumerate(drets):
                    if ret:  # dts already contains a valid datetime for this i
                        continue

                    # try to get a data by checking with a master
                    d = datas[i]
                    d._check(forcedata=dmaster)  # check to force output
                    if d.next(datamaster=dmaster, ticks=False):  # retry
                        dts[i] = d.datetime[0]  # good -> store
                        # self._plotfillers2[i].append(slen)  # mark as fill
                    else:
                        # self._plotfillers[i].append(slen)  # mark as empty
                        pass

                # make sure only those at dmaster level end up delivering
                for i, dti in enumerate(dts):
                    if dti is not None:
                        di = datas[i]
                        rpi = False and di.replaying  # to check behavior
                        if dti > dt0:
                            if not rpi:  # must see all ticks ...
                                di.rewind()  # cannot deliver yet
                            # self._plotfillers[i].append(slen)
                        elif not di.replaying:
                            # Replay forces tick fill, else force here
                            di._tick_fill(force=True)

                        # self._plotfillers2[i].append(slen)  # mark as fill

            elif d0ret is None:
                # meant for things like live feeds which may not produce a bar
                # at the moment but need the loop to run for notifications and
                # getting resample and others to produce timely bars
                for data in datas:
                    data._check()
            else:
                lastret = data0._last()
                for data in datas1:
                    lastret += data._last(datamaster=data0)

                if not lastret:
                    # Only go extra round if something was changed by "lasts"
                    break

            # Datas may have generated a new notification after next
            self._datanotify()
            if self._event_stop:  # stop if requested
                return

            if d0ret or lastret:  # if any bar, check timers before broker
                self._check_timers(runstrats, dt0, cheat=True)
                if self.p.cheat_on_open:
                    for strat in runstrats:
                        strat._next_open()
                        if self._event_stop:  # stop if requested
                            return

            self._brokernotify()
            if self._event_stop:  # stop if requested
                return

            if d0ret or lastret:  # bars produced by data or filters
                self._check_timers(runstrats, dt0, cheat=False)
                for strat in runstrats:
                    strat._next()
                    if self._event_stop:  # stop if requested
                        return

                    self._next_writers(runstrats)

        # Last notification chance before stopping
        self._datanotify()
        if self._event_stop:  # stop if requested
            return
        self._storenotify()
        if self._event_stop:  # stop if requested
            return

    def _runonce(self, runstrats):
        '''
        Actual implementation of run in vector mode.

        Strategies are still invoked on a pseudo-event mode in which ``next``
        is called for each data arrival
        '''
        for strat in runstrats:
            strat._once()
            strat.reset()  # strat called next by next - reset lines

        # The default once for strategies does nothing and therefore
        # has not moved forward all datas/indicators/observers that
        # were homed before calling once, Hence no "need" to do it
        # here again, because pointers are at 0
        datas = sorted(self.datas,
                       key=lambda x: (x._timeframe, x._compression))

        while True:
            # Check next incoming date in the datas
            dts = [d.advance_peek() for d in datas]
            dt0 = min(dts)
            if dt0 == float('inf'):
                break  # no data delivers anything

            # Timemaster if needed be
            # dmaster = datas[dts.index(dt0)]  # and timemaster
            slen = len(runstrats[0])
            for i, dti in enumerate(dts):
                if dti <= dt0:
                    datas[i].advance()
                    # self._plotfillers2[i].append(slen)  # mark as fill
                else:
                    # self._plotfillers[i].append(slen)
                    pass

            self._check_timers(runstrats, dt0, cheat=True)

            if self.p.cheat_on_open:
                for strat in runstrats:
                    strat._oncepost_open()
                    if self._event_stop:  # stop if requested
                        return

            self._brokernotify()
            if self._event_stop:  # stop if requested
                return

            self._check_timers(runstrats, dt0, cheat=False)

            for strat in runstrats:
                strat._oncepost(dt0)
                if self._event_stop:  # stop if requested
                    return

                self._next_writers(runstrats)

    def _check_timers(self, runstrats, dt0, cheat=False):
        timers = self._timers if not cheat else self._timerscheat
        for t in timers:
            if not t.check(dt0):
                continue

            t.params.owner.notify_timer(t, t.lastwhen, *t.args, **t.kwargs)

            if t.params.strats:
                for strat in runstrats:
                    strat.notify_timer(t, t.lastwhen, *t.args, **t.kwargs)
