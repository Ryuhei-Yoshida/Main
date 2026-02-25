#!/usr/bin/env python3
"""Run a local automated daily pipeline for Dragons Data Lab.

This is a lightweight offline implementation so the workflow can be executed
immediately without external APIs.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw" / "games_raw.csv"
FEATURES = DATA / "processed" / "features.csv"
PREDICTIONS = DATA / "processed" / "predictions.csv"
REPORT = DATA / "outputs" / "daily_report.md"
SUMMARY = DATA / "outputs" / "run_summary.json"
LOG = DATA / "logs" / "pipeline.log"


@dataclass
class RunState:
    started_at: str
    steps: list[dict]
    publish_allowed: bool = True

    def add_step(self, name: str, status: str, details: str = "") -> None:
        self.steps.append({"step": name, "status": status, "details": details})
        if status == "failed":
            self.publish_allowed = False


def ensure_dirs() -> None:
    for p in [DATA / "raw", DATA / "processed", DATA / "outputs", DATA / "logs"]:
        p.mkdir(parents=True, exist_ok=True)


def log_line(line: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} {line}\n")


def ingest() -> list[dict]:
    """Create local sample data if no raw file exists, then load it."""
    if not RAW.exists():
        sample = [
            {"date": "2026-04-01", "opponent": "Giants", "runs_for": "3", "runs_against": "2", "hits": "8", "errors": "0"},
            {"date": "2026-04-02", "opponent": "Giants", "runs_for": "1", "runs_against": "4", "hits": "6", "errors": "1"},
            {"date": "2026-04-03", "opponent": "Tigers", "runs_for": "5", "runs_against": "3", "hits": "11", "errors": "0"},
            {"date": "2026-04-04", "opponent": "Tigers", "runs_for": "2", "runs_against": "2", "hits": "7", "errors": "0"},
        ]
        with RAW.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=sample[0].keys())
            writer.writeheader()
            writer.writerows(sample)

    with RAW.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        raise ValueError("raw data is empty")

    return rows


def build_features(rows: list[dict]) -> list[dict]:
    features: list[dict] = []
    for r in rows:
        rf = int(r["runs_for"])
        ra = int(r["runs_against"])
        features.append(
            {
                "date": r["date"],
                "opponent": r["opponent"],
                "run_diff": rf - ra,
                "is_win": 1 if rf > ra else 0,
                "offense_index": round((rf * 0.7) + (int(r["hits"]) * 0.3), 3),
                "defense_penalty": round((ra * 0.8) + (int(r["errors"]) * 0.2), 3),
            }
        )

    with FEATURES.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=features[0].keys())
        writer.writeheader()
        writer.writerows(features)

    return features


def model_predict(features: list[dict]) -> list[dict]:
    # Simple transparent baseline model for offline automation.
    predictions = []
    for item in features:
        score = float(item["offense_index"]) - float(item["defense_penalty"])
        prob = max(0.05, min(0.95, 0.5 + (score / 20)))
        predictions.append(
            {
                "date": item["date"],
                "opponent": item["opponent"],
                "win_probability": round(prob, 3),
                "predicted_result": "W" if prob >= 0.5 else "L",
            }
        )

    with PREDICTIONS.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=predictions[0].keys())
        writer.writeheader()
        writer.writerows(predictions)

    return predictions


def fact_check(rows: list[dict], preds: list[dict]) -> list[str]:
    issues: list[str] = []
    if len(rows) != len(preds):
        issues.append("raw rows and predictions count mismatch")
    for p in preds:
        wp = float(p["win_probability"])
        if wp < 0 or wp > 1:
            issues.append(f"invalid probability on {p['date']}: {wp}")
    return issues


def write_report(rows: list[dict], features: list[dict], preds: list[dict]) -> None:
    wins = sum(int(x["is_win"]) for x in features)
    avg_prob = round(mean(float(x["win_probability"]) for x in preds), 3)
    latest = rows[-1]

    content = "# Daily Report (Auto-generated)\n\n"
    content += f"- 対象試合数: {len(rows)}\n"
    content += f"- 勝利数: {wins}\n"
    content += f"- 平均勝率予測: {avg_prob}\n"
    content += "\n## 最新試合メモ\n"
    content += f"- 日付: {latest['date']}\n"
    content += f"- 対戦: 中日 vs {latest['opponent']}\n"
    content += f"- 得点: {latest['runs_for']} - {latest['runs_against']}\n"
    content += "\n## 次アクション\n- 有料版向けに打席別詳細を追記\n"

    REPORT.write_text(content, encoding="utf-8")


def main() -> int:
    ensure_dirs()
    state = RunState(started_at=datetime.now().isoformat(), steps=[])
    try:
        rows = ingest()
        state.add_step("ingestion", "passed", f"rows={len(rows)}")
        log_line("ingestion passed")

        features = build_features(rows)
        state.add_step("feature_engineering", "passed", f"rows={len(features)}")
        log_line("feature engineering passed")

        preds = model_predict(features)
        state.add_step("modeling", "passed", f"rows={len(preds)}")
        log_line("modeling passed")

        issues = fact_check(rows, preds)
        if issues:
            state.add_step("fact_check", "failed", "; ".join(issues))
            log_line(f"fact-check failed: {issues}")
        else:
            state.add_step("fact_check", "passed", "no issues")
            log_line("fact-check passed")

        if state.publish_allowed:
            write_report(rows, features, preds)
            state.add_step("narrative", "passed", str(REPORT.relative_to(ROOT)))
            log_line("report generated")
        else:
            state.add_step("narrative", "skipped", "publish gate closed")

    except Exception as exc:  # pragma: no cover
        state.add_step("pipeline", "failed", str(exc))
        log_line(f"pipeline failed: {exc}")

    SUMMARY.write_text(
        json.dumps(
            {
                "started_at": state.started_at,
                "finished_at": datetime.now().isoformat(),
                "publish_allowed": state.publish_allowed,
                "steps": state.steps,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return 0 if state.publish_allowed else 1


if __name__ == "__main__":
    raise SystemExit(main())
