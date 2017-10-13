from itertools import count

import matplotlib.pyplot as plt

from binfmt17 import LmaReader

with LmaReader('aq040__0000.lma') as r:
    for d in r:
        tag = d['tag']
        n = len(d['channels'])

        plt.figure(figsize=(8, 16))
        for i, ch in zip(count(1), d['channels']):
            plt.subplot(n, 1, i)
            plt.plot(ch)
        plt.savefig('{}.png'.format(tag), bbox_inches='tight')
        break
