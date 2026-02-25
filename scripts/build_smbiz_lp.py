#!/usr/bin/env python3
"""Build LP data from SMBiz recommendations so LP can be launched quickly."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECOMMENDATIONS = ROOT / "data" / "outputs" / "smbiz_recommendations.json"
CANDIDATES = ROOT / "data" / "raw" / "smbiz_product_candidates.csv"
LP_DATA = ROOT / "lp" / "lp_data.json"


def read_candidates() -> dict:
    by_id: dict[str, dict] = {}
    with CANDIDATES.open("r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            by_id[row["product_id"]] = row
    return by_id


def build_payload() -> dict:
    if not RECOMMENDATIONS.exists():
        raise SystemExit("run python3 scripts/run_smbiz_agents.py first")

    rec = json.loads(RECOMMENDATIONS.read_text(encoding="utf-8"))
    top = rec["top_picks"][0]
    by_id = read_candidates()
    seed = by_id[top["product_id"]]

    product_name = top["product_name"]
    hook = top["lp_hook"]
    price = int(float(seed["price_jpy"]))
    persona = seed["target_persona"]

    return {
        "product_id": top["product_id"],
        "product_name": product_name,
        "lp_hook": hook,
        "price_jpy": price,
        "benefits": [
            f"{persona}向けに使いやすい設計",
            "初回テストLP向けの分かりやすいベネフィット訴求",
            "Meta広告クリエイティブとメッセージを統一しやすい",
        ],
        "values": [
            {"title": "ファーストビュー最適化", "body": "ベネフィット1文 + 価格 + CTAを最上部に集約"},
            {"title": "信頼構築", "body": "レビュー・比較表・FAQを順序立てて表示"},
            {"title": "CV導線", "body": "ページ下部に固定CTAで取りこぼしを抑制"},
        ],
        "comparison": [
            ["訴求の分かりやすさ", "高い", "ばらつきがある"],
            ["購入導線", "固定CTAあり", "スクロール依存"],
            ["配送料・返品表記", "明確", "不明瞭なことが多い"],
        ],
        "reviews": [
            {"name": "LPテスト担当", "text": "訴求が明確で、広告とLPの一貫性が作りやすい"},
            {"name": "運用者", "text": "FAQと保証情報を置くだけで離脱が減った"},
            {"name": "デザイナー", "text": "人気D2Cに近い情報設計で初速を出しやすい"},
        ],
        "faq": [
            {"q": "配送は何日くらい？", "a": "商品ごとに異なりますが、目安5〜10日で発送します。"},
            {"q": "返品ポリシーは？", "a": "到着後30日以内は返品を受け付けます。"},
            {"q": "最初のABテストはどう組む？", "a": "商品は固定し、クリエイティブだけ2〜3案で比較してください。"},
        ],
    }


def main() -> int:
    payload = build_payload()
    LP_DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {LP_DATA.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
