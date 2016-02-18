import argparse
from collections import defaultdict
import logging
import math
import os

def parse_args():
    parser = argparse.ArgumentParser(
        description= 'Compute idf values from corpus')
    parser.add_argument('corpus', help='word per line')
    parser.add_argument( 'init_embed', help='vocab in w2v format') 
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
    with open(args.init_embed) as init_embeed_f:
        init_embed = [line.split(' ', 1) for line in init_embeed_f]
    logger.info('Writing idfs...')
    with open(args.vocab_out, mode='w') as vocab_f, open(
            args.idf, mode='w') as idf_f, open(
                args.embed_weights, mode='w') as embed_out_f:
        for i, (word, weights_newline) in  enumerate(init_embed):
            # heapq.nlargest( args.cutoff, d_freq.items(),
            # key=operator.itemgetter(1)))
            if word not in d_freq:
                continue 
            vocab_f.write('{}\n'.format(word))
            idf_f.write('{}\n'.format(math.log(float(n_sent)/d_freq[word], 2)))
            embed_out_f.write(weights_newline)

if __name__ == '__main__':
    main()
