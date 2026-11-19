import json
from dataclasses import asdict
from datetime import datetime, timezone

from core.scanner import ScanResult
from utils.constants import Risk

RISK_COLOR = {
    Risk.CRITICAL.value: "#c0392b",
    Risk.HIGH.value:     "#e67e22",
    Risk.MEDIUM.value:   "#f1c40f",
    Risk.LOW.value:      "#2980b9",
    Risk.PASS.value:     "#27ae60",
    Risk.UNKNOWN.value:  "#7f8c8d",
}

STATUS_ICON = {"FAIL": "✗", "PASS": "✓", "UNKNOWN": "?"}


def to_json(result: ScanResult, indent: int = 2) -> str:
    data = asdict(result)
    return json.dumps(data, ensure_ascii=False, indent=indent)


def to_html(result: ScanResult) -> str:
    overall_color = RISK_COLOR.get(result.overall_risk, "#7f8c8d")
    rows = ""
    for f in result.findings:
        color = RISK_COLOR.get(f.risk, "#7f8c8d")
        icon = STATUS_ICON.get(f.status, "?")
        rows += f"""
        <tr>
          <td>{f.id}</td>
          <td>{f.check}</td>
          <td>{icon} {f.status}</td>
          <td style="color:{color};font-weight:700">{f.risk}</td>
          <td>{f.detail}</td>
        </tr>"""

    error_section = ""
    if result.error:
        error_section = f'<p class="error">⚠ Error: {result.error}</p>'

    return f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>Laporan JagaAwan — {result.bucket}</title>
  <style>
    body{{font-family:system-ui,sans-serif;background:#f4f6f8;color:#2c3e50;margin:0;padding:2rem}}
    h1{{color:#2c3e50}}
    .badge{{display:inline-block;padding:.4rem 1rem;border-radius:6px;color:#fff;
            font-weight:700;font-size:1.1rem;background:{overall_color}}}
    table{{width:100%;border-collapse:collapse;background:#fff;border-radius:8px;
           overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08);margin-top:1.5rem}}
    th{{background:#2c3e50;color:#fff;padding:.75rem 1rem;text-align:left}}
    td{{padding:.7rem 1rem;border-bottom:1px solid #ecf0f1;vertical-align:top}}
    tr:last-child td{{border-bottom:none}}
    tr:hover td{{background:#f8f9fa}}
    .meta{{color:#7f8c8d;font-size:.9rem;margin:.5rem 0 1.5rem}}
    .error{{color:#c0392b;font-weight:600;padding:1rem;background:#fdecea;
            border-radius:6px;margin-top:1rem}}
    footer{{margin-top:2rem;text-align:center;font-size:.8rem;color:#95a5a6}}
  </style>
</head>
<body>
  <h1>🛡 Laporan Keamanan JagaAwan</h1>
  <p class="meta">Bucket: <strong>{result.bucket}</strong> &nbsp;|&nbsp; Diperiksa: {result.scanned_at}</p>
  <p>Risiko keseluruhan: <span class="badge">{result.overall_risk}</span></p>
  {error_section}
  <table>
    <thead>
      <tr><th>ID</th><th>Pemeriksaan</th><th>Status</th><th>Risiko</th><th>Detail</th></tr>
    </thead>
    <tbody>{rows}
    </tbody>
  </table>
  <footer>Proyek JagaAwan — data fiktif untuk pengujian kuliah</footer>
</body>
</html>"""
