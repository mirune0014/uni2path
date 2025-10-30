from __future__ import annotations

import os
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.utils.config import load_env
from app.api.services.uniprot import normalize_ids, NormalizedID
from app.api.services.kegg import kegg_pathways_for_uniprot
from app.api.services.reactome import reactome_pathways_for_uniprot
from app.core.cache import SqliteCache
from app.utils.logger import get_logger


load_env()  # load .env if present (does not override existing env vars)
app = FastAPI(title="uni2path API", version="1.0.0")
logger = get_logger()
cache = SqliteCache()


class Pathway(BaseModel):
    pathway_id: str
    source: str
    name: str
    url: str


class PathwayRequest(BaseModel):
    ids: List[str] = Field(default_factory=list, max_items=100)
    normalize_isoforms: bool = True


class PathwayResponse(BaseModel):
    valid_ids: List[str]
    invalid_ids: List[str]
    pathways: List[Pathway]


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/v1/pathways", response_model=PathwayResponse)
def get_pathways(req: PathwayRequest):
    if not req.ids:
        raise HTTPException(status_code=400, detail="ids is required")

    normalized, invalid = normalize_ids(req.ids, normalize_isoforms=req.normalize_isoforms)

    human_ids = [n.accession for n in normalized if n.organism_id in (9606, None)]
    if not human_ids:
        return PathwayResponse(valid_ids=[], invalid_ids=req.ids, pathways=[])

    cache_key_payload = {"kind": "pathways", "ids": sorted(human_ids)}
    key = SqliteCache.make_key(cache_key_payload)
    cached = cache.get(key)
    if cached:
        return PathwayResponse(**cached)

    kegg = kegg_pathways_for_uniprot(human_ids)
    react = reactome_pathways_for_uniprot(human_ids)
    merged = {f"{p['source']}:{p['pathway_id']}": p for p in [*kegg, *react]}

    resp = PathwayResponse(valid_ids=human_ids, invalid_ids=invalid, pathways=[Pathway(**v) for v in merged.values()])
    cache.set(key, resp.model_dump())
    return resp


@app.post("/cache/clear")
def clear_cache():
    removed = cache.clear()
    return {"removed": removed}
