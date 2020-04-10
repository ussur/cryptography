# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt


""" Linear congruential generator """
def rand(u, m=5, c=0, p=7):
    while True:
        u = (u * m + c) % p
        assert u >= 1 and u <= p - 1
        r = u / p
        assert r > 0 and r < 1
        yield r


def rand_seq(seed, n, m=5, c=0, p=7):
    g = rand(seed, m, c, p)
    return [g.__next__() for i in range(n)]


""" tests """
def test_period(u0, m, p):
    g = rand(u0, m=m, p=p)
    
    L = 1
    r0 = g.__next__()
    while r0 != g.__next__():
        L += 1
        
    return L


def test_correlation(r, k=1):
    numerator = np.mean([a * b for a, b in zip(r[k:], r[:len(r) - k])]) - np.mean(r[:len(r) - k]) * np.mean(r[k:])
    
    denominator = np.mean([ri * ri for ri in r]) - np.mean(r)**2
    
    return numerator / denominator


def test_pi(r):
    c = sum(1 if np.sqrt(r[2*i]**2 + r[2*i+1]**2) < 1 else 0 for i in range(len(r) // 2))
    return 8 * c / len(r)
    

if __name__ == "__main__":
    points = 100
    u0 = 1
    
    M = [1030, 777, 1140671485, 96230]
    P = [99999, 13652, 5406546, 450641]
    
    for m, p in zip(M, P):
        u = list(range(1, p, p // points))
        
        # 1.1. Test generated sequence period
        L = test_period(u0, m, p)
        print("L = {}".format(L))
        # 1.2. Plot L(u0) dependency
        plt.plot(u, [test_period(x, m, p) for x in u])
        plt.show()
        
        r = rand_seq(u0, L, m=m, p=p)
        k_list = list(range(1, L, L // points))
        plt.plot(k_list, [r[k] for k in k_list])
        plt.show()
        
        # 2. Test correlation
        ck = [test_correlation(r, k=k) for k in k_list]
        plt.plot(k_list, ck)
        plt.show()
        
        # 3. Test pi
        pi = test_pi(r)
        print("pi = {}".format(pi))
        print("pi diff = {}".format(np.pi - pi))
