import math
import random
from itertools import count, islice


# check if a given number is prime
def is_prime(n):
    return n > 1 and all(n % i for i in islice(count(2), int(math.sqrt(n) - 1)))


# calculate the modular inverse x of a and m, i.e. ax ≡ 1 (mod m)
def mod_inverse(a, m):
    if math.gcd(a, m) != 1:
        raise Exception('Modular inverse does not exist')
#    a = a % m
#    for x in range(1, m): 
#        if ((a * x) % m == 1): 
#            return x 
#    return 1
    temp = m + 1
    while temp % a:
        temp += m
    return temp // a


# generate public and private keys for RSA encryption
def generate_keys(p, q):
    if not (is_prime(p) and is_prime(q)):
        raise ValueError('Both numbers must be prime.')
    elif p == q:
        raise ValueError('p and q cannot be equal')
        
    n = p * q  # 1st part of the public key
    
    phi = (p-1) * (q-1)
    e = random.randrange(1, phi)   # 2nd part of the public key
    while math.gcd(phi, e) != 1:
        e = random.randrange(1, phi)
        
    d = mod_inverse(e, phi)  # private key
    
    return n, e, d


def break_key(n):
#    sqrt = round(math.sqrt(n))
#    prime_divisors = (i for i in range(3, sqrt, 2) if is_prime(i) and n % i == 0)
    p = 2432279
    assert n % p == 0
    q = n // p
    return p, q


def rsa_encrypt(message, n, e):
    return [pow(ord(char), e, n) for char in message]


def rsa_decrypt(message, n, d):
    return [pow(part, d, n) for part in message]


def test_rsa(message, p, q):
    print("Input: p={}, q={}".format(p, q))
    
    n, e, d = generate_keys(p, q)
    print("Public key: n={}, e={}".format(n, e))
    print("Private key: d={}".format(d))
    
    print("Message: \"{}\"".format(message))
#    print("Numerical: {}".format("".join(str(ord(x)) for x in message)))
    
    print("===========TEST RSA===========")
    enc = rsa_encrypt(message, n, e)
    print("Encrypted: {}".format("".join(map(str, enc))))
    dec = "".join(chr(ch) for ch in rsa_decrypt(enc, n, d))
    print("Decrypted: \"{}\"".format(dec))
    assert message == dec


def break_rsa():
    #primae numbers for a public key
    n = 889577666850907
    e = 13971
    print("Public key: n={}, e={}".format(n, e))
    
    print("===========HACK RSA===========")
    p, q = break_key(n)
    print("n divisors: p={}, q={}".format(p, q))
    
#    phi = (p-1) * (q-1)
#    d = mod_inverse(e, phi)
    d = 521419261247795
    print("Private key: d={}".format(d))
    
    #encrypted message
    message = 403013074606912545180648978557219641194372024501606729868202878976557455422
    print("Message: {}".format(str(message)))
    
    parts = [403013074606912, 5451806489785, 572196411947, 2024501606729, 8682028789765, 57455422]
    dec_numbers = rsa_decrypt(parts, n, d)
    
    dec_string = str("".join(str(d) for d in dec_numbers))
    print("Decrypted numerical: {}".format(dec_string))
    
    if len(dec_string) % 2:
        dec_string = dec_string + "0"
    dec = "".join(chr(int(dec_string[i:i+2])) for i in range( 0, len(dec_string), 2))
    
    print("Decrypted: \"{}\"".format(dec))


if __name__ == "__main__":
    # hack RSA encrypted message    
    break_rsa()
    print("------------------------------")
    
    # test RSA encryption & decryption
    p = 11
    q = 17
    message = "Top secret"
    test_rsa(message, p, q)
    print("------------------------------\n")
    