# SMBiz Agent Team（無在庫×LP×Meta広告）

このチームは「商品候補の選定精度」を上げるために、1つの意思決定を複数エージェントで分業します。

## エージェント構成
1. **Market Scout**: ニーズ強度・悩みの深さ・競合飽和度を評価
2. **Unit Economics**: 粗利、CPA許容量、LTV見込みを評価
3. **Policy Guard**: Meta広告ポリシー観点でリスク評価
4. **LP Strategist**: LPのファーストビュー訴求・FAQ・オファー設計
5. **Creative Planner**: UGC/動画向け訴求角度を提案
6. **Orchestrator**: 各エージェントの評価を統合し、Top3を確定

## 出力物
- `data/outputs/smbiz_recommendations.json`: 全候補の機械可読スコア
- `data/outputs/smbiz_recommendations.md`: Top3と訴求案
- `lp/lp_data.json`: LP反映用のトップ商品データ
- `lp/index.html`: 人気ショップ設計を参考にしたLPテンプレート

## 実行
```bash
python3 scripts/run_smbiz_agents.py
python3 scripts/build_smbiz_lp.py
```
