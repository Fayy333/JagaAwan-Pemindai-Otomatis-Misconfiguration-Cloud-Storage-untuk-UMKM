import json
from unittest.mock import MagicMock, patch
from scanner.scanner import hitung_skor, periksa_bucket


def _make_mock_bucket(
    versioning=False,
    logging_cfg=None,
    cors=None,
    ubla=False,
    retention=None,
    iam_members=None,
):
    bucket = MagicMock()
    bucket.versioning_enabled = versioning
    bucket.logging = logging_cfg or {}
    bucket.cors = cors or []
    bucket.iam_configuration.uniform_bucket_level_access_enabled = ubla
    bucket.iam_configuration.public_access_prevention = "enforced" if ubla else "unspecified"
    bucket.retention_period = retention

    policy = MagicMock()
    members = iam_members or []
    policy.bindings = [{"members": members}] if members else []
    bucket.get_iam_policy.return_value = policy
    return bucket


def test_all_pass():
    bucket = _make_mock_bucket(
        versioning=True,
        logging_cfg={"logBucket": "log-bucket"},
        cors=[{"origin": ["https://example.com"]}],
        ubla=True,
        retention=86400,
        iam_members=[],
    )
    assert periksa_bucket(bucket)["risiko"] == "AMAN"


def test_public_access_high():
    bucket = _make_mock_bucket(iam_members=["allUsers"])
    assert periksa_bucket(bucket)["risiko"] == "TINGGI"


def test_score_never_negative():
    assert hitung_skor([{"kurang": 30}] * 5) == 0
