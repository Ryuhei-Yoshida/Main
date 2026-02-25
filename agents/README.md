# Agent Team Handbook

このフォルダは、DDLのエージェント運用仕様を管理します。

## Agent一覧
- Data Ingestion: 試合データ・成績・ニュース収集
- Feature Engineering: 指標生成、定義管理
- Modeling: 予測モデル更新、性能監視
- Narrative: SNS/記事向けの文章化
- Fact-check: 数値・固有名詞・引用検証
- Monetization: 課金導線、価格・継続率改善

## 共通ルール
1. 各Agentは入力・出力を`agent.md`で明文化する
2. すべてのアウトプットに「根拠データID」を添付する
3. 最終公開は人間責任者の承認が必要
4. 障害時は`workflows/daily_pipeline.md`のフェイルオーバー手順に従う

## 推奨運用順
1. data-ingestion
2. feature-engineering
3. modeling
4. fact-check
5. narrative
6. monetization
