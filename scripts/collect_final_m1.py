"""Reconcile local M1 evidence and produce small, auditable Book inputs.

Run from the Book root: python scripts/collect_final_m1.py --workspace ..
Requires the five local evidence folders and filtered assigned snapshot; raw corpus is
not read. Fails closed on coverage, version, telemetry or checksum mismatches.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path

RUNS = {
    "only-v1-all": ("only-v1-drive-evidence", "only-v1-all-recovered-book-csv/book_csv"),
    "multi-dang": ("multi-dang-0000-4999-drive-evidence", "multi-dang-0000-4999-recovered-book-csv"),
    "multi-hieu": ("multi-hieu-0000-4999-drive-evidence", "multi-hieu-0000-4999-drive-evidence/book_csv"),
    "multi-thien": ("multi-thien-0000-4999-drive-evidence", "multi-thien-0000-4999-drive-evidence/book_csv"),
    "multi-tien": ("multi-tien-0000-4999-drive-evidence", "multi-tien-0000-4999-drive-evidence/book_csv"),
}
TERMINAL = {"ok", "no_tex", "unavailable"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def reference_summary(run, rows):
    """Keep paper-level status and citation-level denominators distinct."""
    counts = Counter(row["ref_status"] for row in rows)
    total = sum(int(row["n_refs_total"]) for row in rows)
    resolved = sum(int(row["n_refs_meta_ok"]) for row in rows)
    complete = sum(int(row["n_refs_meta_complete"]) for row in rows)
    if min(total, resolved, complete) < 0 or not complete <= resolved <= total:
        raise ValueError(f"{run}: inconsistent reference counts")
    return ([dict(run=run, status=status, papers=count) for status, count in sorted(counts.items())],
            dict(run=run, references=total, with_s2_id=resolved, complete_metadata=complete,
                 s2_id_pct=100 * resolved / total if total else None,
                 complete_metadata_pct=100 * complete / total if total else None))


def timeline_rows(run, path):
    """Validate aggregated minute observations, preserving missingness as an error."""
    rows = read_csv(path)
    if not rows:
        raise ValueError(f"{run}: empty timeline {path}")
    result, seen = [], set()
    for row in rows:
        try:
            minute = row["minute_utc"]
            datetime.strptime(minute, "%Y-%m-%d %H:%M")
            n429, n5xx = int(row["n_429"]), int(row["n_5xx"])
            backoff = float(row["backoff_s"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"{run}: invalid timeline row") from exc
        if minute in seen or not math.isfinite(backoff) or min(n429, n5xx, backoff) < 0:
            raise ValueError(f"{run}: duplicate minute or negative observation")
        seen.add(minute)
        result.append(dict(run=run, minute_utc=minute, n_429=n429, n_5xx=n5xx, backoff_s=backoff))
    return result


def session_measurements(root, run):
    parents = [root / "measurements", root / "work" / "measurements"]
    sessions = [x for parent in parents if parent.is_dir() for x in parent.iterdir() if x.is_dir()]
    if len(sessions) != 1:
        raise ValueError(f"{run}: expected one session; found {len(sessions)}")
    folder = sessions[0]
    start = read_json(folder / "start.json")
    summary = read_json(folder / "summary.json")
    parts = sorted(folder.glob("samples-*.json"))
    if not summary.get("complete") or len(parts) != summary["segments"]:
        raise ValueError(f"{run}: incomplete sample segments")
    all_samples = []
    for sequence, path in enumerate(parts):
        part = read_json(path)
        checksum = hashlib.sha256(json.dumps(part["rows"], sort_keys=True).encode()).hexdigest()
        if path.name != f"samples-{sequence:06d}.json" or part["sequence"] != sequence or checksum != part["sha256"]:
            raise ValueError(f"{run}: invalid segment {path.name}")
        all_samples.extend(part["rows"])
    if not all_samples or all_samples[-1]["t_sec"] != summary["wall_s"] or any(
        b["t_sec"] < a["t_sec"] for a, b in zip(all_samples, all_samples[1:])
    ):
        raise ValueError(f"{run}: invalid sample timeline")
    span = all_samples[-1]["t_sec"] - all_samples[0]["t_sec"]
    rss_mean = sum(a["rss_bytes"] * (b["t_sec"] - a["t_sec"])
                   for a, b in zip(all_samples, all_samples[1:])) / span if span else 0
    if (max(x["rss_bytes"] for x in all_samples) != summary["rss_max_bytes"]
            or max(x["disk_bytes"] for x in all_samples) != summary["disk_max_bytes"]
            or abs(rss_mean - summary["rss_mean_bytes"]) > 1):
        raise ValueError(f"{run}: summary disagrees with sampled resource values")
    # Downsample charts to one observation per minute; peak/mean use original summary.
    chart = []
    minute = -1
    for row in all_samples:
        current = int(row["t_sec"] // 60)
        if current != minute:
            chart.append(dict(run=run, t_sec=row["t_sec"], rss_mb=row["rss_bytes"] / 1e6,
                              disk_mb=row["disk_bytes"] / 1e6))
            minute = current
    return start, summary, chart, len(all_samples), folder


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    snapshot_path = workspace / "snapshot-split/arxiv-assigned-20000.jsonl"
    snapshot = {}
    with snapshot_path.open(encoding="utf-8") as stream:
        for line in stream:
            record = json.loads(line)
            if record["id"] in snapshot:
                raise ValueError("duplicate snapshot ID")
            snapshot[record["id"]] = len(record["versions"])
    if len(snapshot) != 20000 or sum(snapshot.values()) != 26491:
        raise ValueError("unexpected snapshot scope")
    evidence = workspace / "final_evidence"
    papers, metrics, charts, attempts, statuses, provenance = [], [], [], [], Counter(), {}
    run_statuses, reference_states, reference_metadata, timeline = [], [], [], []
    seen = Counter()
    for run, (folder, csv_folder) in RUNS.items():
        root = evidence / folder
        work = root / "work"
        manifest_path = work / "manifest.json"
        manifest = read_json(manifest_path)
        ids = manifest["required_ids"]
        if len(ids) != len(set(ids)):
            raise ValueError(f"{run}: duplicate manifest IDs")
        seen.update(ids)
        csv_path = evidence / csv_folder / "papers_stats.csv"
        rows = read_csv(csv_path)
        if len(rows) != len(ids) or {r["arxiv_id"] for r in rows} != set(ids):
            raise ValueError(f"{run}: paper CSV does not match manifest")
        journal = {}
        journal_path = work / "versions.jsonl"
        with journal_path.open(encoding="utf-8") as stream:
            for line in stream:
                rec = json.loads(line)
                journal[(rec["arxiv_id"], int(rec["version"]))] = rec
        this_run_statuses = Counter()
        for row in rows:
            pid = row["arxiv_id"]
            n = snapshot[pid]
            if int(row["n_versions"]) != n:
                raise ValueError(f"{run}: snapshot mismatch for {pid}")
            records = [journal.get((pid, i), {}) for i in range(1, n + 1)]
            observed = [r.get("status") for r in records]
            if any(s not in TERMINAL for s in observed) or int(row["n_versions_ok"]) != len(observed):
                raise ValueError(f"{run}: version state mismatch for {pid}")
            statuses.update(observed)
            this_run_statuses.update(observed)
            row["run"] = run
            papers.append(row)
        run_statuses.extend(dict(run=run, status=state, versions=this_run_statuses[state])
                            for state in sorted(TERMINAL))
        states, metadata = reference_summary(run, rows)
        reference_states.extend(states)
        reference_metadata.append(metadata)
        start, summary, chart, count, session_dir = session_measurements(root, run)
        charts.extend(chart)
        timing = read_json(work / "timing_audit.json")
        environment_path = work / "sessions" / (start["session_id"] + ".json")
        environment = read_json(environment_path)
        if environment["code_revision"] != manifest["code_revision"]:
            raise ValueError(f"{run}: environment revision differs from manifest")
        bench_path = evidence / csv_folder / "benchmark_summary.csv"
        diagnostics = {r["metric"]: r for r in read_csv(bench_path)}
        timeline_path = evidence / csv_folder / "request_timeline.csv"
        timeline.extend(timeline_rows(run, timeline_path))
        attempt_path = evidence / csv_folder / "paper_attempt_timings.csv"
        run_attempts = read_csv(attempt_path)
        wanted = set(ids)
        if any(r["arxiv_id"] not in wanted for r in run_attempts):
            raise ValueError(f"{run}: attempt timing has unexpected ID")
        attempts.extend(dict(row, run=run) for row in run_attempts)
        metrics.append(dict(run=run, papers=len(ids), versions=sum(snapshot[x] for x in ids),
                            revision=manifest["code_revision"], cpu_count=environment["cpu_count"],
                            machine_ram_mb=environment["ram_bytes"] / 1e6, start_utc=start["started_at"],
                            end_utc=summary["ended_at"], sampler_wall_s=summary["wall_s"],
                            discovery_s=diagnostics["discovery_time"]["value"],
                            retry_backoff_s=diagnostics["retry_backoff_wait"]["value"],
                            peak_rss_mb=summary["rss_max_bytes"] / 1e6,
                            mean_rss_mb=summary["rss_mean_bytes"] / 1e6,
                            peak_disk_mb=summary["disk_max_bytes"] / 1e6,
                            output_mb=summary["output_bytes"] / 1e6,
                            samples=count, original_timing_audit=timing.get("timing_complete"),
                            note="validated session segments; reconcile original audit" if not timing.get("timing_complete") else "validated session segments"))
        provenance[run] = dict(manifest_sha256=digest(manifest_path), papers_csv_sha256=digest(csv_path),
                               benchmark_csv_sha256=digest(bench_path),
                               paper_timing_csv_sha256=digest(attempt_path),
                               request_timeline_sha256=digest(timeline_path),
                               environment_sha256=digest(environment_path),
                               versions_sha256=digest(journal_path), start_sha256=digest(session_dir / "start.json"),
                               summary_sha256=digest(session_dir / "summary.json"), sample_segments=summary["segments"],
                               code_revision=manifest["code_revision"], snapshot_sha256=manifest["snapshot_sha256"])
    if set(seen) != set(snapshot) or any(v != 1 for v in seen.values()):
        raise ValueError("five-run scope has missing, duplicate or extra IDs")
    out = Path("data/m1/final")
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "papers_stats.csv", papers)
    write_csv(out / "run_metrics.csv", metrics)
    write_csv(out / "resource_samples_1min.csv", charts)
    write_csv(out / "paper_attempt_timings.csv", attempts)
    write_csv(out / "version_status.csv", [dict(status=k, versions=v) for k, v in sorted(statuses.items())])
    write_csv(out / "version_status_by_run.csv", run_statuses)
    write_csv(out / "reference_status_by_run.csv", reference_states)
    write_csv(out / "reference_metadata_by_run.csv", reference_metadata)
    write_csv(out / "request_timeline_by_run.csv", timeline)
    (out / "provenance.json").write_text(json.dumps(dict(snapshot_sha256=digest(snapshot_path), runs=provenance), indent=2) + "\n", encoding="utf-8")
    starts = [datetime.fromisoformat(r["start_utc"]) for r in metrics]
    ends = [datetime.fromisoformat(r["end_utc"]) for r in metrics]
    print(f"{len(papers)} papers; {sum(statuses.values())} terminal version records; statuses={dict(statuses)}")
    print(f"sampler interval envelope={(max(ends)-min(starts)).total_seconds():.2f} s (includes gaps)")
    print(f"output: {out}")


if __name__ == "__main__":
    main()
