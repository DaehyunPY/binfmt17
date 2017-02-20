# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 14:10:40 2017

@author: daehyun
"""

from numpy import histogram, histogram2d, meshgrid, array, float32
# from numba import jit, jitclass, types


# @jitclass(dict(
#     __fr=types.float32,
#     __to=types.float32,
#     __edges=types.float32[:],
#     __hist=types.float32[:]
# ))
class Hist1D:
    def __init__(self, fr, to, bins):
        self.__fr = fr
        self.__to = to
        hist, edges = histogram([], range=self.range, bins=bins)
        self.__hist = array(hist, dtype=float32)
        self.__edges = array(edges, dtype=float32)

    @property
    def range(self):
        return self.__fr, self.__to

    @property
    def edges(self):
        return self.__edges

    @property
    def centers(self):
        return (self.edges[:-1]+self.edges[1:])/2.0

    @property
    def hist(self):
        return self.__hist

    @hist.setter
    def hist(self, hist):
        if not self.hist.shape == hist.shape:
            raise ValueError('The shape of hist does not match!')
        self.__hist = hist

    @property
    def xy(self):
        return self.centers, self.hist

    def fill(self, arr, normed=False, weights=None, density=None):
        hist, _ = histogram(arr, range=self.range, bins=self.edges,
                            normed=normed, weights=weights, density=density)
        self.__hist += hist


# @jitclass(dict(
#     __xfr=types.float32,
#     __xto=types.float32,
#     __xedges=types.float32[:],
#     __yfr=types.float32,
#     __yto=types.float32,
#     __yedges=types.float32[:],
#     __hist=types.float32[:, :],
# ))
class Hist2D:
    def __init__(self, xfr, xto, xbins, yfr, yto, ybins):
        self.__xfr = xfr
        self.__xto = xto
        self.__yfr = yfr
        self.__yto = yto
        hist, xedges, yedges = histogram2d(
            [], [], 
            range=self.range, 
            bins=(xbins, ybins))
        self.__hist = array(hist, dtype=float32)
        self.__xedges = array(xedges, dtype=float32)
        self.__yedges = array(yedges, dtype=float32)

    @property
    def xrange(self):
        return self.__xfr, self.__xto

    @property
    def xedges(self):
        return self.__xedges

    @property
    def xcenters(self):
        return (self.xedges[:-1]+self.xedges[1:])/2.0
    
    @property
    def yrange(self):
        return self.__yfr, self.__yto

    @property
    def yedges(self):
        return self.__yedges

    @property
    def ycenters(self):
        return (self.yedges[:-1]+self.yedges[1:])/2.0

    @property
    def range(self):
        return self.xrange, self.yrange

    @property
    def edges(self):
        return self.xedges, self.yedges
    
    @property
    def centers(self):
        return self.xcenters, self.ycenters

    @property
    def edgegrid(self):
        return meshgrid(*self.edges)

    @property
    def centergrid(self):
        return meshgrid(*self.centers)

    @property
    def hist(self):
        return self.__hist

    @hist.setter
    def hist(self, hist):
        if not self.hist.shape == hist.shape:
            raise ValueError('The shape of hist does not match!')
        self.__hist = hist

    @property
    def edgez(self):
        return (*self.edges, self.hist)

    @property
    def xyz(self):
        return (*self.centers, self.hist)

    def fill(self, xarr, yarr, normed=False, weights=None):
        hist, _, _ = histogram2d(xarr, yarr, range=self.range, bins=self.edges,
                                 normed=normed, weights=weights)
        self.__hist += hist
