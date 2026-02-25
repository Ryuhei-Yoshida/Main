# Daily Pipeline

1. Data Ingestion実行
2. Feature Engineering実行
3. Modeling実行
4. Fact-check事前照合
5. Narrativeで配信用原稿作成
6. 人間責任者レビュー
7. 公開 & KPI記録

## フェイルオーバー
- 収集失敗時: 前日データとの差分更新をスキップし速報モードへ
- モデル不調時: 予測抜きの解説投稿へ切り替え
- 検証NG時: 公開延期し修正後に再チェック

