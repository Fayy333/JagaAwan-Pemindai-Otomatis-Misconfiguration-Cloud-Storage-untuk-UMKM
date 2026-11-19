from cryptography.fernet import Fernet


def generate_key() -> bytes:
    """Buat kunci Fernet baru (AES-128-CBC + HMAC-SHA256)."""
    return Fernet.generate_key()


def encrypt(data: str, key: bytes) -> bytes:
    """Enkripsi string data menjadi bytes terenkripsi."""
    return Fernet(key).encrypt(data.encode("utf-8"))


def decrypt(token: bytes, key: bytes) -> str:
    """Dekripsi bytes terenkripsi menjadi string asli."""
    return Fernet(key).decrypt(token).decode("utf-8")
