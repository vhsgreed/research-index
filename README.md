# research-index

Build and maintain a searchable research corpus in sqlite (FTS5).

Indexes your markdown research notes (daily frontier/geopolitics reports,
etc.) into a full-text-searchable database with per-file metadata.

```
python3 research-index.py        # incremental index (skips unchanged files)
python3 research-index.py --rebuild
```

## Why

If you accumulate daily research notes, plain grep stops scaling. This
gives you a single sqlite FTS5 database — fast substring + token queries
over hundreds of files, incremental updates, no external search server.

## Config (env vars)

- `RESEARCH_DIR` — root of your markdown research files (default `~/research`)
- `AGENT2_RESEARCH_DIR` — optional second corpus root (default `~/research/agent2-archive`)
- `RESEARCH_DB` — output database path (default `~/research/research.db`)

## Requirements

- Python 3.8+ (sqlite3 FTS5 built in)

## Companion

Pair with [research-query](https://github.com/vhsgreed/research-query) to
search the corpus and get LLM-answered results.
