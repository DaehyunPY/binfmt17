# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 14:10:40 2017

@author: daehyun
"""

from .handler import Reader
from numpy import array, uint32, uint16, float64
from warnings import warn
from collections import namedtuple


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
  

def genData(*Data):
    print("'genData' will be deleted from this package!")
    return dict(tag = (d.tag for d in Data),
                hits = (d.hits for d in Data),
                x = (d.x for d in Data),
                y = (d.y for d in Data),
                t = (d.t for d in Data),
                method = (d.method for d in Data))


def Data2Gen(*Data):
    print("Do not use 'Data2Gen'! Redirecting to 'genData'")
    return genData(*Data)


class HitDeserializer(Reader):
    def __init__(self, filename, filter=None):
        super().__init__(filename, *self.fmts)
        self.__filter = filter

    def __del__(self):
        super().__del__()
        
    @property
    def fmts(self):
        return ['=IH', '=dddH']
        
    @property
    def unpacked(self):
        return HitData(*super().unpacked,  # hits, x, y, t, method
                    filter=self.__filter)


class Deserializer(HitDeserializer):
    def __init__(self, filename, filter=None):
        warn("Do not use 'Deserializer'! Redirecting to 'HitDeserializer'")
        super().__init__(filename, *self.fmts)
        self.__filter = filter

    def __del__(self):
        super().__del__()


class BinData(namedtuple(
    'BinData',
    'tag FEL_status FEL_shutter UV_shutter dump4 FEL_intensity delay_motor dump7 dump8 hits t x y')):
    def __new__(cls, tag, FEL_status, FEL_shutter, UV_shutter, dump4, FEL_intensity, delay_motor, dump7, dump8, hits, t=None, x=None, y=None):
        if t == None:
            t = ()
        if x == None:
            x = ()
        if y == None:
            y = ()
        array(x, dtype=float64),
        return super().__new__(cls, tag, FEL_status, FEL_shutter, UV_shutter, dump4, FEL_intensity, delay_motor, dump7, dump8, hits, 
            array(t, dtype=float64).reshape(hits), array(x, dtype=float64).reshape(hits), array(y, dtype=float64).reshape(hits))


class BinDeserializer(Reader):
    def __init__(self, filename):
        super().__init__(filename, *self.fmts)

    def __del__(self):
        super().__del__()

    @property
    def fmts(self):
        return ['=IBBBBddddI', '=ddd']

    @property
    def unpacked(self):
        return BinData(*super().unpacked)
