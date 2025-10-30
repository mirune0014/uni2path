# 1. 目的

UniProt IDを入力すると、対象タンパク質の**経路（KEGG/Reactome）**と**PPIネットワーク（STRING）**を取得・可視化し、副作用仮説の探索を支援する。

# 2. 主要ユースケース

* UC1: 単一のUniProt IDから関連経路一覧とKEGG/Reactomeビューを表示。
* UC2: 複数UniProt IDから高信頼PPIネットワークを生成し、中心性でハイライト。
* UC3: 経路とPPIを横断し、共通ノードや富化経路を提示。
* UC4: 結果をPNG/CSV/JSONでエクスポート。

# 3. 入出力

* 入力: UniProt ID（1件 or 改行区切り複数）。任意で生物種（既定: human）。
* 出力:

  * 経路タブ: KEGG Pathway ID・名称・リンク、Reactome ID・名称・リンク。
  * PPIタブ: ノード・エッジ一覧、中心性指標、可視化（操作可）。
  * 解析タブ: 経路富化の概要、共通ノード、上位中心ノード。
  * エクスポート: `ppi_edges.csv`, `nodes.csv`, `pathways.json`, 可視化PNG。

# 4. データフロー

1. UniProt正規化 → 2) KEGG `conv/link` & Reactome検索 → 3) STRING PPI取得 → 4) NetworkX解析（中心性・連結成分） → 5) 可視化（pyvis/Plotly） → 6) エクスポート。

# 5. 外部API（MVP）

* KEGG REST: UniProt→KEGG gene、gene→pathway。
* STRING API: network（`species=9606`, `required_score≥700`）。
* Reactome Content Service: UniProt関連経路取得。
* UniProt ID mapping（旧ID/アイソフォームの正規化）。

# 6. 機能要件

* F1: UniProt→KEGG/Reactome経路一覧を3秒以内に表示（1–5 ID）。
* F2: STRING PPIを取得し、スライダーで`required_score`を調整。
* F3: 中心性（degree, betweenness, eigenvector）計算と上位Nのハイライト。
* F4: 経路富化（ハイパージオメトリック簡易版）を表示。
* F5: 種指定切替（human既定、他種は警告付き）。
* F6: キャッシュ（TTL 24h、キー=APIクエリ）。
* F7: ログ保存（入力ID、API呼数、遅延、失敗率）。

# 7. 非機能要件

* N1: 応答時間 P50≤2s, P95≤8s（5 ID想定）。
* N2: 同時ユーザ5まで。将来はFastAPI＋Uvicornで水平拡張。
* N3: 再現性（全APIレスポンスをローカルにJSONスナップショット保存・再読込可）。
* N4: 表示は日本語UI。英語名称はツールチップ。
* N5: 品質指標：API失敗時の自動リトライ（指数的バックオフ最大3回）。

# 8. 画面構成（Streamlit想定）

* 左ペイン: 入力（IDテキスト、species、STRINGスコア閾値、表示オプション）。
* タブ1 経路: KEGG/Reactomeテーブル＋外部ビューリンク埋め込み。
* タブ2 PPI: 交互作用グラフ（操作: 拡大、ドラッグ、クリックでメタ情報）。
* タブ3 解析: 中心性上位ノード表、富化上位経路、共通ノード一覧。
* タブ4 出力: ダウンロードボタン群。

# 9. 例外・障害対応

* X1: ID未解決→候補提示 or スキップ。ログに残す。
* X2: レート制限→待機＋キャッシュ優先。閾値超過時は「後で再試行」表示。
* X3: 種不一致→警告（自動で最頻種候補を提示）。
* X4: 大規模ネットワーク（>3000エッジ）→可視化をサブグラフ表示に自動切替。

# 10. ライセンス・表記

* KEGGは再配布制限あり。外部リンク参照に限定。結果の再配布はメタ情報のみ。
* STRINGは出典表示とcaller_identity推奨。
* Reactome/UniProtは出典明記。

# 11. 受け入れ基準（抜粋）

* AC1: Q8WZ42を入力して、PPIと少なくとも1件のKEGG/Reactome経路が表示される。
* AC2: `required_score`を700→900に上げると、エッジ数が減る。
* AC3: エクスポート3種（edges.csv, nodes.csv, pathways.json）がダウンロード可能。
* AC4: 同一ID再実行でキャッシュが命中し、API呼数が増えない。

# 12. セキュリティ・プライバシ

* 個人情報なし。入力履歴はローカル保存任意。公開版はIPレート制限のみ。

# 13. 技術スタック

* Python 3.11 / FastAPI（API） / Streamlit（UI）
* httpx + backoff / NetworkX / pyvis / pandas
* SQLiteキャッシュ（sqlite+hashキー） or Redis（任意）

# 14. マイルストーン

* M1（1週）: ID正規化＋KEGG/Reactome取得＋キャッシュ。
* M2（2週）: STRING取得＋PPI可視化＋中心性計算。
* M3（3週）: 富化解析＋共通ノード要約＋エクスポート。
* M4（4週）: 例外処理・ログ・UI磨き込み・最終テスト。

# 15. 前提・仮置き

* 種はhuman中心。非humanは軽サポート。
* 最大入力数は初期50 ID。超過時は分割。
* 研究用途の社内利用を想定。商用配布は別途検討。

# 16. 次の作業

* APIキー不要範囲での実データ疎通テスト。
* スキーマ決定（nodes/edges/pathways JSON）とキャッシュ設計。
* 中心性と富化の既定パラメータ確定。