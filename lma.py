from numpy import fromfile, append, nan, repeat, nan_to_num, ndarray
from struct import Struct
from cytoolz import first, curry, pipe
from cytoolz.curried import reduce, map
from operator import add


@curry
def read_bin(struct, buffer) -> iter:
    s = struct.size
    r = buffer.read(s)
    yield from struct.unpack(r)


class LmaDeserializer:
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
    def channels(self) -> tuple(dict):
        return self.__channels

    def __read_pulses(self, buffer) -> iter(ndarray):
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
