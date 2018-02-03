from itertools import count
from pprint import pprint

import matplotlib.pyplot as plt

from binfmt17 import LmaReader, bin_reader, hit_reader, export_as_bin


with LmaReader('aq040__0000.lma') as r:
    for d in r:
        pprint(d)
        tag = d['tag']
        n = len(d['channels'])

        plt.figure(figsize=(8, 16))
        for i, ch in zip(count(1), d['channels']):
            plt.subplot(n, 1, i)
            plt.plot(ch)
        plt.savefig('{}.png'.format(tag), bbox_inches='tight')
        break

h = hit_reader('aq137.hit')
pprint(next(h))

export_as_bin('aq137.hit')
