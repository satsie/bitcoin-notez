import hashlib
import hmac
import base58

from ecdsa import SigningKey, SECP256k1

original_private_key = 'A546B34748F6CC6A456C9787F6C8A45E41BBC8AAF2828DBA7D950887F1E2E6BA'

# This file contains a bunch of BIP-32 examples for things like:
# - deriving a master private key and chain code
# - converting a private key to a master xpriv
# - getting both compressed and uncompressed master public keys
# - converting a master public key to a master xpub
# - deriving a child private key and chain code
# - converting the child private key to WIF format
# - deriving a child public key (both compressed and uncompressed)
# - deriving a child address

#########################################
#   master private key and chain code   #
#########################################

print('\n========= m/0 ROOT =========')

# This is a constant defined in BIP-32
key = 'Bitcoin seed'
message = original_private_key

# Get the master private key and chain code by performing an HMAC-SHA512 on the private key
hmac_result = hmac.new(bytes(key, 'utf-8'), bytes.fromhex(message),
                       hashlib.sha512).hexdigest()

master_private_key = hmac_result[0:64]
master_chain_code = hmac_result[64:128]

print('\nMaster private key: \n' + master_private_key)
print('\nMaster chain code: \n' + master_chain_code)

####################
#   master xpriv   #
####################

# Let's get the master extended private key (xpriv)
# This is based on the "Serialization format" section of BIP-32

# 4 bytes for network: a constant defined in BIP-32
mainnet_network_private = '0488ADE4'

# 1 byte for depth: 0x00 since this is the root level
depth = '00'

# 4 bytes for the parent key fingerprint: 0x00000000 since this is the root level
parent_key_fingerprint = '00000000'

# 4 bytes for the child number: 0x00000000 since this is the master key
child_number = '00000000'

# concatenate everything with master chain code and 33 byte master private key
extended_private_key_hex = mainnet_network_private + depth + parent_key_fingerprint + child_number + master_chain_code + '00' + master_private_key

# Perform a base58check encoding over it
extended_private_key = base58.b58encode_check(bytes.fromhex(extended_private_key_hex)).decode("UTF-8")

print('\nMaster extended private key:\n' + extended_private_key)

##################
#   public key   #
##################

# Use a library to do the scalar multiplication needed to derive the public key. Public key = private key * secp256k1 generator point
ecdsa_signing_key = SigningKey.from_string(bytes.fromhex(master_private_key),
                                           curve=SECP256k1)
uncompressed_public_key = ecdsa_signing_key.verifying_key.to_string().hex()

public_key_x = uncompressed_public_key[0:64]
public_key_y = uncompressed_public_key[65:128]

# for compressed keys, the prefix is 02 if y is even, and 03 if y is odd
public_key_first_byte = '02' if int(public_key_y, 16) % 2 == 0 else '03'
compressed_master_public_key = public_key_first_byte + public_key_x

# Uncompressed keys have a prefix of 04
print('\nUncompressed master public key: 04' + uncompressed_public_key)
print('\nCompressed master public key: ' + compressed_master_public_key)

############
#   xpub   #
############

# Let's get the master extended public key (xpub)
# This is based on the "Serialization format" section of BIP-32

# 4 bytes for network: a constant defined in BIP-32
mainnet_network_public = '0488B21E'

# concatenate everything with master chain code and 33 byte compressed master public key
extended_public_key_hex = mainnet_network_public + depth + parent_key_fingerprint + child_number + master_chain_code + compressed_master_public_key

# Perform a base58check encoding over it
extended_public_key = base58.b58encode_check(bytes.fromhex(extended_public_key_hex)).decode("UTF-8")

print('\nMaster extended public key:\n' + extended_public_key)

########################
#   Expected Answers   #
########################

#Use a library to verify that the values above are correct

import bip32

print('\n========= EXPECTED ANSWERS =========')

mybip32 = bip32.BIP32.from_seed(bytes.fromhex(original_private_key))

m_xpriv = mybip32.get_xpriv_from_path("m")
[m_chain_code, m_privkey_bytes] = mybip32.get_extended_privkey_from_path("m")
m_pubkey = mybip32.get_pubkey_from_path("m").hex()

print('\nMaster private key:\n' + m_privkey_bytes.hex())
print('\nMaster chain code:\n' + m_chain_code.hex())
print('\nMaster extended private key:\n' + m_xpriv)
print('\nCompressed master public key:' + m_pubkey)

############################################
#   m/0 child private key and chain code   #
############################################

print('\n========= m/0 CHILD =========')

# Now derive a child key using the master public key, the master private key, master chain code, and index 0

# Step 1 - combine the master parent key and index
index_0 = '00000000'
parent_key_index = compressed_master_public_key + index_0

# Step 2 - perform an HMAC-SHA512 on it, with the chain code as the key
child_key_hmac_result = hmac.new(bytes.fromhex(master_chain_code), 
                                 bytes.fromhex(parent_key_index), 
                                 hashlib.sha512).hexdigest()

# Step 3 - the rhs is the child chain code
child_chain_code = child_key_hmac_result[64:128]
print('\nchild chain code (m/0):\n' + child_chain_code)

# Step 3 - the lhs gets added to the private key and then mod n is performed on the sum (addition modulo n)
# n is the order of the secp256k1 curve, FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFE BAAEDCE6 AF48A03B BFD25E8C D0364141
secp256k1_order_hex = 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141'
n = int(secp256k1_order_hex, 16)

child_lhs = child_key_hmac_result[0:64]
sum_lhs_private_key = int(child_lhs, 16) + int(master_private_key, 16)

child_private_key = hex(sum_lhs_private_key % n)[2:]
print('\nchild private key (m/0):\n' + child_private_key)

# EXTRA - not part of exercise, but done to verify that the code is correct
# Convert m/0 child private key to WIF
mainnet_wif_prefix = '80'
child_private_key_extended = mainnet_wif_prefix + child_private_key + '01'
m0_private_key_wif_sha256_hash1 = hashlib.sha256(bytes.fromhex(child_private_key_extended)).hexdigest()
m0_private_key_wif_sha256_hash2 = hashlib.sha256(bytes.fromhex(m0_private_key_wif_sha256_hash1)).hexdigest()
m0_private_key_wif_checksum = m0_private_key_wif_sha256_hash2[:8]
m0_private_key_wif_hex = child_private_key_extended + m0_private_key_wif_checksum
m0_private_key_wif = base58.b58encode(bytes.fromhex(m0_private_key_wif_hex)).decode("UTF-8")
print('\nchild private key in WIF format:\n' + m0_private_key_wif)

########################
# m/0 child public key #
########################

# Now derive the child public key
ecdsa_signing_key2 = SigningKey.from_string(bytes.fromhex(
  child_private_key),
                                            curve=SECP256k1)
uncompressed_child_public_key = ecdsa_signing_key2.verifying_key.to_string(
).hex()

child_public_key_x = uncompressed_child_public_key[0:64]
child_public_key_y = uncompressed_child_public_key[65:128]

# for compressed keys, the prefix is 02 if y is even, and 03 if y is odd
child_public_key_first_byte = '02' if int(child_public_key_y,
                                          16) % 2 == 0 else '03'
compressed_child_public_key = child_public_key_first_byte + child_public_key_x

# Uncompressed keys have a prefix of 04
print('\nUncompressed child public key: 04' + uncompressed_child_public_key)
print('\nCompressed child public key: ' + compressed_child_public_key)

# All values above have also been confirmed accurate with https://guggero.github.io/cryptography-toolkit/#!/hd-wallet

########################
#   Expected Answers   #
########################
import bip32

print('\n========= EXPECTED ANSWERS =========')

mybip32 = bip32.BIP32.from_seed(bytes.fromhex(original_private_key))

m0_xpriv = mybip32.get_xpriv_from_path("m/0")
[m0_chain_code, m0_privkey_bytes] = mybip32.get_extended_privkey_from_path("m/0")
m0_pubkey = mybip32.get_pubkey_from_path("m/0").hex()

print('\nchild chain code (m/0):\n' + m0_chain_code.hex())
print('\nchild private key (m/0):\n' + m0_privkey_bytes.hex())
print('\nchild extended private key (m/0):\n' + m0_xpriv)
print('\ncompressed child public key (m/0):\n' + m0_pubkey)

########################
#      m/0 address     #
########################

print('\n========= m/0 ADDRESS (compressed) =========')

# HASH-160 to get the payload
m0_address_sha256 = hashlib.sha256(bytes.fromhex(compressed_child_public_key)).hexdigest()
m0_address_ripemd160 = hashlib.new('ripemd160', bytes.fromhex(m0_address_sha256)).hexdigest()
m0_address_payload_with_prefix = '00' + m0_address_ripemd160

# double hash to get the checksum
m0_address_checksum_hash1 = hashlib.sha256(bytes.fromhex(m0_address_payload_with_prefix)).hexdigest()
m0_address_checksum_hash2 = hashlib.sha256(bytes.fromhex(m0_address_checksum_hash1)).hexdigest()

m0_address_base58_payload = m0_address_payload_with_prefix + m0_address_checksum_hash2[:8]
m0_address_base58_encoded = base58.b58encode(bytes.fromhex(m0_address_base58_payload))

# compressed because we used the compressed_child_public_key to generate it
print('\nm/0 address (compressed):\n' + m0_address_base58_encoded.decode('ascii'))