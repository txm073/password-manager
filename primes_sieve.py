# Iterative implementation of the Sieve of Erotostines to find prime numbers
#import utils
import numpy as np

#@utils.timed
def sieve(n):
    nums = np.arange(2, n, 1)
    marker = np.zeros(n)
    primes = []
    for index, number in enumerate(nums):
        if marker[index] == 0:    
            primes.append(number)
            for i in range(index + number, len(marker), number):
                marker[i] = 1
    return primes

#@utils.timed
def get_primes(n):
    primes = []
    for i in range(1, n):
        factors = [j for j in range(1, i+1) if i % j == 0]
        if len(factors) == 2:
            primes.append(i)
    return primes


string = str
print(string(5))