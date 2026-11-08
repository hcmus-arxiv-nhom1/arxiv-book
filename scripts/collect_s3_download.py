"""Reconcile the saved bulk download evidence into reproducible Book inputs."""
import csv
import hashlib
import json
from pathlib import Path


def collect(source, output):
    names = ("plan.json", "summary.json", "events.jsonl", "bundles.csv")
    hashes = {name: hashlib.sha256((source / name).read_bytes()).hexdigest() for name in names}
    plan = json.loads((source / names[0]).read_text(encoding="utf-8"))
    summary = json.loads((source / names[1]).read_text(encoding="utf-8"))
    events = [json.loads(line) for line in (source / names[2]).read_text(encoding="utf-8").splitlines()]
    with (source / names[3]).open(encoding="utf-8-sig", newline="") as stream:
        csv_rows = list(csv.DictReader(stream))
    rows = summary["results"]
    expected = [item["key"] for item in plan["bundles"]]
    keys = [item["key"] for item in rows]
    if (not summary["complete"] or plan["scope"] != "full" or len(plan["ids"]) != 20000
            or len(set(plan["ids"])) != 20000 or len(keys) != 144 or len(set(keys)) != 144
            or set(keys) != set(expected) or events != rows or len(csv_rows) != len(rows)
            or any(not plan["id_candidates"].get(pid) for pid in plan["ids"])):
        raise ValueError("Incomplete or inconsistent S3 download evidence")
    fields = ["key", "status", "bytes", "manifest_bytes", "download_s", "verify_local_s",
              "copy_to_drive_s", "peak_process_tree_rss_bytes", "peak_local_stage_bytes"]
    for row, record in zip(rows, csv_rows, strict=True):
        if row["status"] != "downloaded" or row.get("resource_errors"):
            raise ValueError("Unexpected bundle status or resource sampling error")
        for field in fields:
            if field in ("key", "status"):
                matches = record[field] == row[field]
            else:
                matches = float(record[field]) == float(row[field])
            if not matches:
                raise ValueError(f"CSV mismatch: {row['key']} {field}")
    result = dict(run_id=plan["run_id"], revision=plan["revision"], papers=len(plan["ids"]),
                  bundles=len(rows), downloaded=len(rows), reused=0, failed=0,
                  actual_bytes=sum(r["bytes"] for r in rows),
                  manifest_bytes=sum(r["manifest_bytes"] for r in rows),
                  session_wall_s=summary["session_wall_s"], selection_s=summary["selection_s"],
                  download_s=sum(r["download_s"] for r in rows),
                  verify_s=sum(r["verify_local_s"] for r in rows),
                  copy_s=sum(r["copy_to_drive_s"] for r in rows),
                  peak_rss_bytes=max(r["peak_process_tree_rss_bytes"] for r in rows),
                  peak_stage_bytes=max(r["peak_local_stage_bytes"] for r in rows),
                  size_mismatches=sum(r["bytes"] != r["manifest_bytes"] for r in rows))
    output.mkdir(parents=True, exist_ok=True)
    (output / "s3_download_summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (output / "s3_download_provenance.json").write_text(json.dumps({"inputs_sha256": hashes, "snapshot_sha256": plan["snapshot_sha256"], "manifest_sha256": plan["manifest_sha256"], "created_utc": plan["created_utc"], "revision": plan["revision"]}, indent=2) + "\n", encoding="utf-8")
    with (output / "s3_download_bundles.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    collect(Path("../final_evidence/s3-download-benchmark/bulk-plan-01"), Path("data/m1/final"))
