from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

CIPHERS = {"aes-256-gcm": AESGCM, "chacha20-poly1305": ChaCha20Poly1305}

def encrypt(method, key, nonce, data):
    return CIPHERS[method](key).encrypt(nonce, data, None)

def decrypt(method, key, nonce, data):
    return CIPHERS[method](key).decrypt(nonce, data, None)

def _key(method, password):
    import hashlib
    return hashlib.sha256(password.encode()).digest()
