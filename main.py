"""
JagaAwan — Pemindai Otomatis Misconfiguration Cloud Storage untuk UMKM
Penggunaan:
    python main.py --bucket <NAMA_BUCKET> [--output <direktori>] [--encrypt]

Argumen:
    --bucket   Nama bucket GCS yang akan dipindai (wajib)
    --output   Direktori penyimpanan laporan (default: output/)
    --encrypt  Enkripsi laporan JSON menggunakan Fernet sebelum disimpan
"""

import argparse
import base64
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from core.crypto import decrypt, encrypt, generate_key
from core.reporter import to_html, to_json
from core.scanner import scan
from core.validator import sanitize_bucket_name
from utils import logger

load_dotenv()


def _get_or_create_key() -> bytes:
    """Ambil kunci dari env var, atau buat dan simpan kunci baru."""
    raw = os.getenv("JAGAAWAN_KEY", "").strip()
    if raw:
        try:
            return base64.urlsafe_b64decode(raw)
        except Exception:
            logger.error("JAGAAWAN_KEY di .env tidak valid. Membuat kunci baru.")

    key = generate_key()
    logger.warning(
        "Kunci enkripsi baru dibuat. Simpan nilai berikut di JAGAAWAN_KEY pada .env:\n"
        + base64.urlsafe_b64encode(key).decode()
    )
    return key


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jagaawan",
        description="Pemindai keamanan konfigurasi GCS bucket",
    )
    parser.add_argument(
        "--bucket", required=True,
        help="Nama bucket GCS yang akan dipindai",
    )
    parser.add_argument(
        "--output", default="output",
        help="Direktori penyimpanan laporan (default: output/)",
    )
    parser.add_argument(
        "--encrypt", action="store_true",
        help="Enkripsi laporan JSON sebelum disimpan",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    # Validasi & sanitasi input
    try:
        bucket_name = sanitize_bucket_name(args.bucket)
    except (TypeError, ValueError) as exc:
        logger.error(f"Input tidak valid: {exc}")
        sys.exit(1)

    logger.info(f"Memulai pemindaian bucket: {bucket_name}")

    # Jalankan scan
    result = scan(bucket_name)

    # Siapkan direktori output
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Simpan laporan HTML
    html_path = out_dir / f"{bucket_name}_report.html"
    html_path.write_text(to_html(result), encoding="utf-8")
    logger.info(f"Laporan HTML disimpan: {html_path}")

    # Simpan laporan JSON (terenkripsi atau biasa)
    report_json = to_json(result)
    if args.encrypt:
        key = _get_or_create_key()
        encrypted = encrypt(report_json, key)
        enc_path = out_dir / f"{bucket_name}_report.enc"
        enc_path.write_bytes(encrypted)
        logger.info(f"Laporan JSON terenkripsi disimpan: {enc_path}")
    else:
        json_path = out_dir / f"{bucket_name}_report.json"
        json_path.write_text(report_json, encoding="utf-8")
        logger.info(f"Laporan JSON disimpan: {json_path}")

    # Ringkasan di terminal
    print("\n" + "=" * 55)
    print(f"  HASIL SCAN: {bucket_name}")
    print(f"  Risiko Keseluruhan : {result.overall_risk}")
    print("=" * 55)
    if result.error:
        print(f"  ⚠  Error: {result.error}")
    else:
        for f in result.findings:
            icon = "✗" if f.status == "FAIL" else ("✓" if f.status == "PASS" else "?")
            print(f"  [{f.id}] {icon} {f.check:<45} {f.risk}")
    print("=" * 55 + "\n")

    if result.overall_risk in ("CRITICAL", "HIGH", "UNKNOWN"):
        sys.exit(2)


if __name__ == "__main__":
    main()
