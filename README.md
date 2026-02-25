# Dragons Data Lab（DDL）

中日ドラゴンズ特化のデータ解析メディアを、**エージェント分業**で運用するためのリポジトリです。  
このREADMEは「何を作るか」ではなく、**どう実装・運用するか**に焦点を当てています。

## 目的
- データ解析の品質と投稿スピードを両立する
- 無料配信→有料化→B2B展開の導線を再現可能にする
- AIエージェント + 人間レビューのハイブリッド運用を定着させる

## リポジトリ構成

```text
.
├── README.md
├── dragonflies_business_plan.md
├── agents/
│   ├── README.md
│   ├── orchestrator.md
│   ├── data-ingestion/agent.md
│   ├── feature-engineering/agent.md
│   ├── modeling/agent.md
│   ├── narrative/agent.md
│   ├── fact-check/agent.md
│   └── monetization/agent.md
├── workflows/
│   ├── daily_pipeline.md
│   └── weekly_review.md
├── templates/
│   ├── post_game_report.md
│   └── paid_article.md
└── configs/
    └── kpi_targets.yaml
```

## 運用の始め方（最短）
1. `agents/README.md` を読み、役割分担を確定する
2. `workflows/daily_pipeline.md` の手順で毎日の処理を回す
3. 投稿は `templates/` のテンプレートを使って標準化する
4. `configs/kpi_targets.yaml` に実績値を追記し、週次レビューする


## ガバナンス原則
- 予測や主張は必ず根拠データを紐づける
- 公開前にFact-check + 人間責任者レビューを必須化
- KPI未達時は「施策を1つだけ」変えて検証する

## 次の実装候補
- `data/` と `notebooks/` を追加し、再現用データ分析基盤を整備
- `scripts/` にETLと投稿下書き生成を自動化するCLIを実装
- `dashboard/` でKPI可視化（Looker Studio or Metabase）



## 追加ユースケース: 無在庫×自社LP×Meta広告
- `agents/smbiz/README.md` に、複数エージェントで商品選定精度を高める構成を追加
- `workflows/smbiz_pipeline.md` で運用手順を標準化
- `scripts/run_smbiz_agents.py` で商品候補のスコアリングとTop3提案を自動生成
- `lp/index.html` + `scripts/build_smbiz_lp.py` で、人気ショップ構成を参考にした自社LPを自動反映

クイック実行:
```bash
python3 scripts/run_smbiz_agents.py
python3 scripts/build_smbiz_lp.py
```
