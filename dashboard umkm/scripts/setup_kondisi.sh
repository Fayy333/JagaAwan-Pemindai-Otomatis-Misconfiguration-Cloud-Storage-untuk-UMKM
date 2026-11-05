#!/usr/bin/env bash
# setup_kondisi.sh — Menyiapkan kondisi uji A, B, C, D untuk JagaAwan
# Jalankan: bash scripts/setup_kondisi.sh
#
# Prasyarat:
#   - gcloud CLI terautentikasi dan project sudah di-set
#   - Hak akses: roles/storage.admin
#
# PERINGATAN: Skrip ini MENGUBAH konfigurasi bucket.
#             Gunakan hanya di project khusus untuk pengujian/demo.

set -euo pipefail

# ─────────────────────────────────────────────
# Konfigurasi — sesuaikan dengan project Anda
# ─────────────────────────────────────────────
PROJECT_ID=$(gcloud config get-value project)
REGION="asia-southeast2"   # Jakarta

BUCKET_A="${PROJECT_ID}-kondisi-a"   # Publik,  PAP tidak aktif → TINGGI
BUCKET_B="${PROJECT_ID}-kondisi-b"   # Publik,  PAP aktif       → SEDANG
BUCKET_C="${PROJECT_ID}-kondisi-c"   # Privat,  PAP aktif       → AMAN
BUCKET_D="${PROJECT_ID}-kondisi-d"   # Privat,  PAP tidak aktif → RENDAH

echo "========================================"
echo " JagaAwan — Setup Kondisi Uji"
echo " Project : $PROJECT_ID"
echo " Region  : $REGION"
echo "========================================"
echo ""

# ─────────────────────────────────────────────
# Fungsi pembantu
# ─────────────────────────────────────────────

buat_bucket() {
  local nama="$1"
  if gsutil ls -b "gs://${nama}" &>/dev/null; then
    echo "  ✔ Bucket ${nama} sudah ada, dilewati."
  else
    gsutil mb -p "$PROJECT_ID" -l "$REGION" "gs://${nama}"
    echo "  ✔ Bucket ${nama} dibuat."
  fi
}

unggah_foto_contoh() {
  local bucket="$1"
  local warna="$2"
  local kondisi="$3"
  # Buat file gambar placeholder (1x1 pixel PNG transparan, base64)
  echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg==" \
    | base64 --decode > /tmp/foto-placeholder.png

  # Upload beberapa file contoh
  for i in 1 2 3; do
    gsutil cp /tmp/foto-placeholder.png "gs://${bucket}/foto${i}.png" -q
  done
  echo "  ✔ File contoh diunggah ke ${bucket}."
}

# ─────────────────────────────────────────────
# Kondisi A: Publik + PAP tidak aktif → TINGGI
# ─────────────────────────────────────────────
echo "[ Kondisi A ] Bucket Publik, PAP Tidak Aktif → Risiko TINGGI"
buat_bucket "$BUCKET_A"
# Nonaktifkan PAP terlebih dahulu
gcloud storage buckets update "gs://${BUCKET_A}" \
  --no-public-access-prevention 2>/dev/null || true
# Beri akses allUsers
gsutil iam ch allUsers:objectViewer "gs://${BUCKET_A}"
echo "  ✔ allUsers:objectViewer diberikan."
unggah_foto_contoh "$BUCKET_A" "merah" "A"
echo ""

# ─────────────────────────────────────────────
# Kondisi B: Publik + PAP aktif → SEDANG
# ─────────────────────────────────────────────
echo "[ Kondisi B ] Bucket Publik, PAP Aktif → Risiko SEDANG"
buat_bucket "$BUCKET_B"
# Aktifkan PAP
gcloud storage buckets update "gs://${BUCKET_B}" \
  --public-access-prevention
# Catatan: dengan PAP enforced, allUsers binding tidak akan berefek,
# tetapi JagaAwan tetap mendeteksinya di IAM policy.
gsutil iam ch allUsers:objectViewer "gs://${BUCKET_B}" 2>/dev/null || true
echo "  ✔ PAP aktif. allUsers binding ditambahkan (tidak berefek karena PAP)."
unggah_foto_contoh "$BUCKET_B" "kuning" "B"
echo ""

# ─────────────────────────────────────────────
# Kondisi C: Privat + PAP aktif → AMAN
# ─────────────────────────────────────────────
echo "[ Kondisi C ] Bucket Privat, PAP Aktif → Risiko AMAN"
buat_bucket "$BUCKET_C"
gcloud storage buckets update "gs://${BUCKET_C}" \
  --public-access-prevention
# Pastikan tidak ada allUsers
gsutil iam ch -d allUsers:objectViewer "gs://${BUCKET_C}" 2>/dev/null || true
gsutil iam ch -d allAuthenticatedUsers:objectViewer "gs://${BUCKET_C}" 2>/dev/null || true
echo "  ✔ PAP aktif. Tidak ada akses publik."
unggah_foto_contoh "$BUCKET_C" "hijau" "C"
echo ""

# ─────────────────────────────────────────────
# Kondisi D: Privat + PAP tidak aktif → RENDAH
# ─────────────────────────────────────────────
echo "[ Kondisi D ] Bucket Privat, PAP Tidak Aktif → Risiko RENDAH"
buat_bucket "$BUCKET_D"
gcloud storage buckets update "gs://${BUCKET_D}" \
  --no-public-access-prevention 2>/dev/null || true
gsutil iam ch -d allUsers:objectViewer "gs://${BUCKET_D}" 2>/dev/null || true
gsutil iam ch -d allAuthenticatedUsers:objectViewer "gs://${BUCKET_D}" 2>/dev/null || true
echo "  ✔ PAP tidak aktif. Tidak ada akses publik."
unggah_foto_contoh "$BUCKET_D" "biru" "D"
echo ""

# ─────────────────────────────────────────────
# Ringkasan
# ─────────────────────────────────────────────
echo "========================================"
echo " Setup selesai!"
echo ""
echo "  Bucket A (TINGGI) : gs://${BUCKET_A}"
echo "  Bucket B (SEDANG) : gs://${BUCKET_B}"
echo "  Bucket C (AMAN)   : gs://${BUCKET_C}"
echo "  Bucket D (RENDAH) : gs://${BUCKET_D}"
echo ""
echo " Jalankan fungsi scan untuk memulai penilaian."
echo "========================================"
