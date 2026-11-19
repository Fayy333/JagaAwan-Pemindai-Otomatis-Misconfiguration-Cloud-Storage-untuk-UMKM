"""HTTP endpoints for scheduled scans and the dashboard."""

import json
import os

import functions_framework
from google.cloud import firestore

from scanner.scanner import jalankan_pemindai

KOLEKSI = os.getenv("JAGAAWAN_FIRESTORE_COLLECTION", "scans")
db = firestore.Client()


@functions_framework.http
def scan(request):
    try:
        hasil = jalankan_pemindai()
        db.collection(KOLEKSI).document(hasil["scan_id"]).set(hasil)
        return json.dumps({"status": "ok", "scan_id": hasil["scan_id"]}), 200, {"Content-Type": "application/json"}
    except Exception as exc:
        return json.dumps({"status": "error", "pesan": str(exc)}), 500, {"Content-Type": "application/json"}


@functions_framework.http
def results(request):
    headers = {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"}
    if request.method == "OPTIONS":
        return "", 204, {**headers, "Access-Control-Allow-Methods": "GET"}
    try:
        docs = db.collection(KOLEKSI).order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1).stream()
        latest = next((doc.to_dict() for doc in docs), None)
        if latest is None:
            return json.dumps({"status": "belum_ada_data"}), 404, headers
        return json.dumps(latest, ensure_ascii=False), 200, headers
    except Exception as exc:
        return json.dumps({"status": "error", "pesan": str(exc)}), 500, headers
