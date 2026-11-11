# Timing audit: controlled rerun evidence

The original `work/timing_audit.json` files for **only-v1-all** and **multi-dang** both record `timing_complete: false`, `measurement_complete: false`, `paper_timing_complete: true`, no unfinished profiles, no paper timing errors and an observed wall lower bound of zero. These original files remain unchanged.

Both run manifests record CodeRepo revision `ad03e0a3dc8d96bf1404472f6752aac5e2c42857`. At that revision, `timing_audit()` calls `session_report()`, which searches `work/measurements`. In the exported evidence used for this investigation, the separately saved session files are in the run's top-level `measurements/` directory.

On 8 November 2026, a controlled rerun used that exact code revision and temporary copies of each run's `work/manifest.json`, `work/paper_events.jsonl`, `work/profile/` and top-level `measurements/`. It ran the original `timing_audit()` twice per run:

1. With measurements only at the top level, both reruns reproduced all fields listed above from the original audits.
2. After copying the same measurement files into `work/measurements` in the temporary copy, both reruns reported `timing_complete: true`, `measurement_complete: true`, `paper_timing_complete: true`, no unfinished profiles, paper timing errors or incomplete sessions. The observed sampler walls were 31,271.247885057 seconds for only-v1 and 19,511.389182279003 seconds for multi-dang.

The book's independent aggregation also validated the segment sequence, SHA-256 checksums, sample chronology and resource summaries for the supplied measurement files; see `data/m1/final/provenance.json` for the input hashes and revisions. These results show that the exported directory placement is sufficient to reproduce the difference, but they do **not** establish the actual filesystem state or exact cause when the original runtime executed its audit. The sampler starts after initial setup and input hashing and excludes earlier S3 preparation and final evidence publication. It is not a full end-to-end duration or a corpus integrity audit.
