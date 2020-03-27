# -*- coding: utf-8 -*-
import secrets
from functools import reduce


""" constants """


ROUNDS = 8  # num of rounds
BLOCK_SIZE = 8  # block size in bytes
BLOCK_SIZE_BITS = BLOCK_SIZE * 8  # block size in bits
SECRET = 0xD73A01986CB1DDF7  # base key (64-bit)

encoding = 'utf-8'


""" util functions """


# bitwise circular right shift
def ror(x, n, xsize):
    shift = n % xsize
    return tail(x, shift) << (xsize - shift) | (x >> shift)


# bitwise circular left shift
def rol(x, n, xsize):
    shift = n % xsize
    return tail(x, xsize - shift) << shift | head(x, shift, xsize)


# get first n bits of a number
def head(x, n, xsize):
    return x >> (xsize - n)


# get last n bits of a number
def tail(x, n):
    return x & ~(~0 << n)


# generation func
def f(subBlock, key):
    f1 = rol(subBlock, 9, subBlock.bit_length())
    f2 = ror(key, 11, key.bit_length()) + subBlock
    return f1 ^ (not f2)


# split a number into n-bit chunks
def split(block, n):
    return [(block >> i) & ~(~0 << n) for i in
            reversed(range(0, block.bit_length(), n))]

#    hexa = to_n_size_hexa(block, ceil(block.bit_length(), n * 8))
#    count = len(hexa) * 4 // n
#    return [int(hexa[i:i+count]) for i in range(0, len(hexa), count)]
#
#
#def to_n_size_hexa(block, n):
#    assert ceil(block.bit_length(), 8) <= n * 8
#    hexa = hex(block)[2:]
#    return "0" * (n * 2 - len(hexa)) + hexa


# split block into half-block_size chunks
def halves(block, block_size):
    return tuple(split(block, ceil(block_size, 2) // 2))


# get the closest integer larger than n divisible by div
# if n is divisible by div, return n
def ceil(n, div):
    return n + div - n % div if n % div else n


# join a list of numbers into one number
def join(subblocks):
    return reduce(lambda l, r: l << ceil(r.bit_length(), 8) | r, subblocks)


# convert string to hex
def string_to_hex(s, debug=False):
    hex_chars = [ch.encode(encoding).hex() for ch in s]
    hexa = '0x' + reduce(lambda x, y: x + y, hex_chars)
    if debug:
        print(hexa)
    return int(hexa, 16)


# convert hex to string
def hex_to_string(hexa, debug=False):
    s = bytes.fromhex(hex(hexa)[2:]).decode(encoding)
    if debug:
        print(s)
    return s


""" crypto functions """


# generate key for r-th round
def gen_rkey(r, secret, block_size=64):
    return (ror(secret, r * 3, block_size)) &\
            int("1" * ceil(block_size // 2, 2), 2)


# generate round keys
def create_rkeys(secret, rounds=8, block_size=64, debug=False):
    round_keys = [gen_rkey(r, secret, block_size) for r in range(rounds)]
    if debug:
        for r, rkey in enumerate(round_keys):
            print("key[{}] = {}".format(r, hex(rkey)))
    return round_keys


# encrypt one block
def feistel(block, round_keys, block_size=64, debug=False):
    assert block.bit_length() <= block_size
    if debug:
        print("feistel block: {}".format(hex(block)))
    L, R = halves(block, block_size)
    rounds = len(round_keys)

    for r, rkey in enumerate(round_keys):
        if debug:
            print("round {}".format(r))
            print("L = {}  R = {}".format(hex(L), hex(R)))

        Ln = f(L, rkey)
        if r < rounds - 1:
            L, R = R ^ Ln, L
        else:
            L, R = L, R ^ Ln

        if debug:
            print("L = {} R = {}".format(hex(L), hex(R)))

    return join([L, R])


#def feistel_generalized(message, round_keys, block_size=64, debug=False):
#    blocks = split(message, block_size)
#    if debug:
#        print("blocks in = {}".format([hex(x) for x in blocks]))
#    rounds = len(round_keys)
#
#    for r, rkey in enumerate(round_keys):
#        first = blocks[0]
#        blocks = [R ^ f(L, rkey) for L, R in zip(blocks, blocks[1:])]
#        blocks.append(first)
#        if r < rounds - 1:
#            blocks.append(first)
#        else:
#            blocks.insert(0, first)
#
#    return join(blocks)


def cbc(message, secret, iv, rounds=8, decrypt=False, debug=False):
    block_size = ceil(iv.bit_length(), 8)
    round_keys = create_rkeys(secret, rounds, block_size, debug=debug)
    if decrypt:
        round_keys = round_keys[::-1]

    blocks = split(message, block_size)
    key = iv

    for i in range(len(blocks)):
        if debug:
            print("block[{}] = {}".format(i, hex(blocks[i])))
            print("key[{}] = {}".format(i, hex(key)))

        data = blocks[i]
        if not decrypt:
            blocks[i] = feistel(data ^ key, round_keys,
                                block_size, debug)
        else:
            blocks[i] = feistel(data, round_keys,
                                block_size, debug) ^ key
        key = data if decrypt else blocks[i]

    if debug:
        print("block to join: {}".format([hex(b) for b in blocks]))
    return join(blocks)


def cfb(message, secret, iv, rounds=8, decrypt=False, debug=False):
    block_size = ceil(iv.bit_length(), 8)
    round_keys = create_rkeys(secret, rounds, block_size, debug=debug)
    if decrypt:
        round_keys = round_keys[::-1]

    blocks = split(message, block_size)
    key = iv

    for i in range(len(blocks)):
        if debug:
            print("block[{}] = {}".format(i, hex(blocks[i])))
            print("key[{}] = {}".format(i, hex(key)))

        data = blocks[i]
        blocks[i] = feistel(key, round_keys,
                            block_size, debug) ^ data
        key = data if decrypt else blocks[i]

    if debug:
        print("block to join: {}".format([hex(b) for b in blocks]))
    return join(blocks)


def lab1(msg_hex, secret):
    round_keys = create_rkeys(secret, debug=False)

    print("=== Feistel ===")
    print("--- encrypt ---")
    encrypted_msg = feistel(msg_hex, round_keys, debug=True)
    print("encrypted message hex: {}".format(hex(encrypted_msg)))

    print("--- decrypt ---")
    decrypted_msg = feistel(encrypted_msg, round_keys[::-1], debug=False)
    print("decrypted message hex: {}".format(hex(decrypted_msg)))
    assert msg_hex == decrypted_msg
    print("decrypted message: {}"
          .format(hex_to_string(decrypted_msg, debug=False)))


def lab2(msg_hex, secret):
    iv = int(secrets.token_hex(BLOCK_SIZE), 16)
    print("iv: {}".format(hex(iv)))
    
    print("===== CBC =====")
    print("--- encrypt ---")
    cbc_msg = cbc(msg_hex, secret, iv, debug=False)
    print("cbc message hex: {}".format(hex(cbc_msg)))

    print("--- decrypt ---")
    cbc_decrypted_msg = cbc(cbc_msg, secret, iv,  decrypt=True, debug=False)
    print("cbc decrypted message hex: {}".format(hex(cbc_decrypted_msg)))
    assert msg_hex == cbc_decrypted_msg
    print("cbc decrypted message: {}"
          .format(hex_to_string(cbc_decrypted_msg, debug=False)))

    print("===== CFB =====")
    print("--- encrypt ---")
    cfb_msg = cfb(msg_hex, secret, iv, debug=False)
    print("cfb message hex: {}".format(hex(cfb_msg)))

    print("--- decrypt ---")
    cfb_decrypted_msg = cfb(cfb_msg, secret, iv, decrypt=True, debug=False)
    print("cfb decrypted message hex: {}".format(hex(cfb_decrypted_msg)))
    assert msg_hex == cfb_decrypted_msg
    print("cfb decrypted message: {}"
          .format(hex_to_string(cfb_decrypted_msg, debug=False)))


if __name__ == "__main__":
    secret = int(secrets.token_hex(BLOCK_SIZE), 16)
    print("secret: {}".format(hex(secret)))

#    msg = "Hello"
    msg = "Hello World!"
#    msg = "The quick brown fox jumps over a lazy dog."
#    msg = "Note that assumptions on a function are unrelated to the assumptions on the variable it is called on."
    print("message: {}".format(msg))

    msg_hex = string_to_hex(msg, debug=False)
#    msg_hex = int(secrets.token_hex(BLOCK_SIZE), 16)
    print("message hex: {}".format(hex(msg_hex)))

#    lab1(msg_hex, secret)
    lab2(msg_hex, secret)
