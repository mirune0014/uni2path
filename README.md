# uni2path

UniProtのタンパク質IDを入力すると、関連する生物学的な『経路』（KEGG/Reactome）と、今後拡張予定のPPI（タンパク質間相互作用）を取得・可視化して、作用機序や副作用仮説の探索を手助けするツールです。

主な機能（M1現在）
- UniProt ID（最大100件）から、Human（9606）に対応したKEGG/Reactomeの経路一覧を取得
- 結果の表表示と`pathways.json`ダウンロード
- SQLiteによる24hキャッシュ（`.data/uni2path_cache.sqlite3`）

今後の予定（M2以降）
- STRINGからのPPI取得・可視化、中心性解析、簡易富化、エクスポート

ドキュメント
- 使い方（初心者向け）: docs/user_guide.md
- .env 設定ガイド: docs/env.md
- 要件定義（最終版）: docs/requirements.md
- 実装TODO: docs/TODO.md

クイックスタート
1) 依存をインストール（推奨: 仮想環境）
   - `python -m venv .venv`
   - `.\.venv\Scripts\Activate.ps1`
   - `pip install -r requirements.txt`
2) .env を用意（必要に応じて）
   - `Copy-Item .env.example .env`（既定のままでOK）
3) API を起動（別ターミナル）
   - `uvicorn app.api.main:app --reload --port 8000`
   - `http://localhost:8000/healthz` が `{"status":"ok"}` ならOK
4) UI を起動
   - `streamlit run app/ui/main.py`
   - ブラウザで `http://localhost:8501`

代表ID例
- `P31946, P63104, P27348, P61981, Q04917, P62258`

注意・出典
- KEGG/Reactomeの結果は外部リンク参照に限定（再配布不可）。
- 出典は各外部サイト（UniProt/KEGG/Reactome）を明記。
- KEGG RESTはHTTPSを使用し、名称は `/get/{id}` の NAME 行から取得しています。

