import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)


def test_daily_pipeline_generates_outputs():
    run(["python3", "scripts/run_daily_pipeline.py"])

    summary_path = ROOT / "data" / "outputs" / "run_summary.json"
    report_path = ROOT / "data" / "outputs" / "daily_report.md"

    assert summary_path.exists(), "run_summary.json should be generated"
    assert report_path.exists(), "daily_report.md should be generated"

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert "steps" in summary
    assert any(step["step"] == "fact_check" for step in summary["steps"])


def test_weekly_review_generates_output():
    # Ensure prerequisite exists.
    run(["python3", "scripts/run_daily_pipeline.py"])
    run(["python3", "scripts/run_weekly_review.py"])

    weekly_path = ROOT / "data" / "outputs" / "weekly_review.md"
    assert weekly_path.exists(), "weekly_review.md should be generated"

    content = weekly_path.read_text(encoding="utf-8")
    assert "Weekly KPI Review" in content
    assert "KPI Targets" in content
