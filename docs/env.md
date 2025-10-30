# .env 設定ガイド（uni2path）

このドキュメントは `.env.example` に含まれる環境変数の意味と、いつ・どう設定するかの目安をまとめたものです。詳細は各自の環境に合わせて調整してください（キーワードと用途の手掛かりを残しています）。

## まずはクイックスタート
- `.env.example` をコピーして `.env` を作成します。
  - PowerShell: `Copy-Item .env.example .env`
- 原則、既存のOS環境変数が優先され、`.env` は未設定のものだけを補います。
- FastAPI と Streamlit は起動時に `.env` を自動読込します（`app/utils/config.py`）。

## 主要項目
- `UNI2PATH_API`
  - 役割: Streamlit UI から叩く FastAPI のベースURL。
  - 既定: `http://localhost:8000`
  - 変更タイミング: API を別ポート/別ホストで起動する場合。
  - 例: `UNI2PATH_API=http://127.0.0.1:9000`

- `LOG_LEVEL`
  - 役割: JSONロガーのレベル。`DEBUG|INFO|WARN|ERROR`。
  - 既定: `INFO`
  - 変更タイミング: 開発時の詳細ログ（`DEBUG`）や静かな運用（`WARN`以上）。

- `UNI2PATH_DATA`
  - 役割: ローカルデータの保存先（SQLiteキャッシュやスナップショット）。
  - 既定: `.data`（カレント直下）
  - 変更タイミング: 書き込み可能な専用ディレクトリを使いたい場合。
  - 例: `UNI2PATH_DATA=C:\\data\\uni2path`（Windows）

## プロキシ/証明書（社内NW向け）
- `HTTP_PROXY`, `HTTPS_PROXY`
  - 役割: 外部API（UniProt/KEGG/Reactome/STRING）へ接続する際のプロキシ設定。
  - 値例: `http://proxy.example.com:8080`

- `NO_PROXY`
  - 役割: プロキシを経由しないホストの指定。
  - 例: `NO_PROXY=localhost,127.0.0.1`

- `REQUESTS_CA_BUNDLE`
  - 役割: 内部CAを使う環境での証明書パス。`httpx/requests` が参照。
  - 例: `REQUESTS_CA_BUNDLE=C:\\path\\to\\corp-ca.pem`

## 優先順位と配置
- 優先順位: OS環境変数 > `.env` > コード内デフォルト。
- 配置: リポジトリ直下の `.env` を推奨（カレントから自動読込）。
- 秘密情報: このプロジェクトではAPIキーは不要ですが、`.env` は原則コミットしません。

## トラブルシュートのヒント
- 接続エラー（タイムアウト/403/407）
  - プロキシ設定（`HTTP(S)_PROXY`, `NO_PROXY`）を見直す。社内認証が必要な場合は認証付URLが求められるケースあり。
- 証明書エラー（`SSL: CERTIFICATE_VERIFY_FAILED`）
  - `REQUESTS_CA_BUNDLE` に社内CAを指定。ファイルパスのエスケープに注意（Windows）。
- ループバックへの接続不良（UI→API）
  - `UNI2PATH_API` を `http://127.0.0.1:<port>` に変更し、`NO_PROXY` に `127.0.0.1` を含める。

## 参考
- 設定ローダー: `app/utils/config.py`（`.env` を読み込み、既存環境変数を上書きしない方針）
- 使用箇所: `app/api/main.py`, `app/ui/main.py`（起動時に `load_env()` 実行）

