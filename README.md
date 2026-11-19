# JagaAwan

Pemindai otomatis misconfiguration Google Cloud Storage untuk UMKM. Scanner hanya membaca konfigurasi bucket; perubahan konfigurasi dilakukan oleh pemilik project.

## Struktur proyek

```text
jagaawan/
├── scanner/        # pemindai read-only konfigurasi bucket
├── api/            # endpoint Cloud Functions untuk scan dan dashboard
├── dashboard/      # frontend dashboard dan data contoh lokal
├── toko_uji/       # website uji dengan konfigurasi bucket yang sengaja rentan
├── common/         # validators.py, config.py, logging.py
├── tests/          # pengujian scanner dan validasi
├── docs/           # aturan pemindaian dan kontrak payload
├── requirements.txt
└── .gitignore      # .env, key, dan service-account JSON
```

## Menjalankan lokal

1. Buka `toko_uji/index.html` untuk menguji katalog dan ubah `BUCKET` jika perlu.
2. Buka `dashboard/index.html`; default memakai `dashboard/data-contoh.json`.
3. Jalankan pengujian dengan `pytest tests/ -v`.

## Deploy endpoint

```bash
gcloud functions deploy scan --gen2 --runtime=python312 --region=us-central1 --source=api/ --entry-point=scan --trigger-http --no-allow-unauthenticated
gcloud functions deploy results --gen2 --runtime=python312 --region=us-central1 --source=api/ --entry-point=results --trigger-http --allow-unauthenticated
```

`scan` menyimpan hasil terbaru ke Firestore, sedangkan `results` mengembalikannya untuk dashboard. Nama koleksi dapat diubah dengan `JAGAAWAN_FIRESTORE_COLLECTION`.
