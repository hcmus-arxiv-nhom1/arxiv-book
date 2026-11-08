# 2. Methodology

<!-- Owners: Đăng, Thiên. Updated with assistance from OpenAI Codex, disclosed per course rules. -->

The team collects paper metadata, available source files and reference metadata for the assigned IDs described in [Problem and Dataset](00-problem-dataset.md). The implementation is maintained in [CodeRepo](https://github.com/hcmus-arxiv-nhom1/CodeRepo); the corpus contract is described in `docs/data_contract.md`.

## 2.1 Discovery and pipeline selection

The group filters the metadata snapshot by the assigned ID ranges and partitions the selected records by their number of recorded versions before planning crawl chunks. Missing or invalid records stop the split-notebook preflight rather than being silently omitted. The snapshot fixes the expected version scope; it does not establish versions submitted after its cutoff.

The final collection uses two notebooks and five distinct runs:

- **only-v1-all:** processes single-version papers from all four assigned ranges. The crawler indexes candidate S3 bundles, extracts eligible members and falls back to the version-specific arXiv source endpoint when a candidate is missing or cannot be accepted.
- **multi-dang, multi-hieu, multi-thien and multi-tien:** each processes the snapshot's multi-version papers in one member's assigned range. Every expected version is requested separately from arXiv using `/src/{id}vN`.

S3 bulk reduces the number of arXiv source requests for the single-version group. A bulk member does not independently establish the complete history of a multi-version paper; the latter group therefore uses version-specific requests. References are collected separately through Semantic Scholar, including for papers sourced from S3; S3 source extraction does not itself supply reference metadata {cite}`s2-api`.

### Inferring v1 in S3 bundles

For a paper whose complete snapshot history at time $T_{\mathrm{snap}}$ contains only `v1`, suppose a bundle containing that paper reflects its source at time $T_b$, where $T_{\mathrm{snap}} \ge T_b$. Under these assumptions, no later version was submitted by $T_b$: a version submitted by then would also appear in the complete snapshot history. The paper's source in the bundle can therefore be inferred to represent `v1`. Versions submitted after the snapshot are outside this snapshot-defined target scope.

This is a conditional argument, not independent proof of the version of a particular bundle member. In particular, the exact snapshot cutoff and its completeness relative to each bundle have not been established. A date in a paper's `update_date` field does not establish that cutoff, and two sources obtained on the same day need not represent the same instant. Checking that a bundle was created after the recorded `v1` submission does not rule out an unobserved later revision.

The implemented `infer_v1` heuristic checks that the snapshot has one version and its submission precedes the bundle timestamp by at least one day; it does not check $T_{\mathrm{snap}} \ge T_b$. The pipeline checks the bundle MD5 against the manifest, rejects conflicting explicit versions and ambiguous members, and records `version_evidence=inferred_snapshot_bundle_timestamp`. The outer MD5 checks bundle integrity, not the identity or usable TeX content of each member. Missing or unverified S3 candidates can fall back to a version-specific arXiv request; PDF and other sources without usable TeX may instead be retained as `no_tex`. Reference completeness is assessed separately.

## 2.2 Source, metadata and reference processing

The crawler detects source format from content and reads tar/tar.gz members sequentially. It retains `.tex` and `.bib` files, reading past figures and other discarded members, and rejects unsafe paths and links. The retained TeX is not rewritten: figure commands remain for later processing. PDF/PS and other recognized non-TeX sources can result in an explicit `no_tex` record; unexpected or failed downloads remain subject to the crawler's error handling. Single-file gzip and ZIP inputs have different memory and temporary-disk behavior from streaming tar inputs {cite}`arxiv-mimetypes`.

The reported M1 runs predate the subsequent `.bbl` collection work. For M2, the group is adding a conditional `.bbl` fallback to recover reference information where no `.bib` or `\bibitem` is available, following the course Q&A {cite}`hcmus-qa`. This later work is not included in the M1 crawl statistics reported here.

Snapshot metadata supplies the base records. Where the discovery implementation needs missing information or encounters incomplete records, it can use the arXiv API and OAI-PMH `arXivRaw` fallback; unavailable historical fields may remain null {cite}`arxiv-api` {cite}`arxiv-oai`. Reference metadata is fetched separately, including references without an arXiv ID. Reference completion and source completion are evaluated independently.

## 2.3 Rate limiting and recovery

Within a crawler process, a shared limiter governs arXiv API, OAI and source requests, with at least three seconds between request starts and small jitter. Each runtime has its own limiter; this is not a shared cross-runtime rate limiter.

The group used multiple Colab runtimes concurrently. The main crawl account shared the relevant Drive folders with member accounts; members added shortcuts to their own My Drive, mounted their account in Colab and configured paths that resolve to the same shared storage. Each run used a distinct run ID and output directory, allowing results to be collected in the main shared location. A shortcut points to existing shared content rather than copying it; it does not itself grant access, synchronize at a guaranteed speed or coordinate requests across runtimes. The exact account/IP mapping for each measured session has not been independently verified.

:::{note}
The observed sampler timeline and per-run backoff diagnostics are presented in [Performance](03-performance.ipynb). A complete account/IP mapping and aggregate arXiv request rate have not been independently established; no global rate is inferred from one process's limiter.
:::

HTTP 429, 5xx and connection errors are handled with bounded retries and backoff. A transfer interrupted mid-body may use HTTP Range after validating the response; if it cannot safely resume, the body is restarted. Range continuation applies to a live download and is not guaranteed across runtime loss. Persistent errors remain visible for later inspection.

## 2.4 Storage, checkpoints and reproducibility

Crawling and extraction run on the local Colab disk, with raw corpus files and work records checkpointed to the designated Drive run directory. The split notebooks configure `CHUNK_SIZE = 100` and a checkpoint target of `CHECKPOINT_S = 600`; a chunk here is based on the original ID selection and the snapshot-selected subset can contain fewer than 100 papers. These are notebook configurations, and the actual saved configuration for each run remains the authority. A checkpoint target is not a hard deadline: an active version or slow storage can delay publication.

Each run records its selected IDs, configuration and code revision. Resume uses the saved run identity, compatible settings and saved revision. Drive output includes `data/corpus/` and `work/`, with an `INDEX.json` for checkpoint state. Changed indexed files can have prior content preserved for recovery; restored data must still be checked. A destroyed runtime may lose work completed after the last published checkpoint. These files retain the paper/version directory structure needed for the M2 handoff.

## 2.5 Measurement and completion evidence

The crawler uses Python, `requests`, `lxml`, the standard archive and hashing libraries, and Semantic Scholar and arXiv APIs. On CPU-only Colab, `psutil` and process-level tools collect timing and resource observations; the sampling scope, measurement boundaries and aggregation of concurrent runs are discussed in [Performance](03-performance.ipynb). Data coverage and reference statistics are reported in [Data statistics](02-data-stats.ipynb).

Crawler terminal states such as `ok`, `no_tex` and `unavailable` must be reported separately. A checkpoint or crawler-complete paper is not by itself evidence that usable TeX and complete reference metadata exist for every version. Final source coverage, reference QA and timing completeness require their respective evidence.

:::{note}
The five run manifests and version journals have been reconciled against the assigned snapshot; [Data statistics](02-data-stats.ipynb) presents the recorded outcomes and [Performance](03-performance.ipynb) presents the validated sampler observations. Independent raw-corpus verification and the original audit-flag discrepancies remain limitations documented in those pages.
:::
