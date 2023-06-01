# --------------------------------------- #
#      CREATED BY KOLBY MACDONALD         #
# --------------------------------------- #
#    This is an asymmetric encryption and #
# decryption tool that has more possible  #
# combinations than atoms in the oberser- #
# able universe.                          #
#     The three layers of encryption are; #
# A random alpha-numeric character set,   #
# the encrypted message and the encryp-   #
# tion private key.                       #
# ---------------------------------------

from random import sample

PRIVATE_KEY = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()_+-=[]:;<,>?|/. ' #88!

def PrivateKey_Generator():
    global PRIVATE_KEY
    pubKey_rand = ''.join(sample(PRIVATE_KEY, len(PRIVATE_KEY)))
    PRIVATE_KEY = pubKey_rand
    print(f'Your Private Key is: {PRIVATE_KEY}')
 
def encrypt():
    global PRIVATE_KEY
    message = str(input("Enter The Message To Encrypt: "))
    public_key = ''.join(sample(PRIVATE_KEY, len(message)))
    outStr = ''
    for i in range(len(message)):
        new_i = PRIVATE_KEY.index(message[i]) + PRIVATE_KEY.index(public_key[i])
        if new_i >= len(PRIVATE_KEY):
            new_i -= len(PRIVATE_KEY)
        outStr += PRIVATE_KEY[new_i]
    print(f'Public Key: {public_key}')
    print(f'Encrypted Message: {outStr}')
  
def decrypt():
    global PRIVATE_KEY
    PRIVATE_KEY = str(input("Enter Your Private Key: "))
    public_key = str(input("Enter The Public Key: "))
    message = str(input("Enter The Encrypted Message: ")) 
    outStr = ''
    for i in range(len(message)):
        new_i = PRIVATE_KEY.index(message[i]) - PRIVATE_KEY.index(public_key[i])
        if new_i < 0:
            i += len(PRIVATE_KEY)
        outStr += PRIVATE_KEY[new_i]
    print(f'The Decrypted Message is: {outStr}')

#print("------------------------------------------------------------------------------------------------------------------------")
#PrivateKey_Generator()
#print("------------------------------------------------------------------------------------------------------------------------")
encrypt()
print("------------------------------------------------------------------------------------------------------------------------")
decrypt()
print("------------------------------------------------------------------------------------------------------------------------")

