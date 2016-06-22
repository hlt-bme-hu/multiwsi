#!/usr/bin/python
# vim: set fileencoding=utf-8 :

"""Counts the number of distributions per resource."""
from argparse import ArgumentParser
from collections import Counter
from functools import partial
from itertools import groupby
from multiprocessing import Pool


def parse_arguments():
    parser = ArgumentParser(
        description='Counts the number of distributions per resource.')
    parser.add_argument('--max-senses', '-m', type=int, default=6,
                        help='the maximum number of meanings that gets a '
                             'row in the table; meanings above this number '
                             'are merged.')
    parser.add_argument('--processes', '-p', type=int, default=1,
                        help='the number of processes to use parallel.')
    parser.add_argument('resources', nargs='+',
                        help='the resource count files we are evaluating.')
    args = parser.parse_args()

    return args.max_senses, args.processes, args.resources


def read_dict_file(dict_file, lower=False):
    def _lower(s):
        return s.lower() if lower else s
    with open(dict_file) as inf:
        return {_lower(k): float(v) for k, v in
                (line.strip().split("\t") for line in inf)}


def count_senses(resource, max_senses):
    counts = {word: round(senses) for word, senses in
              read_dict_file(resource).iteritems()}
    cnt = Counter()
    for sense, grp in groupby(sorted(counts.values())):
        if sense < max_senses:
            cnt[sense] = len(list(grp))
        else:
            cnt[max_senses] += len(list(grp))
    return {resource: cnt}


def recursive_update(dict1, dict2):
    for k, v in dict2.iteritems():
        if k in dict1 and isinstance(v, dict):
            recursive_update(dict1[k], v)
        else:
            dict1[k] = v
    return dict1


def print_latex_table(table, max_senses):
    print r'\begin{table*}'
    print r'\begin{{tabular}}{{ l | {} }}'.format('r' * max_senses)
    print r'Resources & {}+ \\'.format(
        ' & '.join(str(i + 1) for i in xrange(max_senses)))
    print r'\midrule'
    for resource, counts in sorted(table.iteritems()):
        print r'{} & {} \\'.format(
            resource.replace('_', '\_'),
            ' & '.join(str(count) for _, count in sorted(counts.iteritems())))
    print r'\bottomrule'
    print r'\end{tabular}'
    print r'\caption{{{}}}'.format(
        'Word sense distribution for the examined resources')
    print r'\end{table*}'


def main():
    (max_senses, processes, resources) = parse_arguments()
    p = Pool(min(processes, len(resources)))
    input_files = sorted(resources)
    table = reduce(recursive_update, p.map(
        partial(count_senses, max_senses=max_senses), input_files))
    print_latex_table(table, max_senses)


if __name__ == '__main__':
    main()
