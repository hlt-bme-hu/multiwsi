import argparse
from collections import Counter
import logging
import os


def parse_args():
    parser = argparse.ArgumentParser(
        description='Extracts the vocabulary from the corpus.')
    parser.add_argument('corpus', help='sentence/document per line')
    parser.add_argument('init_embed', help='vectors in w2v format')
    # w2v embeddings contain words in freq order (that may != idf ord)
    parser.add_argument('vocab_out')
    parser.add_argument('--cutoff', type=int, default=199999)

    args = parser.parse_args()
    if os.path.isfile(args.vocab_out):
        parser.error('output file {} exists'.format(args.vocab_out))
    return args


def get_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(module)s (%(lineno)s) %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger


if __name__ == '__main__':
    logger = get_logger()
    args = parse_args()
    logger.info('Counting words...')
    word_freqs = Counter()
    with open(args.corpus) as inf:
        for i, line in enumerate(inf):
            if i % 1000000 == 0 and i > 0:
                logger.info('{:,} sentences read'.format(i))
            word_freqs.update(line.strip().lower().split())

    logger.info('Reading embedded words...')
    with open(args.init_embed) as inf:
        inf.readline()  # Header
        embed_set = {line.strip().split(' ', 1)[0].lower()
                     for line in inf.readlines()}

    logger.info('Assembling list...')
    vocab = ['UUUNKKK']
    for word, _ in word_freqs.most_common():
        if word in embed_set:
            vocab.append(word)

    logger.info('Writing vocabulary...')
    with open(args.vocab_out, 'w') as outf:
        for word in vocab[:args.cutoff + 1]:
            outf.write("{}\n".format(word))
