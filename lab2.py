from collections import namedtuple
from itertools import accumulate
from random import sample, choice
from Crypto.Util import number
from numpy import sum
from timeit import timeit


# Tests
# print("Recovered: ", sss(S=91694388364660, n = 5, k = 3, p = 91994388364979, coeffs = (4103884901909, 5481390490034)))
# print("Recovered: ", sss(S=11, n = 5, k = 3, p = 13, coeffs = (7, 8)))

class Secret():
    def __init__(self, prime_size: "Number of bytes for secret"=4, parties_nr: "Number of parties that share main secret"=1,
                 parties_share: "Number of members in party"=(8,), k_shares: "Number of member in party to recover the secret"=(3,)):
        assert parties_nr == len(parties_share) == len(k_shares)
        self.l_stronnictw = parties_nr
        self.prime_size = prime_size
        party = namedtuple("party", ["number", "shares", "k", "secret"])
        # range(number.getPrime(self.prime_size)
        self.parties  = [party(*params) for params in zip(range(1, parties_nr + 1), parties_share, k_shares, sample(range(7337488745629403488410174275830423641502142554560856136484326749638755396267050319392266204256751706077766067020335998122952792559058552724477442839630133), parties_nr))]
        self.main_secret  = list(accumulate([x.secret for x in self.parties], lambda a, b: a ^ b))[-1]
        print("Glowny sekret: \n", self.main_secret)
    #

    def calc_partys_secret(self):
        for s in self.parties:
            p = number.getPrime(self.prime_size)
            sekret_stronnictwa = choice(range(p))
            print("-"*10)
            print(f"Stronnictwo nr: {s.number}")
            print("Sekret stronnictwa: \n", sekret_stronnictwa)
            print("Odtworzony sekret:  \n",self.sss(S=sekret_stronnictwa, n = s.shares, k = s.k, p = p, coeffs = sample(range(p), s.k - 1)))
    #

    def calc_main_secret(self):
        assert len(self.parties) > 1
        return list(accumulate([x.secret for x in self.parties], lambda a, b: a ^ b))[-1]
    #

    # Secret sharing using Lagrange polynomials
    # More: https://en.wikipedia.org/wiki/Shamir%27s_Secret_Sharing
    def sss(self, S:'Secret'  = 11, n:'Number of shadows' = 5, k:'Number of shadows necessary to recover the secret' = 3,
                       p:'Prime modulo'=13, coeffs:'Coefficients of lagrange polynomial W(x) = coeff1, coeff2, ... , coeffn-1'=(7, 8)):
        # Check whether user passed proper number of coefficients to build lagrange polynomial
        if len(coeffs) != k - 1:
            print("Wrong lagrange polynomials for the given m")
            return None

        # Conditions that must be met before executing
        assert p > S and p > n
        # Shadow bases may be random numbers
        shadows = sample(range(p), n)
        # Lagrange polynomial: (returned actual shadows m1, m2 ... m5 (n shadows))
        values_sh = [sum([a * pow(arg, b, p) for a,arg,b in zip(coeffs + [S], [x] * (len(coeffs) + 1), range(len(coeffs) + 1)[::-1])]) % p for x in shadows]
        # Left this original loop for reference:
        # def poly_value(poly, arg):
        # sk = 0
        # n  = range(len(poly))[::-1]
        # sk = sum([a * pow(x, b, p) for a,x,b in zip(poly, [arg] * len(poly), range(len(poly))[::-1])])
        # for i,x in enumerate(poly):
        # sk +=  x * pow(arg, n[i], p)
        # return sk
        # values_sh = [poly_value(coeffs + [S], x) % p for x in shadows]

        # Recovery of the secret:

        print("Udzialy: ")
        for sh, sh_val in zip(shadows, values_sh):
            print(f"{sh}, {sh_val}")

        # Shadows which are chosen for the recovery of the secret
        given_shadows = {x for x in sample(list(zip(values_sh, shadows)), k)}
        recovered_secret = sum([list(accumulate([m[0]] + [(gs_wth_crr[1] % p) * pow((gs_wth_crr[1] - m[1]), -1, p)
                                                          for gs_wth_crr in given_shadows - {m}], lambda a, b: (a * b) % p))[-1]
                                for m in given_shadows])
        # Original loop, for the reference
        # gen_sum = 0
        # for m in given_shadows:
        #     cm = m[0] # should assign current shadow here
        #     for gs_wth_crr in given_shadows - {m}:
        #             cm *= ((gs_wth_crr[1] % p) * pow((gs_wth_crr[1] - m[1]), -1, p)) % p
        #     print("CORR: ", cm % p)
        #     gen_sum += cm % p
        return recovered_secret % p
    #

print("Kryptologia: Laboratorium nr 2 - Podzial sekretow.")
print("")
s = Secret(63, parties_nr=3, parties_share=(6, 4, 10), k_shares=(3, 3, 6))
s.calc_partys_secret()
print("Glowny sekret: \n", s.calc_main_secret())





