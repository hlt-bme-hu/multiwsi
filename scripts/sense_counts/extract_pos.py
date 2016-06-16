import sys
from collections import defaultdict
from itertools import chain
import numpy

V = defaultdict(lambda: defaultdict(lambda: 0))

for line in sys.stdin:
    line = line.strip().split()
    for w in line:
        ww = w.split('_')
        if len(ww) < 2:
            continue
        V["_".join(ww[:-1])][ww[-1]] += 1

V = list(V.iteritems())
V.sort(key=lambda x: sum(f for y,f in x[1].iteritems()), reverse=True)

for w, poses in V:
    print w + "\t" + "\t".join(map(str, chain(*poses.iteritems())))
    numbers = numpy.array(poses.values(), dtype=float)
    numbers /= numbers.sum()
    print >>sys.stderr, w + "\t" + str(2**(-(numbers * numpy.log2(numbers))).sum())