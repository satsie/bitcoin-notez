from ecdsa import SigningKey, SECP256k1, VerifyingKey
import ecdsa
import base64
import hashlib
import random

# A complete implementation of message signing and verification using the
# "old Bitcoin Armory Style" (sometimes incorrectly referred to as "Satoshi style")
# See https://delvingbitcoin.org/t/satoshi-style-message-signing/850

# Sample values come from Chapter 4, challenge 3 (HD wallets)
address_compressed = '1NGqssC5PSTZ95oYbfs3wmHtRMoEvsDy6A'
private_key = '2770b74d984baa5cd94bb505647a49143cda0d13a1c1f02320bfe27167873f51'

compressed_public_key = '030d31df30e92e6c97ce6c2875df6b7a49cfff5844a17beb4feeaa76632d6e31b7'

# Not actually used in this repl but helpful for cross checking with other tools. These values also comes from chapter 4, challenge 3
private_key_wif = 'KxYNriaz9cw4JZEZX5jpBEqCQXVphkcK5zR9cSYTkyV6tedgL3ER'
compressed_public_key = '030d31df30e92e6c97ce6c2875df6b7a49cfff5844a17beb4feeaa76632d6e31b7'

message = "Don't trust, verify"

##################
# HELPER METHODS #
##################

# Add the magic bytes to the message. This code was written before the
# BIP process was established.
# See bitcoin core src/util/message.cpp - https://github.com/bitcoin/bitcoin/blob/v25.0rc1/src/util/message.cpp#L25


def msg_magic(message):
  return "\x18Bitcoin Signed Message:\n" + chr(len(message)) + message


# For some reason the bitcoin core code has this as a double hash.
# https://github.com/bitcoin/bitcoin/blob/v25.0rc1/src/hash.h#L112
def DoubleHash(data):
  return hashlib.sha256(hashlib.sha256(bytes(data, 'utf-8')).digest()).digest()


###################
# MESSAGE SIGNING #
###################

print('###################')
print('# MESSAGE SIGNING #')
print('###################\n')

# Examples this is based on:

# https://github.com/stequald/bitcoin-sign-message/blob/b5e8b478713fdbb8d65e6cd1aeff8b2d5545ff91/signmessage.py#L271

# https://github.com/nanotube/supybot-bitcoin-marketmonitor/blob/master/GPG/local/bitcoinsig.py

# (newest, most current code example)
# https://github.com/shadowy-pycoder/bitcoin_message_tool/blob/master/bitcoin_message_tool/bmt.py

# Step 1 - add the magic bytes to the message
message_magic = msg_magic(message)

# Step 2 - double hash the message
hashed_message = DoubleHash(message_magic)

# Step 3 - sign using ECDSA. This returns the 64 byte signature
ecdsa_signing_key = SigningKey.from_string(bytes.fromhex(private_key),
                                           curve=SECP256k1)

# If you just needed a signature, you could use line of code that has been commented out below
# However we need to know the k value that is used during signature generation. The library does not provide this, so we are going to use the signature generation method that allows us to set it ourselves
# signature = ecdsa_signing_key.sign_digest_deterministic(hashed_message)

# Set the k value and generate a signature (for more information on what k is, see the "Sign" section of this page: https://learnmeabitcoin.com/technical/ecdsa)
# The reason why the k value is so important to is is because we can use it to get the x and y coordinates of the signature (also known as R)
# The signature's header byte depends on the parity of the y coordinate, and the size of the x coordinate.
# In the real world, you want to use a k value that comes from a good source of randomness. Here's some sample code that can be used for generating k securely: https://github.com/tlsfuzzer/python-ecdsa/blob/master/src/ecdsa/keys.py#L1417
# https://asecuritysite.com/encryption/ecdsa3
# k = 344
# N is the order of the secp256k1 curve
N = 115792089237316195423570985008687907852837564279074904382605163141518161494337
k = random.randint(0, N - 1)
signature = ecdsa_signing_key.sign_digest(digest=hashed_message, k=k)

# We now have a signature, and we know the k value that was used to create it.
# ECDSA signatures are made up of two values: r and s
# r is the x coordinate of R, mod n
# n is the order of the secp256k1 curve
# In simpler terms, r = (x coordinate of R) mod n
# The problem is you can't get R (the x, y coordinates of the signature) from just r and s. Luckily, you can compute R by multiplying k by the generator point of the secp256k1 curve
# R = k * G (the generator point)
# see https://github.com/tlsfuzzer/python-ecdsa/blob/master/src/ecdsa/ecdsa.py#L233 for some sample code that uses k to compute R (called p1 in the sample)
# Step 4 - Let's compute R!

# The x and y coordinates of the generator point. Just for reference
# G_x = 55066263022277343669578718895168534326250603453777594175500187360389116729240
# G_y = 32670510020758816978083085130507043184471273380659243275938904335757337482424

# ECC is speshal. can't just multiply. Have to use specific ECC function
R = SECP256k1.generator.__rmul__(k)
R.scale()  # this is just for efficiency

print('Got R')
print(f'    x-coordinate = {R.x()}')
print(f'    y-coordinate = {R.y()}')

# Check if y is even or odd, this will be important when we set the signature's header byte later
y_is_even = False
if (R.y() % 2 == 0):
  y_is_even = True
print(f'\n    y is {"even" if y_is_even else "odd"}')

# Check if x is smaller than the order of the secp256k1 curve, this information will also be used later on for setting the signature's header byte
# N is the order of the secp256k1 curve
N = 115792089237316195423570985008687907852837564279074904382605163141518161494337
x_less_than_n = True

if (R.x() < N):
  x_less_than_n = True
print(
  f'    x is {"" if x_less_than_n else "not "}less than n (the order of the secp256k1 curve)\n'
)

# ECDSA signatures are made up of r and s values
r = signature[0:32]
s = signature[32:64]
# print(f'Length of bytes in r is {len(r)}')

# Sanity check - manually compute the r value (using the R that we got earlier) and make sure it matches the r value returned by the signature
my_r = R.x() % N
r_decimal = int.from_bytes(r, 'big')

if my_r != r_decimal:
  print('r values do not match!!! Check that R was computed correctly')
  print(f'r as a decimal number: {r_decimal}')
  print(f'manually computed r: {my_r}')

# Step 5 - verify
public_key = ecdsa_signing_key.get_verifying_key()
result = public_key.verify_digest(signature, hashed_message)
print(
  f'Signature verification with public key {"passed" if result else "did not pass!!!"}\n'
)
print(f'Public key: {public_key.to_string("compressed").hex()}')

# Step 5 - add the header byte
# header byte = recovery + 27 + (compress ? 4 : 0)
# where recovery = recid
# recid = (R.y)isOdd() | (!x.eq(r) << 1)

# Background reading: https://bitcoin.stackexchange.com/questions/83035/how-to-determine-first-byte-recovery-id-for-signatures-message-signing

# First look at the P2PKH address that the signature corresponds to.
# Is it compressed?
# We'll be working with a set of possible header values that depend on if the address is compressed or not.

# from https://github.com/shadowy-pycoder/bitcoin_message_tool/blob/master/bitcoin_message_tool/bmt.py
headers = [
  [b'\x1b', b'\x1c', b'\x1d', b'\x1e'],  # 27 - 30 P2PKH uncompressed
  [b'\x1f', b'\x20', b'\x21', b'\x22'],  # 31 - 34 P2PKH compressed
  [b'\x23', b'\x24', b'\x25', b'\x26'],  # 35 - 38 P2WPKH-P2SH compressed
  [b'\x27', b'\x28', b'\x29', b'\x2a'],  # 39 - 42 P2WPKH compressed
  [b'\x2b', b'\x2c', b'\x2d', b'\x2e']
]  # 43 - 46 P2WPKH compressed

# The long way of doing it - loop through every possible header value and try them all. This is not ideal. The good thing is since we produced the signature and know the x and y coordinates of it, we can intelligently choose the header byte
#print('Possible signatures:')
# Since we know the address is compressed, so we're going to look at values 31-34
# for header in headers[1]:
#   signature_with_header = base64.b64encode(header + signature).decode('utf-8')
#   # many libraries just do a verification at this point to see which value works
#   print(signature_with_header)

if y_is_even == True:
  if x_less_than_n == True:
    header = headers[1][0]
  else:
    header = headers[1][2]
else:
  if x_less_than_n == True:
    header = headers[1][1]
  else:
    header = headers[1][3]

signature_with_header = base64.b64encode(header + signature).decode('utf-8')
print(f'Signature: {signature_with_header}')
print(f'Message: {message}')
# Public key recovery is why you can verify a signature with just an address: https://bitcoin.stackexchange.com/questions/38351/ecdsa-v-r-s-what-is-v
print(f'Address: {address_compressed}')

#print(f'Length of bytes in the signature is {len(header + signature)}')

# To verify, use one of these message verification tools:
# - https://reinproject.org/bitcoin-signature-tool/#
# - https://checkmsg.org/

########################
# MESSAGE VERIFICATION #
########################

print('\n########################')
print('# MESSAGE VERIFICATION #')
print('########################\n')

# Using these as a guide: https://github.com/stequald/bitcoin-sign-message/blob/b5e8b478713fdbb8d65e6cd1aeff8b2d5545ff91/signmessage.py#L225
# https://github.com/nanotube/supybot-bitcoin-marketmonitor/blob/master/GPG/local/bitcoinsig.py#L195
# https://github.com/shadowy-pycoder/bitcoin_message_tool/blob/master/bitcoin_message_tool/bmt.py#L678
# As well as the bitcoin wiki for P2PKH compressed addresses https://en.bitcoin.it/wiki/Message_signing#ECDSA_signing.2C_with_P2PKH_compressed_addresses

# Step 1 - Decode the base64 signature
decoded_signature = base64.b64decode(signature_with_header)

# Step 2 - Separate the header byte from the signature
# We know we're working with compressed P2PKH in our example, otherwise we could look at the ranges of header bytes to figure out the address type.
header_byte = decoded_signature[0]

# Also get the r and s values
raw_signature = decoded_signature[1:]
signature_r = int.from_bytes(raw_signature[0:32], 'big')
signature_s = int.from_bytes(raw_signature[32:], 'big')
known_r = int.from_bytes(r, "big")
known_s = int.from_bytes(s, "big")

print('Recovered r and s values from the signature')
print(f'    Does the recovered r value match the known r value? {"yes!" if signature_r == known_r else "no!"}')
print(f'    Does the recovered s value match the known s value? {"yes!" if signature_s == known_s else "no!"}')

# Step 3 - get the recid (recovery ID)
# If the header byte is in the range of 31-34, we know we're dealing with compressed P2PKH and can subtract the 4 that was added to indicate compression.
# For handling other address types, see this sample code: https://github.com/shadowy-pycoder/bitcoin_message_tool/blob/master/bitcoin_message_tool/bmt.py#L695
header_value_minus_compression = header_byte
if (header_byte > 30 and header_byte < 35):
  header_value_minus_compression = header_byte - 4

# Subtract 27 to get the recid
recid = header_value_minus_compression - 27

# Step 4 - use the recid to get R, the x and y coordinates of the signature
# x = (recid / 2) * the order of secp256k1 + r
recovered_x = (recid >> 1) * N + signature_r # >> 1 shifts the bits to the right, and it is the same as dividing by 2

# Before going further, we need to identify the p value of the secp256k1 curve
# where p = 2256 - 232 - 29 - 28 - 27 - 26 - 24 - 1 (see https://en.bitcoin.it/wiki/Secp256k1)
p_hex = 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F'
p = int(p_hex, 16)

# now that we know x, we can compute y
# https://crypto.stackexchange.com/a/98364
# recall that for secp256k1, y^2 = x^3 + 7
recovered_y_squared = ((recovered_x * recovered_x * recovered_x) + 7)
alpha = recovered_y_squared

# to get the square root, use the following equation:
# a^((p+1)/4) mod p
exponent = (p + 1) >> 2  # >> 2 is the same as dividing by 4 (it shifts the bits to the right by 2 * 2)
beta = pow(alpha, exponent, p)  # the last argument is value to mod by

# Two possible values for y. To figure out which to use, subtract the recid and check the parity of that value.
recovered_y = beta
if ((beta - recid) % 2 != 0):
  recovered_y = p - beta

# Sanity check x and y
print('\nRecovered R')
print(f'    Do the x coordinates match? {"yes!" if R.x() == recovered_x else "no!"}')
print(f'    Do the y coordinates match? {"yes!" if R.y() == recovered_y else "no!"}')

# Step 5 - Recreate the hashed message
verification_message = "Don't trust, verify"
hashed_verification_message = DoubleHash(msg_magic(verification_message))

# convert it to an integer
z = int.from_bytes(hashed_verification_message, 'big')

# Step 6 - compute e.
# e = (-z) mod n (where n is the order of the secp256k1 curve)
# I don't know where this equation comes from except the bitcoin wiki.
# This section of the normal wiki for ECDSA has a little information on e and z: https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm#Signature_verification_algorithm
e = (-z) % N

# Step 7 - compute the public key
# PublicKey = (R*s + G*e) * modinv(r, n)
Rs = R.__rmul__(signature_s)
Ge = SECP256k1.generator.__rmul__(e)
modular_inverse_r = pow(signature_r, -1, N)

recovered_public_key_point = (Rs.__add__(Ge)).__mul__(modular_inverse_r)
print(f'\nRecovered the public key point:\n   {recovered_public_key_point.to_affine()}')

recovered_public_key = VerifyingKey.from_public_point(recovered_public_key_point,
                                                         curve=SECP256k1)

verification_result = recovered_public_key.verify_digest(
  decoded_signature[1:],
  hashed_verification_message,
  sigdecode=ecdsa.util.sigdecode_string)
print(f'\nCan the public key be used to verify the signature? {verification_result}')

recovered_public_key_y = recovered_public_key_point.to_affine().y()

public_key_prefix = '03'
if (recovered_public_key_y % 2 == 0):
  public_key_prefix = '02'

# Python's integer -> hex conversion with `hex()` doesn't include leading zeroes
compressed_public_key = public_key_prefix + recovered_public_key_point.to_affine().x(
).to_bytes(32, "big").hex()

print(f'Compressed public key (hex): {compressed_public_key}')
expected_compressed_public_key = recovered_public_key.to_string("compressed").hex()
