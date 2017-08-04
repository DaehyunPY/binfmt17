from numpy import fromfile, append, nan, repeat, nan_to_num, ndarray
from struct import Struct
from cytoolz import first, curry, pipe
from cytoolz.curried import reduce, map
from operator import add
from os.path import getsize
from abc import ABC, abstractmethod


@curry
def read_bin(struct, buffer) -> iter:
    s = struct.size
    r = buffer.read(s)
    yield from struct.unpack(r)


class Deserializer(ABC):
    @abstractmethod
    def __init__(self, buffer):
        pass

    @abstractmethod
    def header_size(self) -> int:
        return 0

    @abstractmethod
    def __call__(self, buffer) -> dict:
        return {}


class LmaDeserializer(Deserializer):
    """
    Deserializer for LMA format
    Example:
        from os.path import getsize
        last = getsize(filename)
        with open(filename, 'rb') as buffer:
            deserialize = LmaDeserializer(buffer)
            while buffer.tell() < last:
                deserialized = deserialize(buffer)
    """
    def __init__(self, buffer):
        """
        Read header from buffer
        :param buffer: binary buffer
        """
        self.__header = tuple(read_bin(Struct("=ihhdidhdhIIh"), buffer))
        channels = (
            tuple(read_bin(Struct("=hhdhhii"), buffer))
            if ((self.used_channels >> i) & 0b1) == 1 else None
            for i in range(self.nchannels))
        self.__channels = tuple(
            {'fullscale': ch[0], 'gain': ch[2], 'baseline': ch[3]}
            if ch is not None else None
            for ch in channels)
        self.__read_event = read_bin(Struct("=id"))
        self.__read_npulses = read_bin(Struct("=h"))
        self.__read_pulseinfo = read_bin(Struct("=ii"))
        self.__read_pulse = curry(fromfile, dtype='int16')

    @property
    def header(self) -> tuple:
        return self.__header

    @property
    def header_size(self) -> int:
        return self.header[0] + 4

    @property
    def nchannels(self) -> int:
        return self.header[1]

    @property
    def nbytes(self) -> int:
        return self.header[2]

    @property
    def sample_interval(self) -> float:
        return self.header[3]

    @property
    def nsamples(self) -> int:
        return self.header[4]

    @property
    def used_channels(self) -> int:
        return self.header[9]

    @property
    def channels(self) -> [dict]:
        return self.__channels

    def __read_pulses(self, buffer) -> [ndarray]:
        n = self.nsamples
        nans = curry(repeat, nan)
        for _ in range(first(self.__read_npulses(buffer))):
            n0, n1 = self.__read_pulseinfo(buffer)
            d = self.__read_pulse(buffer, count=n1)
            yield reduce(append, (nans(n0), d, nans(n-n0-n1)))

    def __call__(self, buffer) -> dict:
        """
        Deserialize LMA file
        :param buffer: binary buffer
        :return: dict
        """
        return {'tag': first(self.__read_event(buffer)),
                'channels': tuple(
                    pipe(self.__read_pulses(buffer),
                         map(lambda pulse: (pulse-ch['baseline'])*ch['gain']),
                         map(nan_to_num),
                         reduce(add))
                    if ch is not None else None for ch in self.channels)}


@curry
class ReadWith:
    """
    Binary reader
    Example:
        LmaReader = ReadWith(LmaDeserializer)
        with LmaReader(filename) as r:
            for d in r:
                print(d)
                break
    """
    def __init__(self, deserializer: Deserializer.__init__, filename: str):
        self.__size = getsize(filename)
        self.__file = open(filename, 'br')
        self.__current_bit = 0
        self.__deserializer = deserializer(self.__file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__file.close()

    @property
    def deserializer(self) -> Deserializer:
        return self.__deserializer

    @property
    def first_bit(self) -> int:
        return self.deserializer.header_size

    @property
    def last_bit(self) -> int:
        return self.__size

    @property
    def __current_bit(self) -> int:
        return self.__file.tell()

    @__current_bit.setter
    def __current_bit(self, i):
        self.__file.seek(i)

    @property
    def current_bit(self) -> int:
        return self.__current_bit

    def __iter__(self) -> iter:
        self.__current_bit = self.first_bit
        return self

    def __next__(self) -> dict:
        if not (self.current_bit < self.last_bit):
            raise StopIteration
        return self.deserializer(self.__file)

LmaReader = ReadWith(LmaDeserializer)
# HitReader = ReadWith(HitDeserializer)
# BinReader = ReadWith(BinDeserializer)
