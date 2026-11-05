# Discussion and limitations

<!-- Drafted with assistance from OpenAI Codex and Claude (Anthropic), disclosed per course rules. -->

## What is established

The implementation includes shared request pacing, streaming tar extraction, filtered storage, retries, Range recovery, version-level resume, chunk-level retry after a cooldown, snapshot-first discovery and independent, checkpointed runs. Automated tests exercise these behaviors with simulated responses. They establish covered software behavior, not full-crawl performance on arXiv.

The audited 200-ID Đăng sample (`2604.20535`–`2604.20734`, implementation `6c8c2b3`) completed 279 version records: 266 with TeX, 12 without TeX and one unavailable. Its two chunk profiles totaled 1,805.18 seconds; this is a legacy chunk-only scope, not the new full-session measurement. The supplied evidence also revealed overlapping component timers, so download/transfer component means from that revision are not used. These observations do not establish full-corpus performance; committed analysis CSVs remain placeholders pending the final run.

## What the throttled run taught us

A 1,000-ID Colab run on 01/11/2026 (`m1-dang-1000-01`, chunks of 100) stopped after four chunks with 399 papers complete. The first 20 minutes ran at the 3 s floor without a single HTTP 429; then arXiv answered 429 more and more often and slowed the transfers, so the chunks took 404, 476, 936 and 1,415 s although the later papers were smaller. One version was refused five times within 33 s, recorded as failed, and the chunk check stopped the run, leaving 600 IDs never tried. Three changes follow from this (spec 0004 in CodeRepo): a chunk that stays incomplete is retried after a cooldown and then recorded instead of stopping the run; arXiv requests get a longer retry budget (up to 246 s of waiting); and a per-minute request timeline separates volume-based from request-based throttling. Adaptive pacing is implemented but off by default, because the cause of the throttle (volume, request count or a shared Colab address) is unknown and the effect of slowing down is not proven. Opening more connections or switching addresses was rejected: the Terms of Use ask not to overcome the limits with more machines {cite}`arxiv-tou`.

## Why the selected optimizations matter

A metadata snapshot removes the base-ID discovery requests, but historical per-version titles and authors still use the API, so discovery 429s are reduced, not eliminated. Batch discovery reduces metadata requests when the API responds successfully. A bounded API retry budget avoids repeated backoff before trying OAI. Stream extraction avoids storing normal tar archives; filtering avoids retaining figure binaries. Range recovery avoids restarting long live transfers when supported. Reference collection overlaps the arXiv lane using its own limiter.

Larger chunks amortize process startup and bookkeeping but delay chunk-boundary persistence. Periodic completed-version checkpoints add another persistence opportunity, at a real compression/Drive/verification cost. More download workers cannot be assumed to improve throughput while maintaining the group's single arXiv lane.

## Remaining limits

- Network latency, large sources, retries and availability can dominate runtime. CPU-only does not imply CPU-bound.
- OAI can recover version history without necessarily supplying all per-version titles/authors. The contract permits unavailable per-version fields; fallback is not equivalent to successful versioned API metadata.
- ZIP spooling and single-file buffering differ from tar streaming. No universal constant-RAM or zero-temporary-disk guarantee is made.
- Checkpoints are durable only after verification. Runtime death can lose uncommitted progress. Restore reads checkpoint archives and may take substantial time/disk.
- Drive shift markers are advisory: coordinate one active crawler. Record hardware for each resumed session.
- Snapshot-based version coverage is as of the chosen snapshot; it cannot prove the absence of later revisions.
- Source from S3 bulk bundles carries no version label. v1 is inferred from the snapshot and the bundle timestamp, not compared byte by byte with `/src/{id}v1`, and whether the teaching team accepts this for M1 is still to be confirmed.
- The rate limiter lives inside each Colab runtime. Independent runs do not share a limit, so only one arXiv crawler may run at a time, and the grading treatment of a run split over several runtimes is still open (`official_final_certified` stays false).
- Sample throughput and sampled peaks do not establish final performance. Missing interrupted summaries make exact timing incomplete even when corpus recovery succeeds.

## Completing the final report

Benchmark all 20,000 assigned IDs and all discovered versions, as independent partition runs combined by `src.analysis.group_evidence`. Before replacing placeholder CSVs, verify full source/reference QA and that no chunk is listed as incomplete, record the exact CodeRepo revision and snapshot hash of every run, retain attempts/timing audits and disclose session boundaries and exclusions. Do not describe multiple sessions or runtimes as one uninterrupted runtime.

The [operational notebook](arxiv_nhom1_crawl_benchmark.ipynb) (arXiv only) is embedded for inspection and launch in Colab; the hybrid and partition notebooks are listed in the [methodology](01-methodology.md). Book builds execute CSV analysis notebooks, never the crawler. The submitted Book retains one M1 chapter group and one M2 chapter group.
