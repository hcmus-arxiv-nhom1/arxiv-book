# Discussion and limitations

<!-- Drafted with assistance from OpenAI Codex, disclosed per course rules. -->

## What is established

The implementation includes shared request pacing, streaming tar extraction, filtered storage, retries, Range recovery and version-level resume. Automated tests exercise these behaviors with simulated responses. They establish covered software behavior, not full-crawl performance on arXiv.

The audited 200-ID Đăng sample (`2604.20535`–`2604.20734`, implementation `6c8c2b3`) completed 279 version records: 266 with TeX, 12 without TeX and one unavailable. Its two chunk profiles totaled 1,805.18 seconds; this is a legacy chunk-only scope, not the new full-session measurement. The supplied evidence also revealed overlapping component timers, so download/transfer component means from that revision are not used. These observations do not establish full-corpus performance; committed analysis CSVs remain placeholders pending the final run.

## Why the selected optimizations matter

Batch discovery reduces metadata requests when the API responds successfully. A bounded API retry budget avoids repeated backoff before trying OAI. Stream extraction avoids storing normal tar archives; filtering avoids retaining figure binaries. Range recovery avoids restarting long live transfers when supported. Reference collection overlaps the arXiv lane using its own limiter.

Larger chunks amortize process startup and bookkeeping but delay chunk-boundary persistence. Periodic completed-version checkpoints add another persistence opportunity, at a real compression/Drive/verification cost. More download workers cannot be assumed to improve throughput while maintaining the group's single arXiv lane.

## Remaining limits

- Network latency, large sources, retries and availability can dominate runtime. CPU-only does not imply CPU-bound.
- OAI can recover version history without necessarily supplying all per-version titles/authors. The contract permits unavailable per-version fields; fallback is not equivalent to successful versioned API metadata.
- ZIP spooling and single-file buffering differ from tar streaming. No universal constant-RAM or zero-temporary-disk guarantee is made.
- Checkpoints are durable only after verification. Runtime death can lose uncommitted progress. Restore reads checkpoint archives and may take substantial time/disk.
- Drive shift markers are advisory: coordinate one active crawler. Record hardware for each resumed session.
- Sample throughput and sampled peaks do not establish final performance. Missing interrupted summaries make exact timing incomplete even when corpus recovery succeeds.

## Completing the final report

Benchmark all 20,000 assigned IDs and all discovered versions. Before replacing placeholder CSVs, verify full source/reference QA, record the exact CodeRepo revision, retain attempts/timing audits and disclose session boundaries and exclusions. Do not describe multiple sessions as one uninterrupted runtime.

The [operational notebook](arxiv_nhom1_crawl_benchmark.ipynb) is embedded for inspection and launch in Colab. Book builds execute CSV analysis notebooks, never the crawler. The submitted Book retains one M1 chapter group and one M2 chapter group.
