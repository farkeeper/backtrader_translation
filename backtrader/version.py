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


__version__ = '1.9.76.123'

__btversion__ = tuple(int(x) for x in __version__.split('.'))

if __name__ == "__main__":
    print(__btversion__)
    print("split():分割字符串", 'ab,cde,f'.split(','))

    import collections

    # collections.Counter
    # 统计出现的次数。  split()分割字符串
    print(collections.Counter("hello hello world hello nihao".split()))