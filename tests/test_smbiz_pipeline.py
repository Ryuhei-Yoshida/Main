import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)


def test_smbiz_pipeline_generates_ranked_recommendations():
    run(["python3", "scripts/run_smbiz_agents.py"])

    json_path = ROOT / "data" / "outputs" / "smbiz_recommendations.json"
    md_path = ROOT / "data" / "outputs" / "smbiz_recommendations.md"

    assert json_path.exists(), "smbiz_recommendations.json should be generated"
    assert md_path.exists(), "smbiz_recommendations.md should be generated"

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert len(payload["top_picks"]) == 3

    scores = [item["final_score"] for item in payload["all_candidates"]]
    assert scores == sorted(scores, reverse=True)

    content = md_path.read_text(encoding="utf-8")
    assert "Top 3 推奨商品" in content
    assert "全候補スコア" in content
