from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable, List, Tuple

try:
    import backoff  # type: ignore
except Exception:  # pragma: no cover - fallback when backoff is unavailable
    class _BackoffCompat:
        @staticmethod
        def on_exception(*_args, **_kwargs):
            def _deco(func):
                return func
            return _deco

    backoff = _BackoffCompat()
import httpx


UNIPROT_BASE = "https://rest.uniprot.org"


@dataclass
class NormalizedID:
    input_id: str
    accession: str
    organism_id: int | None


def _client(timeout: float = 20.0) -> httpx.Client:
    return httpx.Client(timeout=timeout, headers={"User-Agent": "uni2path/1.0"}, trust_env=True)


def _chunk(ids: List[str], size: int = 100) -> Iterable[List[str]]:
    for i in range(0, len(ids), size):
        yield ids[i : i + size]


@backoff.on_exception(backoff.expo, (httpx.HTTPError,), max_tries=3)
def _fetch_accessions(client: httpx.Client, ids: List[str]) -> List[NormalizedID]:
    result: List[NormalizedID] = []
    for part in _chunk(ids, 50):
        q = " OR ".join([f"(accession:{i})" for i in part])
        url = f"{UNIPROT_BASE}/uniprotkb/search?query={httpx.QueryParams({'query': q})['query']}&fields=accession,organism_id&format=json"
        r = client.get(url)
        r.raise_for_status()
        data = r.json()
        for e in data.get("results", []):
            acc = e.get("primaryAccession")
            org = None
            try:
                org = int(e.get("organism","{}").get("taxonId"))
            except Exception:
                org = None
            if acc:
                result.append(NormalizedID(input_id=acc, accession=acc, organism_id=org))
    return result


def normalize_ids(ids: Iterable[str], normalize_isoforms: bool = True) -> Tuple[List[NormalizedID], List[str]]:
    cleaned = []
    for s in ids:
        x = s.strip()
        if not x:
            continue
        if normalize_isoforms and "-" in x:
            x = x.split("-")[0]
        cleaned.append(x)
    cleaned = list(dict.fromkeys(cleaned))
    if not cleaned:
        return [], []
    invalid: List[str] = []
    with _client() as client:
        normalized = _fetch_accessions(client, cleaned)
    found_set = {n.accession for n in normalized}
    for x in cleaned:
        if x not in found_set:
            invalid.append(x)
    return normalized, invalid


def sha1_of_ids(ids: Iterable[str]) -> str:
    joined = ",".join(sorted([i.strip() for i in ids if i.strip()]))
    return hashlib.sha1(joined.encode("utf-8")).hexdigest()
