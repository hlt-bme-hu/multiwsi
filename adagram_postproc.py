import argparse
from itertools import izip
import logging
import os

import numpy

class AdagramToWord2vecConverter():
    """
    Converts  an AdaGram VSM to a word2vec-like format

    Usage 
        python adagram_to_word2vec.py model.epi vocab model.jtxt2 model.mpt
    Creating the input files:
        in julia 
            using AdaGram
            vm, dict = load_model("model.jbin");
            epi = [expected_pi(vm, i) for i in 1:length(dict.id2word)];
            writedlm("model.epi", epi)
            writedlm("vocab", dict.id2word)
            writedlm("model.jtxt", vm.In)
        then in bash 
            tr -d '][' < model.jtxt > model.jtxt2

    Output: 
        like w2v but more vectors for the same word corresponding to different
        senses
    """
    def parse_args(self):
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument("dimension", type=int)
        arg_parser.add_argument("vocab")
        arg_parser.add_argument("vectors")
        arg_parser.add_argument("outfile")
        arg_parser.add_argument(
            "-s", "--max-sense-num", type=int, default=5, metavar="K",
            dest="max_sense_num", 
            help="only keep the K most frequent (highest PI) senses")
        self.argv = arg_parser.parse_args()
        
    def __init__(self):
        format_ = "%(asctime)s %(module)s (%(lineno)s) %(levelname)s %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=format_)
        self.parse_args()
        self.vocab = [line.strip() for line in open(self.argv.vocab)]
        self.get_embed()
        self.outfile = open(self.argv.outfile, mode="w")

    def get_embed(self):
        filename, ext = os.path.splitext(self.argv.vectors)
        logging.info("Reading embedding from {} ...".format(self.argv.vectors))
        flat_vm = self.iter_loadtxt(self.argv.vectors, dtype=float)
        new_shape = (-1, self.argv.dimension, flat_vm.shape[1])
        self.vm = flat_vm.reshape(new_shape)

    def iter_loadtxt(self, filename, delimiter=None, skiprows=0, dtype=float):
        def iter_func():
            with open(filename, 'r') as infile:
                for _ in range(skiprows):
                    next(infile)
                for line in infile:
                    line = line.rstrip().split(delimiter)
                    for item in line:
                        yield dtype(item)
            self.rowlength = len(line)
            
        data = numpy.fromiter(iter_func(), dtype=dtype)
        data = data.reshape((-1, self.rowlength))
        return data

    def main(self):
        big_voc_size = int(sum(numpy.minimum(
            numpy.sum(numpy.any(self.vm, axis=1), axis=1),
            self.argv.max_sense_num*numpy.ones((1,self.vm.shape[0]))).reshape(-1)))
        logging.info("Writing embedding with shape {} {} to {} ...".format(
            big_voc_size, self.vm.shape[1], self.argv.outfile))
        self.outfile.write("{} {}\n".format(big_voc_size, self.vm.shape[1]))
        for word, vecs in izip(self.vocab, self.vm):
            for vec in vecs.T[:self.argv.max_sense_num]:
                if numpy.any(vec):
                    self.outfile.write("{} {}\n".format(word, " ".join(
                        str(cell) for cell in vec)))


if __name__ == "__main__":
    AdagramToWord2vecConverter().main() 
