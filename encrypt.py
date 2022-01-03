import base64
from string import *
import random


chars = ascii_letters + digits + punctuation + " £"
char2int = {c: i for i, c in enumerate(chars, 1)}
int2char = {i: c for i, c in enumerate(chars, 1)}

def generate(length):
    return "".join([random.choice(chars) for i in range(length)])

def encrypt(string=None, key=None, layers=1, _rec_level=0, verbose=False):    
    temp_key_ints = [char2int[char] for char in key]
    
    string = base64.b64encode(string.encode()).decode()

    key_ints = []
    for index, i in enumerate(temp_key_ints):
        if index % 2 == 0:
            key_ints.append(i ** 2)
        else:
            key_ints.append(i * 2)

    string_ints = []
    for index, integer in enumerate([char2int[char] for char in string], 1):
        shift = integer + index + sum(key_ints)
        if shift <= len(chars):
            string_ints.append(shift)
        else:
            if shift % len(chars) == 0:
                string_ints.append(len(chars))
            else:
                string_ints.append(shift % len(chars))

    enc = "".join([int2char[i] for i in string_ints])
    if verbose:
        print(f"Layer {_rec_level + 1} encryption: {enc}")
    if layers > 1:
        _rec_level += 1
        layers -= 1 
        enc = encrypt(enc, key, layers, _rec_level)    
    return enc

def decrypt(string=None, key=None, layers=1, _rec_level=0, verbose=False):    
    temp_key_ints = [char2int[char] for char in key]

    key_ints = []
    for index, i in enumerate(temp_key_ints):
        if index % 2 == 0:
            key_ints.append(i ** 2)
        else:
            key_ints.append(i * 2)

    string_ints = []
    for index, integer in enumerate([char2int[char] for char in string], 1):
        shift = integer - index - sum(key_ints)
        if shift > 0:
            string_ints.append(shift)
        else:
            if shift % len(chars) == 0:
                string_ints.append(len(chars))
            else:
                string_ints.append(shift % len(chars))

    msg = "".join([int2char[i] for i in string_ints])
    if verbose:
        print(f"Layer {layers} decryption: {msg}")
    try:
        msg = base64.b64decode(msg.encode()).decode()
    except Exception:
        msg = generate(len(msg))
    if layers > 1:
        _rec_level += 1
        layers -= 1
        msg = decrypt(msg, key, layers, _rec_level)    
    return msg

"""
if __name__ == "__main__":
    key = "encryption_key"
    msg = "Hello World!"
    enc = encrypt(msg, key, len(key))
    print(enc)
    print(decrypt(enc, key, len(key)))
"""

import random
from string import *
import numpy as np

chars = ascii_letters + digits + punctuation + " £"
char2int = {c: i for i, c in enumerate(chars, 1)}
int2char = {i: c for i, c in enumerate(chars, 1)}

def shift(string, n):
    return "".join([chars[i - 1 + (n % len(chars) if n >= len(chars) else n)]
                         for i in [char2int[char] for char in string]])

key = input("Enter an encryption key: ")
    
def get_hash(key):
    key_ints = [char2int[char] for char in key]
    seed = int("".join([str(i) for i in key_ints]))

    random.seed(seed)
    hash_value = np.prod([random.random() for i in range(len(key))])
    print(hash_value)
    return hash_value
"""
i = 0
msg = "a"
while True:
    i += 1
    msg += "a"
    if get_hash(msg) == 0.0:
        break

print("Max length:", i)
"""
print(get_hash(key))