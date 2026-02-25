# SMBiz Pipeline（無在庫×自社LP×Meta広告）

## 目的
- 広告出稿前に「売れる可能性 × 採算性 × 規約安全性」を事前に点検する
- 商品掲載判断を属人化せず、再現性あるスコアリングで決定する

## 手順
1. `data/raw/smbiz_product_candidates.csv` に候補商品を追記
2. `configs/smbiz_constraints.yaml` で制約条件を設定
3. `python3 scripts/run_smbiz_agents.py` を実行
4. `data/outputs/smbiz_recommendations.md` のTop3を確認
5. `python3 scripts/build_smbiz_lp.py` で `lp/lp_data.json` を生成
6. `lp/index.html` を公開前レビュー（FV/比較表/FAQ/固定CTAを確認）
7. Top3のうち1つだけを先にテスト配信（ABはクリエイティブのみ）

## 運用ルール
- 初回は1商品1LP1訴求角度で検証する
- CPA悪化時は商品を変えず、クリエイティブだけ変更する
- 規約リスクが高い候補は、訴求を緩和して再評価する


## LPデザイン方針（人気ショップ準拠）
- ファーストビューは「1メッセージ + 価格 + CTA」の最短導線
- ソーシャルプルーフ（レビュー・評価・比較表）をCTA前に配置
- 固定CTAでモバイル離脱を抑制
- 送料・返品・配送日数を明示して不安要素を先回り
