# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 14:10:40 2017

@author: daehyun
"""

from numpy import histogram, histogram2d, meshgrid, array, float32
from warnings import warn 


class Hist1D:
    def __init__(self, *args, **kwargs):
        warn('Watch out args! This class have been modified!')
        hist, edges = histogram([], *args, **kwargs)
        self.__hist = array(hist, dtype=float32)
        self.__edges = array(edges, dtype=float32)

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

    def fill(self, arr, **kwargs):
        hist, _ = histogram(arr, bins=self.edges, **kwargs)
        self.__hist += hist


class Hist2D:
    def __init__(self, *args, **kwargs):
        warn('Watch out args! This class have been modified!')
        hist, xedges, yedges = histogram2d([], [], *args, **kwargs)
        self.__hist = array(hist, dtype=float32).T
        self.__xedges = array(xedges, dtype=float32)
        self.__yedges = array(yedges, dtype=float32)

    @property
    def xedges(self):
        return self.__xedges

    @property
    def xcenters(self):
        return (self.xedges[:-1]+self.xedges[1:])/2.0
    
    @property
    def yedges(self):
        return self.__yedges

    @property
    def ycenters(self):
        return (self.yedges[:-1]+self.yedges[1:])/2.0

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

    def fill(self, xarr, yarr, **kwargs):
        hist, _, _ = histogram2d(xarr, yarr, bins=self.edges, **kwargs)
        self.__hist += hist.T
