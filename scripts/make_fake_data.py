# Drafted with the help of an AI assistant (Claude, Anthropic), cited per the course rules.
"""Sinh CSV GIẢ đúng schema trong data contract để book build được trước khi có số liệu thật.

Chạy: python scripts/make_fake_data.py  (ghi đè data/m1/*.csv)
Khi có dữ liệu thật, thay các file trong data/m1/ bằng CSV export từ arxiv-pipeline.
"""

from __future__ import annotations

import csv
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "m1"
N_PAPERS = 2000
SEED = 1


def papers(rng: random.Random) -> list[dict]:
    rows = []
    for i in range(N_PAPERS):
        n_versions = rng.choices([1, 2, 3, 4], weights=[60, 28, 9, 3])[0]
        n_ok = n_versions if rng.random() < 0.93 else rng.randint(0, n_versions - 1)
        has_source = rng.random() < 0.95
        before = int(rng.lognormvariate(14.5, 1.2)) if has_source else 0
        after = int(before * rng.uniform(0.01, 0.15)) if has_source else 0
        n_refs = max(0, int(rng.gauss(45, 20)))
        n_arxiv = int(n_refs * rng.uniform(0.2, 0.6))
        n_meta_ok = int(n_refs * rng.uniform(0.85, 1.0))
        rows.append(
            {
                "arxiv_id": f"2606.{30734 + i:05d}",
                "n_versions": n_versions,
                "n_versions_ok": n_ok,
                "has_source": int(has_source),
                "size_before_bytes": before,
                "size_after_bytes": after,
                "n_refs_total": n_refs,
                "n_refs_arxiv": n_arxiv,
                "n_refs_meta_ok": n_meta_ok,
                "process_sec": round(3.2 * n_versions + rng.uniform(0.5, 6.0), 2),
            }
        )
    return rows


def references(rng: random.Random) -> list[dict]:
    rows = []
    for source in ("semantic_scholar", "arxiv_api"):
        total = rng.randint(40_000, 60_000) if source == "semantic_scholar" else 2000
        miss = int(total * rng.uniform(0.03, 0.08))
        err_429 = rng.randint(0, 200)
        rows.append(
            {
                "source": source,
                "n_requests": total + err_429,
                "n_hit": total - miss,
                "n_miss": miss,
                "n_http_429": err_429,
                "n_http_5xx": rng.randint(0, 30),
            }
        )
    return rows


def benchmark() -> list[dict]:
    return [
        {"metric": "wall_time_e2e", "value": 5321, "unit": "s", "tool": "/usr/bin/time -v"},
        {"metric": "discovery_time", "value": 182, "unit": "s", "tool": "time.perf_counter"},
        {"metric": "ram_max", "value": 412, "unit": "MB", "tool": "psutil (RSS tổng, gồm process con)"},
        {"metric": "ram_mean", "value": 268, "unit": "MB", "tool": "psutil (RSS tổng, gồm process con)"},
        {"metric": "disk_max", "value": 1840, "unit": "MB", "tool": "du -sb"},
        {"metric": "output_size", "value": 236, "unit": "MB", "tool": "du -sb"},
    ]


def timeseries(rng: random.Random) -> list[dict]:
    rows, disk = [], 0.0
    for t in range(0, 5321, 30):
        disk = min(1840.0, disk + rng.uniform(0, 12))
        rows.append(
            {
                "t_sec": t,
                "rss_total_mb": round(240 + 60 * rng.random() + (100 if rng.random() < 0.05 else 0), 1),
                "disk_mb": round(disk, 1),
            }
        )
    return rows


def write(name: str, rows: list[dict]) -> None:
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    write("papers_stats.csv", papers(rng))
    write("references_stats.csv", references(rng))
    write("benchmark_summary.csv", benchmark())
    write("resource_timeseries.csv", timeseries(rng))


if __name__ == "__main__":
    main()
