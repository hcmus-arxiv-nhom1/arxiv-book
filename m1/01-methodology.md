# Crawling methodology

<!-- Owners: Đăng, Thiên. Updated with assistance from OpenAI Codex, disclosed per course rules. -->

Milestone 1 collects metadata, reference metadata and the available LaTeX source of **every version** of the assigned arXiv papers. Only `.tex` and `.bib` source files are retained; a version without usable TeX remains an explicit empty record {cite}`hcmus-statement`. Implementation lives in [CodeRepo](https://github.com/hcmus-arxiv-nhom1/CodeRepo); paths and schemas follow its `docs/data_contract.md`.

## Scope and reproducibility

| Member | Inclusive assigned range | IDs |
| --- | --- | ---: |
| Cao Tiến Thiên | `2606.30734` → `2607.03693` | 5,000 |
| Trần Minh Tiến | `2606.25734` → `2606.30733` | 5,000 |
| Trương Lê Trung Hiếu | `2606.05734` → `2606.10733` | 5,000 |
| Lý Huỳnh Minh Đăng | `2604.20535` → `2604.25534` | 5,000 |

The final benchmark must cover **all 20,000 assigned IDs**. Samples validate the pipeline but do not replace that benchmark. Thiên's range crosses a month boundary: the generator uses the configured last June sequence (`2606.32040`) and restarts July at `00001`.

The [group crawl and benchmark notebook](arxiv_nhom1_crawl_benchmark.ipynb) provides one entrypoint for both modes. It records the code revision, exact ID selection, parameters, dependency versions, hardware and sessions. Final mode rejects partial ranges and disabled references. A new run uses a new run ID; resume must match its saved configuration and implementation revision.

## Discovery and source processing

1. **Generate and discover IDs.** Query the arXiv API with batches of up to 100 base IDs {cite}`arxiv-api`. The latest `vN` identifies the number of versions. `published` supplies the v1 date; versioned queries retrieve earlier versions' metadata. Cached valid metadata avoids another lookup.
2. **Fallback without prolonged API retries.** Each API request has a two-attempt budget. A failed base-ID batch proceeds to OAI-PMH `arXivRaw`; missing entries or malformed feeds can receive a further API pass. OAI also supplies incomplete version dates. This reduces avoidable API backoff but cannot repair an unreachable network {cite}`arxiv-oai`.
3. **Fetch every version.** Request `/src/{id}vN` separately, skipping only versions with a final journal status and existing output. Detect source type from content, not merely the filename {cite}`arxiv-mimetypes`.
4. **Extract during transfer.** Read tar/tar.gz sequentially, member by member. Write only `.tex` and `.bib`; read past figures and other members. The normal tar path does not store the whole archive on disk. Unsafe paths and links are rejected. Kept source bytes are not edited: figure environments and `\includegraphics` commands remain for M2.
5. **Handle other formats explicitly.** PDF/PS and recognized HTML submissions become empty records; detection can stop the body early. Unexpected plain HTML is a failed response. Single-file gzip/TeX can buffer its full contents in RAM. ZIP needs a temporary spool file and has a size limit. The implementation does **not** claim constant memory or zero temporary disk for every input format.
6. **Collect references independently.** A separate thread requests Semantic Scholar batches of up to 100 and uses pagination when needed. All fetched references are retained, including references without an arXiv ID. Reference failures remain retryable and are checked separately from source completion {cite}`s2-api`.

## Rate limiting and recovery

One shared limiter within a crawler process governs API, OAI and source requests. Its lock covers the entire request body; starts are at least three seconds apart plus 0–0.1 seconds of jitter. The benchmark runner also separates successive child processes. Only one group crawler may operate at a time, including local tests {cite}`arxiv-tou`.

- **HTTP 429, 5xx and connection failures:** bounded retries with backoff and `Retry-After`; no idle backoff after the final unsuccessful attempt. Discovery has a smaller API budget because it has an OAI fallback.
- **Body interrupted during transfer:** request remaining bytes with HTTP Range and verify `Content-Range`. If the server ignores or misreports the range, restart the body. A cut body differs from a rate-limit response; rejected Range requests still respect retry rules.
- **Repeated HTTP 403:** circuit-breaker pauses and slower pacing; persistent blocking stops the run for inspection.
- **Pipeline interruption:** append and flush per-version records, retry failed work on resume, retain empty versions. A work-directory OS lock prevents two local pipeline processes sharing bookkeeping.

Range recovery is **within a live download process**. A destroyed runtime does not preserve the connection or guarantee byte-level continuation of that version.

## Drive persistence and M2 handoff

The group operates a designated Google crawl account in shifts at `/content/drive/MyDrive/arxiv-nhom1`. The notebook validates a pre-existing team marker and write access. It never silently creates a substitute folder or deletes an existing run.

Process corpus on the Colab local disk. Request checkpoints approximately every 300 seconds at a completed-version boundary and at chunk boundaries. Archive new/changed completed data and matching journals; read back each uploaded delta and verify SHA-256 before publishing its completion record. Ignore incomplete uploads and validate a chain of generations during restore.

Five minutes is a **target, not a maximum loss guarantee**: a large version or failed sync can delay saving. A hard kill cannot execute cleanup. Only verified Drive checkpoints survive; uncommitted work may need to run again. Heartbeats help coordinate shifts, but Drive markers are advisory rather than an atomic distributed lock.

A four-hour session budget is checked between chunks for an orderly handoff; it does not guarantee that Colab keeps the runtime alive that long. Resume uses the same run ID and saved code revision in a fresh local destination. M2 restores and validates that corpus, keeping original `.tex`/`.bib` immutable and writing parsed outputs elsewhere.

## Measurement boundaries

The primary measurements span a session from before restore through final corpus sync and shift release. A sampler measures the runner/notebook kernel (including its baseline) and all descendants every second, with local data/work and telemetry staging disk sampled every 30 seconds. Each chunk also runs under `/usr/bin/time -v` and `src.utils.profiler`; these narrower measurements remain diagnostic cross-checks.

- Session wall includes restore, orchestration, discovery, source processing, reference completion, retry waits, checkpoints, QA and final corpus sync. Setup/installation, final telemetry publication/collection, final evidence re-export/download and offline gaps are excluded. Earlier report generation inside the runner is included.
- `pipeline_wall_time` retains the chunk-only sum; `wall_time_e2e` uses full-session measurements. Never add checkpoints or overlapping reference durations again.
- `retry_backoff_wait` is a log-derived diagnostic already included in runtime; do not add it again or subtract it.
- Mean time per requested ID divides session wall by required IDs, including unsuccessful IDs. `paper_attempt_timings.csv` separately records each paper's admission-to-source/reference-readiness latency and source work, retaining retries. Batch waiting makes lifecycle latencies overlap; they must not be summed.
- Peaks are **observed sampled peaks**; short spikes may be missed. RSS observations are integrated over time and sessions combined by sampled duration. Output size is the actual final corpus size, not summed chunk output.
- Independent, checksummed Drive telemetry targets publication every 30 seconds, separately from corpus checkpoints, and is restored even when newer than the corpus chain. Failed/stalled uploads can exceed this target. An unfinalized/corrupt session exports only an observed lower bound; exact end-to-end and mean-time rows are omitted. Missing chunk summaries also flag incomplete timing. Corpus completeness alone does not prove complete timing.

## Success and evidence

A source paper is complete when all discovered versions have final status `ok`, `no_tex` or `unavailable`, with required directories and valid metadata. Empty records count as required output, not successful TeX downloads. Report source QA and reference QA separately.

`coverage.json` covers the whole selection. `final_corpus_complete` requires all 20,000 IDs and required data; `final_complete` additionally requires intact timing summaries. The evidence ZIP contains manifests, dependency/hardware details, coverage/QA, version/discovery journals, logs, attempt profiles and Book CSVs. Raw corpus and Secrets are excluded.

:::{important}
Full-crawl measurements have not yet been supplied. Analysis CSVs remain placeholders. The supplied 200-ID Dang smoke has been audited separately, with its legacy implementation and measurement scope retained; it does not replace a full-corpus benchmark using the new measurement contract.
:::
