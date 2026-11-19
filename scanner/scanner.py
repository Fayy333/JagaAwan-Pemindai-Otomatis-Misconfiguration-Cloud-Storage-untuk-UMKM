"""Read-only Cloud Storage configuration scanner."""

from datetime import datetime, timezone

from google.cloud import storage

RISK_RULES = {
    "TINGGI": {"pengurang": 30, "kode": "PUB-NO-PAP", "penjelasan": "Bucket dapat diakses publik dan Public Access Prevention (PAP) tidak aktif."},
    "SEDANG": {"pengurang": 15, "kode": "PUB-PAP", "penjelasan": "Bucket dapat diakses publik, tetapi PAP sudah aktif."},
    "RENDAH": {"pengurang": 5, "kode": "PRIV-NO-PAP", "penjelasan": "Bucket tidak publik, namun PAP belum diaktifkan."},
    "AMAN": {"pengurang": 0, "kode": "PRIV-PAP", "penjelasan": "Bucket tidak publik dan PAP aktif. Konfigurasi sudah baik."},
}
SARAN = {
    "TINGGI": "Segera aktifkan Public Access Prevention dan hapus binding allUsers / allAuthenticatedUsers dari IAM policy.",
    "SEDANG": "Tinjau kembali kebutuhan akses publik. Jika tidak diperlukan, cabut binding allUsers / allAuthenticatedUsers.",
    "RENDAH": "Aktifkan Public Access Prevention untuk mencegah pemberian akses publik secara tidak sengaja di masa mendatang.",
    "AMAN": "Tidak ada tindakan yang diperlukan.",
}
PUBLIC_MEMBERS = {"allUsers", "allAuthenticatedUsers"}


def cek_akses_publik(bucket: storage.Bucket) -> bool:
    """Return whether the bucket IAM policy grants public access."""
    try:
        policy = bucket.get_iam_policy(requested_policy_version=3)
        return any(PUBLIC_MEMBERS & set(binding.get("members", [])) for binding in policy.bindings)
    except Exception:
        return False


def cek_pap_aktif(bucket: storage.Bucket) -> bool:
    """Read Public Access Prevention state without changing the bucket."""
    try:
        return bucket.iam_configuration.public_access_prevention == "enforced"
    except Exception:
        return False


def periksa_bucket(bucket: storage.Bucket) -> dict:
    publik, pap = cek_akses_publik(bucket), cek_pap_aktif(bucket)
    risiko = "TINGGI" if publik and not pap else "SEDANG" if publik else "RENDAH" if not pap else "AMAN"
    aturan = RISK_RULES[risiko]
    return {"bucket": bucket.name, "risiko": risiko, "kode": aturan["kode"], "kurang": aturan["pengurang"],
            "penjelasan": aturan["penjelasan"], "saran": SARAN[risiko], "publik": publik, "pap_aktif": pap}


def hitung_skor(temuan: list[dict]) -> int:
    return max(0, 100 - sum(int(t.get("kurang", 0)) for t in temuan))


def jalankan_pemindai() -> dict:
    """Scan every bucket in the current project; this function never mutates GCS."""
    client = storage.Client()
    temuan = []
    for bucket in client.list_buckets():
        bucket.reload()
        temuan.append(periksa_bucket(bucket))
    now = datetime.now(timezone.utc)
    return {"scan_id": now.strftime("scan-%Y%m%d-%H%M%S"), "timestamp": now.isoformat(),
            "skor": hitung_skor(temuan), "jumlah_bucket": len(temuan), "temuan": temuan}
