"""
scanner.py - Modul pemindai keamanan bucket Cloud Storage
JagaAwan | Hanya membaca konfigurasi, tidak mengubah apa pun.
"""

import datetime
from google.cloud import storage


# ─────────────────────────────────────────────
# Aturan penilaian risiko (Langkah 4)
# ─────────────────────────────────────────────
RISK_RULES = {
    "TINGGI":  {"pengurang": 30, "kode": "PUB-NO-PAP",  "penjelasan": "Bucket dapat diakses publik dan Public Access Prevention (PAP) tidak aktif."},
    "SEDANG":  {"pengurang": 15, "kode": "PUB-PAP",     "penjelasan": "Bucket dapat diakses publik, tetapi PAP sudah aktif."},
    "RENDAH":  {"pengurang": 5,  "kode": "PRIV-NO-PAP", "penjelasan": "Bucket tidak publik, namun PAP belum diaktifkan."},
    "AMAN":    {"pengurang": 0,  "kode": "PRIV-PAP",    "penjelasan": "Bucket tidak publik dan PAP aktif. Konfigurasi sudah baik."},
}

SARAN = {
    "TINGGI":  "Segera aktifkan Public Access Prevention dan hapus binding allUsers / allAuthenticatedUsers dari IAM policy.",
    "SEDANG":  "Tinjau kembali kebutuhan akses publik. Jika tidak diperlukan, cabut binding allUsers / allAuthenticatedUsers.",
    "RENDAH":  "Aktifkan Public Access Prevention untuk mencegah pemberian akses publik secara tidak sengaja di masa mendatang.",
    "AMAN":    "Tidak ada tindakan yang diperlukan.",
}

PUBLIC_MEMBERS = {"allUsers", "allAuthenticatedUsers"}


# ─────────────────────────────────────────────
# Fungsi inti
# ─────────────────────────────────────────────

def cek_akses_publik(bucket: storage.Bucket) -> bool:
    """
    Mengembalikan True jika IAM policy bucket memiliki member allUsers
    atau allAuthenticatedUsers pada role apa pun.
    Hanya membaca policy, tidak mengubah apa pun.
    """
    try:
        policy = bucket.get_iam_policy(requested_policy_version=3)
        for binding in policy.bindings:
            members = set(binding.get("members", []))
            if members & PUBLIC_MEMBERS:
                return True
    except Exception:
        # Jika tidak ada izin membaca IAM, anggap tidak publik
        pass
    return False


def cek_pap_aktif(bucket: storage.Bucket) -> bool:
    """
    Mengembalikan True jika Public Access Prevention bernilai 'enforced'.
    Hanya membaca atribut bucket, tidak mengubah apa pun.
    """
    try:
        pap = bucket.iam_configuration.public_access_prevention
        return pap == "enforced"
    except Exception:
        return False


def periksa_bucket(bucket: storage.Bucket) -> dict:
    """
    Memeriksa satu bucket dan mengembalikan dict temuan.

    Masukan : Objek bucket (google.cloud.storage.Bucket)
    Keluaran: Dict berisi nama, risiko, kode, pengurang, penjelasan, saran
    """
    publik = cek_akses_publik(bucket)
    pap    = cek_pap_aktif(bucket)

    if publik and not pap:
        risiko = "TINGGI"
    elif publik and pap:
        risiko = "SEDANG"
    elif not publik and not pap:
        risiko = "RENDAH"
    else:
        risiko = "AMAN"

    aturan = RISK_RULES[risiko]
    return {
        "bucket":     bucket.name,
        "risiko":     risiko,
        "kode":       aturan["kode"],
        "pengurang":  aturan["pengurang"],
        "penjelasan": aturan["penjelasan"],
        "saran":      SARAN[risiko],
        "publik":     publik,
        "pap_aktif":  pap,
    }


def hitung_skor(temuan: list[dict]) -> int:
    """
    Menghitung skor akhir dari daftar temuan.

    Masukan : Daftar temuan (output periksa_bucket)
    Keluaran: Angka 0–100
    """
    total_pengurang = sum(t["pengurang"] for t in temuan)
    return max(0, 100 - total_pengurang)


def jalankan_pemindai() -> dict:
    """
    Fungsi utama pemindai.
    Mengambil semua bucket di project, memeriksa masing-masing,
    lalu mengembalikan JSON sesuai kontrak output.

    Masukan : (tidak ada)
    Keluaran: Dict JSON sesuai kontrak (scan_id, skor, temuan, timestamp)
    """
    client  = storage.Client()
    buckets = list(client.list_buckets())

    temuan = []
    for bucket in buckets:
        # reload() memastikan atribut IAM configuration tersedia
        bucket.reload()
        hasil = periksa_bucket(bucket)
        temuan.append(hasil)

    skor     = hitung_skor(temuan)
    scan_id  = datetime.datetime.utcnow().strftime("scan-%Y%m%d-%H%M%S")
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"

    return {
        "scan_id":   scan_id,
        "timestamp": timestamp,
        "skor":      skor,
        "jumlah_bucket": len(temuan),
        "temuan":    temuan,
    }
