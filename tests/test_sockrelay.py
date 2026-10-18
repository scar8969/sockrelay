"""A10 aioshadowsocks — tests. Run: pytest test_sockrelay.py"""
import sys, os

import pytest

def test_cipher_aes_roundtrip():
    from aioshadowsocks.ss.ciphers import decrypt, encrypt
    key = b"k" * 32
    nonce = b"n" * 12
    ct = encrypt("aes-256-gcm", key, nonce, b"secret data")
    assert decrypt("aes-256-gcm", key, nonce, ct) == b"secret data"

def test_cipher_chacha_roundtrip():
    from aioshadowsocks.ss.ciphers import decrypt, encrypt
    key = b"k" * 32
    nonce = b"n" * 12
    ct = encrypt("chacha20-poly1305", key, nonce, b"data")
    assert decrypt("chacha20-poly1305", key, nonce, ct) == b"data"

def test_cipher_tamper_detected():
    from aioshadowsocks.ss.ciphers import decrypt, encrypt
    key = b"k" * 32
    nonce = b"n" * 12
    ct = bytearray(encrypt("aes-256-gcm", key, nonce, b"secret"))
    ct[0] ^= 0xFF
    with pytest.raises(Exception):
        decrypt("aes-256-gcm", key, nonce, bytes(ct))

def test_ciphers_registry():
    from aioshadowsocks.ss.ciphers import CIPHERS
    assert "aes-256-gcm" in CIPHERS
    assert "chacha20-poly1305" in CIPHERS
