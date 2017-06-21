import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('dim')
    parser.add_argument('vocab')
    parser.add_argument('sense_vects')
    parser.add_argument('--out_fn')
    return parser.parse_args()


def jiweil_postproc(args):
    full_vocab = [line.strip() for line in open(args.vocab)]
    used_vocab = set()
    output_lines = []
    with open(args.sense_vects) as embed_f:
        for line in embed_f:
            line = line.strip()
            if ' ' in line:
                field1, tail = line.split(maxsplit=1)
            else:
                field1 = line
            if field1 == 'word':
                try:
                    # line is like "word 0"
                    word_i = int(tail)
                except:
                    word_i = int(tail.split()[1]) 
                used_vocab.add(word_i)
            elif field1.startswith('sense'):
                # line is like "sense0" or "sense0 0.8816724201743471"
                continue
            else:
                output_lines.append('{} {} {}'.format(full_vocab[word_i], field1, tail))
    if not args.out_fn:
        args.out_fn = '{}.mse'.format(args.sense_vects) 
    with open(args.out_fn, mode='w') as out_f:
        out_f.write('{} {}\n'.format(len(used_vocab), args.dim))
        for line in output_lines:
            out_f.write('{}\n'.format(line))


if __name__ == '__main__':
    jiweil_postproc(parse_args())
