import sys

V = []

for line in sys.stdin:
    parts = line.strip().split()
    if len(parts) != 2:
        sys.stderr.write(line)
    elif parts not in V:
        V.append(parts)

for source, translation in V:
    print source, translation
