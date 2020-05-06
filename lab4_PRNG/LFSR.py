# Generic class to operate on LFSRs
# All specific LFSRs inherit methods and params from it
class LFSR:
    def __init__(self, registry_state : "Initial registry state"="11111111", tapmask : "initial tap mask or polynomial"="10000001"):
        assert len(tapmask) == len(registry_state) # initial registry and tapmask lengths must be equal
        self.st = int(registry_state, 2)
        self.tm = int(tapmask, 2)
    #
    # Having tapmask 1001 is same as x**4 + x**1
    # For this instance, return [4, 1] (in general, a list of powers)
    def get_powers(self):
        return [i+1 for i, val in enumerate(bin(self.tm)[::-1]) if val == '1'][::-1]
    #
    def get_lsb(self):
        return int(bin(self.st)[-1])
    #
    def get_str(self, nr):
        return bin(nr).lstrip('0b')
    #
#


# Implements Galois LFSR. On each iteration returns 0 or 1
class Galois(LFSR):
    def __next__(self):
        if self.st & 1:
            self.st = (self.st >> 1) ^ self.tm
            return self.get_lsb()
        else:
            self.st >>= 1
            return self.get_lsb()
    #
    def __iter__(self):
        return self
    #
    def __repr__(self):
        return self.get_lsb()
    #
#


# Implements Fibonacci LFSR. On each iteration returns 0 or 1
class Fibonacci(LFSR):
    def __next__(self):
        bit = self.popcnt(self.st & self.tm)
        self.st  = (self.st >> 1) | (bit << (len(self.get_str(self.tm)) - 1))
        return self.get_lsb()
    #
    def __iter__(self):
        return self
    #
    # hamming distance - number of 1's in a binary
    def popcnt(self, nr):
        return bin(nr).count('1')
    #
#


# Implements XORSHIFT LFSR. On each iteration returns 0 or 1
class XORSHIFT(LFSR):
    def __next__(self):
        for i, pw in enumerate(self.get_powers()):
            if pw % 2:
                self.st ^= self.st << pw
            else:
                self.st ^= self.st >> pw
        return self.get_lsb()
    #
    def __iter__(self):
        return self
    #
#