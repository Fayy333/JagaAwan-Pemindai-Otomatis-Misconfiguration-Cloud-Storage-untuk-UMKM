"""
main.py - Entry point Cloud Run Functions untuk JagaAwan
Dua fungsi HTTP:
  - scan(request)    → dipanggil Cloud Scheduler, hasil disimpan ke Firestore
  - results(request) → publik, mengembalikan dokumen pindai terbaru sebagai JSON
"""

import json
import os
import functions_framework
from google.cloud import firestore
from scanner import jalankan_pemindai

# Nama koleksi Firestore
KOLEKSI = "scans"

# Inisialisasi client Firestore (di-reuse antar invokasi)
db = firestore.Client()


# ─────────────────────────────────────────────
# Fungsi 1 – scan (privat, dipanggil Scheduler)
# ─────────────────────────────────────────────

@functions_framework.http
def scan(request):
    """
    Menjalankan pemindai lalu menyimpan hasilnya ke Firestore.

    Dipanggil oleh Cloud Scheduler setiap hari.
    Endpoint ini bersifat privat (hanya service account Scheduler yang boleh memanggil).

    Returns:
        JSON {"status": "ok", "scan_id": "..."} dengan HTTP 200
        JSON {"status": "error", "pesan": "..."} dengan HTTP 500
    """
    try:
        hasil = jalankan_pemindai()
        scan_id = hasil["scan_id"]

        # Simpan dokumen ke Firestore dengan scan_id sebagai document ID
        db.collection(KOLEKSI).document(scan_id).set(hasil)

        return (
            json.dumps({"status": "ok", "scan_id": scan_id}),
            200,
            {"Content-Type": "application/json"},
        )

    except Exception as exc:
        return (
            json.dumps({"status": "error", "pesan": str(exc)}),
            500,
            {"Content-Type": "application/json"},
        )


# ─────────────────────────────────────────────
# Fungsi 2 – results (publik, untuk dashboard)
# ─────────────────────────────────────────────

@functions_framework.http
def results(request):
    """
    Mengembalikan dokumen pindai terbaru dari Firestore sebagai JSON.

    Endpoint publik – hanya aman digunakan dengan data fiktif / demo.
    Mendukung CORS agar bisa dipanggil dari halaman HTML statis (GitHub Pages).

    Returns:
        JSON dokumen pindai terbaru dengan HTTP 200
        JSON {"status": "belum_ada_data"} dengan HTTP 404 jika koleksi kosong
        JSON {"status": "error", "pesan": "..."} dengan HTTP 500
    """
    # Header CORS agar dashboard di GitHub Pages bisa memanggil endpoint ini
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json",
    }

    # Tangani preflight OPTIONS
    if request.method == "OPTIONS":
        return ("", 204, {**cors_headers, "Access-Control-Allow-Methods": "GET"})

    try:
        # Ambil dokumen terbaru berdasarkan field timestamp (descending)
        docs = (
            db.collection(KOLEKSI)
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(1)
            .stream()
        )

        dokumen = None
        for doc in docs:
            dokumen = doc.to_dict()

        if dokumen is None:
            return (
                json.dumps({"status": "belum_ada_data"}),
                404,
                cors_headers,
            )

        return (json.dumps(dokumen, ensure_ascii=False), 200, cors_headers)

    except Exception as exc:
        return (
            json.dumps({"status": "error", "pesan": str(exc)}),
            500,
            cors_headers,
        )
