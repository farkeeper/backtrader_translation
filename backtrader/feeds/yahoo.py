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

import collections
from datetime import date, datetime
import io
import itertools

from ..utils.py3 import (urlopen, urlquote, ProxyHandler, build_opener,
                         install_opener)

import backtrader as bt
from .. import feed
from ..utils import date2num

__all__ = ['YahooFinanceCSVData',   # yahoo财经CSV数据类 ，继承自 CSV数据基类 feed.CSVDataBase （在feed模块内定义）
           'YahooLegacyCSV',
           'YahooFinanceCSV',
           'YahooFinanceData',
           'YahooFinance',
           ]
class YahooFinanceCSVData(feed.CSVDataBase):
    '''
    Parses pre-downloaded Yahoo CSV Data Feeds (or locally generated if they
    comply to the Yahoo format)
    解析预加载CSV数据（如果符合雅虎格式则本地生成）

    Specific parameters:
    指定参数如下：

      - ``dataname``: The filename to parse or a file-like object
      dataname：要解析的文件名 或者 诸如此类的对象

      - ``reverse`` (default: ``False``)
        反转数据：否

        It is assumed that locally stored files have already been reversed
        during the download process
        本地存储的文件在下载过程中是否被反转：默认 否

      - ``adjclose`` (default: ``True``)
        是否复权：是
        Whether to use the dividend/split adjusted close and adjust all
        values according to it.

      - ``adjvolume`` (default: ``True``)

        Do also adjust ``volume`` if ``adjclose`` is also ``True``

      - ``round`` (default: ``True``)

        Whether to round the values to a specific number of decimals after
        having adjusted the close
        是否调节小数精度

      - ``roundvolume`` (default: ``0``)

        Round the resulting volume to the given number of decimals after having
        adjusted it

      - ``decimals`` (default: ``2``)

        Number of decimals to round to

      - ``swapcloses`` (default: ``False``)

        [2018-11-16] It would seem that the order of *close* and *adjusted
        close* is now fixed. The parameter is retained, in case the need to
        swap the columns again arose.

    '''
    # 类变量 可通过 类名.类变量名 直接调用，类的实例 可直接拥有
    lines = ('adjclose',)

    params = (
        ('reverse', False),     # 反转数据：否
        ('adjclose', True),     # 复权：是
        ('adjvolume', True),    #
        ('round', True),        # 调节小数精度
        ('decimals', 2),        # 小数点后的精度 ： 2位
        ('roundvolume', False),
        ('swapcloses', False),
    )

    def start(self):
        super(YahooFinanceCSVData, self).start()    # 调用超类的start()

        if not self.params.reverse:     # 是否反转数据 这个参数必须有，如果没有则退出
            return

        # Yahoo sends data in reverse order and the file is still unreversed
        # Yahoo以倒序发送数据 并且 文件没有反转数据
        dq = collections.deque()    # 定义一个数据容器（双向队列），类似list，可以在头尾快速增删元素
        for line in self.f:
            dq.appendleft(line)     # 左侧添加元素

        # StringIO 在内存中以 io（输入输出） 流的方式读写 str https://www.cnblogs.com/mtcnn/p/9421724.html
        # https://www.jianshu.com/p/c9ecddf8b87f
        f = io.StringIO(newline=None)
        f.writelines(dq)    # 从读写位置将dq写入给对象f。读写位置被移动。
        f.seek(0)       # 将指针移到开头
        self.f.close()
        self.f = f
        """
        StringIO的行为与file对象非常像，但它不是磁盘上文件，而是一个内存里的"文件"，
        在内存中读写str，我们可以像操作磁盘文件那样来操作StringIO，主要用于在内存缓冲区中读写数据.
        创建一个StingIO对象，寄存在缓冲区，可选参数buf是一个str或unicode类型，它将会与后续写的数据存放一起。
        """

    def _loadline(self, linetokens):
        while True:
            nullseen = False
            for tok in linetokens[1:]:
                if tok == 'null':
                    nullseen = True
                    linetokens = self._getnextline()  # refetch tokens
                    if not linetokens:
                        return False  # cannot fetch, go away

                    # out of for to carry on wiwth while True logic
                    break

            if not nullseen:
                break  # can proceed

        i = itertools.count(0)

        dttxt = linetokens[next(i)]
        dt = date(int(dttxt[0:4]), int(dttxt[5:7]), int(dttxt[8:10]))
        dtnum = date2num(datetime.combine(dt, self.p.sessionend))

        self.lines.datetime[0] = dtnum
        o = float(linetokens[next(i)])
        h = float(linetokens[next(i)])
        l = float(linetokens[next(i)])
        c = float(linetokens[next(i)])
        self.lines.openinterest[0] = 0.0

        # 2018-11-16 ... Adjusted Close seems to always be delivered after
        # the close and before the volume columns
        adjustedclose = float(linetokens[next(i)])
        try:
            v = float(linetokens[next(i)])
        except:  # cover the case in which volume is "null"
            v = 0.0

        if self.p.swapcloses:  # swap closing prices if requested
            c, adjustedclose = adjustedclose, c

        adjfactor = c / adjustedclose

        # in v7 "adjusted prices" seem to be given, scale back for non adj
        if self.params.adjclose:
            o /= adjfactor
            h /= adjfactor
            l /= adjfactor
            c = adjustedclose
            # If the price goes down, volume must go up and viceversa
            if self.p.adjvolume:
                v *= adjfactor

        if self.p.round:
            decimals = self.p.decimals
            o = round(o, decimals)
            h = round(h, decimals)
            l = round(l, decimals)
            c = round(c, decimals)

        v = round(v, self.p.roundvolume)

        self.lines.open[0] = o
        self.lines.high[0] = h
        self.lines.low[0] = l
        self.lines.close[0] = c
        self.lines.volume[0] = v
        self.lines.adjclose[0] = adjustedclose

        return True


class YahooLegacyCSV(YahooFinanceCSVData):
    '''
    This is intended to load files which were downloaded before Yahoo
    discontinued the original service in May-2017

    '''
    params = (
        ('version', ''),
    )


class YahooFinanceCSV(feed.CSVFeedBase):
    DataCls = YahooFinanceCSVData


class YahooFinanceData(YahooFinanceCSVData):
    '''
    Executes a direct download of data from Yahoo servers for the given time
    range.

    Specific parameters (or specific meaning):

      - ``dataname``

        The ticker to download ('YHOO' for Yahoo own stock quotes)

      - ``proxies``

        A dict indicating which proxy to go through for the download as in
        {'http': 'http://myproxy.com'} or {'http': 'http://127.0.0.1:8080'}

      - ``period``

        The timeframe to download data in. Pass 'w' for weekly and 'm' for
        monthly.

      - ``reverse``

        [2018-11-16] The latest incarnation of Yahoo online downloads returns
        the data in the proper order. The default value of ``reverse`` for the
        online download is therefore set to ``False``

      - ``adjclose``

        Whether to use the dividend/split adjusted close and adjust all values
        according to it.

      - ``urlhist``

        The url of the historical quotes in Yahoo Finance used to gather a
        ``crumb`` authorization cookie for the download

      - ``urldown``

        The url of the actual download server

      - ``retries``

        Number of times (each) to try to get a ``crumb`` cookie and download
        the data

      '''

    params = (
        ('proxies', {}),
        ('period', 'd'),
        ('reverse', False),
        ('urlhist', 'https://finance.yahoo.com/quote/{}/history'),
        ('urldown', 'https://query1.finance.yahoo.com/v7/finance/download'),
        ('retries', 3),
    )

    def start_v7(self):
        try:
            import requests
        except ImportError:
            msg = ('The new Yahoo data feed requires to have the requests '
                   'module installed. Please use pip install requests or '
                   'the method of your choice')
            raise Exception(msg)

        self.error = None
        url = self.p.urlhist.format(self.p.dataname)

        sesskwargs = dict()
        if self.p.proxies:
            sesskwargs['proxies'] = self.p.proxies

        crumb = None
        sess = requests.Session()
        sess.headers['User-Agent'] = 'backtrader'
        for i in range(self.p.retries + 1):  # at least once
            resp = sess.get(url, **sesskwargs)
            if resp.status_code != requests.codes.ok:
                continue

            txt = resp.text
            i = txt.find('CrumbStore')
            if i == -1:
                continue
            i = txt.find('crumb', i)
            if i == -1:
                continue
            istart = txt.find('"', i + len('crumb') + 1)
            if istart == -1:
                continue
            istart += 1
            iend = txt.find('"', istart)
            if iend == -1:
                continue

            crumb = txt[istart:iend]
            crumb = crumb.encode('ascii').decode('unicode-escape')
            break

        if crumb is None:
            self.error = 'Crumb not found'
            self.f = None
            return

        crumb = urlquote(crumb)

        # urldown/ticker?period1=posix1&period2=posix2&interval=1d&events=history&crumb=crumb

        # Try to download
        urld = '{}/{}'.format(self.p.urldown, self.p.dataname)

        urlargs = []
        posix = date(1970, 1, 1)
        if self.p.todate is not None:
            period2 = (self.p.todate.date() - posix).total_seconds()
            urlargs.append('period2={}'.format(int(period2)))

        if self.p.todate is not None:
            period1 = (self.p.fromdate.date() - posix).total_seconds()
            urlargs.append('period1={}'.format(int(period1)))

        intervals = {
            bt.TimeFrame.Days: '1d',
            bt.TimeFrame.Weeks: '1wk',
            bt.TimeFrame.Months: '1mo',
        }

        urlargs.append('interval={}'.format(intervals[self.p.timeframe]))
        urlargs.append('events=history')
        urlargs.append('crumb={}'.format(crumb))

        urld = '{}?{}'.format(urld, '&'.join(urlargs))
        f = None
        for i in range(self.p.retries + 1):  # at least once
            resp = sess.get(urld, **sesskwargs)
            if resp.status_code != requests.codes.ok:
                continue

            ctype = resp.headers['Content-Type']
            # Cover as many text types as possible for Yahoo changes
            if not ctype.startswith('text/'):
                self.error = 'Wrong content type: %s' % ctype
                continue  # HTML returned? wrong url?

            # buffer everything from the socket into a local buffer
            try:
                # r.encoding = 'UTF-8'
                f = io.StringIO(resp.text, newline=None)
            except Exception:
                continue  # try again if possible

            break

        self.f = f

    def start(self):
        self.start_v7()

        # Prepared a "path" file -  CSV Parser can take over
        super(YahooFinanceData, self).start()


class YahooFinance(feed.CSVFeedBase):
    DataCls = YahooFinanceData

    params = DataCls.params._gettuple()
