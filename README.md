# JagaAwan

JagaAwan adalah pemindai konfigurasi keamanan **Google Cloud Storage** untuk UMKM. Sistem ini memeriksa bukti akses publik pada bucket, status Public Access Prevention (PAP), lalu menghitung skor keamanan dan menampilkan hasilnya pada dashboard.

Proyek ini dibuat untuk demonstrasi dan penggunaan pembelajaran. Pemindai bersifat **read-only** terhadap bucket: tidak membaca isi file dan tidak mengubah IAM atau konfigurasi bucket.

## Fitur

- Memindai seluruh bucket pada Google Cloud project.
- Mendeteksi `allUsers` dan `allAuthenticatedUsers` pada IAM policy.
- Memeriksa status PAP (`enforced` atau tidak).
- Menghitung skor keamanan dari 0 sampai 100.
- Menyimpan hasil pindai terbaru ke Firestore.
- Menyediakan API `results` untuk dashboard.
- Menyediakan dashboard HTML statis dan website UMKM sebagai target pengujian.
- Mendukung penjadwalan pemindaian harian melalui Cloud Scheduler.

## Struktur Folder

```text
.
├── dashboard umkm/
│   ├── backend/
│   │   ├── main.py              # Cloud Functions: scan dan results
│   │   ├── scanner.py           # Logika pemindaian dan penilaian risiko
│   │   └── requirements.txt     # Dependensi Python
│   ├── dashboard/
│   │   ├── dashboard.html       # Tampilan hasil pemindaian
│   │   └── data-contoh.json     # Data demo/offline
│   ├── docs/
│   │   ├── prd.md               # Product requirement document
│   │   ├── aturan.md            # Aturan penilaian risiko
│   │   └── kontrak.json         # Kontrak format data output
│   ├── scripts/
│   │   └── setup_kondisi.sh     # Membuat kondisi uji bucket A-D
│   └── website/
│       └── index.html           # Website demo di dalam folder dashboard
├── website umkm/
│   └── index.html               # Website demo UMKM
└── README.md
```

## Arsitektur

```text
Cloud Scheduler
      │ HTTP POST berkala
      ▼
Cloud Run Function: scan
      │ jalankan_pemindai()
      │ IAM policy + PAP tiap bucket
      ▼
Firestore koleksi "scans"
      ▲
      │ Dokumen terbaru
Cloud Run Function: results
      ▲
      │ JSON + CORS
Dashboard HTML
```

## Aturan Penilaian

Skor dimulai dari **100**, lalu dikurangi berdasarkan kondisi tiap bucket:

| Kondisi | Risiko | Kode | Pengurangan |
|---|---|---|---:|
| Publik, PAP tidak aktif | TINGGI | `PUB-NO-PAP` | 30 |
| Publik, PAP aktif | SEDANG | `PUB-PAP` | 15 |
| Privat, PAP tidak aktif | RENDAH | `PRIV-NO-PAP` | 5 |
| Privat, PAP aktif | AMAN | `PRIV-PAP` | 0 |

```text
Skor = max(0, 100 - total pengurangan seluruh bucket)
```

Satu bucket publik dengan PAP aktif tetap dianggap berisiko karena IAM policy masih memiliki binding publik. Detail lengkap tersedia di [aturan.md](dashboard%20umkm/docs/aturan.md).

## Prasyarat

- Google Cloud Platform project aktif dan Billing API diaktifkan.
- Google Cloud CLI (`gcloud`) terpasang dan terautentikasi.
- Python 3.11 atau lebih baru.
- Hak akses untuk Cloud Storage, Firestore, Cloud Functions/Run, dan Cloud Scheduler.
- Git Bash atau WSL untuk menjalankan `setup_kondisi.sh`.

## Menjalankan Dashboard Secara Lokal

Dashboard dapat dibuka langsung melalui browser, atau dijalankan sebagai server statis:

```powershell
cd ".\dashboard umkm\dashboard"
python -m http.server 8080
```

Buka `http://localhost:8080/dashboard.html`. Jika URL endpoint belum dikonfigurasi, dashboard otomatis menggunakan `data-contoh.json`.

Untuk menghubungkan dashboard dengan hasil Cloud:

1. Buka `dashboard umkm/dashboard/dashboard.html`.
2. Ganti `GANTI_DENGAN_URL_ENDPOINT_RESULTS` pada variabel `URL_RESULTS`.
3. Gunakan URL endpoint fungsi `results`.
4. Muat ulang dashboard.

## Menjalankan Backend Secara Lokal

```powershell
cd ".\dashboard umkm\backend"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Pastikan Application Default Credentials tersedia:

```powershell
gcloud auth application-default login
gcloud config set project PROJECT_ID
```

Jalankan fungsi `scan` atau `results` pada terminal terpisah:

```powershell
functions-framework --target scan --port 8081
```

```powershell
functions-framework --target results --port 8082
```

Catatan: jalankan `scan` hanya pada project yang berisi bucket demo/ujian karena pemindai membaca seluruh bucket pada project.

## Menyiapkan Firestore dan Izin

```powershell
gcloud config set project PROJECT_ID
gcloud firestore databases create --location=asia-southeast2
```

Deploy dengan service account runtime yang memiliki izin membaca bucket dan IAM policy serta menulis Firestore. Contoh peran minimum yang perlu dipertimbangkan:

- `roles/storage.admin` untuk demonstrasi penuh.
- `roles/iam.securityReviewer` untuk membaca IAM policy.
- `roles/datastore.user` untuk menulis dan membaca Firestore.

Gunakan peran paling rendah yang memenuhi kebutuhan lingkungan produksi.

## Deployment ke Google Cloud

Masuk ke folder backend, lalu deploy fungsi `scan` dan `results`.

```powershell
cd ".\dashboard umkm\backend"

gcloud functions deploy scan `
  --gen2 `
  --runtime=python311 `
  --region=asia-southeast2 `
  --source=. `
  --entry-point=scan `
  --trigger-http `
  --set-env-vars=GOOGLE_CLOUD_PROJECT=PROJECT_ID
```

Fungsi `scan` sebaiknya dipertahankan privat. Gunakan Cloud Scheduler dengan service account yang memiliki `roles/run.invoker`.

```powershell
gcloud functions deploy results `
  --gen2 `
  --runtime=python311 `
  --region=asia-southeast2 `
  --source=. `
  --entry-point=results `
  --trigger-http `
  --allow-unauthenticated
```

Untuk data demo, endpoint `results` dapat dibuat publik. Pada penggunaan nyata, batasi akses sesuai kebutuhan dan jangan menampilkan informasi sensitif.

### Menjalankan Scan dan Membuat Jadwal

Ambil URL fungsi `scan` dari hasil deploy, lalu buat Cloud Scheduler job:

```powershell
gcloud scheduler jobs create http jagaawan-daily `
  --schedule="0 8 * * *" `
  --uri="URL_SCAN" `
  --http-method=POST `
  --location=asia-southeast2 `
  --oidc-service-account-email=SCHEDULER_SERVICE_ACCOUNT `
  --oidc-token-audience="URL_SCAN"
```

Jadwal `0 8 * * *` berarti pemindaian dijalankan setiap hari pukul 08.00 sesuai timezone job.

Pemindaian manual dapat dilakukan dengan memanggil URL fungsi `scan` melalui request terautentikasi atau menekan **Run now** pada Cloud Scheduler.

## Kondisi Uji A-D

Skrip `setup_kondisi.sh` membuat empat bucket dan mengatur kombinasi akses publik serta PAP:

| Kondisi | Konfigurasi | Risiko |
|---|---|---|
| A | Publik, PAP tidak aktif | TINGGI |
| B | Publik, PAP aktif | SEDANG |
| C | Privat, PAP aktif | AMAN |
| D | Privat, PAP tidak aktif | RENDAH |

Pada Bash/Git Bash atau WSL:

```bash
gcloud auth login
gcloud config set project PROJECT_ID
chmod +x scripts/setup_kondisi.sh
bash scripts/setup_kondisi.sh
```

Jalankan skrip tersebut dari folder `dashboard umkm` agar path `scripts/setup_kondisi.sh` tersedia.

> Peringatan: skrip ini mengubah konfigurasi bucket dan IAM. Gunakan hanya pada project khusus demo atau pengujian, bukan project produksi.

## Website Uji UMKM

Folder `website umkm` berisi website Batik Kita Jogja dengan data produk fiktif. Website dapat dibuka langsung atau di-host pada GitHub Pages. Bucket foto masih berformat placeholder dan perlu diganti melalui variabel `BUCKET` pada HTML dengan nama bucket demonstrasi.

## Kontrak Output

Format output dipertahankan sesuai [kontrak.json](dashboard%20umkm/docs/kontrak.json) dan berisi:

- `scan_id`
- `timestamp`
- `skor`
- `jumlah_bucket`
- `temuan`

Setiap temuan berisi nama bucket, risiko, kode, pengurangan skor, penjelasan, saran, status publik, dan status PAP.

## Batasan

- Hanya mendukung Google Cloud Storage.
- Tidak memindai isi atau kelas data file.
- Tidak mengubah konfigurasi bucket secara otomatis.
- Pemeriksaan IAM dianggap gagal membaca policy dan menganggap bucket tidak publik jika izin tidak tersedia; hasil harus tetap diverifikasi.
- Endpoint `results` sebaiknya hanya menampilkan data fiktif atau data yang aman untuk dipublikasikan.

## Dokumentasi Tambahan

- [PRD](dashboard%20umkm/docs/prd.md)
- [Aturan Penilaian](dashboard%20umkm/docs/aturan.md)
- [Kontrak Output](dashboard%20umkm/docs/kontrak.json)
