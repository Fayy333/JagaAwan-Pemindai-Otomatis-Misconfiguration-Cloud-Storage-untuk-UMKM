# Aturan Pemeriksaan dan Penilaian Risiko JagaAwan

Dokumen ini menjelaskan aturan pemeriksaan postur keamanan Google Cloud Storage (GCS) serta rumus perhitungan skor keamanan untuk UMKM.

---

## 1. Konsep yang Diperiksa

Pemindai memeriksa 2 elemen konfigurasi utama pada setiap bucket:
1. **Public Access Prevention (PAP)**: Pengaman bawaan GCP untuk memblokir akses publik ke bucket (`enforced` / `inherited` / tidak aktif).
2. **IAM Policy (Akses Publik)**: Keberadaan entitas publik `allUsers` (siapa saja di internet tanpa login) atau `allAuthenticatedUsers` (siapa saja yang memiliki akun Google) pada role pembaca/pengunduh objek.

---

## 2. Matriks Risiko per Bucket

| Akses Publik (allUsers / allAuthenticatedUsers) | Public Access Prevention (PAP) | Status Risiko | Kode Temuan | Pengurang Skor (`kurang`) |
| :--- | :--- | :--- | :--- | :--- |
| **Ada (Publik)** | **Tidak Aktif (Unspecified / Inherited False)** | **TINGGI** | `BUCKET_PUBLIK` | **-30** |
| **Ada (Publik)** | **Aktif (Enforced)** | **SEDANG** | `BUCKET_PUBLIK` | **-15** |
| **Tidak Ada (Privat)**| **Tidak Aktif** | **RENDAH** | `PAP_NONAKTIF` | **-5** |
| **Tidak Ada (Privat)**| **Aktif (Enforced)** | **AMAN** | `-` | **0** |

---

## 3. Rumus Perhitungan Skor

$$\text{Skor Akhir} = \max\left(0, 100 - \sum \text{Pengurang Skor Seluruh Bucket}\right)$$

- **Skor Awal**: 100
- **Skor Minimal**: 0 (tidak bisa bernilai negatif)
- **Kategori Skor**:
  - `80 - 100`: **Aman / Sehat (Hijau)**
  - `50 - 79` : **Perlu Perhatian (Kuning)**
  - `< 50`    : **Bahaya / Kritis (Merah)**

---

## 4. Kamus Penjelasan Awam dan Saran

### A. Risiko TINGGI (`BUCKET_PUBLIK`)
- **Penjelasan**: Siapa pun di internet bisa mengunduh seluruh file dan data di dalam bucket ini tanpa memerlukan password atau akun.
- **Saran**: Pisahkan bucket data rahasia dari bucket aset publik, aktifkan Public Access Prevention, dan hapus izin `allUsers` pada bucket.

### B. Risiko SEDANG (`BUCKET_PUBLIK` dengan PAP Enforced)
- **Penjelasan**: Terdapat aturan izin untuk publik, namun saat ini tertahan oleh proteksi Public Access Prevention.
- **Saran**: Bersihkan anggota `allUsers` dari IAM policy bucket agar konfigurasi tidak membingungkan dan tidak berisiko terbuka jika proteksi PAP dicabut.

### C. Risiko RENDAH (`PAP_NONAKTIF`)
- **Penjelasan**: Bucket saat ini bersifat privat, tetapi pengaman anti-akses-publik (Public Access Prevention) belum diaktifkan.
- **Saran**: Aktifkan fitur Public Access Prevention pada bucket untuk mencegah kebocoran data akibat kesalahan konfigurasi anggota tim di masa mendatang.

### D. AMAN
- **Penjelasan**: Konfigurasi bucket sudah terlindungi dengan baik dari akses publik.
- **Saran**: Pertahankan konfigurasi saat ini dan pantau secara berkala melalui pemindaian rutin.
