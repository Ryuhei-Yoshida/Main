#!/usr/bin/env python3
"""Run a multi-agent evaluator for dropshipping LP + Meta Ads business ideas."""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "data" / "raw" / "smbiz_product_candidates.csv"
CONSTRAINTS = ROOT / "configs" / "smbiz_constraints.yaml"
OUTPUT_JSON = ROOT / "data" / "outputs" / "smbiz_recommendations.json"
OUTPUT_MD = ROOT / "data" / "outputs" / "smbiz_recommendations.md"


@dataclass
class AgentScore:
    product_id: str
    product_name: str
    market_score: float
    economics_score: float
    logistics_score: float
    policy_score: float
    creative_score: float
    final_score: float
    recommended_angle: str
    lp_hook: str
    meta_creative_hint: str


def parse_simple_yaml(path: Path) -> dict:
    result: dict = {}
    stack: list[tuple[int, dict]] = [(-1, result)]
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        text = raw.strip()

        if text.startswith("- "):
            parent = stack[-1][1]
            parent.setdefault("_list", []).append(text[2:].strip())
            continue

        key, _, value = text.partition(":")
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


def bounded(value: float, low: float = 0.0, high: float = 10.0) -> float:
    return round(max(low, min(high, value)), 3)


def angle_for_category(category: str) -> tuple[str, str, str]:
    table = {
        "home": (
            "家事時短",
            "1日10分の掃除を3分に。散らかりを一気に吸引",
            "散らかった机→3秒で吸うUGC風ショート動画",
        ),
        "beauty": (
            "頭皮ケア習慣",
            "お風呂3分で“すっきり感”をつくる新習慣",
            "使用前後の主観コメント+使用手順のハウツー動画",
        ),
        "pet": (
            "留守番の安心",
            "外出中でも水切れ不安を減らす",
            "帰宅時も水が残っている安心シーン",
        ),
        "fitness": (
            "在宅リセット",
            "デスクワーク後の5分リセットストレッチ",
            "肩が丸まった姿勢→伸ばすビフォーアフター風(誇大NG)",
        ),
        "kitchen": (
            "食品ロス削減",
            "余った食材を長持ち、まとめ買いがムダにならない",
            "買い物直後に小分け真空する時短ルーティン",
        ),
        "baby": (
            "外出時の安心",
            "おむつ替えをどこでも清潔・スムーズに",
            "公園・車内・商業施設で使える携帯性を見せる",
        ),
    }
    return table.get(
        category,
        (
            "日常の小さな課題解決",
            "毎日の手間を減らすアイテム",
            "利用シーン中心の短尺動画",
        ),
    )


def evaluate(row: dict, constraints: dict) -> AgentScore:
    price = float(row["price_jpy"])
    cogs = float(row["cogs_jpy"])
    ship_days = float(row["shipping_days"])
    problem_fit = float(row["problem_fit_score"])
    novelty = float(row["novelty_score"])
    risk = float(row["policy_risk_score"])

    cogs_ratio = cogs / price
    margin = 1 - cogs_ratio

    market_score = bounded(problem_fit * 0.75 + novelty * 0.25)
    economics_score = bounded((margin * 10) + (1 - abs(cogs_ratio - 0.3)) * 2)

    max_ship_days = constraints["smbiz_constraints"]["max_shipping_days"]
    logistics_score = bounded(10 - max(0, ship_days - max_ship_days) * 2)

    policy_score = bounded(10 - (risk * 1.2))
    creative_score = bounded((problem_fit * 0.5) + (10 - risk) * 0.3 + novelty * 0.2)

    final_score = bounded(
        market_score * 0.28
        + economics_score * 0.24
        + logistics_score * 0.14
        + policy_score * 0.2
        + creative_score * 0.14
    )

    angle, hook, hint = angle_for_category(row["category"])

    if margin < constraints["smbiz_constraints"]["min_gross_margin"]:
        hint += " / 粗利が低いため価格テスト前提"
    if ship_days > max_ship_days:
        hint += " / 配送日数が長くCVR低下リスクあり"

    return AgentScore(
        product_id=row["product_id"],
        product_name=row["product_name"],
        market_score=market_score,
        economics_score=economics_score,
        logistics_score=logistics_score,
        policy_score=policy_score,
        creative_score=creative_score,
        final_score=final_score,
        recommended_angle=angle,
        lp_hook=hook,
        meta_creative_hint=hint,
    )


def load_candidates(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_outputs(ranked: list[AgentScore]) -> None:
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now().isoformat(),
        "top_picks": [asdict(x) for x in ranked[:3]],
        "all_candidates": [asdict(x) for x in ranked],
    }
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# 無在庫×自社LP×Meta広告: 商品提案レポート",
        "",
        "## Top 3 推奨商品",
        "",
    ]
    for i, item in enumerate(ranked[:3], start=1):
        lines.extend(
            [
                f"### {i}. {item.product_name} ({item.product_id})",
                f"- 総合スコア: {item.final_score}",
                f"- 推奨訴求角度: {item.recommended_angle}",
                f"- LPフック案: {item.lp_hook}",
                f"- Meta広告クリエイティブ案: {item.meta_creative_hint}",
                "",
            ]
        )

    lines.extend(["## 全候補スコア", "", "|ID|商品名|総合|市場性|採算|物流|規約|クリエイティブ|", "|---|---|---:|---:|---:|---:|---:|---:|"])
    for item in ranked:
        lines.append(
            f"|{item.product_id}|{item.product_name}|{item.final_score}|{item.market_score}|{item.economics_score}|{item.logistics_score}|{item.policy_score}|{item.creative_score}|"
        )

    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    constraints = parse_simple_yaml(CONSTRAINTS)
    candidates = load_candidates(INPUT_CSV)
    scored = [evaluate(row, constraints) for row in candidates]
    ranked = sorted(scored, key=lambda x: x.final_score, reverse=True)
    save_outputs(ranked)
    print(f"wrote {OUTPUT_JSON.relative_to(ROOT)} and {OUTPUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
