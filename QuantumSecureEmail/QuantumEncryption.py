import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from pathlib import Path
from Crypto.Util.Padding import unpad

#generate random key of given length
def generateRandomKeys(length):
    return np.random.randint(2, size=length)

def measureBases(state, basis):
    if basis == 0: # Z basis
        return state
    else: # X basis
        return 1 - state

def computeQuantumKeys(message):
    key_length = len(message) * 8
    # Alice generates a key and a basis
    alice_key = generateRandomKeys(key_length)
    alice_bases = generateRandomKeys(key_length)
    # Bob generates a basis
    bob_bases = generateRandomKeys(key_length)
    # Alice measures her qubits in her basis
    alice_measurements = [measureBases(alice_key[i], alice_bases[i]) for i in range(key_length)]
    # Bob measures the qubits in his basis
    bob_measurements = [measureBases(alice_key[i], bob_bases[i]) for i in range(key_length)]
    # Both discard the measurements where their bases do not match
    final_key = [alice_measurements[i] for i in range(key_length) if alice_bases[i] == bob_bases[i]]
    # Make sure the key length is valid for AES
    if len(final_key) > 32:
        final_key = final_key[:32]
    elif len(final_key) < 24:
        final_key = final_key + [0] * (24 - len(final_key))
    # Convert the key to bytes
    key = bytes(final_key)
    return key

def quantumEncryptMessage(msg, key, msg_path):
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(msg, AES.block_size))
    with open(msg_path, "wb") as file:
        file.write(key)
        file.write(cipher.iv)
        file.write(ciphertext)
    file.close()    
    return cipher.iv, ciphertext

def quantumDecryptMessage(msg_path):
    with open(msg_path, "rb") as file:
        key = file.read(32)  # The key has a length of 32 bytes
        iv = file.read(16)  # The IV has a length of 16 bytes
        ciphertext = file.read()  # The rest of the file is the encrypted message
    file.close()
    cipher_dec = AES.new(key, AES.MODE_CBC, iv=iv)
    plaintext = unpad(cipher_dec.decrypt(ciphertext), AES.block_size)
    return plaintext
