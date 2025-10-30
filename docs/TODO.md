# 実装TODO（M1→M4）

本TODOは`docs/requirements.md` v1.0に準拠。チェックボックスは実装進捗用。

## M1: UC1の土台（1週）
- [x] `app/utils/logger.py`: JSON Linesロガー（INFO/WARN/ERROR, 入力IDをハッシュ化）
- [x] `app/core/cache.py`: SQLiteキャッシュ（キー:ハッシュ、値:JSON、TTL=24h、手動クリアAPI）
- [x] `app/api/services/uniprot.py`: ID正規化（mapping, アイソフォーム処理ON/OFF対応）
- [x] `app/api/services/kegg.py`: UniProt→gene→pathway取得と正規化
- [x] `app/api/services/reactome.py`: 関連経路取得と正規化
- [x] `app/api/main.py`: FastAPIエンドポイント（UC1用）とリトライ
- [x] `app/ui/main.py`: 入力フォーム（100件まで、アイソフォーム正規化ON/OFF）
- [x] `app/ui/pages.py`: 経路/出力タブの整備（表・DL・サマリ）
- [ ] エラーハンドリング: 無効ID/非Humanの一覧表示と続行の文言洗練
- [x] 設定: `.env.example`整備と`.env`ローダー組込み（HTTP(S)_PROXY/NO_PROXY/CAパス）

## M2: STRING/PPIと可視化（1週）
- [ ] `app/api/services/string_db.py`: PPI取得（species=9606、required_scoreスライダー）
- [ ] `app/core/network.py`: NetworkXで中心性（degree/betweenness/eigenvector）計算
- [ ] サブグラフ抽出: 3,000エッジ超でLCC→k-core→半径2誘導サブグラフ
- [ ] `pyvis`描画: 色/サイズ/凡例、ノード検索（名前ジャンプ）
- [ ] UI: 中心性上位N=20ハイライト、しきい値変更で再描画

## M3: 解析/エクスポート（1週）
- [ ] 富化: ハイパージオメトリ＋BH補正（母集団=Human全遺伝子、q<0.05）
- [ ] 共通ノード提示と上位中心性ノード表
- [ ] エクスポート: `nodes.csv`/`ppi_edges.csv`/`pathways.json`
- [ ] 可視化エクスポート: PNG/SVG

## M4: 仕上げ/テスト（1週）
- [ ] 例外・再試行メッセージ（簡潔、禁則/出典注意はUIに含めない）
- [ ] ログ/メトリクス表示（API呼数/命中率/遅延）
- [ ] テスト: 単体/結合/UI/E2E、代表IDセット（P31946等）で性能計測（smokeを追加済）
- [ ] ドキュメント更新（README/運用ノート/リリース手順）

## 参考（後続案）
- [ ] サブグラフ抽出のパラメータ設定UI化
- [ ] 代表IDセットの管理とスナップショット比較
