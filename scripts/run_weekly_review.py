#!/usr/bin/env python3
"""Generate a simple weekly review from daily run logs."""
from __future__ import annotations

import csv
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "data" / "logs" / "daily_runs.csv"
OUT_PATH = ROOT / "data" / "reports" / "weekly_review.md"


def main() -> int:
    if not LOG_PATH.exists():
        print("[weekly] no daily logs found. Run daily pipeline first.")
        return 1

    rows = []
    with LOG_PATH.open("r", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        rows = list(reader)

    week_ago = dt.datetime.now() - dt.timedelta(days=7)
    recent = [r for r in rows if dt.datetime.fromisoformat(r["timestamp"]) >= week_ago]
    total = len(recent)
    passed = sum(1 for r in recent if r["status"] == "PASS")
    failed = total - passed
    pass_rate = (passed / total * 100) if total else 0

    text = f"""# Weekly Review

- 対象実行数: {total}
- PASS: {passed}
- NG: {failed}
- PASS率: {pass_rate:.1f}%
- 生成日時: {dt.datetime.now().isoformat(timespec='seconds')}

## Next Action
- PASS率が95%未満の場合、Fact-check条件と入力データ品質を確認する。
- 投稿リードタイム短縮のため、Narrativeテンプレートを改善する。
"""
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(text, encoding="utf-8")
    print(f"[weekly] report={OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
