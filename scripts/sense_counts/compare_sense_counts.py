#!/usr/bin/python
# vim: set fileencoding=utf-8 :

"""Compares sense counts."""
from argparse import ArgumentParser
from operator import itemgetter

import numpy as np
from scipy.stats import entropy, linregress, pearsonr, spearmanr
from sklearn.metrics import cohen_kappa_score


def parse_arguments():
    parser = ArgumentParser(
        description='Compares sense counts.')
    parser.add_argument('file1', help='the first file.')
    parser.add_argument('file2', help='the second file.')
    parser.add_argument('--lower', '-l', action='store_true',
                        help='lowercase words in the dictionaries.')
    parser.add_argument('--partial', '-p',
                        help='subtract the effect of this file from file1 and '
                             'file2 by computing the partial correlation. In '
                             'order for this to word, the subtracted '
                             'dictionary has to include all words that occur '
                             'in file1 and file2.')
    args = parser.parse_args()

    return args.file1, args.file2, args.lower, args.partial


def read_dict_file(dict_file, lower):
    def _lower(s):
        return s.lower() if lower else s
    with open(dict_file) as inf:
        return {_lower(k): float(v) for k, v in
                (line.strip().split("\t") for line in inf)}


def js_divergence(p, q):
    m = (p + q) / 2
    return (entropy(p, m) + entropy(q, m)) / 2


def cos_number(a, b):
    return (a / np.linalg.norm(a)).dot(b / np.linalg.norm(b))


def common_dicts(dict1, dict2):
    """
    Return the parts of dict1 and dict2 that correspond to the common keys in
    both as lists of tuples.
    """
    common_keys = dict1.viewkeys() & dict2.viewkeys()
    d1 = {k: v for k, v in dict1.iteritems() if k in common_keys}
    d2 = {k: v for k, v in dict2.iteritems() if k in common_keys}
    l1 = sorted(d1.iteritems(), key=itemgetter(0))
    l2 = sorted(d2.iteritems(), key=itemgetter(0))
    return l1, l2, common_keys


def dict_vectors(dict1, dict2):
    """Returns the dictionary vectors for the common keys."""
    l1, l2, common_keys = common_dicts(dict1, dict2)
    v1 = np.array(map(itemgetter(1), l1))
    v2 = np.array(map(itemgetter(1), l2))
    return v1, v2, common_keys


def compare_dicts(dict1, dict2):
    """Computes various correlation metrics between two dictionaries."""
    v1, v2, common_keys = dict_vectors(dict1, dict2)
    sp = tuple(spearmanr(v1, v2))
    ps = pearsonr(v1, v2)
    cn = cos_number(v1, v2)
    kappa = cohen_kappa_score(v1.round(), v2.round())
    dist1 = v1 / v1.sum()
    dist2 = v2 / v2.sum()
    return {'dict1': len(dict1), 'dict2': len(dict2), 'common': len(common_keys),
            'kl': entropy(dist1, dist2), 'js': js_divergence(dist1, dist2),
            'spearman': sp, 'pearson': ps, 'cos': cn, 'kappa': kappa}


def subtract_dict(data_dict, base_dict):
    """
    Subtracts the effect of base_dict from data_dict via partial correlation.

    See http://math.bme.hu/~koitomi/statprog2011osznegyedikgyak.html.
    """
    ld, lb, common_keys = common_dicts(data_dict, base_dict)
    vd = np.array(map(itemgetter(1), ld))
    vb = np.array(map(itemgetter(1), lb))
    slope, intercept, _, _, _ = linregress(vb, vd)
    vdiff = vd - (vb * slope + intercept)
    vmin = np.min(np.min(vdiff), 0)  # Get rid of negative numbers (for KL)
    return {ld[i][0]: vdiff[i] - vmin + 0.001 for i in xrange(len(ld))}


if __name__ == '__main__':
    dict_file1, dict_file2, lower, dict_file_partial = parse_arguments()
    dict1 = read_dict_file(dict_file1, lower)
    dict2 = read_dict_file(dict_file2, lower)
    if dict_file_partial:
        dict_partial = read_dict_file(dict_file_partial, lower)
        dict1 = subtract_dict(dict1, dict_partial)
        dict2 = subtract_dict(dict2, dict_partial)
    d = compare_dicts(dict1, dict2)
    print 'words 1 & words 2 & shared words & Spearman & Pearson & KL & JS & cos & Cohen \\\\'
    print '{} & {} & {} & {} & {} & {:.3} & {:.3} & {:.3} & {:.3} \\\\'.format(
        d['dict1'], d['dict2'], d['common'],
        '{:.3} @ {:.3}'.format(*d['spearman']),
        '{:.3} @ {:.3}'.format(*d['pearson']), d['kl'], d['js'], d['cos'], d['kappa'])
