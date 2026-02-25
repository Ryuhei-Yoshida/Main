import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)


def test_smbiz_lp_data_builds_from_top_pick():
    run(["python3", "scripts/run_smbiz_agents.py"])
    run(["python3", "scripts/build_smbiz_lp.py"])

    lp_data = ROOT / "lp" / "lp_data.json"
    assert lp_data.exists(), "lp_data.json should be generated"

    payload = json.loads(lp_data.read_text(encoding="utf-8"))
    assert payload["product_name"]
    assert payload["price_jpy"] > 0
    assert len(payload["faq"]) >= 3


def test_lp_template_has_core_conversion_sections():
    html = (ROOT / "lp" / "index.html").read_text(encoding="utf-8")
    for marker in ["hero", "選ばれる理由", "他の選択肢との比較", "FAQ", "sticky-cta"]:
        assert marker in html
