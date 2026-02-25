#!/usr/bin/env python3
"""Run the DDL daily pipeline end-to-end.

This script simulates the agent workflow so the repository can be executed
non-interactively from cron/GitHub Actions/local scheduler.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = DATA_DIR / "reports"
LOG_DIR = DATA_DIR / "logs"


def ensure_dirs() -> None:
    for path in [RAW_DIR, PROCESSED_DIR, REPORTS_DIR, LOG_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def ingest(target_date: str) -> Path:
    """Create deterministic sample ingestion data for the target date."""
    random.seed(target_date)
    output = RAW_DIR / f"game_{target_date}.json"
    payload = {
        "date": target_date,
        "opponent": random.choice(["Giants", "Tigers", "Carp", "BayStars"]),
        "runs_scored": random.randint(0, 8),
        "runs_allowed": random.randint(0, 8),
        "hits": random.randint(3, 14),
        "errors": random.randint(0, 2),
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def feature_engineering(raw_path: Path) -> Path:
    data = json.loads(raw_path.read_text(encoding="utf-8"))
    game_score = (data["runs_scored"] - data["runs_allowed"]) * 10 + data["hits"] - (data["errors"] * 2)
    quality = {
        "date": data["date"],
        "opponent": data["opponent"],
        "run_diff": data["runs_scored"] - data["runs_allowed"],
        "game_score": game_score,
        "win": int(data["runs_scored"] > data["runs_allowed"]),
    }
    output = PROCESSED_DIR / f"features_{data['date']}.json"
    output.write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def modeling(feature_path: Path) -> dict:
    row = json.loads(feature_path.read_text(encoding="utf-8"))
    win_prob = max(0.05, min(0.95, 0.5 + row["run_diff"] * 0.08 + row["game_score"] * 0.005))
    return {
        "date": row["date"],
        "opponent": row["opponent"],
        "win_probability_next_game": round(win_prob, 3),
        "confidence": "high" if 0.35 <= win_prob <= 0.65 else "medium",
    }


def fact_check(model_output: dict) -> tuple[bool, list[str]]:
    issues: list[str] = []
    prob = model_output["win_probability_next_game"]
    if not (0 <= prob <= 1):
        issues.append("win probability out of range")
    if model_output["confidence"] not in {"high", "medium", "low"}:
        issues.append("invalid confidence label")
    return len(issues) == 0, issues


def narrative(raw_path: Path, feature_path: Path, model_output: dict) -> str:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    feat = json.loads(feature_path.read_text(encoding="utf-8"))
    result = "勝利" if raw["runs_scored"] > raw["runs_allowed"] else "敗戦"
    return (
        f"{raw['date']} vs {raw['opponent']} は{result}。"
        f"得失点差は{feat['run_diff']}、試合スコアは{feat['game_score']}。"
        f"次戦勝率予測は{model_output['win_probability_next_game']:.1%}。"
    )


def monetization_summary(message: str) -> str:
    return f"無料版要約: {message}\n有料版CTA: 打席別詳細分析と次戦キープレイヤー解説を公開中。"


def write_report(target_date: str, message: str, model_output: dict, issues: list[str]) -> Path:
    report = REPORTS_DIR / f"daily_report_{target_date}.md"
    lines = [
        f"# Daily Report {target_date}",
        "",
        "## Narrative",
        message,
        "",
        "## Model Output",
        "```json",
        json.dumps(model_output, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Fact-check",
        "PASS" if not issues else "NG",
    ]
    if issues:
        lines.extend(["", "- " + "\n- ".join(issues)])
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def write_log(target_date: str, status: str, report_path: Path) -> Path:
    log_path = LOG_DIR / "daily_runs.csv"
    exists = log_path.exists()
    with log_path.open("a", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        if not exists:
            writer.writerow(["timestamp", "date", "status", "report"])
        writer.writerow([dt.datetime.now().isoformat(timespec="seconds"), target_date, status, str(report_path.relative_to(ROOT))])
    return log_path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run DDL daily pipeline")
    p.add_argument("--date", default=dt.date.today().isoformat(), help="Target date YYYY-MM-DD")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    ensure_dirs()
    raw_path = ingest(args.date)
    feature_path = feature_engineering(raw_path)
    model_out = modeling(feature_path)
    ok, issues = fact_check(model_out)

    message = narrative(raw_path, feature_path, model_out)
    final_message = monetization_summary(message)
    report_path = write_report(args.date, final_message, model_out, issues)
    write_log(args.date, "PASS" if ok else "NG", report_path)

    print(f"[daily] date={args.date} status={'PASS' if ok else 'NG'} report={report_path}")
    if issues:
        for issue in issues:
            print(f"[issue] {issue}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
