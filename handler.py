# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 14:10:40 2017

@author: daehyun
"""

from struct import Struct, error
from numba import jit


@jit
def lazyReader(file, struct, loop=1):
    s = struct.size
    for _ in range(loop):
        r = file.read(s)
        yield struct.unpack(r)


def read(file, struct, *others, loop=1):
    if loop == 0:
        return tuple()
    if len(others) == 0:
        reader = lazyReader(file, struct, loop=loop)
        if loop == 1:
            return tuple(*reader)
        elif loop > 1:
            zipped = zip(*reader)
            return tuple(zipped)
    else:
        if loop == 1:
            ret = read(file, struct)
            arr = read(file, others[0], *others[1:], loop=ret[-1])
            return (*ret, *arr)
        elif loop > 1:
            gen = lambda: read(file, struct, *others)
            zipped = zip(*(gen() for _ in range(loop)))
            return tuple(zipped)
    raise ValueError('loop must be 0 or larger int!')


def genWriter(file, struct, *others, loop=1):
    def writer(data=None, *dtail):
        if loop == 0:
            if data is not None:
                ValueError('loop does not match with data!')
            return None
        if len(others) == 0:
            if loop == 1:
                file.write(struct.pack(*data))
                return None
            # if not loop == len(data):
            #     raise ValueError('loop does not match with data!')
            else:
                for d in data:
                    file.write(struct.pack(*d))
                return None
        else:
            if loop == 1:
                w = genWriter(file, struct)
                w(data)
                wother = genWriter(file, *others, loop=data[-1])
                wother(*dtail)
                return None
            zipped = tuple(zip(data, dtail))
            if not loop == len(zipped):
                raise ValueError('loop does not match with data!')
            else:
                for d, t in zipped:
                    w = genWriter(file, struct, *others)
                    w(d, *t)
                return None
    return writer


class Reader:
    def __init__(self, filename, *fmts):
        self.__file = open(filename, 'br')
        self.__structs = [Struct(f) for f in fmts]
        self.current = 0

    def __del__(self):
        self.__file.close()

    @property
    def current(self):
        return self.__file.tell()

    @current.setter
    def current(self, i):
        self.__file.seek(i)

    @property
    def unpacked(self):
        return read(self.__file, *self.__structs)

    def __iter__(self):
        self.current = 0
        return self

    def __next__(self):
        try:
            return self.unpacked
        except error:
            raise StopIteration
