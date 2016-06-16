import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('vocab')
    parser.add_argument('sense_vects')
    return parser.parse_args()


def jiweil_posproc(args):
    vocab = [line.strip() for line in open(args.vocab)]
    with open(args.sense_vects) as embed_f:
        while True:
            vals = embed_f.readline().strip().split()
            if vals:
                len_vals = len(vals)
                if len_vals == 4:
                    raise NotImplementedError(
                    'the version that wrties lines of the form `"word" word_i\
                    sense_i prob` is not handled')
                elif len_vals in [1, 2]:
                    if vals[0] == 'word':
                    # line is like
                    # len_vals == 2 "word 0" or 
                        word_i = int(vals[1])
                    else:
                        # line is like "sense0" or "sense0 0.8816724201743471"
                        pass
                    continue
                else:
                    print '{} {}'.format(vocab[word_i], ' '.join(vals[1:]))
            else:
                break


if __name__ == '__main__':
    jiweil_posproc(parse_args())
