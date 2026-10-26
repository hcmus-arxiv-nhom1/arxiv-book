# Crawling methodology

<!-- Owners: Đăng, Thiên. The crawler sections were written by Thiên with the help of an AI assistant (Claude, Anthropic), cited per the course rules. -->

This chapter describes how the group built the Milestone 1 corpus: resolving the assigned arXiv IDs, downloading the LaTeX source of **every version**, keeping only `.tex` and `.bib` files, and collecting reference metadata from Semantic Scholar {cite}`hcmus-statement`. The code lives in the [code repository](https://github.com/hcmus-arxiv-nhom1/CodeRepo) (`src/crawler/`, `src/run_pipeline.py`); the data schema is fixed in `docs/data_contract.md` of that repository.

## Scope

The group is responsible for 20,000 arXiv IDs, split into four ranges of 5,000 IDs as given by the registration sheet:

| Member | ID range |
| --- | --- |
| Cao Tiến Thiên | `2606.30734` → `2607.03693` |
| Trần Minh Tiến | `2606.25734` → `2606.30733` |
| Trương Lê Trung Hiếu | `2606.05734` → `2606.10733` |
| Lý Huỳnh Minh Đăng | `2604.20535` → `2604.25534` |

arXiv sequence numbers restart at `00001` every month, so the range `2606.30734` → `2607.03693` is not one run of consecutive numbers. The crawler generates IDs **month by month** (`iter_id_range`) using the last sequence number of June, which was looked up with the arXiv API: `2606.32040` exists and `2606.32041` onwards do not. The range therefore holds exactly 1,307 + 3,693 = 5,000 IDs.

## Pipeline

```{mermaid}
flowchart LR
    R["ID range"] --> G["Month-aware ID generation"]
    G --> D["Discovery<br/>arXiv API id_list"]
    D -->|metadata.json| C[("corpus/&lt;yymm-id&gt;/")]
    D --> V["Version queue<br/>skip finished versions"]
    V --> DL["Download /src/{id}vN"]
    DL --> X["File type detection<br/>keep .tex, .bib"]
    X -->|vN/| C
    X -->|one line per version| J[("work/versions.jsonl")]
    D -. separate thread .-> S["Semantic Scholar<br/>POST /paper/batch"]
    S -->|references.json| C
```

1. **Discovery** {cite}`arxiv-api`. The arXiv API is queried with `id_list`, 100 IDs per request, which is about 50 requests for 5,000 IDs. The answer gives the title, authors, `journal_ref` (venue), DOI and the **identifier of the latest version**: its `vN` suffix tells how many versions a paper has. `published` is the date of v1 and `updated` the date of the latest version. For papers with three or more versions, the dates of v2…v(N-1) come from versioned queries (`2606.30762v2`). OAI-PMH `arXivRaw` {cite}`arxiv-oai` is the fallback for IDs the API does not return.
2. **Source download.** Every version is fetched on its own from `https://export.arxiv.org/src/{id}vN`, including papers that only have `v1`. The body is streamed to a `.part` file and renamed only once `Content-Length` matches.
3. **File type detection by magic bytes**, never by file name {cite}`arxiv-mimetypes`:

   | First bytes | Kind | Handling |
   | --- | --- | --- |
   | `1f 8b` + tar header | `tar.gz` | Read member by member, write only `.tex` and `.bib` |
   | `1f 8b`, TeX inside | single gzipped file | Written as one `.tex` file |
   | `1f 8b`, HTML inside | `html.gz` | HTML submission (e.g. an EPTCS proceedings volume) → empty record |
   | `%PDF`, `%!PS` | PDF / PostScript only | Empty record |
   | plain HTML with HTTP 200 | Error page | `failed`, retried on the next run |
   | HTTP 404/410 | Source no longer available | `unavailable`, empty record |

4. **Figure removal by extraction**, as the statement requires: only `.tex` and `.bib` members are written, so figure binaries never enter the corpus. `.tex` files are kept byte for byte, so `figure` environments and `\includegraphics` commands remain for Milestone 2. Members with absolute paths, `..`, links or names the file system cannot store are skipped. For every version the crawler records the size before and after filtering and the extensions it dropped (`dropped`) in `work/versions.jsonl`.
5. **Reference metadata** {cite}`s2-api`. A separate thread calls Semantic Scholar's `POST /paper/batch` with 100 papers per request. The answer contains the **complete** reference list of each paper, so 20,000 papers need only about 200 requests. Every reference is kept, with or without an arXiv ID. A paper whose list is too long is completed through the paginated `/paper/{id}/references` endpoint.

## Politeness

arXiv's Terms of Use ask for *"no more than 1 request every 3 seconds"* and a single connection at a time, counted over all machines of the group {cite}`arxiv-tou`.

- **One shared `RateLimiter`** serves every arXiv request (API, OAI-PMH, `/src/`). Its lock is held for the whole request, so two arXiv requests never overlap. Request starts are at least 3 s apart plus a random jitter of 0–0.1 s. `run.log` records the `gap` of every request so the pace can be audited; a test run on 27/10/2026 measured a minimum gap of 3.015 s.
- Requests go only to the mirrors `export.arxiv.org` and `oaipmh.arxiv.org`, never to `arxiv.org`, with a descriptive User-Agent.
- **One run per work directory:** `run_pipeline` holds an operating-system lock on `work/run.lock`. The corpus is collected by **one** instance, in shifts shared by the members, never on two machines at once.
- **Retries:** connection errors, timeouts, bodies cut mid-transfer, 429 and 5xx are retried up to 5 times with a `2^n` s backoff plus jitter, honouring `Retry-After`. Three consecutive 403 answers pause the crawl for 15–30 minutes and slow the pace to 5 s; more than three such pauses stop the run so it can be resumed later.
- **Semantic Scholar has its own limiter:** 1.1 s per request with an API key, 3 s without one, matching the limit of 100 requests per 5 minutes.

## Output layout

```text
data/corpus/
  2606-30734/                # arXiv ID as yymm-id
    metadata.json            # arxiv_id, title, authors[], submission_date, revised_dates[], venue, num_versions
    references.json          # every reference returned by S2: title, authors, date, arXiv ID (if any), S2 ID
    v1/                      # .tex/.bib only; empty when the version has no TeX source
    v2/
work/
  versions.jsonl             # one line per version: status, kind, sizes, dropped files, timings
  discovery.jsonl  failed.csv  run_summary.json  run.log  profile/
```

`metadata.json` holds every column of the `papers` table; the references of `references.json` that carry an arXiv ID become the `references` table of Milestone 3.

## Resume

Every finished version is appended to `work/versions.jsonl` at once (flushed and fsynced), so even a hard kill loses no finished line. Running the **same command** again skips versions already in a final state and retries `failed` ones; existing `metadata.json` and `references.json` files are skipped too. In a test, the crawl was killed after 16 versions and restarted: all 16 were skipped and no line was written twice.

## Benchmark protocol

The statement measures the running time over *"each of the required papers"*, with *"no upper limit on the running time"*, on *"a Google Colab instance running on CPU-only mode"*. The group therefore benchmarks the **official crawl of all 20,000 IDs itself** rather than a sample. Each chunk of 500 IDs runs on Colab CPU-only under `/usr/bin/time -v` and the group's profiler (`src/utils/profiler.py`), which samples every second the resident memory of the crawler **and all its child processes** and walks the size of `data/` and `work/`. The [Performance](03-performance.ipynb) chapter aggregates the chunks: wall time is the sum over chunks, peak RAM and peak disk are the maxima, and average RAM is weighted by duration.

## Definition of success

- **A paper is crawled successfully** when it exists on arXiv and **every version** reached a final status `ok`, `no_tex` or `unavailable` with its `vN/` folder. A version without TeX counts as done, because the statement asks to keep an empty record instead of dropping the paper. This matches `papers_complete` in `run_summary.json` and the test `n_versions_ok == n_versions` in the statistics notebook.
- **The success rate of reference metadata** is the share of papers Semantic Scholar knows (`status = ok`). The notebook also reports the share of references whose metadata S2 could resolve (`s2_id` not null).

## Observations from the test runs (4 × 200 IDs, 19–20/10/2026, laptop)

These are not the official benchmark, which runs on Google Colab (CPU-only).

- After one resume, all four ranges reached 200/200 complete papers. 57 of 1,061 versions (5.4 %) have no TeX source: PDF or HTML only, or a 404 from arXiv.
- The most frequent errors were connections closed by arXiv in the middle of large downloads and HTTP 429 at peak hours; retries and resume handled both.
- Extraction takes 19 ms at the median (66 ms at p90), negligible next to the 3 s pace. The group therefore did not move extraction to a separate process; the part worth running in parallel is Semantic Scholar.
- Semantic Scholar: the 800 test papers needed 21 batch requests; they have 35.6 references on average, 49.9 % of which carry an arXiv ID.
