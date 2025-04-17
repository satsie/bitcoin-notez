import hashlib
import base58

# Convert a public key to a bitcoin P2PKH address

# Public key in hex format
public_key = '0342ce81b5538ad5beddf090912f3337f1856d9d2a27a916dc8ac75b71de55deab'

# Perform a SHA-256 hash on the public key
sha256_hash = hashlib.sha256(bytes.fromhex(public_key)).hexdigest()
print('\nSHA-256 hash in hex format:\n' + sha256_hash)

# Now perform a RIPEMD-160 hash on that digest
ripemd160_hash = hashlib.new('ripemd160', bytes.fromhex(sha256_hash)).hexdigest()
print('\nRIPEMD-160 hash in hex format:\n' + ripemd160_hash)

# Add the 00 prefix
payload_with_prefix = '00' + ripemd160_hash
print('\nPayload with 0x00 prefix:\n' + payload_with_prefix)

# Perform a double SHA-256 hash
checksum_hash1 = hashlib.sha256(bytes.fromhex(payload_with_prefix)).hexdigest()
checksum_hash2 = hashlib.sha256(bytes.fromhex(checksum_hash1)).hexdigest()
print('\ndouble SHA-256 for the full checksum:\n' + checksum_hash2)

# Take the first 4 bytes of that to get the checksum
# 1 byte = 2 hex characters
checksum_first_four_bytes = checksum_hash2[0:8]
print('\nFirst 4 bytes of the checksum:\n' + checksum_first_four_bytes)

# Add the checksum to the end of the result
base58_payload = payload_with_prefix + checksum_first_four_bytes
print('\nPayload for base58 encoding:\n' + base58_payload)

# Encode it all in Base58
base58_encoded = base58.b58encode(bytes.fromhex(base58_payload))
print('\nAddress:\n' + base58_encoded.decode('ascii'))

