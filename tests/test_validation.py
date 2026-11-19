from common.validators import valid_temuan, valid_hasil
from scanner.scanner import hitung_skor


def test_valid_temuan_lolos():
    t = {
        "bucket": "jagaawan-foto-4827",
        "risiko": "TINGGI",
        "kode": "BUCKET_PUBLIK",
        "penjelasan": "Semua orang bisa download foto.",
        "saran": "Aktifkan PAP.",
        "kurang": 30
    }
    assert valid_temuan(t) is True


def test_valid_temuan_karakter_ilegal():
    t = {
        "bucket": "jagaawan<script>alert(1)</script>",
        "risiko": "TINGGI",
        "kode": "BUCKET_PUBLIK",
        "penjelasan": "Penjelasan aman",
        "saran": "Saran aman",
        "kurang": 30
    }
    assert valid_temuan(t) is False


def test_valid_hasil_skor_invalid():
    h = {
        "scan_id": "2026-11-05T01:00:00Z",
        "skor": 150,  # Tidak boleh > 100
        "temuan": []
    }
    assert valid_hasil(h) is False


def test_valid_hasil_format_scan_id_salah():
    h = {
        "scan_id": "bukan-waktu-utc",
        "skor": 90,
        "temuan": []
    }
    assert valid_hasil(h) is False


def test_hitung_skor():
    temuan = [
        {"kurang": 30},
        {"kurang": 15}
    ]
    assert hitung_skor(temuan) == 55

    # Skor tidak boleh tembus di bawah 0
    banyak_temuan = [{"kurang": 30}] * 5
    assert hitung_skor(banyak_temuan) == 0
