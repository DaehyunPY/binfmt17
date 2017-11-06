# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 14:10:40 2017

@author: daehyun
"""

from collections import namedtuple
from warnings import warn

from numpy import array, uint32, uint16, float64

from .handler import Reader


class HitData:
    __slots__ = ['__tag', '__hits', '__x', '__y', '__t', '__method']

    def __init__(self, tag, hits, x=None, y=None, t=None, method=None, filter=None):
        if x is None: x = []
        if y is None: y = []
        if t is None: t = []
        if method is None: method = []
        self.__tag = uint32(tag)
        ret = self.__filter(*self.__reshape(hits, x, y, t, method), filter=filter)
        self.__hits, self.__x, self.__y, self.__t, self.__method = ret

    def __reshape(self, hits, x, y, t, method):
        return (uint16(hits),  # hits
                array(x, dtype=float64).reshape(hits),  # x
                array(y, dtype=float64).reshape(hits),  # y
                array(t, dtype=float64).reshape(hits),  # t
                array(method, dtype=uint16).reshape(hits))  #method

    def __filter(self, hits, x, y, t, method, filter):
        if filter is None:
            return hits, x, y, t, method
        else:
            idx = filter(x=x, y=y, t=t, method=method)
            return uint16(idx.sum()), x[idx], y[idx], t[idx], method[idx]

    @property
    def tag(self):
        return self.__tag

    @property
    def hits(self):
        return self.__hits

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def t(self):
        return self.__t

    @property
    def method(self):
        return self.__method


class HitDeserializer(Reader):
    def __init__(self, filename, filter=None):
        super().__init__(filename, *self.fmts)
        self.__filter = filter

    @property
    def fmts(self):
        return ['=IH', '=dddH']

    @property
    def unpacked(self):
        return HitData(*super().unpacked,  # hits, x, y, t, method
                    filter=self.__filter)


def Deserializer(filename, filter=None):
    warn("Do not use 'Deserializer'! Redirecting to 'HitDeserializer'")
    return HitDeserializer(filename, filter=filter)


class BinData(
    namedtuple('BinData',
               'tag FEL_status FEL_shutter UV_shutter dump4 FEL_intensity delay_motor dump7 dump8 hits t x y')):
    def __new__(cls, tag, FEL_status, FEL_shutter, UV_shutter, dump4, FEL_intensity, delay_motor, dump7, dump8, hits,
                t=None, x=None, y=None):
        if t is None:
            t = ()
        if x is None:
            x = ()
        if y is None:
            y = ()
        super().__new__(cls, tag, FEL_status, FEL_shutter, UV_shutter, dump4,
                        FEL_intensity, delay_motor, dump7, dump8, hits,
                        array(t, dtype=float64).reshape(hits),
                        array(x, dtype=float64).reshape(hits), array(y, dtype=float64).reshape(hits))


class BinDeserializer(Reader):
    def __init__(self, filename):
        super().__init__(filename, *self.fmts)

    @property
    def fmts(self):
        return ['=IBBBBddddI', '=ddd']

    @property
    def unpacked(self):
        return BinData(*super().unpacked)
