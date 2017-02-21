# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 14:10:40 2017

@author: daehyun
"""

from struct import error
from struct import Struct as OrigStruct
from numba import jit
from functools import reduce


class Struct(OrigStruct):
    def __init__(self, fmt):
        super().__init__(fmt)
        self.__entries = len(self.unpack(b'\0' * self.size))

    @property
    def entries(self):
        return self.__entries


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


def easyWrite(file, struct, *data, loop=1):
    if not loop >= 0:
        raise ValueError("'loop' have to be 0 or larger!")
    for i in range(loop):
        slice = data[i*struct.entries:(i+1)*struct.entries]
        file.write(struct.pack(*slice))
    return data[loop*struct.entries:]


def genWriter(file, struct, *others, loop=1):
    def writer(*data):
        if len(others) == 0:
            return easyWrite(file, struct, *data, loop=loop)
        else:
            if loop==0:
                return data
            elif loop == 1:
                whead = genWriter(file, struct)
                dhead = data[:struct.entries]
                whead(*dhead)
                wtail = genWriter(file, *others, loop=dhead[-1])
                dtail = data[struct.entries:]
                return wtail(*dtail)
            elif loop > 1:
                tail = data
                for _ in range(loop):
                    w = genWriter(file, struct, *others)
                    tail = w(*tail)
                return tail
            else:
                raise ValueError("'loop' have to be 0 or larger!")
    return writer
