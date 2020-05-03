from collections import Counter
from re import finditer
from more_itertools import chunked
from PRNG import PRNG

# Testing randomness of PRNGs according
# To FIPS 140-2 (prior to 2002).
# Generate sequence of 20 000 bits as a start
# True => test passed # False => otherwise
class FIPS_TEST:
    def __init__(self, params, gen=None, lfsr=None,  length=20000):
        self.gen      = PRNG(iS=params[0],tm=params[1], gen=gen, LFSR=lfsr).get_generator()
        self.sequence = ''.join(next(self.gen) for i in range(length))
        self.length   = length
    #
    # Count bits '1' in the sequence
    def monobit(self, thresholds : "Default values for test"=(9725, 10275)):
        count_1  = self.sequence.count('1')
        if  count_1 > thresholds[0] and count_1 < thresholds[1]:
            return True
        else:
            return False
    #
    # Divide into 4-bit chunks
    # http://www.cmsim.eu/papers_pdf/april_2013_papers/4_CMSIM_Journal_2013_Min_Chen_Zang_2_273-280.pdf
    def poker(self, chunk_size=4, thresholds : "Default values for test"=(2.16, 46.17)):
        self.sequence = chunked(self.sequence, chunk_size) # divide iterable into n-size chunks
        self.sequence = [''.join(chunk) for chunk in list(self.sequence)] # join chunks
        # Parameters for the test
        combinations  = 2 ** chunk_size # number of possible combinations that self.sequence may contain
        counts   = Counter(self.sequence).most_common() # number of occurences for each chunk
        nr_of_chunks   = self.length / chunk_size
        # Calculate result of test
        X = (combinations / nr_of_chunks ) * sum([cnt ** 2 for ocur, cnt in counts]) - nr_of_chunks
        # return test value
        return True if X > thresholds[0] and X < thresholds[1] else False
    #
    # If there is a sequence of (or more) 26 same bits test fails
    def long_runs(self):
        # return list of repeated sequences of 0 or 1 in generated sequence
        repeated   = [m.group(0) for m in finditer(r"(\d)\1*", self.sequence)]
        # sorted (ascending) list of lengths of these occurences
        occurences = sorted([len(x) for x in repeated])[-1]
        # return test value
        return True if occurences < 26 else False
    #
#