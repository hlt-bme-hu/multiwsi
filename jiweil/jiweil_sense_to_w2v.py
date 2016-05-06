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
                if len_vals in [4,2]:
                    #4: "word", word_i, sense_i, prob
                    word_i = int(vals[1])
                elif len_vals == 1:
                    # line is like "sense0"
                    continue
                else:
                    print '{} {}'.format(vocab[word_i], ' '.join(vals[1:]))
            else:
                break


if __name__ == '__main__':
    jiweil_posproc(parse_args())
