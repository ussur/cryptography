# -*- coding: utf-8 -*-
import sys


""" constants """


ROUNDS = 8  # num of rounds
BLOCK_SIZE = 8  # block size in bytes
BLOCK_SIZE_BITS = BLOCK_SIZE * 8  # block size in bits
SECRET = 0xD73A01986CB1DDF7  # base key (64-bit)
F32 = 0xFFFFFFFF


""" util functions """


# bitwise circular right shift
def ror(x, n, xsize):
    return (x >> n) + (x << (xsize - n))


# bitwise circular left shift
def rol(x, n, xsize):
    remains = x >> (xsize - n)
    return (x << n) - (remains << xsize) + remains


# round key generation
def gen_rkey(r):
    return (ror(SECRET, r * 3, BLOCK_SIZE_BITS)) & F32


# gen func
def f(subBlock, key):
    f1 = rol(subBlock, 9, sys.getsizeof(subBlock))
    f2 = ror(key, 11, sys.getsizeof(key)) + subBlock
    return f1 ^ (not f2)


def split(block):
    return block >> (int(BLOCK_SIZE_BITS/2)) & F32, block & F32


def join(left, right):
    return (left << (int(BLOCK_SIZE_BITS/2))) + (right & F32)


""" functions """


# generate keys for a round
def create_rkeys(debug=False):
    round_keys = [gen_rkey(r) for r in range(ROUNDS)]
    if debug:
        for r, rkey in enumerate(round_keys):
            print("key[{}] = {}".format(r, hex(rkey)))
    return round_keys


# encrypt one block
def cipher(block, round_keys, debug=False):
    L, R = split(block)

    for r, rkey in enumerate(round_keys):
        if debug:
            print("round {}".format(r))
            print("L = {}  R = {}".format(hex(L), hex(R)))

        Ln = f(L, rkey)
        if r < ROUNDS - 1:
            L, R = R ^ Ln, L
        else:
            L, R = L, R ^ Ln

        if debug:
            print("L = {} R = {}".format(hex(L), hex(R)))

    return join(L, R)


def main():
    print("key {}".format(hex(SECRET)))
    round_keys = create_rkeys(debug=False)

    msg = 0xaa876392feb31059
    print("message {}".format(hex(msg)))

    encrypted_msg = cipher(msg, round_keys, debug=False)
    print("encrypted message {}".format(hex(encrypted_msg)))

    decrypted_msg = cipher(encrypted_msg, round_keys[::-1], debug=False)
    print("decrypted message {}".format(hex(decrypted_msg)))


if __name__ == "__main__":
    main()
