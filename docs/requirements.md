# 要件定義書 v1.0（uni2path）

本書は`project.md`と`question.md`の合意回答を統合し、実装可能な最終仕様として確定する。

## 1. 概要
- 目的: UniProt ID群からKEGG/Reactome経路とSTRING PPIを取得・可視化し、機序・副作用仮説探索を支援する研究用途ツール。
- 対象: 研究者（最優先）。初期リリースはUC1を優先する。
- 言語: 日本語UI（英語名称はツールチップ）。

## 2. ユースケース（優先度）
- UC1: 単一ID→関連経路一覧＋KEGG/Reactomeビュー表示（優先）。
- UC2: 複数ID→高信頼PPI生成＋中心性上位をハイライト。
- UC3: 経路×PPI横断（共通ノード、富化）。
- UC4: 結果エクスポート（PNG/SVG/CSV/JSON）。

## 3. スコープ
- 内: 公開API（KEGG/Reactome/STRING/UniProt）の取得・正規化・可視化・簡易富化、ローカルキャッシュ、再現性（スナップショット任意）。
- 外: 独自DB同梱、商用再配布ライセンス付与、自動論文生成。
- 非Human入力は非対応（削除）。Human限定のため種フィルタUIは設けない。

## 4. 入力仕様
- 受理: UniProt IDの改行/カンマ/タブ混在。空白はトリム、重複/空行は除去。
- 上限: 100件/回。
- 無効ID: 受理しない（一覧で明示）。
- アイソフォーム: 正規化の有無をUIで選択（既定: 正規化する）。
- 既定種: Human(9606) 固定。

## 5. 出力仕様
- 経路タブ: KEGG/ReactomeのID・名称・URL・該当ノード数。
- PPIタブ: ノード/エッジ表、中心性スコア、インタラクティブグラフ（pyvis）。
- 解析タブ: 富化上位（BH補正）、共通ノード、中心性上位。
- エクスポート: `nodes.csv`/`ppi_edges.csv`/`pathways.json`/可視化PNG・SVG。
- 文字コード: UTF-8、改行LF。

## 6. 機能要件
- F1 経路一覧: UniProt→KEGG/Reactome検索、2–5秒以内目標（単一ID）。
- F2 PPI取得: STRING `required_score`スライダー（400–990、既定700）。
- F3 中心性: degree/betweenness/eigenvector計算、上位N=20をハイライト。
- F4 富化: ハイパージオメトリ、BH補正、q<0.05。母集団=Human全遺伝子。
- F5 キャッシュ: キー=APIクエリ（ID集合/スコア等）、TTL=24h。
- F6 ログ: 入力IDはハッシュ化。API呼数/遅延/失敗率/例外をJSON Linesで出力。
- F7 再現性: APIレスポンスのJSONスナップショット保存は既定OFF（切替可）。
- F8 手動キャッシュクリア: UIでクリア可能。

## 7. 非機能要件
- 性能SLO: P50≤2s / P95≤8s（単一IDの各ビュー初回）。
- 同時利用: 想定5ユーザ。FastAPI+Uvicornで水平拡張可能。
- 品質: 自動リトライ（指数バックオフ最大3回）。
- i18n: 日本語UI・英名ツールチップ。

## 8. 可視化要件
- ライブラリ: 既定pyvis（必要に応じPlotly補助）。
- 操作: 拡大/ドラッグ/ノード選択、ノード検索（名前ジャンプ）。
- 色/サイズ: 中心性上位・入力ノード・共通ノードを差別化、凡例表示。
- ツールチップ: 名称、スコア、経路数（ノード）。
- 大規模ネットワーク対応: 3,000エッジを閾値に警告＋自動サブグラフ抽出。
  - 抽出手順: 最大連結成分→k-core(k=2)→中心性上位ノード周辺の誘導サブグラフ（半径=2）。
  - 根拠: ブラウザ上の力学レイアウト/反復描画は数千エッジで顕著に劣化。3,000超は操作性低下が大きいため、可視性と応答性のバランスで設定。パフォーマンステストで見直し可。

## 9. 外部API/レート制御
- KEGG REST: `conv/link`でUniProt→gene→pathway。
- Reactome: Content Serviceで関連経路取得。
- STRING: `species=9606`, `required_score>=700`既定。
- UniProt: ID mappingで旧ID/アイソフォーム正規化。
- レート制限: QPS=2/host程度、HTTP429/5xxは指数バックオフ（最大3回）。

## 10. データモデル（エクスポート）
- nodes.csv: `node_id, source, symbol, degree, betweenness, eigenvector`。
- ppi_edges.csv: `source_id, target_id, score, evidence_types`。
- pathways.json: `{pathway_id, source, name, url, matched_genes[], p, q}`。

## 11. エラー方針
- 無効ID: 受理せず一覧表示（有効件数のみ続行）。
- 非Human: 入力から除外（一覧表示）。
- レート/タイムアウト: リトライ→キャッシュ→再試行案内。UIの注意文は簡潔（禁則/出典注意は含めない）。
- 大規模: 自動サブグラフ＋警告。

## 12. セキュリティ/ライセンス
- KEGG結果は外部リンク参照に限定（再配布不可）。
- 出典明記（STRING/Reactome/UniProt）。
- 入力履歴の保存はオプション（既定OFF）。

## 13. 運用ノート（プロキシ/社内環境）
- HTTP(S)_PROXY/NO_PROXY環境変数、`httpx`の`proxies`設定をサポート。
- 設定例: `.env`で`HTTP_PROXY`/`HTTPS_PROXY`を指定、アプリ起動時に読込。
- 社内CAが必要な場合は`REQUESTS_CA_BUNDLE`相当の証明書パスを指定可能にする。

## 14. テスト/計測
- 単体: APIクライアント、正規化、パース、富化、中心性。
- 結合: UniProt→KEGG/Reactome/STRING疎通（モック併用）。
- UI/E2E: UC1～UC3の代表操作、ダウンロード内容のスナップショット一致。
- 性能: 代表IDセットでP50/P95測定し閾値回帰テスト。
- 代表ID: P31946, P63104, P27348, P61981, Q04917, P62258。

## 15. 受け入れ基準
- AC1: UC1で単一IDを入力し、PPIと少なくとも1件以上のKEGG/Reactome経路が表示される。
- AC2: `required_score`を700→900に上げるとエッジ数が減少する。
- AC3: `nodes.csv`/`ppi_edges.csv`/`pathways.json`/PNG/SVGがダウンロードできる。
- AC4: 同一ID再実行でキャッシュヒットが発生しAPI呼数が増えない。
- AC5: 失敗時にユーザフレンドリなメッセージと再試行導線が表示される（禁則/出典注意はUI文言に含めない）。

## 16. リリース計画
- M1（1週）: UC1の土台（ID正規化/KEGG/Reactome取得/キャッシュ/UI基礎）。
- M2（1週）: STRING取得/可視化/中心性/サブグラフ抽出。
- M3（1週）: 富化/共通ノード/エクスポート（PNG/SVG/CSV/JSON）。
- M4（1週）: 例外処理/ログ/プロキシ設定/UI磨き/最終テストと性能測定。

