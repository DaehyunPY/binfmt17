# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 14:10:40 2017

@author: daehyun
"""

from .handler import Reader
from numpy import array, uint32, uint16, float64
# from numba import jitclass, jit
# from numba import uint16 as __uint16
# from numba import uint16 as __uint32
# from numba import float32 as __float32
# from numba import float64 as __float64


# dspec = {
#     '__tag': __uint32,
#     '__hits': __uint16,
#     '__x': __float64[:],
#     '__y': __float64[:],
#     '__t': __float64[:],
#     '__method': __uint16[:]
# }


# @jitclass(dspec)
class Data:
    __slots__ = ['__tag', '__hits', '__x', '__y', '__t', '__method']
    
    def __init__(self, tag, hits, x=[], y=[], t=[], method=[], filter=None):
        self.__tag = uint32(tag)
        ret = self.__filter(*self.__reshape(hits, x, y, t, method), 
                            filter=filter)
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
    return dict(tag = (d.tag for d in Data),
                hits = (d.hits for d in Data),
                x = (d.x for d in Data),
                y = (d.y for d in Data),
                t = (d.t for d in Data), 
                method = (d.method for d in Data))


def Data2Gen(*Data):
    print("Do not use 'Data2Gen'! Redirecting to 'genData'")
    return genData(*Data)


class Deserializer(Reader):
    def __init__(self, filename, filter=None):
        super().__init__(filename, *self.fmts)
        self.__filter = filter
        
    @property
    def fmts(self):
        return ['=IH', '=dddH']
        
    @property
    def unpacked(self):
        return Data(*super().unpacked,  # hits, x, y, t, method
                    filter=self.__filter)
