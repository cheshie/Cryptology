import random
from collections import namedtuple
from math import ceil
from sys import byteorder
from functools import reduce, partial
from Crypto.Util.number import  getPrime, inverse, GCD, isPrime
from Crypto.Hash import SHA256
from binascii import hexlify

# Source: https://gist.github.com/JonCooperWorks/5314103
# Cryptographic functions:
# https://pycryptodome.readthedocs.io/en/latest/src/util/util.html
class RSA():
    def __init__(self, message, security=300, hash=SHA256.SHA256Hash, echo=True):
        self.echo = echo
        if self.echo: print("Bezpieczenstwo: ", security, " bitow")
        if self.echo: print("Wiadomosc: \n", message)
        self.message = message
        self.public  = None
        self.private = None
        self.Hash = hash
        self.security = security
    #

    def generate_keypair(self):
        # https://www.swarthmore.edu/NatSci/echeeve1/Ref/BinaryMath/BinaryMath.html
        p_size = self.security // 2
        q_size = self.security - p_size
        p, q = int(getPrime(p_size)), int(getPrime(q_size))

        if p == q:
            raise ValueError('p and q cannot be equal')
        # n = pq
        n = p * q

        # Totient of n
        phi = (p - 1) * (q - 1)

        # Choose an integer e such that e and phi(n) are coprime
        e = random.randrange(1, phi)
        if self.echo: print("Klucz publiczny: \n", e)

        # Use Euclid's Algorithm to verify that e and phi(n) are comprime
        g = GCD(e, phi)
        while g != 1:
            e = random.randrange(1, phi)
            g = GCD(e, phi)
        if self.echo: print("Test e*d == 1 OK")


        # Use Extended Euclid's Algorithm to generate the private key
        d = inverse(e, phi)
        if self.echo: print("Klucz prywatny: \n", d)

        # Return public and private keypair
        # Public key is (e, n) and private key is (d, n)
        self.public  = namedtuple('public_key', ['e', 'n'])(e=e, n=n)
        self.private = namedtuple('private_key', ['d', 'n'])(d=d, n=n)
    #

    def encrypt(self, plaintext=None):
        if not plaintext:
            plaintext = self.message
        # Convert each letter in the digest of plaintext to numbers based on the character using a^b mod m
        # Then (.to_bytes()) convert each element to a fixed len bytearray. Len is the len of mod, which is a largest
        # Integer that could occur. This way we have message divided into fixed-length blocks
        self.sig = pow(int.from_bytes(plaintext.encode() if self.Hash is None else self.Hash(plaintext.encode()).digest(), byteorder), self.private.d, self.private.n)
        if self.echo: print("Podpis\n", self.sig)
        return self.sig
    #

    def decrypt(self, ciphertext, e = None, n = None):
        # Generate the plaintext based on the ciphertext and key using a^b mod m
        if e is None or n is None:
            return pow(ciphertext, self.public.e, self.public.n)
        else:
            return pow(ciphertext, e, n)
    #

    def check_signature(self, message, sig):
        org_message = message.encode() if self.Hash is None else self.Hash(message.encode()).digest()
        org_message = int.from_bytes(org_message, byteorder)
        if self.echo: print("Weryfikacja podpisu:", self.decrypt(sig) == org_message)
    #

    def get_msg_to_bytes(self):
        if self.echo: print("Wiadomosc w bajtach: \n", hexlify(self.message.encode()).decode().upper())
    #
#

# Experiment 1
def no_message_attack():
    # https: // crypto.stackexchange.com / questions / 20085 / which - attacks - are - possible - against - raw - textbook - rsa
    # Probably:
    cRSA = RSA(hash=None, message="Losowa wiadomosc", echo=False)
    cRSA.generate_keypair()
    # Attacker gets random signature from random message
    sig = cRSA.encrypt()
    # Generates m
    m = pow(sig, cRSA.public.e, cRSA.public.n)
    # Now he gets pair of signature, m which are correct, meaning
    # he "created" (or just has) a signature for a random message without knowing the private key
    print("Signature oraz podrobiona wartosc m (s, m): \n", sig,'\n', m)
    print("Weryfikacja 'decrypt(sig)' == m: ")
    print(cRSA.decrypt(sig) == m)
    #

# Experiment 2
def chosen_plaintext_attack():
    m1 = "Losowa wiadomosc 1"
    m2 = "Inna losowa wiad"

    cRSA = RSA(hash=None, message=m1, echo=False)
    cRSA.generate_keypair()
    # m = m1 * m2 mod N
    m = (int.from_bytes(m1.encode(), byteorder) * int.from_bytes(m2.encode(), byteorder)) % cRSA.public.n
    # m1
    sig1 = cRSA.encrypt()
    # m2
    cRSA.message = "Inna losowa wiad"
    sig2 = cRSA.encrypt()
    # Now, attacker:
    # s = s1 * s2 mod N
    sig = (sig1 * sig2) % cRSA.public.n
    print(cRSA.decrypt(sig) == m)


# Experiment 3
# Many attacks here:
# https://crypto.stackexchange.com/questions/8059/prove-that-textbook-rsa-is-susceptible-to-a-chosen-ciphertext-attack
# https://crypto.stackexchange.com/questions/6713/low-public-exponent-attack-for-rsa
# https://github.com/sonickun/cryptools/blob/master/cryptools/rsa.py
# https://www.youtube.com/watch?v=nrgGU2mUum4
# https://en.wikipedia.org/wiki/Coppersmith%27s_attack
# It is actually a Coppersmith method, accoring to: https://en.wikipedia.org/wiki/Coppersmith%27s_attack
def weak_public_exponent_attack():
    # m ** e mod N:
    ciphertext = 2829246759667430901779973875
    e=3
    N=74863748466636279180898113945573168800167314349007339734664557033677222985045895878321130196223760783214379338040678233908010747773264003237620590141174028330154012139597068236121542945442426074367017838349905866915120469978361986002240362282392181726265023378796284600697013635003150020012763665368297013349
    cRSA = RSA(hash=None, message=None, echo=False)

    m = int(pow(ciphertext, e ** -1)) + 1
    print(m.to_bytes(10, byteorder).rstrip(b'\x00'))
    print(m ** e % N) # Encipher again to verify

# Experiment 4
def broadcast_attack():
    # https://rosettacode.org/wiki/Chinese_remainder_theorem
    def chinese_remainder(n, a):
        sum = 0
        prod = reduce(lambda a, b: a * b, n)
        for n_i, a_i in zip(n, a):
            p = prod // n_i
            sum += a_i * pow(p, -1, n_i) * p
        return sum % prod

    # Generate keys
    cRSA = RSA(hash=None, message="a", echo=False)
    cRSA.generate_keypair()

    # Encipher message with three different modules
    get_n = lambda x: getPrime(x) * getPrime(x)
    # modules =  [1927, 187, 667] => for testing
    modules = [get_n(50) for x in range(3)]
    assert modules[0] != modules[1] and modules[1] != modules[2]
    cphtxts = []
    for md in modules:
        cphtxts.append(cRSA.decrypt(int.from_bytes(cRSA.message.encode(), byteorder), e=3, n=md))

    # Calculate CRT of modules and ciphertexts
    x = chinese_remainder(modules, cphtxts)
    print("x", x)
    # Calculate root of x in order to retrieve plaintext
    print("plaintext: ", ceil(x ** (1./3.)).to_bytes(20, byteorder).rstrip(b'\x00').decode())
#


def benchmark_rsa():
    from timeit import timeit
    cRSA = RSA(hash=None, message="Za oknem pada deszcz..", echo=False)
    for x in [2048, 3072, 4096, 7680]:
        cRSA.security = x
        cRSA.generate_keypair()
        print(f"enc for {x}: ", timeit(partial(cRSA.encrypt, ), number=5))
        sig = cRSA.encrypt()
        print(f"verify for {x}: ", timeit(partial(cRSA.check_signature, cRSA.message, sig), number=5))
        print("-"*10)
#


def main():
    cRSA =  RSA(hash=None, message="Za oknem pada deszcz..", security=2048)
    cRSA.generate_keypair()
    sig = cRSA.encrypt()
    cRSA.check_signature(cRSA.message, sig)

# main()

