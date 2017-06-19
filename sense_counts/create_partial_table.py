#!/usr/bin/python
# vim: set fileencoding=utf-8 :

"""Creates partial metric tables."""
from argparse import ArgumentParser
from functools import partial
from itertools import product
from multiprocessing import Pool
import os
from subprocess import check_output

#from .compare_sense_counts import read_dict_file


def parse_arguments():
    parser = ArgumentParser(
        description='Creates partial metric tables.')
    parser.add_argument('--dictionary', '-d', required=True,
                        help='the dictionary counst file against which the '
                             'embedding counts are measured.')
    parser.add_argument('--base', '-b', action='append',
                        help='the base count files against which the partial '
                             'correlations are run; can specify more.')
    parser.add_argument('--lower', '-l', action='store_true',
                        help='lowercase words in the dictionaries.')
    parser.add_argument('--format', '-f', choices=['latex', 'html'],
                        help='the format of the output table.')
    parser.add_argument('--processes', '-p', type=int, default=1,
                        help='the number of processes to use parallel.')
    parser.add_argument('embeddings', nargs='+',
                        help='the embedding count files we are evaluating.')
    args = parser.parse_args()

    return (args.dictionary, args.base, args.lower, args.format,
            args.processes, args.embeddings)


def run_compare(base_embedding_files, script_file, dict_file, lower):
    """Runs the comparison by invoking compare_sense_counts.py."""
    base_file, embedding_file = base_embedding_files
    output = check_output([script_file] + (['-l'] if lower else []) +
                          (['-p', base_file] if base_file else []) +
                          [dict_file, embedding_file])
    fields = output.split("\n")[1].split(' & ')
    return {embedding_file:
            {base_file: [f.split(' @ ')[0] for f in fields[3: 5]]}}


def recursive_update(dict1, dict2):
    for k, v in dict2.iteritems():
        if k in dict1 and isinstance(v, dict):
            recursive_update(dict1[k], v)
        else:
            dict1[k] = v
    return dict1


def print_html_table(table, dict_file, bases):
    print '<html><head><title>{}</title></head><body>'.format(
        'Resources vs {} (Spearman / Pearson)'.format(
            os.path.basename(dict_file)))
    print '<table border=1>'
    print '<tr><th>Resources</th>'
    for base in sorted(bases):
        if base:
            print '<th>{}</th>'.format(os.path.basename(base))
        else:
            print '<th>Vanilla</th>'
    print '</tr>'
    for embed, data in sorted(table.iteritems()):
        print '<tr><td>{}</td>'.format(os.path.basename(embed))
        for _, values in sorted(data.iteritems()):
            print '<td>{}</td>'.format('&nbsp;/&nbsp;'.join(values))
    print '</table>'


def print_latex_table(table, dict_file, bases):
    print r'\begin{table*}'
    print r'\begin{{tabular}}{{ l | {} }}'.format('r' * len(bases))
    print r'Resources & {} \\'.format(' & '.join(os.path.basename(base)
                                      if base else 'Vanilla' for base in bases))
    print r'\midrule'
    for embed, data in sorted(table.iteritems()):
        print r'{} & {} \\'.format(
            os.path.basename(embed).replace('_', '\_'),
            ' & '.join(' / '.join(values) for _, values in sorted(data.iteritems())))
    print r'\bottomrule'
    print r'\end{tabular}'
    print r'\caption{{{}}}'.format(
        'Resources vs {} (Spearman / Pearson)'.format(
            os.path.basename(dict_file).replace('_', '\_')))
    print r'\end{table*}'


def main():
    (dict_file, base_files, lower,
     output_format, processes, embedding_files) = parse_arguments()
    base_files.insert(0, '')  # the vanilla case
    input_list = list(product(base_files, embedding_files))
    p = Pool(min(processes, len(input_list)))
    script_file = os.path.join(os.path.dirname(__file__),
                               'compare_sense_counts.py')
    fn = partial(run_compare, script_file=script_file, dict_file=dict_file,
                 lower=lower)
    dicts = p.map(fn, input_list)
    table = reduce(recursive_update, dicts)
    if output_format == 'latex':
        print_latex_table(table, dict_file, base_files)
    else:
        print_html_table(table, dict_file, base_files)


if __name__ == '__main__':
    main()
