# PRD — JagaAwan

**Versi:** 1.0  
**Tanggal:** November 2025  
**Status:** Draft

---

## 1. Latar Belakang

Bucket Cloud Storage yang salah konfigurasi (terbuka publik tanpa disengaja)
merupakan salah satu penyebab kebocoran data paling umum di lingkungan cloud.
JagaAwan hadir sebagai alat audit otomatis yang membaca konfigurasi akses bucket,
menilai risikonya, dan menyajikan hasilnya di dashboard.

---

## 2. Tujuan

- Mendeteksi bucket yang dapat diakses publik secara tidak sengaja.
- Memberikan skor keamanan yang mudah dipahami (0–100).
- Menyajikan saran perbaikan yang actionable.
- Berjalan otomatis setiap hari tanpa intervensi manual.

---

## 3. Pengguna Sasaran

| Peran | Kebutuhan |
|-------|-----------|
| Developer / Cloud Engineer | Memantau keamanan bucket project |
| Dosen / Penguji | Melihat demo audit keamanan cloud |

---

## 4. Ruang Lingkup

### Termasuk
- Pembacaan IAM policy bucket.
- Pembacaan status Public Access Prevention (PAP).
- Penilaian risiko dan perhitungan skor.
- Penyimpanan hasil ke Firestore.
- Dashboard HTML statis.
- Notifikasi Telegram untuk risiko TINGGI (opsional).

### Tidak Termasuk
- Pembacaan atau analisis isi file di dalam bucket.
- Pengubahan konfigurasi bucket (read-only).
- Multi-cloud (hanya Google Cloud).
- Autentikasi pengguna pada dashboard.

---

## 5. Komponen Sistem

| Komponen | Teknologi | Penanggung Jawab |
|----------|-----------|-----------------|
| Pemicu otomatis | Cloud Scheduler | Orang 1 |
| Pemindai | Python + google-cloud-storage | Orang 2 |
| Fungsi scan | Cloud Run Functions (privat) | Orang 1 & 2 |
| Penyimpanan | Firestore | Orang 1 |
| Fungsi results | Cloud Run Functions (publik) | Orang 1 & 2 |
| Dashboard | HTML + JavaScript | Orang 3 |
| Website uji | HTML (GitHub Pages) | Orang 3 |
| Notifikasi | Bot Telegram | Orang 3 |

---

## 6. Alur Sistem

```
Cloud Scheduler (tiap hari)
        │  HTTP POST
        ▼
  [scan] Cloud Run Function (privat)
        │  jalankan_pemindai()
        │  simpan ke Firestore
        ▼
  Firestore koleksi "scans"
        ▲
        │  baca dokumen terbaru
  [results] Cloud Run Function (publik)
        ▲
        │  fetch JSON
  Dashboard (GitHub Pages)
```

---

## 7. Kontrak Output

Lihat [`kontrak.json`](kontrak.json) untuk skema lengkap.

---

## 8. Kriteria Keberhasilan

- [ ] Scan berjalan otomatis setiap hari via Cloud Scheduler.
- [ ] Skor dihitung dengan benar sesuai aturan penilaian.
- [ ] Hasil tersimpan di Firestore dan bisa diambil via endpoint `results`.
- [ ] Dashboard menampilkan skor, tabel temuan, dan waktu pindai.
- [ ] Website uji dapat memperlihatkan perbedaan kondisi A, B, C.

---

## 9. Risiko Proyek

| Risiko | Mitigasi |
|--------|---------|
| Endpoint results diakses orang tidak dikenal | Hanya diisi data fiktif di demo |
| IAM tidak cukup untuk membaca policy | Beri service account peran `roles/storage.admin` atau `roles/iam.securityReviewer` |
| Firestore belum diinisialisasi | Jalankan `gcloud firestore databases create` sebelum deploy |
