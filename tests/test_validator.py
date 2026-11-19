import pytest
from core.validator import sanitize_bucket_name


def test_valid_bucket():
    assert sanitize_bucket_name("  My-Bucket-01  ") == "my-bucket-01"


def test_too_short():
    with pytest.raises(ValueError, match="Panjang"):
        sanitize_bucket_name("ab")


def test_too_long():
    with pytest.raises(ValueError, match="Panjang"):
        sanitize_bucket_name("a" * 64)


def test_invalid_characters():
    with pytest.raises(ValueError, match="karakter"):
        sanitize_bucket_name("my_bucket!")


def test_starts_with_hyphen():
    with pytest.raises(ValueError, match="karakter"):
        sanitize_bucket_name("-mybucket")


def test_ends_with_hyphen():
    with pytest.raises(ValueError, match="karakter"):
        sanitize_bucket_name("mybucket-")


def test_reserved_prefix_goog():
    with pytest.raises(ValueError, match="dicadangkan"):
        sanitize_bucket_name("goog-mybucket")


def test_reserved_prefix_google():
    with pytest.raises(ValueError, match="dicadangkan"):
        sanitize_bucket_name("google-photos")


def test_empty_string():
    with pytest.raises(ValueError, match="kosong"):
        sanitize_bucket_name("   ")


def test_non_string():
    with pytest.raises(TypeError):
        sanitize_bucket_name(12345)
