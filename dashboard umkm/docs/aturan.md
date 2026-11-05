# Aturan Penilaian JagaAwan

## Cara Kerja Skor

Skor dimulai dari **100** dan dikurangi berdasarkan risiko tiap bucket yang ditemukan.
Skor minimal adalah **0** (tidak bisa negatif).

```
Skor = max(0, 100 − Σ pengurang)
```

**Contoh:**
Satu bucket TINGGI (−30) + satu bucket AMAN (−0) = skor **70**.

---

## Tabel Risiko

| Kondisi Bucket                        | Risiko   | Kode        | Pengurang |
|---------------------------------------|----------|-------------|-----------|
| Publik + PAP tidak aktif              | TINGGI   | PUB-NO-PAP  | 30        |
| Publik + PAP aktif                    | SEDANG   | PUB-PAP     | 15        |
| Tidak publik + PAP tidak aktif        | RENDAH   | PRIV-NO-PAP | 5         |
| Tidak publik + PAP aktif              | AMAN     | PRIV-PAP    | 0         |

---

## Definisi Istilah

| Istilah | Penjelasan |
|---------|-----------|
| **Publik** | IAM policy bucket memiliki member `allUsers` atau `allAuthenticatedUsers` pada role apa pun |
| **PAP** | Public Access Prevention — pengaturan GCS yang mencegah pemberian akses publik |
| **enforced** | Status PAP yang berarti akses publik diblokir sepenuhnya |

---

## Batasan Program

1. Hanya memeriksa **konfigurasi akses**, bukan isi file.
2. Satu provider: **Google Cloud Storage**.
3. Endpoint `results` bersifat **publik** — hanya aman dengan data fiktif / demo.
4. Bucket foto yang sengaja dibuat publik tetap ditandai **SEDANG** atau **RENDAH**
   karena program belum membedakan tujuan bucket.

---

## Alur Penilaian

```
Ambil daftar bucket
        │
        ▼
  Untuk tiap bucket:
    ├─ Cek IAM policy → publik?
    └─ Cek PAP        → aktif?
        │
        ▼
  Tentukan risiko (AMAN/RENDAH/SEDANG/TINGGI)
        │
        ▼
  Hitung skor total
        │
        ▼
  Simpan JSON ke Firestore
```
