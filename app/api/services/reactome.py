from __future__ import annotations

from typing import Dict, Iterable, List

import backoff
import httpx


REACTOME_BASE = "https://reactome.org/ContentService"


def _client(timeout: float = 20.0) -> httpx.Client:
    return httpx.Client(timeout=timeout, headers={"User-Agent": "uni2path/1.0"}, trust_env=True)


@backoff.on_exception(backoff.expo, (httpx.HTTPError,), max_tries=3)
def _fetch_pathways_for_uniprot(client: httpx.Client, accession: str) -> List[Dict[str, str]]:
    url = f"{REACTOME_BASE}/data/mapping/UniProt/{accession}/pathways?species=Homo%20sapiens"
    r = client.get(url)
    r.raise_for_status()
    items: List[Dict[str, str]] = []
    for x in r.json():
        items.append(
            {
                "pathway_id": str(x.get("stId") or x.get("dbId")),
                "source": "reactome",
                "name": x.get("displayName") or str(x.get("name") or ""),
                "url": f"https://reactome.org/PathwayBrowser/#/{x.get('stId')}",
            }
        )
    return items


def reactome_pathways_for_uniprot(ids: Iterable[str]) -> List[Dict[str, str]]:
    results: Dict[str, Dict[str, str]] = {}
    with _client() as client:
        for acc in ids:
            for row in _fetch_pathways_for_uniprot(client, acc):
                pid = row["pathway_id"]
                if pid not in results:
                    results[pid] = row
    return list(results.values())
