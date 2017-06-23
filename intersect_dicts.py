import sys

def read_from_mse(file):
    V=set()
    file.readline()
    for line in file:
        word = line.strip().split()[0]
        V.add(word)
    return V

if "-" not in sys.argv:
    print >>sys.stderr, "No - was given!"
    exit(1)

lang1_files = sys.argv[1:sys.argv.index("-")]
lang2_files = sys.argv[sys.argv.index("-")+1:]

if len(lang1_files) == 0 or len(lang2_files) == 0:
    print >>sys.stderr, "There are no files for one or both of the languages!"
    exit(1)

V1 = read_from_mse(open(lang1_files[0]))
V2 = read_from_mse(open(lang2_files[0]))

print >>sys.stderr, len(V1)

for file in lang1_files[1:]:
    V1 &= read_from_mse(open(file))
    print >>sys.stderr, len(V1)

print >>sys.stderr, "",  len(V2)
for file in lang2_files[1:]:
    V2 &= read_from_mse(open(file))
    print >>sys.stderr, "",  len(V2)

i = 0
total = 0
for line in sys.stdin:
    parts = line.strip().split()
    if len(parts) != 2:
        sys.stderr.write(line)
        continue
    if parts[0] in V1 and parts[1] in V2:
        sys.stdout.write(line)
        i += 1
    total += 1
print >>sys.stderr, "%d/%d" % (i, total)
