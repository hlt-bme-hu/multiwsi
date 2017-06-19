import codecs
import pickle
import sys

pmodel = pickle.load(open(sys.argv[1]))
items = zip(*pmodel)
with codecs.open(sys.argv[2], mode='w', encoding='utf-8') as w2v_file:
    w2v_file.write('{} {}\n'.format(len(items), len(items[0][1])))
    for word, vec in items:
        w2v_file.write(word)
        w2v_file.write(' {}\n'.format(' '.join(map(str, vec))))
