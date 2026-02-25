#!/usr/bin/env python3
"""Generate a weekly KPI review summary from local config and latest run output."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "kpi_targets.yaml"
SUMMARY = ROOT / "data" / "outputs" / "run_summary.json"
OUTPUT = ROOT / "data" / "outputs" / "weekly_review.md"


def parse_simple_yaml(path: Path) -> dict:
    # Minimal parser for current tiny config format (no external deps).
    result: dict = {}
    stack: list[tuple[int, dict]] = [(-1, result)]
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        key, _, value = raw.strip().partition(":")
        value = value.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if value == "":
            parent[key] = {}
            stack.append((indent, parent[key]))
        else:
            if value.replace(".", "", 1).isdigit():
                parent[key] = float(value) if "." in value else int(value)
            else:
                parent[key] = value
    return result


def main() -> int:
    if not SUMMARY.exists():
        raise SystemExit("run daily pipeline first: missing data/outputs/run_summary.json")

    config = parse_simple_yaml(CONFIG)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    content = [
        "# Weekly KPI Review (Auto-generated)",
        "",
        f"- 生成時刻: {datetime.now().isoformat()}",
        f"- 直近日次公開可否: {'OK' if summary['publish_allowed'] else 'NG'}",
        "",
        "## KPI Targets",
        f"- Xフォロワー（年）: {config['kpi_targets']['social']['x_followers_year1']}",
        f"- YouTube登録者（年）: {config['kpi_targets']['social']['youtube_subscribers_year1']}",
        f"- 有料会員CVR目標: {config['kpi_targets']['revenue']['paid_member_cvr_min']:.2f}〜{config['kpi_targets']['revenue']['paid_member_cvr_max']:.2f}",
        f"- 解約率上限: {config['kpi_targets']['revenue']['monthly_churn_max']:.2f}",
        "",
        "## Daily Pipeline Steps",
    ]

    for s in summary["steps"]:
        content.append(f"- {s['step']}: {s['status']} ({s.get('details','')})")

    OUTPUT.write_text("\n".join(content) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
