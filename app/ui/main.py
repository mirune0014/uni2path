import json
import os
import streamlit as st
import httpx


API_BASE = os.getenv("UNI2PATH_API", "http://localhost:8000")


def call_pathways(ids: list[str], normalize_isoforms: bool = True) -> dict:
    with httpx.Client(timeout=30.0) as client:
        r = client.post(f"{API_BASE}/v1/pathways", json={"ids": ids, "normalize_isoforms": normalize_isoforms})
        r.raise_for_status()
        return r.json()


st.set_page_config(page_title="uni2path", layout="wide")
st.title("uni2path: UniProt→Pathways (KEGG/Reactome)")

default_ids = "\n".join(["P31946", "P63104"])

with st.sidebar:
    st.header("入力")
    ids_text = st.text_area("UniProt ID（改行/カンマ/タブ区切り, 最大100）", value=default_ids, height=160)
    normalize = st.checkbox("アイソフォームを正規化する (-N を除去)", value=True)
    run = st.button("実行")

if run:
    raw = [x.strip() for x in ids_text.replace(",", "\n").replace("\t", "\n").splitlines()]
    ids = [x for x in raw if x]
    if not ids:
        st.warning("IDを入力してください。")
        st.stop()

    with st.spinner("取得中..."):
        try:
            data = call_pathways(ids, normalize)
        except httpx.HTTPError as e:
            st.error(f"API呼び出しに失敗: {e}")
            st.stop()

    st.subheader("結果")
    st.write(f"有効ID: {len(data.get('valid_ids', []))} / 無効ID: {len(data.get('invalid_ids', []))}")
    if data.get("invalid_ids"):
        st.info("無効ID: " + ", ".join(data["invalid_ids"]))

    pws = data.get("pathways", [])
    if pws:
        st.dataframe(pws, use_container_width=True)
        st.download_button("pathways.json ダウンロード", data=json.dumps(pws, ensure_ascii=False, indent=2), file_name="pathways.json")
    else:
        st.warning("経路が見つかりませんでした。")
