"""Environment-backed configuration shared by scanner and API."""

import os

from dotenv import load_dotenv

load_dotenv()
FIRESTORE_COLLECTION = os.getenv("JAGAAWAN_FIRESTORE_COLLECTION", "scans")
API_URL = os.getenv("JAGAAWAN_API_URL", "data-contoh.json")
