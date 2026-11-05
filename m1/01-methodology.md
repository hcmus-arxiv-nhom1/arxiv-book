# Crawling methodology

<!-- Owners: Đăng, Thiên. Updated with assistance from OpenAI Codex and Claude (Anthropic), disclosed per course rules. -->

Milestone 1 collects metadata, reference metadata and the available LaTeX source of **every version** of the assigned arXiv papers. Only `.tex` and `.bib` source files are retained; a version without usable TeX remains an explicit empty record {cite}`hcmus-statement`. Implementation lives in [CodeRepo](https://github.com/hcmus-arxiv-nhom1/CodeRepo); paths and schemas follow its `docs/data_contract.md`.

## Scope and reproducibility

| Member | Inclusive assigned range | IDs |
| --- | --- | ---: |
| Cao Tiến Thiên | `2606.30734` → `2607.03693` | 5,000 |
| Trần Minh Tiến | `2606.25734` → `2606.30733` | 5,000 |
| Trương Lê Trung Hiếu | `2606.05734` → `2606.10733` | 5,000 |
| Lý Huỳnh Minh Đăng | `2604.20535` → `2604.25534` | 5,000 |

The final benchmark must cover **all 20,000 assigned IDs**. Samples validate the pipeline but do not replace that benchmark. Thiên's range crosses a month boundary: the generator uses the configured last June sequence (`2606.32040`) and restarts July at `00001`.

Four Colab notebooks in CodeRepo (`src/notebooks/`) drive the same runner. All of them record the code revision, exact ID selection, parameters, dependency versions, hardware and sessions; a new run uses a new run ID, and a resume must match its saved configuration and implementation revision.

| Notebook | Use |
| --- | --- |
| `arxiv_nhom1_crawl_benchmark` | arXiv only, sample / partition / final mode. Mirrored in this Book, [not executed](arxiv_nhom1_crawl_benchmark.ipynb). |
| `arxiv_nhom1_s3_arxiv_benchmark` | Hybrid: arXiv bulk (S3) for papers whose snapshot lists one version, arXiv for the rest (see below). |
| `arxiv_nhom1_only_v1_benchmark` | The snapshot partition of papers with a single version; all four ranges in one run. |
| `arxiv_nhom1_multi_version_benchmark` | The snapshot partition of papers with several versions; one run per member. |

The two partitions are cut from the filtered 20,000-ID snapshot (26,491 versions as of that snapshot) by `src.crawler.split_assigned_snapshot`, which checks every ID and version and refuses to overwrite files; each partition file has a SHA-256 that the notebook verifies before use. 14,913 papers have a single version (only-v1); 5,087 papers with 11,578 versions have several (Đăng 1,466 / 3,389, Hiếu 1,343 / 3,060, Tiến 1,164 / 2,619, Thiên 1,114 / 2,510 papers / versions). Raw snapshot files are never committed.

Final mode rejects partial ranges and disabled references. A `partition` run covers part of the assigned IDs and is not a final benchmark by itself: independent runs are combined afterwards (see "Success and evidence" below).

## Discovery and source processing

1. **Generate and discover IDs.** With a metadata snapshot configured (the Kaggle arXiv dataset {cite}`kaggle-arxiv-metadata`, filtered to the 20,000 assigned IDs), a valid matching record supplies the paper metadata and all version dates, so no base-ID API or OAI call is needed. The input's SHA-256 is recorded in the run manifest and a compact `work/snapshot_index.jsonl` of the selected IDs is checkpointed instead of the multi-GB original. Historical per-version titles and authors still need versioned API queries; unknown fields stay null and are never copied from the latest version. Version coverage is therefore **as of the chosen snapshot**, not a claim about live arXiv. A missing or invalid record, or a run without a snapshot, uses the API path: batches of up to 100 base IDs {cite}`arxiv-api`, where the latest `vN` identifies the number of versions, `published` supplies the v1 date and versioned queries retrieve earlier versions' metadata. Cached valid metadata avoids another lookup.
2. **Fallback without prolonged API retries.** Each API request has a two-attempt budget. A failed base-ID batch proceeds to OAI-PMH `arXivRaw`; missing entries or malformed feeds can receive a further API pass. OAI also supplies incomplete version dates. This reduces avoidable API backoff but cannot repair an unreachable network {cite}`arxiv-oai`.
3. **Fetch every version.** Request `/src/{id}vN` separately, skipping only versions with a final journal status and existing output. Detect source type from content, not merely the filename {cite}`arxiv-mimetypes`.
4. **Extract during transfer.** Read tar/tar.gz sequentially, member by member. Write only `.tex` and `.bib`; read past figures and other members. One exception follows the lecturer's answer on the course Q&A sheet {cite}`hcmus-qa`: a `.bbl` member is held in memory until the archive has been read, and is written only if the version has **no `.bib` and no `\bibitem` in its `.tex`**, so that a paper whose reference list exists only as a compiled `.bbl` does not lose it (M2 turns it back into BibTeX). Every other `.bbl` is dropped as before. Versions crawled before this rule have no `.bbl`; re-downloading the versions that ended without references recovers them. The normal tar path does not store the whole archive on disk. Unsafe paths and links are rejected. Kept source bytes are not edited: figure environments and `\includegraphics` commands remain for M2.
5. **Handle other formats explicitly.** PDF/PS and recognized HTML submissions become empty records; detection can stop the body early. Unexpected plain HTML is a failed response. Single-file gzip/TeX can buffer its full contents in RAM. ZIP needs a temporary spool file and has a size limit. The implementation does **not** claim constant memory or zero temporary disk for every input format.
6. **Collect references independently.** A separate thread requests Semantic Scholar batches of up to 100 and uses pagination when needed. All fetched references are retained, including references without an arXiv ID. Reference failures remain retryable and are checked separately from source completion {cite}`s2-api`.

### Optional hybrid source: arXiv bulk data on S3

The hybrid notebook can read papers whose snapshot lists **only v1** from arXiv's bulk source bundles on S3 {cite}`arxiv-bulk-s3` instead of requesting `/src/{id}v1`, and fetches every other paper version by version from arXiv, as above. The design has these properties:

- Each monthly bundle is checked against the MD5 in the S3 manifest before it is indexed; a size that differs from the manifest is accepted only when the MD5 matches. Downloads from the bucket are requester-pays; the team's prepared bundles on Drive need no S3 request.
- A paper missing from the bundles falls back to arXiv. Output paths, filtering (`.tex` and `.bib`, plus the conditional `.bbl` above) and journals are identical to the arXiv-only path.
- A bundle carries no version label. The pipeline **infers** v1 when the snapshot lists a single version and the bundle timestamp is at least one day after the v1 date, and records `version_evidence = inferred_snapshot_bundle_timestamp` in the journal. This is not a byte comparison with `/src/{id}v1`; it relies on a complete snapshot, the right ID and the bundle date, all of which must be reported with the results.
- A monthly bundle may keep a newer submission in place of an earlier same-month version, so multi-version papers are never taken from it.

Whether the teaching team accepts bulk S3 sources for M1 is still to be confirmed with them. Until then the arXiv-only notebook remains available for the official run; both write the same corpus layout, so M2 is not affected by the choice.

## Rate limiting and recovery

One shared limiter within a crawler process governs API, OAI and source requests. Its lock covers the entire request body; starts are at least three seconds apart plus 0–0.1 seconds of jitter. The benchmark runner also separates successive child processes. Only one group crawler may operate at a time, including local tests {cite}`arxiv-tou`.

- **HTTP 429, 5xx and connection failures:** bounded retries with exponential backoff, honouring `Retry-After` when sent; no idle backoff after the final unsuccessful attempt. A throttled arXiv run showed that a 429 carries no `Retry-After` and can last minutes, so source and OAI requests now get 8 attempts with waits of 2, 4, 8, 16, 32, 64 and 120 s (at most 246 s). Discovery's API calls keep 2 attempts because they have an OAI fallback {cite}`arxiv-oai`.
- **A chunk that stays incomplete:** the runner no longer stops. It waits `k × 300 s` before try *k+1* of the same chunk (3 tries by default); finished versions are skipped, so only the failed ones are fetched again. A chunk still incomplete after the last try is listed in `coverage.json` as `incomplete_chunks`, the run continues, and `final_complete` stays false until a later resume repairs it. Cooldown time counts in the session wall time. A crashed child process (for example `BlockedError`) still stops the run.
- **Adaptive pacing (off by default):** after a 429 the pace is multiplied by 1.5 (capped at 10 s) and 20 successes in a row win 0.5 s back. The pace never goes below the 3 s minimum. Whether it helps is unproven and is to be decided by an A/B run of the same 200 IDs.
- **Observing throttling:** `request_timeline.csv` counts arXiv responses per minute (200, 206 Range resumes, 429, 5xx) with megabytes downloaded, backoff seconds and the pace in force, which separates a throttled run from a healthy one.
- **Body interrupted during transfer:** request remaining bytes with HTTP Range and verify `Content-Range`. If the server ignores or misreports the range, restart the body. A cut body differs from a rate-limit response; rejected Range requests still respect retry rules.
- **Repeated HTTP 403:** circuit-breaker pauses and slower pacing; persistent blocking stops the run for inspection.
- **Pipeline interruption:** append and flush per-version records, retry failed work on resume, retain empty versions. A work-directory OS lock prevents two local pipeline processes sharing bookkeeping.

Range recovery is **within a live download process**. A destroyed runtime does not preserve the connection or guarantee byte-level continuation of that version.

## Drive persistence and M2 handoff

The group's designated Google crawl account stores each run at `/content/drive/MyDrive/arxiv-nhom1/runs/<RUN_ID>/`. The notebook validates a pre-existing `TEAM.json` marker and write access; it never silently creates a substitute folder or deletes an existing run. Runs are **independent**: each has its own checkpoint, journals and raw corpus tree, and no global shift marker is read or written. A run ID is never used by two runtimes at once, including during a resume, and only one arXiv crawler runs at a time because the rate limiter lives inside each Colab runtime and does not coordinate several machines.

Process the corpus on the Colab local disk. A checkpoint is requested about every 300 seconds at a completed-version boundary and at chunk boundaries. It is a **plain mirror, not an archive**: completed version folders, `metadata.json`, `references.json` and the `work/` journals are copied as real files under `runs/<RUN_ID>/`, so M2 reads the corpus directly without unpacking anything. Before a changed file is replaced, its old bytes are kept as a content-addressed object under `.checkpoint-objects/`; the new file is copied through a temporary name, verified, and `INDEX.json` is published last. If a runtime dies between those steps, restore verifies the mirror against the index and falls back to the saved object, so the visible mirror may be ahead of the committed generation. M2 therefore starts by restoring and verifying the committed generation. The objects stay on Drive, which grows with every updated journal; a checkpoint that was already corrupt before this design cannot be repaired automatically.

Five minutes is a **target, not a maximum loss guarantee**: a large version or a failed sync can delay saving. A hard kill cannot execute cleanup. Only verified Drive checkpoints survive; uncommitted work may need to run again. The `TEAM.json` marker is advisory rather than an atomic distributed lock. There is no session-time budget: the notebook does not stop itself for a handoff, and Colab can end the runtime at any time. Resume uses the same run ID, the same settings and the code revision saved in the manifest, in a fresh local destination. M2 keeps the original `.tex`/`.bib` files immutable and writes parsed outputs elsewhere.

## Measurement boundaries

The primary measurements span a session from before restore through final corpus sync. A sampler measures the runner/notebook kernel (including its baseline) and all descendants every second, with local data/work and telemetry staging disk sampled every 30 seconds. Each chunk also runs under `/usr/bin/time -v` and `src.utils.profiler`; these narrower measurements remain diagnostic cross-checks.

- Session wall includes restore, orchestration, discovery, source processing, reference completion, retry waits, chunk cooldowns, checkpoints, QA and final corpus sync. Setup/installation, final telemetry publication/collection, final evidence re-export/download and offline gaps are excluded. Earlier report generation inside the runner is included.
- With a metadata snapshot, building the compact snapshot index is sampled inside the session and added once per session to the `discovery_time` metric, on top of each chunk's own `discovery_s`; do not add it to session wall again. Copying the snapshot to the local disk, hashing it against the manifest and the Kaggle download are setup costs outside the sampler and are disclosed separately. The filtered snapshot is part of the sampled disk. Preparing or downloading S3 bulk bundles is also outside the session.
- `pipeline_wall_time` retains the chunk-only sum; `wall_time_e2e` uses full-session measurements. Never add checkpoints or overlapping reference durations again.
- `retry_backoff_wait` is a log-derived diagnostic already included in runtime; do not add it again or subtract it.
- Mean time per requested ID divides session wall by required IDs, including unsuccessful IDs. `paper_attempt_timings.csv` separately records each paper's admission-to-source/reference-readiness latency and source work, retaining retries. Batch waiting makes lifecycle latencies overlap; they must not be summed.
- Peaks are **observed sampled peaks**; short spikes may be missed. RSS observations are integrated over time and sessions combined by sampled duration. Output size is the actual final corpus size, not summed chunk output.
- Independent, checksummed Drive telemetry targets publication every 30 seconds, separately from corpus checkpoints, and is restored even when newer than the corpus chain. Failed/stalled uploads can exceed this target. An unfinalized/corrupt session exports only an observed lower bound; exact end-to-end and mean-time rows are omitted. Missing chunk summaries also flag incomplete timing. Corpus completeness alone does not prove complete timing.

## Success and evidence

A source paper is complete when all discovered versions have final status `ok`, `no_tex` or `unavailable`, with required directories and valid metadata. Empty records count as required output, not successful TeX downloads. Report source QA and reference QA separately.

`coverage.json` covers the whole selection. `final_corpus_complete` requires all 20,000 IDs and required data; `final_complete` additionally requires intact timing summaries and no `incomplete_chunks`. The evidence ZIP contains manifests, dependency/hardware details, coverage/QA, version/discovery journals, logs, attempt profiles and Book CSVs (including `request_timeline.csv`). Raw corpus and Secrets are excluded.

Each independent run exports its own evidence. `python -m src.analysis.group_evidence` combines several extracted runs into a new report: `group_audit.json` lists missing, extra and duplicated IDs and inconsistent code or snapshot provenance, and `papers_stats.csv` keeps the run of every row. Coverage is judged from each run's QA reports and journals, not by re-reading corpus files, and a sample cannot certify final coverage. `active_wall_sum_s` adds the measured active sessions, whereas `timeline_span_s` includes the gaps and depends on the machines' clocks; neither is automatically the official end-to-end wall time when runtimes overlap, and memory peaks of different machines are never combined. `official_final_certified` stays false until the grading treatment of a distributed run is confirmed.

:::{important}
Full-crawl measurements have not yet been supplied. Analysis CSVs remain placeholders until the runs of all partitions (the only-v1 run and the four multi-version runs) are combined and audited against the 20,000 assigned IDs. The supplied 200-ID Dang smoke has been audited separately, with its legacy implementation and measurement scope retained; it does not replace a full-corpus benchmark using the new measurement contract.
:::
