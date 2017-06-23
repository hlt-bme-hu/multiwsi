#!/usr/bin/python
# vim: set fileencoding=utf-8 :
"""Counts the number of real senses per word in the CMultiVec output."""

from argparse import ArgumentParser
import gzip
import sys

import numpy as np


def parse_arguments():
    parser = ArgumentParser(description='Counts the number of real senses per '
                                        'word in the CMultiVec output.')
    parser.add_argument('embedding', help='The multiembedding file.')
    parser.add_argument('--format', '-f',
                        choices=['neelakantan', 'cmultivec', 'mse', 'mseh'],
                        help='The embedding format.')
    parser.add_argument('--centers-per-word', '-c', default=5, type=int,
                        help='The number of senses per word. Need to specify '
                             'for cmultivec.')
    parser.add_argument('--vocab', '-v', help='The vocabulary. Need to specify '
                        'for cmultivec.')
    parser.add_argument('--zero-threshold', '-z', default=0, type=float,
                        help='If the vector norm falls below this, the sense '
                             'is thrown away.')
    parser.add_argument('--similarity-threshold', '-s', default=1, type=float,
                        help='If the vectors that correspond to two senses are '
                             'closer than this number (in the cosine '
                             'similarity sense), only one of them is kept.')
    args = parser.parse_args()

    return (args.embedding, args.format, args.centers_per_word, args.vocab,
            args.zero_threshold, args.similarity_threshold)


def open_file(file_name, mode='r'):
    if file_name.endswith('.gz'):
        return gzip.open(file_name, mode)
    else:
        return open(file_name, mode)


def read_neelakantan(nk_file):
    """Neelakantan's output format."""
    with open_file(nk_file) as inf:
        header = inf.readline().strip().split()  # dimensions
        no_words = int(header[0])
        vec_per_sense = int(header[3]) if len(header) == 4 else 2
        for word_no in xrange(no_words):
            try:
                line = inf.readline().strip()
                token, senses = line.split()
                inf.readline()  # global vector
                centers = []
                for _ in xrange(int(senses)):
                    for _ in xrange(vec_per_sense - 1):
                        inf.readline()  # "word sense vector"
                    centers.append([float(n) for n in inf.readline().strip().split()])
                if word_no % 5000 == 0 and word_no > 0:
                    print >>sys.stderr, "Read", word_no, "words."
                yield token, centers
            except:
                print >>sys.stderr, "Error in line >{}<".format(line)
                raise
    print >> sys.stderr, "Done."


def read_cmultivec(center_file, vocab_file):
    """CMultiVec format with separate vocabulary and centroid files."""
    with open_file(vocab_file) as vocabf, open_file(center_file) as centerf:
        word, centers = None, []
        for word_no, v_l in enumerate(vocabf):
            token = v_l.strip()[2:]
            vector = [float(n) for n in centerf.readline().strip().split()]
            if token != word:
                if word:
                    yield word, np.array(centers)
                word, centers = token, []
            centers.append(vector)
            if word_no % 5000 == 0 and word_no > 0:
                print >>sys.stderr, "Read", word_no, "words."
        if word:
            yield word, np.array(centers)
    print >> sys.stderr, "Done."


def read_mse(mse_file, header):
    with open_file(mse_file) as inf:
        word, centers = None, []
        if header:
            inf.readline()
        for line in inf:
            fields = line.strip().split()
            token, vector = fields[0], [float(n) for n in fields[1:]]
            if token != word:
                if word:
                    yield word, np.array(centers)
                word, centers = token, []
            centers.append(vector)
        if word:
            yield word, np.array(centers)


def filter_senses(centers, zero_threshold, max_distance):
    """Filters centers that are too close to zero or to one another."""
    dist_to_zero = np.linalg.norm(centers, axis=1)
    norm_centers = centers / np.where(dist_to_zero != 0, dist_to_zero, 1)[:, np.newaxis]
    norm_centers = norm_centers[dist_to_zero >= zero_threshold]
    dists = norm_centers.dot(norm_centers.T)
    dists[np.eye(dists.shape[0]) == 1] = -1
    dists = dists >= max_distance
    for i in xrange(dists.shape[0] - 1, -1, -1):
        if any(dists[i]):
            dists = np.delete(np.delete(dists, i, 0), i, 1)
            centers = np.delete(centers, i, 0)
    return centers


if __name__ == '__main__':
    (embedding_file, eformat, centers_per_word, vocab_file,
     zero_threshold, similarity_threshold) = parse_arguments()
    if eformat == 'neelakantan':
        gen = read_neelakantan(embedding_file)
    elif eformat == 'cmultivec':
        gen = read_cmultivec(embedding_file, vocab_file)
    elif eformat.startswith('mse'):
        gen = read_mse(embedding_file, header=eformat=='mse')
    for word, centers in gen:
        senses = filter_senses(centers, zero_threshold, similarity_threshold)
        print "{}\t{}".format(word, len(senses))
