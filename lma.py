from os.path import getsize
from numpy import fromfile, append, nan, repeat, nan_to_num
from struct import Struct
from cytoolz import first, curry, pipe
from cytoolz.curried import reduce, map
from operator import add


def read_bin(struct, buffer):
    s = struct.size
    r = buffer.read(s)
    yield from struct.unpack(r)


class LmaReader:
    def __init__(self, filename):
        self.__size = getsize(filename)
        self.__file = open(filename, 'br')
        self.__current_bit = 0
        # short:h int32:i double:d unsighed int32:I
        self.__header = tuple(read_bin(Struct("=ihhdidhdhIIh"), self.__file))

        channels = (
            tuple(read_bin(Struct("=hhdhhii"), self.__file))
            if ((self.used_channels >> i) & 0b1) == 1 else None
            for i in range(self.nchannels))
        self.__channels = tuple(
            {'fullscale': ch[0], 'gain': ch[2], 'baseline': ch[3]}
            if ch is not None else None
            for ch in channels)

        self.__read_event = lambda: read_bin(Struct("=id"), self.__file)
        self.__read_npulses = lambda: read_bin(Struct("=h"), self.__file)
        self.__read_pulseinfo = lambda: read_bin(Struct("=ii"), self.__file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__file.close()

    @property
    def first_bit(self):
        return self.header_size

    @property
    def last_bit(self):
        return self.__size

    @property
    def __current_bit(self):
        return self.__file.tell()

    @__current_bit.setter
    def __current_bit(self, i):
        self.__file.seek(i)

    @property
    def current_bit(self):
        return self.__current_bit

    @property
    def header(self):
        return self.__header

    @property
    def header_size(self):
        return self.header[0] + 4

    @property
    def nchannels(self):
        return self.header[1]

    @property
    def nbytes(self):
        return self.header[2]

    @property
    def sample_interval(self):
        return self.header[3]

    @property
    def nsamples(self):
        return self.header[4]

    @property
    def used_channels(self):
        return self.header[9]

    @property
    def channels(self):
        return self.__channels

    def __read_pulses(self):
        n = self.nsamples
        nans = curry(repeat, nan)
        for _ in range(first(self.__read_npulses())):
            n0, n1 = self.__read_pulseinfo()
            d = fromfile(self.__file, dtype='int16', count=n1)
            yield reduce(append, (nans(n0), d, nans(n-n0-n1)))

    def __iter__(self):
        self.__current_bit = self.first_bit
        return self

    def __next__(self):
        if not (self.current_bit < self.last_bit):
            raise StopIteration
        return {'bit': self.current_bit,
                'tag': first(self.__read_event()),
                'channels': tuple(
                    pipe(self.__read_pulses(),
                         map(lambda pulse: (pulse-ch['baseline'])*ch['gain']),
                         map(nan_to_num),
                         reduce(add))
                    if ch is not None else None for ch in self.channels)}
