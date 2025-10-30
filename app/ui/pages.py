from __future__ import annotations

import json
from typing import List, Dict
import streamlit as st


def render_pathways_tab(pathways: List[Dict]) -> None:
    st.subheader("経路一覧")
    st.dataframe(pathways, use_container_width=True)
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "pathways.json ダウンロード",
            data=json.dumps(pathways, ensure_ascii=False, indent=2),
            file_name="pathways.json",
            mime="application/json",
        )
    with col2:
        # テーブルはStreamlitのエクスポートAPIがないため、JSONのみ提供
        st.caption("KEGG/Reactome結果は外部リンク参照（再配布不可）")


def render_output_tab(data: Dict) -> None:
    st.subheader("出力/サマリ")
    valid = data.get("valid_ids", [])
    invalid = data.get("invalid_ids", [])
    st.write({"valid_count": len(valid), "invalid_count": len(invalid)})
    if invalid:
        with st.expander("無効IDの一覧"):
            st.code("\n".join(invalid))
