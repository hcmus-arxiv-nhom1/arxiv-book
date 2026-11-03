"""Extract historical smoke metrics; raw benchmark bundles remain outside the Book."""
import argparse
import csv
import hashlib
import json
from pathlib import Path


def collect(root, destination):
    rows, sources = [], []
    experiments = [
        ("bench_results_old", "API/OAI + Drive (200 IDs)"),
        ("bench_results_new", "Snapshot + Drive (100 IDs)"),
        ("bench_results_newhf", "Snapshot + HF (100 IDs)"),
        ("bench_results_1000", "Snapshot + Drive (incomplete 1000-ID run)"),
        ("bench_results_500999_new", "Snapshot + Drive (500 IDs, offsets 500-999)"),
        ("bench_results_hybrid_dang1000", "Hybrid + Drive (1000 IDs, offsets 0-999)"),
        ("bench_results_10001999", "Hybrid + Drive (1000 IDs, offsets 1000-1999)"),
    ]

    def read(relative):
        path = root / relative
        raw = path.read_bytes()
        sources.append(dict(path=relative, sha256=hashlib.sha256(raw).hexdigest()))
        return raw.decode("utf-8-sig")

    for directory, label in experiments:
        manifest = json.loads(read(f"{directory}/work/manifest.json"))
        coverage = json.loads(read(f"{directory}/work/coverage.json"))
        metrics = {r["metric"]: r["value"] for r in csv.DictReader(
            read(f"{directory}/book_csv/benchmark_summary.csv").splitlines()
        )}
        legacy = directory == "bench_results_old"
        exact = coverage.get("timing_complete", False) and coverage.get("measurement_complete", False)
        wall_key = "wall_time_e2e" if exact or legacy else "observed_wall_lower_bound"
        scope = "legacy chunk wall" if legacy else ("session wall" if exact else "observed session; timing audit incomplete")
        cfg = manifest["config"]
        rows.append(dict(
            experiment=label, evidence=directory, run_id=cfg["run_id"],
            revision=manifest["code_revision"], offset=cfg["offset"],
            required=coverage["required_ids"], complete=coverage["papers_source_complete"],
            coverage_complete=coverage["complete"], timing_complete=coverage.get("timing_complete", False),
            wall_s=metrics[wall_key], scope=scope,
            discovery_s=metrics["discovery_time"], retry_backoff_s=metrics.get("retry_backoff_wait", ""),
            s3_inferred=coverage.get("s3_inferred_versions", 0),
        ))
    destination.mkdir(parents=True, exist_ok=True)
    with (destination / "attempts.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (destination / "provenance.json").write_text(json.dumps(
        dict(scope="Historical smoke evidence, not final benchmark or controlled A/B tests",
             inputs=sources), indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path(__file__).parents[1] / "data/m1/effort")
    args = parser.parse_args()
    collect(args.evidence_root, args.out)
