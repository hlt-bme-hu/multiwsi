import argparse
from collections import Counter
import logging
from math import log
import os


def parse_args():
    parser = argparse.ArgumentParser(
        description='Prepare input files for CMultiVec form a corpus.')
    parser.add_argument('corpus', help='sentence/document per line')
    parser.add_argument('init_embed', help='vectors in w2v format')
    # w2v embeddings contain words in freq order (that may != idf ord)
    parser.add_argument('vocab', help='vocabulary list (see extract_vocab.py)')
    parser.add_argument('corpus_out', help='the corpus output file')
    parser.add_argument('embed_out', help='the output embedding file')
    parser.add_argument('idf_out', help='the idf output file')

    args = parser.parse_args()
    for out_fn in [args.corpus_out, args.embed_out, args.idf_out]:
        if os.path.isfile(out_fn):
            parser.error('output file {} exists'.format(out_fn))
    return args


def get_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(module)s (%(lineno)s) %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger


def main():
    logger = get_logger()
    args = parse_args()
    d_freq = Counter()

    logger.info('Reading vocab file...')
    with open(args.vocab) as inf:
        vocab = [word.strip() for word in inf.readlines()]
        vocab_set = set(vocab)

    logger.info('Processing corpus...')
    with open(args.corpus) as cinf, open(args.corpus_out, 'w') as coutf:
        for n_sent, line in enumerate(cinf):
            if n_sent % 1000000 == 0 and n_sent > 0:
                logger.info('{:,} sentences read'.format(n_sent))
            words = [w if w in vocab_set else 'UUUNKKK'
                     for w in line.strip().lower().split()]
            d_freq.update(set(words))
            coutf.write("\n".join(words))
            coutf.write("\noooeddd\n")

    logger.info('Writing idfs...')
    with open(args.idf_out, mode='w') as outf:
        for word in vocab:
            outf.write("{}\n".format(log(1 + float(n_sent) / d_freq[word])))

    logger.info('Filtering embedding...')
    embed = {}
    unks = 0
    with open(args.init_embed) as inf:
        inf.readline()  # Header
        for line in inf:
            word, vector = line.strip().split(' ', 1)
            wl = word.lower()
            if word in vocab_set:  # lowercase
                embed[word] = vector
            elif wl in vocab_set and wl not in embed:  # uppercase
                embed[wl] = vector
            else:
                unks += 1
                v = [float(num) for num in vector.split()]
                if 'UUUNKKK' in embed:
                    vunk = embed['UUUNKKK']
                    for i in xrange(len(v)):
                        vunk[i] += v[i]
                else:
                    embed['UUUNKKK'] = v
        vunk = embed['UUUNKKK']
        for i in xrange(len(vunk)):
            vunk[i] = vunk[i] / unks
        embed['UUUNKKK'] = ' '.join(str(f) for f in vunk)

    logger.info('Writing embedding...')
    with open(args.embed_out, 'w') as outf:
        for word in vocab:
            outf.write("{}\n".format(embed[word]))

if __name__ == '__main__':
    main()
