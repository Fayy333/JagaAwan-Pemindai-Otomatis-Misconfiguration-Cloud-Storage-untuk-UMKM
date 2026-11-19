from core.crypto import generate_key, encrypt, decrypt


def test_roundtrip():
    key = generate_key()
    original = '{"bucket": "test", "overall_risk": "CRITICAL"}'
    token = encrypt(original, key)
    assert decrypt(token, key) == original


def test_different_keys_fail():
    key1 = generate_key()
    key2 = generate_key()
    token = encrypt("hello", key1)
    from cryptography.fernet import InvalidToken
    import pytest
    with pytest.raises(InvalidToken):
        decrypt(token, key2)


def test_encrypted_is_bytes():
    key = generate_key()
    result = encrypt("test", key)
    assert isinstance(result, bytes)
