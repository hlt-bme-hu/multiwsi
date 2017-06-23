import argparse
import gzip
from os.path import splitext
import sys
import logging

def neela_filter(inembed_fn, global_fn, sense_fn, ccent_fn):
    with gzip.open(inembed_fn) as inembed_f, \
            open(global_fn, mode='w') as global_f, \
            open(sense_fn, mode='w') as sense_f, \
            open(ccent_fn, mode='w') as ccent_f:
        header = inembed_f.readline().strip().split()
        if len(header) == 4:
            vocab_size, dim, max_sense, vec_per_sense = header
        else:
            vocab_size, dim = header
            vec_per_sense = 2
        sense_files = [sense_f, ccent_f][:int(vec_per_sense)]
        for file_ in global_f, sense_f, ccent_f:
            file_.write('{} {}\n'.format(vocab_size, dim))
        count = 0
        vocab_size = float(vocab_size)
        while True:
            line = inembed_f.readline()
            if line:
                count +=1
                if not count % 10000:
                    sys.stdout.write('\rProgress: {:.1%}'.format(count/vocab_size))
                    sys.stdout.flush()
                if line.startswith(' '):
                    logging.warn('word starts with space')
                    word = None
                    sense_num = line.strip()
                else:
                    word, sense_num = line.strip().split()
                    logging.debug('{} {}'.format(word, sense_num))
                vector = inembed_f.readline() # vector ends with '\n'
                if word:
                    logging.debug('global')
                    global_f.write('{} {}'.format(word, vector))
                for sense in range(int(sense_num)):
                    logging.debug('sense {}'.format(sense_num))
                    for file_ in sense_files:
                        logging.debug(file_)
                        vector = inembed_f.readline() # vector end with '\n'
                        if word:
                            file_.write('{} {}'.format(word, vector))
            else:
                sys.stdout.write('\n'.format(count/vocab_size))
                break


def parse_args(): 
    parser = argparse.ArgumentParser(
        description='Filter Neelakantan sense vectors by type')
    parser.add_argument('inembed_gz')
    parser.add_argument('--glob')
    parser.add_argument('--sense')
    parser.add_argument('--clust_cent')
    args = parser.parse_args()
    if not args.glob or not args.sense or not args.clust_cent:
        if not args.glob and not args.sense and not args.clust_cent:
            root, ext =  splitext(args.inembed_gz)
            args.glob = '{}_glob.w2v'.format(root)
            args.sense = '{}_sense.mse'.format(root)
            args.clust_cent = '{}_cluscent.mse'.format(root)
        else:
            raise Exception(
                'optional command-line arguments: specified none or all')
    return args

if __name__ == '__main__':
    format_ = "%(asctime)s %(module)s (%(lineno)s) %(levelname)s %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=format_)
    args = parse_args()
    neela_filter(args.inembed_gz, args.glob, args.sense, args.clust_cent)
