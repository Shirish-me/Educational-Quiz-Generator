import secrets

# Generate a random secret key
secret_key = secrets.token_hex(16)  # Generates a random key of 32 hex characters (16 bytes)
print(secret_key)
