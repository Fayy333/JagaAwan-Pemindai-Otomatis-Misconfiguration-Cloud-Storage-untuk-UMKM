import re

BUCKET_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{1,61}[a-z0-9]$")
RESERVED_PREFIXES = ("goog", "google")


def sanitize_bucket_name(raw: str) -> str:
    """
    Validasi dan sanitasi nama bucket GCS.
    Melempar ValueError jika input tidak memenuhi aturan penamaan GCS.
    """
    if not isinstance(raw, str):
        raise TypeError("Nama bucket harus berupa string.")

    name = raw.strip().lower()

    if not name:
        raise ValueError("Nama bucket tidak boleh kosong.")

    if not (3 <= len(name) <= 63):
        raise ValueError(
            f"Panjang nama bucket harus 3–63 karakter (diterima: {len(name)})."
        )

    if not BUCKET_RE.match(name):
        raise ValueError(
            "Nama bucket hanya boleh mengandung huruf kecil, angka, dan tanda hubung, "
            "serta tidak boleh diawali atau diakhiri tanda hubung."
        )

    if any(name.startswith(p) for p in RESERVED_PREFIXES):
        raise ValueError(
            f"Nama bucket tidak boleh diawali dengan kata yang dicadangkan Google: {RESERVED_PREFIXES}."
        )

    return name
