import sys
from collections import defaultdict

ordering = defaultdict(lambda: sys.maxint)

for i, line in enumerate(open(sys.argv[1])):
    ordering[line.strip().split()[0]] = i

data=[]
for line in sys.stdin:
    data.append((line, ordering[line.strip().split()[0]]))

for d in sorted(data, key=lambda x: x[1]):
    sys.stdout.write(d[0])