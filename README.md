# Dragons Data Lab（DDL）

中日ドラゴンズ特化のデータ解析メディアを、**エージェント分業**で運用するためのリポジトリです。  
このREADMEは「何を作るか」ではなく、**どう実装・運用するか（自動実行含む）**に焦点を当てています。

## 目的
- データ解析の品質と投稿スピードを両立する
- 無料配信→有料化→B2B展開の導線を再現可能にする
- AIエージェント + 人間レビューのハイブリッド運用を定着させる

## リポジトリ構成

```text
.
├── README.md
├── dragonflies_business_plan.md
├── Makefile
├── scripts/
│   ├── run_daily_pipeline.py
│   └── run_weekly_review.py
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
├── configs/
│   └── kpi_targets.yaml
└── data/
    ├── raw/
    ├── processed/
    ├── reports/
    └── logs/
```

## 自動実行の始め方

### 1) 日次パイプライン実行
```bash
make daily
```
- `data/raw/` に収集データ
- `data/processed/` に特徴量データ
- `data/reports/` に日次レポート
- `data/logs/daily_runs.csv` に実行ログ

### 2) 週次レビュー作成
```bash
make weekly
```
- 直近7日分の実行結果を集計して `data/reports/weekly_review.md` を生成

### 3) 一括実行
```bash
make run-all
```

## 運用の基本フロー
1. `agents/README.md` で役割分担を確認
2. `workflows/daily_pipeline.md` に沿って日次運用
3. 投稿は `templates/` を使って標準化
4. `configs/kpi_targets.yaml` を基準に週次レビュー

## ガバナンス原則
- 予測や主張は必ず根拠データを紐づける
- 公開前にFact-check + 人間責任者レビューを必須化
- KPI未達時は「施策を1つだけ」変えて検証する

## 次の実装候補
- 実データAPI接続（取得処理を`run_daily_pipeline.py`に統合）
- `scripts/` にチャネル別投稿文の自動生成CLIを追加
- `dashboard/` でKPI可視化（Looker Studio or Metabase）
