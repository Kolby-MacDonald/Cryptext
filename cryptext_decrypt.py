PRIVATE_KEY = '34X81CG5SI)T#V:0%H?Q/D7B|;FL6!=^"ZJEUO~@+R 9*M$.WP_(NY2KA-&' #Demonstration Private Key Example

def decrypt():
    enc_data = str(input("Enter the THINGSPEAK MESSAGE: "))
    split_data = (enc_data.split(']')) #Split the message from it's altered sent form.
    message = (split_data[0])[1:]
    public_key = (split_data[1])[1:]
    outStr = ''
    for i in range(len(message)): #Decrypt by reversing the assymetric encryption.
        new_i = PRIVATE_KEY.index(message[i]) - PRIVATE_KEY.index(public_key[i])
        if new_i < 0:
            i += len(PRIVATE_KEY)
        outStr += PRIVATE_KEY[new_i]
    print(f'The Decrypted Message is: {outStr}')

decrypt()