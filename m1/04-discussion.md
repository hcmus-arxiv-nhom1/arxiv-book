# 5. Discussion and limitations

<!-- Drafted with assistance from OpenAI Codex, disclosed per course rules. -->

## 5.1. Results and interpretation

The collection is divided into one only-v1 run and four member-specific multi-version runs. The scope is defined by the assigned IDs and the metadata snapshot described in [Problem and Dataset](00-problem-dataset.md). Completion of a crawl or a checkpoint must be distinguished from the availability of usable TeX and complete reference metadata; `no_tex`, `unavailable`, failures and reference statuses require separate reporting.

The five manifests and exported paper records reconcile with all 20,000 assigned IDs, and the journals record a terminal state for all 26,491 snapshot versions. Of these records, 25,041 are `ok`, 1,364 are `no_tex` and 86 are `unavailable`. A total of 18,878 papers have at least one version with TeX. The [Data statistics](02-data-stats.ipynb) page reports reference-list and citation-level outcomes separately; 17 paper reference lists were recorded as `not_found`. These are exporter and journal results, not an independent audit of every corpus file.

## 5.2. Design trade-offs

The filtered metadata snapshot reduces base discovery requests and fixes a reproducible target scope, but revisions after its cutoff are outside that scope. S3 bulk supplies source candidates for papers with only `v1` in the snapshot; the version assignment is conditional on the assumptions explained in [Methodology](01-methodology.md), not independent proof of every member's version. Multi-version papers use version-specific arXiv requests to retain their history.

Streaming tar extraction and retaining only `.tex`/`.bib` reduce retained material, while retry, backoff and HTTP Range recovery address network interruptions. These choices do not guarantee constant memory for every source format, remove all network errors, or establish a particular speedup by themselves. [Attempts and effort](05-attempts-effort.ipynb) documents the experiments and their evidence and limitations.

Drive checkpoints preserve published progress across runtime interruptions, with storage, synchronization and restore costs. A checkpoint target is not a strict guarantee of when data becomes durable; work after the latest published state can be lost. Multiple runtimes were used concurrently with distinct run directories and shared Drive access. Per-process request pacing does not provide a global limiter across machines.

The [Performance](03-performance.ipynb) page presents validated sampler intervals on a shared timeline. Its group interval includes gaps between runs and excludes work outside the sampler, including earlier bulk preparation; it is not obtained by adding overlapping session times. Network behavior and different code revisions limit causal comparisons across runs.

## 5.3. Remaining limits and M2 handoff

- Network availability, rate limiting and source size can affect runtime independently of CPU capacity. Sampled RAM and disk peaks may miss short spikes.
- PDF/PS and other submissions without usable TeX can produce `no_tex`; unavailable versions are tracked separately. A terminal status does not guarantee a parseable source file.
- Reference collection is independent of S3 source extraction. A missing or unsuccessful reference record is not evidence that a paper has zero references.
- Some historical version metadata can remain incomplete. The snapshot may not include subsequent revisions, and its exact cutoff relative to every S3 bundle is not established.
- M2 should use the raw paper/version corpus together with metadata, reference records, snapshot scope and source/QA journals, and validate accessible files before parsing. The current journal reconciliation is not a full readback audit of the corpus.

:::{note}
**Pending handoff audit:** validate raw corpus accessibility and source/reference QA, review the `no_tex` and `unavailable` cases, and reconcile the original timing-audit flags with the recovered session telemetry before using the corpus for M2.
:::
