import argparse
from collections import defaultdict
import logging
import math
import os

def parse_args():
    parser = argparse.ArgumentParser(
        description= 'Compute idf values from corpus')
    parser.add_argument('corpus', help='word per line')
    parser.add_argument( 'embed_in', help='vocab in w2v format') 
    # w2v embeddings contain words in freq order (that may != idf ord)
    parser.add_argument('vocab_out')
    parser.add_argument('idf')
    parser.add_argument('embed_weights')
    parser.add_argument('--cutoff', type=int, default=300000)
    return parser.parse_args()

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
    logger.info('Counting words...')
    n_sent = 0
    d_freq = defaultdict(int)
    with open(args.corpus) as corpus_fn:
        for i, line in enumerate(corpus_fn):
            if not i % 1000000:
                logger.info('{:,} sentences read'.format(i))
            n_sent += 1
            words = set()
            for word in line.strip().split():
                words.add(word) 
            for word in words:
                d_freq[word] += 1 
    for out_fn in [args.vocab_out, args.idf, args.embed_weights]:
        if os.path.isfile(out_fn):
            raise IOError('output file exists')
    logger.info('Reading initial embedding...')
    vocab = []
    with open(args.embed_in) as embed_in_f, open(
            args.embed_weights, mode='w') as embed_out_f:
        for line in embed_in_f:
            word, weights_newline = line.split(' ', 1)
            vocab.append(word)
            embed_out_f.write(weights_newline)
    logger.info('Writing idfs...')
    with open(args.vocab_out, mode='w') as vocab_f, open(
            args.idf, mode='w') as idf_f:
        for i, word in  enumerate(vocab):
            # heapq.nlargest( args.cutoff, d_freq.items(),
            # key=operator.itemgetter(1))):
            vocab_f.write('{}\n'.format(word))
            idf_f.write('{}\n'.format(math.log(float(n_sent)/d_freq[word], 2)))

if __name__ == '__main__':
    main()
