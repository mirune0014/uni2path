import hashlib
import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Optional


class SqliteCache:
    def __init__(self, db_path: str | Path | None = None) -> None:
        root = Path(os.getenv("UNI2PATH_DATA", "."))
        path = Path(db_path) if db_path else root / "uni2path_cache.sqlite3"
        path.parent.mkdir(parents=True, exist_ok=True)
        self._path = str(path)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self._path) as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    k TEXT PRIMARY KEY,
                    v TEXT NOT NULL,
                    expire_at INTEGER NOT NULL
                )
                """
            )
            con.execute("CREATE INDEX IF NOT EXISTS idx_expire ON cache(expire_at)")

    @staticmethod
    def make_key(payload: Any) -> str:
        dump = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        now = int(time.time())
        with sqlite3.connect(self._path) as con:
            cur = con.execute("SELECT v, expire_at FROM cache WHERE k=?", (key,))
            row = cur.fetchone()
            if not row:
                return None
            v, expire_at = row
            if expire_at < now:
                con.execute("DELETE FROM cache WHERE k=?", (key,))
                return None
            return json.loads(v)

    def set(self, key: str, value: Any, ttl_sec: int = 60 * 60 * 24) -> None:
        expire_at = int(time.time()) + int(ttl_sec)
        data = json.dumps(value, ensure_ascii=False)
        with sqlite3.connect(self._path) as con:
            con.execute(
                "REPLACE INTO cache(k, v, expire_at) VALUES(?,?,?)",
                (key, data, expire_at),
            )

    def clear(self) -> int:
        with sqlite3.connect(self._path) as con:
            cur = con.execute("DELETE FROM cache")
            return cur.rowcount

    def cleanup(self) -> int:
        now = int(time.time())
        with sqlite3.connect(self._path) as con:
            cur = con.execute("DELETE FROM cache WHERE expire_at < ?", (now,))
            return cur.rowcount
