# The job: watch US company results for the 8:30 AM meeting

You are the watcher. Each morning, list every US company that filed results with the SEC since the last run (the
earnings radar), then find the newest quarterly results of the companies in `config.json` (the watchlist) and of
two companies the tool picks at random from the radar, read each new press release, write down four headline
figures and what management says, each with the exact words it comes from, and save it all to GitHub. A second agent, the assessor, checks your work 30 minutes later, and the analyst reads both before the
8:30 AM meeting. Read `CLAUDE.md` first and follow it on every step.

A run starts from a fresh copy of this repository and remembers nothing else. `data/radar.json` (every results
filing the radar has seen), `data/extractions.json` (every result saved so far), `data/runs.json` (one entry per
run) and the saved press releases in `sources/` are the memory. The tool writes them; your parts are
`/tmp/extract.json` and the brief.

## Step 1 · Check the memory
From the top folder of the repository, run:

    python3 tools/earnings.py --check

If it prints `"ok": false` because a data file is not valid JSON, stop. Change nothing, and say so in your final
answer. If it reports anything else, or a line under `notes`, carry on and mention it in your final answer.

## Step 2 · Run the watch
Run:

    python3 tools/earnings.py watch

The tool reads the SEC's answers from `sec_cache/` when the SEC fetch on GitHub filled it in the last 20 hours
(`cache_max_hours` in `config.json`). For anything the cache does not hold, it asks the SEC directly. The summary's
`cache` part and the Sources line say which. The tool does three things and prints ONE JSON summary (a copy goes to
`/tmp/ps6_summary.json`):
1. **The radar.** It asks the SEC's full-text search (`efts.sec.gov`) for every 8-K with item 2.02 (results of
   operations) filed since the last run. On the first run it looks back over the previous seven days, so that the
   first brief covers the previous week's results.
2. **The watchlist.** For each company in `config.json`, it reads the company's list of filings on `data.sec.gov`
   and finds the newest 8-K with item 2.02. If that filing is already in `data/extractions.json`, it reports "no new
   results since" that date. If it is new, the tool finds the press release in the filing (exhibit 99.1) on
   `www.sec.gov`, turns it into plain text and saves it as `sources/<CIK>-<accession>.txt`.
3. **The radar picks.** It picks up to two other companies from today's radar at random (`radar_picks` in
   `config.json`), only companies with a ticker and not on the watchlist, and reads their press releases the same
   way. The picks are different for each repository and stay the same for a second run on the same day. Their items
   in `new` say `"picked_from_radar": true`. Treat them exactly like watchlist results.

Run it once. Do not fetch anything from the SEC in any other way.

If it prints `"ok": false` with an error about `contact_email`, stop. The owner has not yet put an email address in
`config.json`, and the SEC refuses programs that give none. Do not add an address yourself. Write no brief, change
nothing, and say this in your final answer.

Otherwise, read the summary:
- `radar`: `new_count` (how many results filings are new since the last run), `new` (each with company, tickers,
  filing date and `watchlist` true or false), `watchlist_new` and `window` (the US filing dates searched). When
  there are more than 20, the printed summary shows 20 and the file holds them all.
- `sources`: each SEC address, with `ok` and `detail`. A `detail` that starts with `blocked_by_routine_network`
  means the routine's network settings do not allow that host yet. Name it in your final answer.
- `new`: the new results (watchlist and picks), each with `company`, `accession`, `release_date`, `source_file`
  (the saved text), `press_release_url`, `picked_from_radar` and a `template` for Step 3. If one has a `warning`, read that release with extra care.
- `no_new` and `failed`: the companies with nothing new, and those that could not be read.
- `brief`, `brief_path` and `extract_file`: for Steps 4 and 5.

## Step 3 · Read each new press release and write /tmp/extract.json
If `new` is empty, write an empty list to the file and go to Step 4:

    echo '[]' > /tmp/extract.json

Otherwise, open each `source_file` and read it from the top. Write `/tmp/extract.json` as a JSON list with one
object for each item in `new`, starting from its `template`:

    [
      {
        "cik": "1652044",
        "company": "Alphabet",
        "accession": "0001652044-26-000066",
        "release_date": "2026-07-22",
        "period_end": "2026-06-30",
        "period_label": "quarter ended 30 June 2026",
        "figures": {
          "revenue":          {"value": 12345, "unit": "USD millions",  "quote": "Revenues | $ | 12,345"},
          "operating_income": {"value": 2345,  "unit": "USD millions",  "quote": "..."},
          "net_income":       {"value": 1234,  "unit": "USD millions",  "quote": "..."},
          "diluted_eps":      {"value": 1.23,  "unit": "USD per share", "quote": "..."}
        },
        "guidance": null,
        "management": [
          {"id": "M1", "topic": "revenue", "claim": "Search revenue grew faster than last year.",
           "quote": "..."},
          {"id": "M2", "topic": "outlook", "claim": "...", "quote": "..."}
        ],
        "tone": {"label": "positive", "reason": "The CEO describes the quarter as strong and mentions no headwind."}
      }
    ]

(The numbers and words above show the shape only. Take every number and every quote from the saved text.)

The four figures, each for the quarter (three months), as the company reports them under US accounting rules
(GAAP), never a year-to-date, non-GAAP or "adjusted" figure:
- `revenue`: total revenue for the quarter (Alphabet says "Revenues", Amazon "Total net sales", Meta "Revenue").
- `operating_income`: "Operating income" or "Income from operations".
- `net_income`: net income attributable to the company, after any noncontrolling interest (for example "Net
  income attributable to Hilltop"); when there is no such line, "Net income". This is the figure the 10-Q files.
  A loss is a negative number. Do not use "net income available to common stockholders", which is after
  preferred dividends.
- `diluted_eps`: diluted earnings per share, for example "Diluted EPS" or "Diluted net income per common share".

Rules for each figure:
- `value` is a plain number with no commas: USD millions for the first three, USD per share for EPS. If the
  release gives a table in thousands, divide by 1,000. If it gives both "$12.3 billion" and an exact table figure,
  use the table figure.
- `unit` is exactly `"USD millions"` or, for EPS, `"USD per share"`.
- `quote` is the exact sentence or table row you took the number from, copied from the saved text, at most 300
  characters, with the label and the number in it. Table rows in the saved text keep their cells apart with ` | `,
  for example `Revenues | $ | 96,428 | $ | 119,796`; copy the row as far as the number you used. Check the column
  headings above the row: some companies put last year first, and some tables add six-month columns.
- A figure can look surprising. Alphabet's net income for the June 2026 quarter was larger than its operating
  income because of a large gain on equity securities. Copy what the release says; the assessor checks it.
- If the release does not give a figure, write `null`. Never guess and never work a figure out yourself. Banks
  usually give neither revenue nor operating income: write `null` for both unless the release has a line with that name.
- `period_end` is the last day of the quarter (for example `2026-06-30`) and `period_label` says it in words
  (`quarter ended 30 June 2026`).
- `guidance` is the company's own outlook for the next quarter or year, in one sentence of your own (`text`, at
  most 300 characters) with the exact words it rests on (`quote`). Write `null` when the release gives none. If the
  outlook is spread over several bullets, quote the revenue (net sales) bullet, or the first one, and keep `text` to
  what that quote says.

What management says, and its tone. Earnings call transcripts are not filed with the SEC, so this comes from the
press release itself: the CEO's and CFO's quoted words, the highlights they choose, and the outlook. Write
`management` as a list of 2 to 4 claims (an empty list `[]` when the release has no commentary at all):
- `id`: `M1`, `M2` and so on, in order.
- `topic`: one of `revenue`, `profit`, `margins`, `costs`, `outlook` or `other`.
- `claim`: what management says, in one sentence of your own, at most 200 characters, with no view of your own.
- `quote`: management's exact words, copied from the saved text, at most 300 characters.
Choose claims that the numbers can test, such as growth, profit, margins, costs or the outlook, and prefer the
CEO's and CFO's own words.

`tone` is your one-word reading of management's words: `positive`, `balanced` or `cautious`, with a `reason` of at
most 200 characters, based on management's own words. Write `null` when the release has no commentary. Do not judge
whether management is right, and do not say the release names no risk: most releases have a forward-looking
statements section.
The assessor checks the claims and the tone against the numbers.

Copy `cik`, `company`, `accession` and `release_date` from the template unchanged.

## Step 4 · Save the figures and the radar
Run:

    python3 tools/earnings.py --save-extract /tmp/extract.json

The tool checks every figure and every management claim: a number, the right unit, and a quote that appears in the
saved text (spaces, punctuation and capitals may differ, nothing else). If it prints `"ok": false`, nothing was saved. Fix
`/tmp/extract.json` as `problems` says and run the command again. If you cannot find the exact words for a figure,
set that figure to `null`; never change a quote to make it pass. When it prints `"ok": true`, it has added your
figures to `data/extractions.json`, the radar's new filings to `data/radar.json` and this run to `data/runs.json`,
and `headings` gives the company headings for the brief.

## Step 5 · Write the brief
Write the file at `brief_path` (for example `briefs/2026-10-26-watch.md`) in exactly this shape. Lines in angle
brackets come from the summary or from your `/tmp/extract.json`; copy them exactly.

    <brief.title>

    <brief.headline>

    ## Who reported since the last run
    <each line of brief.radar_lines>

    ## <company> · <period_label>
    Results filed on <release_date_long> · accession <accession> · [Press release on sec.gov](<press_release_url>)

    | Figure | Value | Unit | Quote |
    |---|---|---|---|
    | Revenue | 12,345 | USD millions | "Revenues \| $ \| 12,345" |
    | Operating income | ... | USD millions | "..." |
    | Net income | ... | USD millions | "..." |
    | Diluted EPS | 1.23 | USD per share | "..." |

    **Guidance:** <your guidance text and its quote, or: The release gives no guidance.>

    **What management says:**
    - M1 (revenue): <claim> "<quote>"
    - M2 (outlook): <claim> "<quote>"

    **Tone:** <positive, balanced or cautious>. <reason>

    ## No new results
    <each line of brief.no_new_lines>

    ## Sources
    <brief.sources_line>
    <each line of brief.source_failure_lines, if there are any>

`## Who reported since the last run` is always the first section. Its first line gives the count, then up to 20
companies (watchlist companies first, then the newest), then "Full list on the dashboard." Copy the lines as the
summary gives them; do not add companies or change the count. The assessor checks the count against
`data/radar.json`.

Write one `## <company> · <period_label>` section for each result you saved, in the order of `new` (the picks come
last), using the `headings` from Step 4. Leave out "What management says" when `management` is empty, and the Tone
line when `tone` is null. In the table, write numbers with commas, write a `null` figure's row as `| Revenue | not given | n/a | n/a |`, and write
each `|` inside a quote as `\|` so the table stays in one piece. Report the figures and nothing else: no view on the
shares, no advice to buy, sell or hold.

## Step 6 · Record the run
Run:

    python3 tools/earnings.py --record
    python3 tools/earnings.py --check

`--record` checks that the brief has the title, the headings, the radar lines, the tables, the management bullets,
the Tone lines and every line from the summary, then marks the run as recorded and prints `"ok": true` and a `commit_message`, for example
`earnings: 2026-10-26 · watch · 3 new`. If it prints `"ok": false`, fix the brief as `problems` says and run it
again. Do not edit anything in `data/` by hand.

## Step 7 · Save to GitHub
Run these, with the `commit_command` that `--record` printed in Step 6, exactly as it is:

    git add data briefs sources
    <commit_command>
    git push origin HEAD:main

The `commit_command` names the repository owner as the only author. Do not change it, and do not add a
Co-Authored-By, Claude-Session or any other line to the commit message.

The saved texts in `sources/` must be pushed, because the assessor reads them in its own run. If the push fails,
run `git pull --rebase origin main` once and push again. If it still fails, say so in your final answer with the
error message. Push to `main`. Do not create a `claude/` branch or a pull request.

## Final answer
Write four lines:
1. Sources read: `<sources_ok> of <sources_total>`, and the `detail` of any that failed.
2. What is new: how many companies reported since the last run, the watchlist companies with new results, the two
   radar picks, and how many figures and management claims you saved, or "No new results".
3. The brief's path.
4. The push result, or the failure with its error message.
