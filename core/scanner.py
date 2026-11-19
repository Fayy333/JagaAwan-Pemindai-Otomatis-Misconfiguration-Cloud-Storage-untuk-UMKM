from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List

from google.cloud import storage
from google.api_core.exceptions import Forbidden, NotFound, GoogleAPIError

from utils.constants import CHECKS, RISK_ORDER, Risk
from utils import logger


@dataclass
class Finding:
    id: str
    check: str
    status: str
    risk: str
    detail: str


@dataclass
class ScanResult:
    bucket: str
    scanned_at: str
    overall_risk: str
    findings: List[Finding] = field(default_factory=list)
    error: str = ""


def _overall_risk(findings: List[Finding]) -> str:
    statuses = {f.risk for f in findings if f.status == "FAIL"}
    for level in RISK_ORDER:
        if level.value in statuses:
            return level.value
    return Risk.PASS.value


def scan(bucket_name: str) -> ScanResult:
    scanned_at = datetime.now(timezone.utc).isoformat()
    findings: List[Finding] = []

    try:
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
    except NotFound:
        msg = f"Bucket '{bucket_name}' tidak ditemukan."
        logger.error(msg)
        return ScanResult(bucket=bucket_name, scanned_at=scanned_at,
                          overall_risk=Risk.UNKNOWN.value, error=msg)
    except Forbidden:
        msg = f"Akses ditolak ke bucket '{bucket_name}'. Periksa izin Service Account."
        logger.error(msg)
        return ScanResult(bucket=bucket_name, scanned_at=scanned_at,
                          overall_risk=Risk.UNKNOWN.value, error=msg)
    except GoogleAPIError as exc:
        msg = f"GCS API error: {type(exc).__name__}"
        logger.error(msg)
        return ScanResult(bucket=bucket_name, scanned_at=scanned_at,
                          overall_risk=Risk.UNKNOWN.value, error=msg)

    # --- S-01 & S-02: IAM Public Access ---
    try:
        policy = bucket.get_iam_policy(requested_policy_version=3)
        all_members: set = set()
        for binding in policy.bindings:
            all_members.update(binding.get("members", []))

        for check_id, member in [("S-01", "allUsers"), ("S-02", "allAuthenticatedUsers")]:
            check = next(c for c in CHECKS if c["id"] == check_id)
            fail = member in all_members
            findings.append(Finding(
                id=check_id,
                check=check["name"],
                status="FAIL" if fail else "PASS",
                risk=check["risk"].value if fail else Risk.PASS.value,
                detail=check["detail_fail"] if fail else check["detail_pass"],
            ))
    except (Forbidden, GoogleAPIError) as exc:
        logger.warning(f"Tidak dapat membaca IAM policy: {type(exc).__name__}")
        for check_id in ("S-01", "S-02"):
            check = next(c for c in CHECKS if c["id"] == check_id)
            findings.append(Finding(id=check_id, check=check["name"],
                                    status="UNKNOWN", risk=Risk.UNKNOWN.value,
                                    detail="Tidak dapat membaca IAM policy."))

    # --- S-03: Versioning ---
    check = next(c for c in CHECKS if c["id"] == "S-03")
    versioning_on = bucket.versioning_enabled
    findings.append(Finding(
        id="S-03", check=check["name"],
        status="PASS" if versioning_on else "FAIL",
        risk=Risk.PASS.value if versioning_on else check["risk"].value,
        detail=check["detail_pass"] if versioning_on else check["detail_fail"],
    ))

    # --- S-04: Access Logging ---
    check = next(c for c in CHECKS if c["id"] == "S-04")
    logging_on = bool(bucket.logging)
    findings.append(Finding(
        id="S-04", check=check["name"],
        status="PASS" if logging_on else "FAIL",
        risk=Risk.PASS.value if logging_on else check["risk"].value,
        detail=check["detail_pass"] if logging_on else check["detail_fail"],
    ))

    # --- S-05: CORS Wildcard ---
    check = next(c for c in CHECKS if c["id"] == "S-05")
    cors_configs = bucket.cors or []
    has_wildcard = any("*" in c.get("origin", []) for c in cors_configs)
    findings.append(Finding(
        id="S-05", check=check["name"],
        status="FAIL" if has_wildcard else "PASS",
        risk=check["risk"].value if has_wildcard else Risk.PASS.value,
        detail=check["detail_fail"] if has_wildcard else check["detail_pass"],
    ))

    # --- S-06: Uniform Bucket-Level Access ---
    check = next(c for c in CHECKS if c["id"] == "S-06")
    ubla_on = bucket.iam_configuration.uniform_bucket_level_access_enabled
    findings.append(Finding(
        id="S-06", check=check["name"],
        status="PASS" if ubla_on else "FAIL",
        risk=Risk.PASS.value if ubla_on else check["risk"].value,
        detail=check["detail_pass"] if ubla_on else check["detail_fail"],
    ))

    # --- S-07: Retention Policy ---
    check = next(c for c in CHECKS if c["id"] == "S-07")
    retention_on = bucket.retention_period is not None
    findings.append(Finding(
        id="S-07", check=check["name"],
        status="PASS" if retention_on else "FAIL",
        risk=Risk.PASS.value if retention_on else check["risk"].value,
        detail=check["detail_pass"] if retention_on else check["detail_fail"],
    ))

    overall = _overall_risk(findings)
    logger.info(f"Scan selesai untuk bucket '{bucket_name}'. Overall risk: {overall}")
    return ScanResult(bucket=bucket_name, scanned_at=scanned_at,
                      overall_risk=overall, findings=findings)
