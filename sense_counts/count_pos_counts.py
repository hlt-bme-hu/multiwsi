#!/usr/bin/python
# vim: set fileencoding=utf-8 :
"""
Counts how many POS senses a word has -- we use perplexity so that the errors
/ insignificant usage patterns do not influence the result too much.
"""

from argparse import ArgumentParser
import json

from scipy.stats import entropy

def perplexity(distribution):
    return pow(2, entropy(distribution, base=2))


def read_pos_data(pos_freq_data, threshold=0):
    data = {}
    for line in pos_freq_data:
        word, json_freqs = line.rstrip().split("\t")
        freqs = json.loads(json_freqs)
        if word and sum(freqs.values()) > threshold:
            data[word] = freqs
    return data


def parse_arguments():
    parser = ArgumentParser(
        description='Counts how many POS senses a word has -- we use '
                    'perplexity so that the errors / insignificant usage '
                    'patterns do not influence the result too much.')
    parser.add_argument('pos_freq_data', type=open,
                        help='The input file that lists the POS frequencies '
                             'for each word. The format is word <TAB> '
                             '<JSON dump of the POS->frequency dict>.')
    parser.add_argument('--threshold', '-t', type=int,
                        help='The frequency threshold.')
    args = parser.parse_args()

    return args.pos_freq_data, args.threshold


if __name__ == '__main__':
    pos_freq_data, threshold = parse_arguments()
    data = read_pos_data(pos_freq_data, threshold)
    for word, freqs in sorted(data.iteritems()):
        print '{}\t{}'.format(word, perplexity(freqs.values()))
