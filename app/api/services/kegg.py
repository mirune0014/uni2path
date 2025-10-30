from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

try:
    import backoff  # type: ignore
except Exception:  # pragma: no cover
    class _BackoffCompat:
        @staticmethod
        def on_exception(*_args, **_kwargs):
            def _deco(func):
                return func
            return _deco

    backoff = _BackoffCompat()
    backoff.expo = None  # type: ignore
import httpx


KEGG_BASE = "http://rest.kegg.jp"


def _client(timeout: float = 20.0) -> httpx.Client:
    return httpx.Client(timeout=timeout, headers={"User-Agent": "uni2path/1.0"}, trust_env=True)


@backoff.on_exception(backoff.expo, (httpx.HTTPError,), max_tries=3)
def _conv_uniprot_to_kegg_gene(client: httpx.Client, accession: str) -> List[str]:
    url = f"{KEGG_BASE}/conv/hsa/uniprot:{accession}"
    r = client.get(url)
    r.raise_for_status()
    genes: List[str] = []
    for line in r.text.strip().splitlines():
        parts = line.split("\t")
        if len(parts) == 2 and parts[1].startswith("hsa:"):
            genes.append(parts[1])
    return genes


@backoff.on_exception(backoff.expo, (httpx.HTTPError,), max_tries=3)
def _link_gene_to_pathway(client: httpx.Client, gene_id: str) -> List[str]:
    url = f"{KEGG_BASE}/link/pathway/{gene_id}"
    r = client.get(url)
    r.raise_for_status()
    pws: List[str] = []
    for line in r.text.strip().splitlines():
        parts = line.split("\t")
        if len(parts) == 2 and parts[1].startswith("path:hsa"):
            pws.append(parts[1].replace("path:", ""))
    return pws


@backoff.on_exception(backoff.expo, (httpx.HTTPError,), max_tries=3)
def _get_pathway_name(client: httpx.Client, pathway_id: str) -> str | None:
    url = f"{KEGG_BASE}/list/{pathway_id}"
    r = client.get(url)
    r.raise_for_status()
    line = r.text.strip().splitlines()[0] if r.text.strip() else ""
    if not line:
        return None
    parts = line.split("\t")
    return parts[1] if len(parts) > 1 else None


def kegg_pathways_for_uniprot(ids: Iterable[str]) -> List[Dict[str, str]]:
    result: Dict[str, Dict[str, str]] = {}
    with _client() as client:
        for acc in ids:
            for gene in _conv_uniprot_to_kegg_gene(client, acc):
                for pw in _link_gene_to_pathway(client, gene):
                    if pw not in result:
                        name = _get_pathway_name(client, pw)
                        result[pw] = {
                            "pathway_id": pw,
                            "source": "kegg",
                            "name": name or pw,
                            "url": f"https://www.kegg.jp/pathway/{pw}",
                        }
    return list(result.values())
