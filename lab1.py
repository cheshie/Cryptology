from binascii import hexlify, unhexlify
from operator import xor
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class MyAES:
    def __init__(self, m):
        self.key = b'\x9d\xa5\xd9\x07\xf5\xed\r\xaeW\xe1\xe8X"\xd5\x08u'
        self.iv  = b"\xeev\x89\x85\x19\xd1'\xe8\x04\xd0\xe9\xbfR\x1b\xc0:"
        self.m   = m
        self.deciphered = []
        self.padlist    = []
        self.range_byte = [bytes([i]) for i in range(0, 255)]
    #
    # Encrypt message
    def encrypt(self):
        # Create encrypted string
        encrypted = AES.new(self.key, AES.MODE_CBC, self.iv).encrypt(pad(self.m.encode(), AES.block_size, style='pkcs7'))
        # Create a list of [[ b, l, o, c, k, 1], [...] ...] data
        self.enc = [row for row in [encrypted[i * AES.block_size:(i + 1) * AES.block_size]
                 for i in range((len(encrypted) + AES.block_size - 1) // (AES.block_size))]]
        # Copy ciphertext to be able to tamper with it without losing any data
        self.ccopy = self.enc[:]
    #

    # Check whether padding is correct
    def padding_oracle(self):
        raw = b''.join(self.ccopy)
        try:
            unpad(AES.new(self.key, AES.MODE_CBC, self.iv).decrypt(raw), AES.block_size, style='pkcs7')
        except ValueError:
            return 500
        else:
            return 200
    #

    def oracle_attack(self):
        # Iterate over blocks
        for block in range(2, len(self.enc)+1):
            # Iterate over bytes in one block
            for padding in range(1, 0xF + 2):
                self.fill_padlist(padding)

                # Generate random byte from byte range 0 - 255 and check it with oracle
                for hbyte in self.range_byte:
                    self.rplc_row_nr(padding, hbyte)

                    # Check whether oracle returned correct padding for non-original byte (if) original byte (else)
                    if self.padding_oracle() == 200:
                        if hbyte != bytes([self.enc[-2][-padding]]):
                            self.calc_p2_i2(hbyte, padding)
                            break
                        else:
                            self.calc_p2_i2(hbyte, padding)
                            break
            # Reinitialize copy of ciphertext and padlist
            self.block_cleanup()
    #

    # Replace element rplc_nr in [-2] block for rplc_byte
    def rplc_row_nr(self, rplc_nr, rplc_byte):
        self.ccopy =  self.ccopy[:-2] + [self.ccopy[-2][:-rplc_nr] + rplc_byte
                                         + self.ccopy[-2][len(self.ccopy[-2]) - rplc_nr + 1:]] + self.ccopy[-1:]
    #

    # If, in particular block, any bytes are already deciphered
    # Based on padlist, calculate bytes to replace at the end of currently attacked block (i.e. \x02 \x02)
    def fill_padlist(self, padding):
        if len(self.padlist):
            for i, pd in enumerate(self.padlist):
                self.rplc_row_nr(i + 1, bytes(map(xor, self.padlist[-i - 1], bytes([padding]))))
    #

    # Calculate plaintext nad intermediary state byte values and save them to lists
    def calc_p2_i2(self, hbyte, padding):
        I2 = self.xor(hbyte, bytes([padding]))
        P2 = self.xor(bytes([self.enc[-2][-padding]]), I2)
        self.deciphered = [P2] + self.deciphered
        self.padlist = [I2] + self.padlist
    #

    # Clean padlist for new block, shorten ciphertext and make a copy of it in order to tamper with it
    def block_cleanup(self):
        self.padlist = []
        # delete the last block from original ciphertext
        self.enc = self.enc[:-1]
        # Paddings calculated after first byte in each block - to make i.e. \x02 \x02 etc happen
        self.ccopy = self.enc[:]
    #

    def xor(self, byte_a, byte_b):
        return bytes(map(xor, byte_a, byte_b))
    #

    def print_ciphertext(self):
        print('\nCiphertext: ')
        for x in self.enc: print(hexlify(x).decode().upper())
    #

    # Print results of the attack
    def print_deciphered(self):
        print("Solution: ")
        for x in self.deciphered:
            try:
                print(x.decode(), end="")
            except UnicodeDecodeError as x:
                print("#", end="")
    #
#

print("CBC padding oracle attack demo\nPrzemyslaw Samsel 2020")
m = input("Plaintext: \n")
cobj = MyAES(m if m != "" else "One must acknowledge with cryptography no amount of violence will ever solve a math problem.")
cobj.encrypt()
cobj.print_ciphertext()
cobj.oracle_attack()
cobj.print_deciphered()
