#!/usr/bin/python
# vim: set fileencoding=utf-8 :

"""Compares sense counts."""
from argparse import ArgumentParser
from operator import itemgetter

import numpy as np
from scipy.stats import spearmanr, pearsonr
from sklearn.metrics import cohen_kappa_score


def parse_arguments():
    parser = ArgumentParser(
        description='Compares sense counts.')
    parser.add_argument('file1', help='The first file.')
    parser.add_argument('file2', help='The second file.')
    args = parser.parse_args()

    return args.file1, args.file2


def read_dict_file(dict_file):
    with open(dict_file) as inf:
        return dict(line.strip().split("\t") for line in inf)


def kl_divergence(p, q):
    return (p * np.log2(p / q)).sum()


def js_divergence(p, q):
    m = (p + q) / 2
    return (kl_divergence(p, m) + kl_divergence(q, m)) / 2


def cos_number(a, b):
    return (a / np.linalg.norm(a)).dot(b / np.linalg.norm(b))


def compare_dicts(file1, file2):
    dict1 = read_dict_file(file1)
    dict2 = read_dict_file(file2)
    common_keys = dict1.viewkeys() & dict2.viewkeys()
    v1 = np.array(map(itemgetter(1), sorted(
        ((k, float(v)) for k, v in dict1.iteritems() if k in common_keys),
        key=itemgetter(0))))
    v2 = np.array(map(itemgetter(1), sorted(
        ((k, float(v)) for k, v in dict2.iteritems() if k in common_keys),
        key=itemgetter(0))))
    sp = tuple(spearmanr(v1, v2))
    ps = pearsonr(v1, v2)
    cn = cos_number(v1, v2)
    kappa = cohen_kappa_score(v1.round(), v2.round())
    dist1 = v1 / v1.sum()
    dist2 = v2 / v2.sum()
    return {'dict1': len(dict1), 'dict2': len(dict2), 'common': len(common_keys),
            'kl': kl_divergence(dist1, dist2), 'js': js_divergence(dist1, dist2),
            'spearman': sp, 'pearson': ps, 'cos': cn, 'kappa': kappa}


if __name__ == '__main__':
    dict_file1, dict_file2 = parse_arguments()
    d = compare_dicts(dict_file1, dict_file2)
    print 'words 1 & words 2 & shared words & Spearman & Pearson & KL & JS & cos & Cohen \\\\'
    print '{} & {} & {} & {} & {} & {:.3} & {:.3} & {:.3} & {:.3} \\\\'.format(
        d['dict1'], d['dict2'], d['common'],
        '{:.3} @ {:.3}'.format(*d['spearman']),
        '{:.3} @ {:.3}'.format(*d['pearson']), d['kl'], d['js'], d['cos'], d['kappa'])
