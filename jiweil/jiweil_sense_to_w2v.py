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
                if len(vals) == 4:
                    # "word", word_i, sense_i, prob
                    word_i = int(vals[1])
                weights = embed_f.readline().strip()
                print '{} {}'.format(vocab[word_i], weights)
            else:
                break


if __name__ == '__main__':
    jiweil_posproc(parse_args())
