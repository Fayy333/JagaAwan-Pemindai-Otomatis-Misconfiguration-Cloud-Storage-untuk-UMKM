import json
from unittest.mock import MagicMock, patch
from core.scanner import scan, ScanResult
from utils.constants import Risk


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
    bucket.retention_period = retention

    policy = MagicMock()
    members = iam_members or []
    policy.bindings = [{"members": members}] if members else []
    bucket.get_iam_policy.return_value = policy
    return bucket


@patch("core.scanner.storage.Client")
def test_all_pass(mock_client):
    bucket = _make_mock_bucket(
        versioning=True,
        logging_cfg={"logBucket": "log-bucket"},
        cors=[{"origin": ["https://example.com"]}],
        ubla=True,
        retention=86400,
        iam_members=[],
    )
    mock_client.return_value.get_bucket.return_value = bucket

    result = scan("my-safe-bucket")

    assert result.overall_risk == Risk.PASS.value
    for f in result.findings:
        assert f.status == "PASS"


@patch("core.scanner.storage.Client")
def test_public_access_critical(mock_client):
    bucket = _make_mock_bucket(iam_members=["allUsers"])
    mock_client.return_value.get_bucket.return_value = bucket

    result = scan("my-public-bucket")

    assert result.overall_risk == Risk.CRITICAL.value
    s01 = next(f for f in result.findings if f.id == "S-01")
    assert s01.status == "FAIL"
    assert s01.risk == Risk.CRITICAL.value


@patch("core.scanner.storage.Client")
def test_bucket_not_found(mock_client):
    from google.api_core.exceptions import NotFound
    mock_client.return_value.get_bucket.side_effect = NotFound("bucket")

    result = scan("missing-bucket")

    assert result.overall_risk == Risk.UNKNOWN.value
    assert "tidak ditemukan" in result.error
