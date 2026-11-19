from enum import Enum

class Risk(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH     = "HIGH"
    MEDIUM   = "MEDIUM"
    LOW      = "LOW"
    PASS     = "PASS"
    UNKNOWN  = "UNKNOWN"

CHECKS = [
    {
        "id": "S-01",
        "name": "Public Access (allUsers)",
        "risk": Risk.CRITICAL,
        "detail_fail": "Bucket dapat diakses siapa saja tanpa autentikasi (allUsers).",
        "detail_pass": "Tidak ada member allUsers pada IAM bucket.",
    },
    {
        "id": "S-02",
        "name": "Authenticated Public Access (allAuthenticatedUsers)",
        "risk": Risk.CRITICAL,
        "detail_fail": "Bucket dapat diakses oleh semua pengguna Google yang terautentikasi.",
        "detail_pass": "Tidak ada member allAuthenticatedUsers pada IAM bucket.",
    },
    {
        "id": "S-03",
        "name": "Object Versioning",
        "risk": Risk.HIGH,
        "detail_fail": "Versioning dinonaktifkan. Objek yang terhapus/tertimpa tidak dapat dipulihkan.",
        "detail_pass": "Versioning aktif.",
    },
    {
        "id": "S-04",
        "name": "Access Logging",
        "risk": Risk.HIGH,
        "detail_fail": "Logging akses bucket tidak dikonfigurasi. Aktivitas tidak tercatat.",
        "detail_pass": "Access logging aktif.",
    },
    {
        "id": "S-05",
        "name": "CORS Wildcard Origin",
        "risk": Risk.MEDIUM,
        "detail_fail": "Konfigurasi CORS mengizinkan semua origin (*). Rawan Cross-Site Request.",
        "detail_pass": "CORS tidak terkonfigurasi atau tidak menggunakan wildcard origin.",
    },
    {
        "id": "S-06",
        "name": "Uniform Bucket-Level Access",
        "risk": Risk.MEDIUM,
        "detail_fail": "Uniform Bucket-Level Access dinonaktifkan. ACL per-objek dapat membuka celah.",
        "detail_pass": "Uniform Bucket-Level Access aktif.",
    },
    {
        "id": "S-07",
        "name": "Retention Policy",
        "risk": Risk.LOW,
        "detail_fail": "Retention policy tidak dikonfigurasi. Objek dapat dihapus kapan saja.",
        "detail_pass": "Retention policy aktif.",
    },
]

RISK_ORDER = [Risk.CRITICAL, Risk.HIGH, Risk.MEDIUM, Risk.LOW, Risk.PASS, Risk.UNKNOWN]
