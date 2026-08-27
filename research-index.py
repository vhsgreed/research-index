#!/usr/bin/env python3
"""research-index.py — build/maintain the searchable research corpus (sqlite FTS5).

Goalpost (roadmap Q3'26): "corpus searchable". Indexes:
  - research/frontier-YYYY-MM-DD.md
  - research/geopolitics-YYYY-MM-DD.md
  - research/trends/*.md
  - research/agent2-archive/campaign-*/synthesis.md

Idempotent: only re-indexes files newer than the stored mtime. DB at
~/.local/share/research/research.db. Query via research-query.py.
"""
import hashlib, os, re, sqlite3, sys, time

DB = os.environ.get("RESEARCH_DB", os.path.expanduser("~/.local/share/research/research.db"))
WS = os.environ.get("RESEARCH_DIR", os.path.expanduser("~/research"))
AGENT2 = os.environ.get("AGENT2_RESEARCH_DIR", os.path.join(WS, "agent2-archive"))
GLOBS = [
    (os.path.join(WS, "research", "frontier-*.md"), "frontier"),
    (os.path.join(WS, "research", "geopolitics-*.md"), "geopolitics"),
    (os.path.join(WS, "research", "trends", "*.md"), "trends"),
    (os.path.join(AGENT2, "campaign-*", "synthesis.md"), "campaign"),
]
HASH_TABLE = "file_hashes"  # path -> sha1 of content (cheaper than mtime drift)


def files():
    import glob
    out = []
    for pat, kind in GLOBS:
        for p in sorted(glob.glob(pat)):
            out.append((p, kind))
    return out


def main():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    con = sqlite3.connect(DB)
    con.execute("CREATE VIRTUAL TABLE IF NOT EXISTS research USING fts5(kind, date, path, title, body)")
    con.execute(f"CREATE TABLE IF NOT EXISTS {HASH_TABLE} (path TEXT PRIMARY KEY, sha TEXT)")
    added = updated = skipped = 0
    for path, kind in files():
        with open(path, encoding="utf-8", errors="replace") as f:
            content = f.read()
        sha = hashlib.sha1(content.encode()).hexdigest()
        row = con.execute(f"SELECT sha FROM {HASH_TABLE} WHERE path=?", (path,)).fetchone()
        if row and row[0] == sha:
            skipped += 1
            continue
        m = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(path))
        date = m.group(1) if m else ""
        title = os.path.basename(path)
        body = content[:400000]  # cap per-file body
        con.execute("DELETE FROM research WHERE path=?", (path,))
        con.execute("INSERT INTO research(kind, date, path, title, body) VALUES (?,?,?,?,?)",
                    (kind, date, path, title, body))
        con.execute(f"INSERT OR REPLACE INTO {HASH_TABLE}(path, sha) VALUES (?,?)", (path, sha))
        if row:
            updated += 1
        else:
            added += 1
    con.commit()
    n = con.execute("SELECT count(*) FROM research").fetchone()[0]
    print(f"indexed: {n} docs | added {added}, updated {updated}, skipped {skipped} | {DB}")


if __name__ == "__main__":
    main()
