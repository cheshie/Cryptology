from LFSR import LFSR, Galois, Fibonacci, XORSHIFT

# Main class that programmer can interact with
# In order to use a specific random number generator
class PRNG:
    def __init__(self, iS : "Initial states for all LFSRs", tm : "Tapmasks for all LFSRs",
                 gen : "PRNG used. Default is Geffe"=None, LFSR : "LFSR of choice" = None):
        # Default generator and default LFSR
        if gen  is None: gen  = self.Geffe
        if LFSR is None: LFSR = (Galois, Galois, Galois)
        # Make sure you give required number of initial vectors to registers
        # Also make sure lists containing these vectors are of the same length
        # List of LFSR's must
        assert len(tm) == len(iS) and len(tm) == len(LFSR) == gen.required_generators
        self.gen = gen
        self.iS  = iS
        self.tm  = tm
        self.LFSR = LFSR
    # Function takes polynomial mod 2 as a binary string
    # i.e. 10101 => x^4 + x^2 + 1 as argument
    # returns True if polynomial is primitive
    # False otherwise
    # Primitive polynomial as tapmask is used to generate
    # entire cycle for LFSR(n) of size 2 ^ n - 1
    # Need more research, this is not an easy task
    # see https://www.embeddedrelated.com/showarticle/1193.php
    # see https://www.embeddedrelated.com/showarticle/1070.php
    # see www.quadibloc.com/crypto/co040801.htm
    def check_if_poly_is_primitive(self, poly: "binary string"):
        pass
    # Take number of bits that polynomial must fit in
    # generates string of binary that represents
    # a random primitive polynomial for given powers
    # returns binary string that might be safely used
    # as a tapmask for a generator's LFSR's
    # need more research - see function above
    def generate_primitive_poly(self, bits : "int"):
        pass
    #
    # Returns a fully functional PRNG generator that returns 1's and 0's in str format, bit by bit
    # Works by mapping initial vectors into pairs and calling chosen LFSR for initialization
    def get_generator(self):
        # Map into initial states into a list of 2-el tuple(s): (is_i, tm_i)
        lfsrs = tuple(zip(self.iS, self.tm))
        lfsrs = [self.LFSR[i](state[0], state[1]) for i,state in enumerate(lfsrs)]
        return self.gen(lfsrs=lfsrs)
    #
    # Implements shrinking generator
    # It returns 1 or 0 for each iteration using next() method (bcoz it's a generator())
    class Geffe:
        required_generators = 3
        def __init__(self, lfsrs: "Chosen LFSRs from: Galois, Fibonacci, XORSHIFT"):
            # Geffe's generator has only 3 registers
            self.regs = (lfsrs[0], lfsrs[1], lfsrs[2])
            self.val  = ''
        #
        def __next__(self):
            digit = str((next(self.regs[0]) & next(self.regs[1])) ^ (not next(self.regs[0]) & next(self.regs[2])))
            self.val += digit
            return digit
        #
        def __iter__(self):
            return self
        #
    #
    # Implements shrinking generator
    # It returns 1 or 0 for each iteration using next() method (bcoz it's a generator())
    class Shrinking:
        required_generators = 2
        def __init__(self, lfsrs: "Chosen LFSR from: Galois, Fibonacci, XORSHIFT"):
            # Shrinking generator has only 2 registers
            self.regs = (lfsrs[0], lfsrs[1])
            self.val = ''
            self.A   = next(self.regs[0])
            self.S   = next(self.regs[1])
        #
        def __next__(self):
            while self.A != 1:
                self.A = next(self.regs[0])
                self.S = next(self.regs[1])
            digit = str(self.S)
            self.val += digit
            return digit
        #
        def __iter__(self):
            return self
        #
    #
    # Implements Stop and Go
    # It returns 1 or 0 for each iteration using next() method (bcoz it's a generator())
    class StopAndGo:
        required_generators = 3
        def __init__(self, lfsrs: "Chosen LFSR from: Galois, Fibonacci, XORSHIFT"):
            # StopAndGo generator has only 3 registers
            self.regs = (lfsrs[0], lfsrs[1], lfsrs[2])
            self.val = ''
            self.v1, self.v2, self.v3 = next(self.regs[0]), next(self.regs[1]), next(self.regs[2])
        #
        def __next__(self):
            self.v1 = next(self.regs[0])
            if self.v1:
                self.v2 = next(self.regs[1])
            else:
                self.v3 = next(self.regs[1])
            digit = str(self.v2 ^ self.v3)
            self.val += digit
            return digit
        #
        def __iter__(self):
            return self
        #
    #
#