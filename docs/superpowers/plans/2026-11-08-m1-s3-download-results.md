# Plan to add the S3 download benchmark to the M1 book

**Goal:** Report the download of 144 bundles in the Performance section, with clear provenance and measurement boundaries.

**Source:** `final_evidence/s3-download-benchmark/bulk-plan-01/{plan.json,summary.json,events.jsonl,bundles.csv}` in the workspace. M1 Performance is in `m1/03-performance.ipynb`. This download took place on 8 November 2026 after the M1 crawl sessions; it is not a measurement of the bulk preparation that preceded them.

## 1. Verify and normalize the evidence

- [ ] Reconcile summary, events, CSV and plan: 144 unique keys with `downloaded` status, scope of 20,000 IDs, total bytes, bundle count, and manifest/snapshot hashes. Report inconsistencies rather than inventing explanations.
- [ ] Export a compact per-bundle CSV and summary CSV/JSON to `data/m1/` using the existing convention. Record SHA-256 hashes of the four inputs, revision `d4a92cd0192950e7bb3a8abc60ceba9da335d255`, scope, timestamp and run name; exclude secrets and unnecessary personal paths from the book.
- [ ] Retain integer byte counts and original timings in the data; round seconds only for display. Check `resource_errors`, missing values, 144 size differences and status consistency; do not claim an MD5 check after copying to Drive.

## 2. Present the results in Performance

- [ ] Add an appropriately numbered subsection in `m1/03-performance.ipynb`, renumbering later sections if necessary. Include a captioned summary table that wraps and scrolls horizontally when needed: ID, counts of downloaded/reused/failed bundles, actual and manifest bytes, session wall, selection, download, MD5 and copy durations, throughput, peak RSS and staging disk.
- [ ] Report session wall of 1,913 seconds (~31 minutes 53 seconds): download 1,136 seconds, MD5 230 seconds, copy 507 seconds, and approximately 40 seconds remaining. Selection (~4 seconds) was measured separately before the session. Weighted download throughput is total newly downloaded bytes divided by total download seconds (~67.5 MB/s); session throughput (~40.1 MB/s) uses session wall. Do not recompute copy time or count components twice.
- [ ] Add a stacked bar chart of measured time intervals and the remainder, labeled in whole seconds, stating that selection is outside session wall. Add the per-bundle time distribution only if it helps show variation; do not sum per-bundle throughputs to calculate overall throughput.
- [ ] State that RSS samples the process tree and disk samples the local staging directory every two seconds, so peaks may be missed; disk is not Drive usage. Put captions under tables and use the existing wrapping limits.

## 3. Scope and relationship to the crawl

- [ ] Calculate an **estimated end-to-end time** combining the S3 download benchmark and the group crawl interval on the shared timeline. Add the unrounded download `session_wall_s` to the interval from the earliest crawl sampler start to the latest sampler end; do not sum overlapping crawl-session durations or add retry, checkpoint or copy time already included in measurements. Round seconds only for display.
- [ ] State that the S3 download was a benchmarked rerun; the raw download before crawling had no benchmark audit. Since the new measurement followed the crawl, the sum is an **estimate combining two measurements**, not a continuously observed wall-clock time for the original M1 run. Do not use the rerun throughput to certify the old download speed.
- [ ] Keep unmeasured intervals separate: setup/mount, `selection_s` (approximately 4 seconds, reported separately), manifest/snapshot retrieval, evidence download and other work outside the sampler. Do not call this an exhaustive actual elapsed time. If `selection_s` is added to an extended metric, show the formula and avoid double counting.
- [ ] Explain that MD5 verifies local files before copying; a size difference from the manifest alone does not prove corruption if MD5 matches. Drive FUSE copy/rename does not prove durable synchronization. Manifest boundaries are candidates, not confirmation of member contents or versions; no member index or independent readback is available.
- [ ] If updating `m1/04-discussion.md`, add only a link and a brief limitation; do not repeat benchmark details in Attempts & Effort. Preserve existing local timing-audit changes and M2 updates on main.

## 4. Verify and hand off

- [ ] Test extraction using real evidence; reconcile output totals with summary and events and check units, denominators and hashes. Confirm the table, chart and captions appear in the build; run existing tests and build/execute the book where the environment allows.
- [ ] Report validation and any build limitations; do not commit or push unless requested.
