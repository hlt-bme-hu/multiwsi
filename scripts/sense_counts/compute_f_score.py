#!/usr/bin/python
# vim: set fileencoding=utf-8 :

"""Computes the F-score for binary adaptivity."""
from argparse import ArgumentParser
from functools import partial
from multiprocessing import Pool
import os
import re


def parse_arguments():
    parser = ArgumentParser(
        description='Computes the F-score for binary adaptivity.')
    parser.add_argument('--dictionary', '-d', required=True,
                        help='the dictionary counts file against which the '
                             'embeddings are measured.')
    parser.add_argument('--lower', '-l', action='store_true',
                        help='lowercase words in the dictionaries.')
    parser.add_argument('--processes', '-p', type=int, default=1,
                        help='the number of processes to use parallel.')
    parser.add_argument('embeddings', nargs='+',
                        help='the embedding count files we are evaluating.')
    args = parser.parse_args()

    return args.dictionary, args.lower, args.processes, args.embeddings


def read_dict_file(dict_file, lower):
    def _lower(s):
        return s.lower() if lower else s
    with open(dict_file) as inf:
        return {_lower(k): float(v) for k, v in
                (line.strip().split("\t") for line in inf)}


def common_dicts(dict1, dict2):
    """
    Return the parts of dict1 and dict2 that correspond to the common keys in
    both as lists of tuples.
    """
    common_keys = dict1.viewkeys() & dict2.viewkeys()
    d1 = {k: v for k, v in dict1.iteritems() if k in common_keys}
    d2 = {k: v for k, v in dict2.iteritems() if k in common_keys}
    return d1, d2, common_keys


def rate_embedding(embedding_file, dict_file, lower):
    dictionary, embedding, _ = common_dicts(
        read_dict_file(dict_file, lower), read_dict_file(embedding_file, lower))

    gold = {k for k, v in dictionary.iteritems() if v > 1}
    positives = {k for k, v in embedding.iteritems() if v > 1}
    negatives = {k for k, v in embedding.iteritems() if v <= 1}
    tp = float(len(gold & positives))
    fp = float(len(positives - gold))
    fn = float(len(negatives & gold))
    #tn = float(len(negatives - gold))
    precision = tp / (tp + fp) if tp + fp > 0 else 1.0
    recall = tp / (tp + fn) if tp + fn > 0 else 1.0
    f1_score = 2 * tp / (2 * tp + fn + fp)
    return precision, recall, f1_score


def print_latex_table(data, dict_file):
    print r'\begin{table*}'
    print r'\begin{tabular}{ lrrr }'
    print r'Resources & Precision & Recall & F-score \\'
    print r'\midrule'
    for resource, scores in sorted(data):
        print r'{} & {} \\'.format(
            os.path.basename(resource).replace('_', '\_'),
            ' & '.join(re.sub(r'0+$', '0', '%.3f' % score) for score in scores))
    print r'\bottomrule'
    print r'\end{tabular}'
    print r'\caption{{{}}}'.format(
        'Resources vs {}'.format(
            os.path.basename(dict_file).replace('_', '\_')))
    print r'\end{table*}'


def main():
    (dict_file, lower, processes, embedding_files) = parse_arguments()
    p = Pool(min(processes, len(embedding_files)))
    input_files = sorted(embedding_files)
    res = p.map(partial(rate_embedding, dict_file=dict_file, lower=lower),
                input_files)
    print_latex_table(zip(input_files, res), dict_file)


if __name__ == '__main__':
    main()
