# The job: check the watcher's work before the 8:30 AM meeting

You are the assessor. Thirty minutes after the watcher has run, check every figure it saved: against the words of
the press release, and against the figures the company filed with the SEC in its quarterly report (10-Q). Then
check what management says against the company's fundamentals: how revenue, profit and margins changed on a year
ago and on the previous quarter. Check the count in the watcher's radar too. Then rate the watcher's work and save your verdicts to GitHub. You judge the
watcher's work; you never change it. Read `CLAUDE.md` first and follow it on every step.

A run starts from a fresh copy of this repository and remembers nothing else. `data/extractions.json` (the
watcher's figures), `data/radar.json` (the radar's filings), `data/assessments.json` (every verdict so far),
`data/runs.json` and the saved press releases in `sources/` are the memory. The tool writes the data files; your
parts are `/tmp/assess.json` and the brief.

## Step 1 · Check the memory
From the top folder of the repository, run:

    python3 tools/earnings.py --check

If it prints `"ok": false` because a data file is not valid JSON, stop. Change nothing, and say so in your final
answer. If it reports anything else, or a line under `notes`, carry on and mention it in your final answer.

## Step 2 · Collect the facts
Run:

    python3 tools/earnings.py assess

For every extraction not yet assessed, the tool does three checks, builds the fundamentals, checks the radar count,
and prints ONE JSON summary (a copy goes to `/tmp/ps6_summary.json`). It reads the SEC's answers from `sec_cache/`
when the SEC fetch on GitHub filled it in the last 20 hours (`cache_max_hours` in `config.json`), and otherwise asks
the SEC directly. The summary's `cache` part and the Sources line say which. It reads each company's filed figures once, from `data.sec.gov`.
Run it once. Do not fetch anything from the SEC in any other way. The tool never changes `data/extractions.json`.

If it prints `"ok": false` with an error about `contact_email`, stop. Do not add an address yourself. Write no
brief, change nothing, and say in your final answer that the owner must put an email address in `config.json`.

An extraction is listed again, marked `"recheck": true`, when the 10-Q was not yet filed at the last check and the
results came out in the last 10 days, or the quarter ended less than 50 days ago. Large companies often file the 10-Q a
day after the press release; smaller ones up to 45 days after the quarter ends.

Read the summary:
- `nothing_to_assess`: if it holds a sentence, there are no figures to check today. Go to Step 3 and save an empty
  list. You still write a brief with the radar check.
- `to_assess`: one item per extraction, with `company`, `heading`, `source_file` and, under `figures`, the facts
  for each of the four figures:
  - `extracted` and `quote`: what the watcher wrote.
  - `quote_found`: whether the quote is in the saved press release.
  - `number_in_quote`: whether the quote holds the extracted number (allowing for rounding, so "$12.3 billion"
    counts for 12,345 USD millions).
  - `filed`, `filed_period`, `difference` and `match`: the figure from the 10-Q, the three months it covers, how
    far apart the two are, and whether they agree (within 0.5 per cent, or the same to the cent for EPS). `match`
    is `null` when no filed figure exists yet.
  - `note` and `allowed_verdicts`: what the facts allow you to say.
- `missing`: the figures the watcher left empty.
- `fundamentals`: one row each for revenue, operating income, net income, diluted EPS, operating margin and net
  margin: this quarter (the 10-Q figure, or the watcher's figure until the 10-Q is filed, as `this_quarter_from`
  says), the same quarter a year ago, the previous quarter, and the changes (per cent, or percentage points for the
  margins). `fundamentals_lines` holds the same rows as a table for your brief. "not filed as a quarter" means the
  SEC holds no three-month figure for that period, as is usual for a December quarter, or, for a bank, that the
  company files no revenue or operating income at all. "n.m." means a per cent change is not meaningful because the
  base is a loss or the result turned into one; compare the amounts instead. A quote from a table in USD thousands
  holds the number when it equals the value times 1,000 (24,299 thousand is 24.299 million); that is not a mismatch.
- `claims`: what management says, as the watcher saved it (`id`, `topic`, `claim`, `quote`), with `quote_found`
  and the fundamentals rows that test it (`numbers`). `tone` is the watcher's reading of the tone, or null.
- `picked_from_radar`: true for a company the watcher picked at random from the radar. Check it like any other.
- `radar_check`: the count in the newest watch brief (`brief_says`), the number of new radar entries the tool
  saved in that run (`saved_for_run`), whether they agree (`match`), and a `line` for your brief.
- `sources`: each SEC address, with `ok` and `detail`.

## Step 3 · Judge and rate, then write /tmp/assess.json
For each figure, give one verdict and a one-line reason that quotes the numbers:
- `confirmed`: the quote is in the saved text, it holds the number, and the 10-Q agrees (`match` is true).
- `mismatch`: the 10-Q disagrees, the quote is not in the saved text, or the quote does not hold the number.
  Say what differs, with both numbers.
- `cannot check`: no filed figure exists yet, the filed figures could not be read, or the watcher left the
  figure empty. Say which.

When `quote_found` or `number_in_quote` is false, open the `source_file` and read the lines around the quote
before you decide, so that your reason is exact. Your verdict must be one of `allowed_verdicts`; the tool refuses
any other.

Then judge each management claim against the fundamentals, with a one-line reason that quotes the numbers:
- `matches`: the numbers bear the claim out, for example "growth accelerated" and revenue grew faster on a year ago
  than in the previous quarter.
- `does not match`: the numbers point the other way, or the claim leaves out a change that a reader would need, for
  example "demand accelerated" while revenue growth slowed from 12% to 5% on a year ago. Also when `quote_found` is
  false.
- Judge on the reported fundamentals first. When the release itself puts a number on a one-off item (a legal charge,
  a gain on investments) and gives the figure without it, you may also judge the claim on that figure; say which you
  used and give both. You may test a claim against the release's own tables as well as the fundamentals; say which.
  Use `cannot check` only when neither can test it. If the reported figure and the figure without the one-off point
  opposite ways, give the verdict on the reported figure, unless the claim itself is about the figure without it (it
  says adjusted or excluding, or names the item). Give both numbers in the reason either way.
- `cannot check`: the fundamentals cannot test it, for example a claim about a product, or a figure not filed as a
  quarter.
An outlook claim is about the future, so judge whether it is consistent with the latest trend, and say so.
Then judge the watcher's `tone`: `supported` when the fundamentals bear it out, `not supported` when they do not.
Keep every reason, for figures, claims, tone and ratings, to 300 characters or fewer; the tool refuses longer ones.
Judge only whether management's words fit the numbers. Never say whether the shares are worth buying.

Then rate the watcher's work on each extraction, from 1 to 5, with a one-line reason each. Students copy these
ratings into their self-assessment form, so make each reason specific:
- **S1 Correct.** Are the figures right? 5 when every figure that could be checked is confirmed; 3 when one is a
  mismatch that a careful reader would catch; 1 when the headline figures are wrong. When no figure can be checked
  against a 10-Q yet, score S1 on the quotes: 5 when every quote is in the release and holds its number, and say that
  the 10-Q check is still to come.
- **S2 Complete.** Are all four figures there, and the guidance when the release gives one? Take off one point for
  each figure the release gives but the watcher left empty. A figure the release does not give is not a fault.
- **S3 Useful.** Could the analyst act on the extract before 8:30 AM without opening the release? 5 when it can be
  used as it stands; 3 when a figure must be checked by hand first; 1 when it cannot be used.

Write `/tmp/assess.json`, one object for each item in `to_assess`, starting from its `template`:

    [
      {
        "accession": "0000000000-26-000000",
        "verdicts": {
          "revenue":          {"verdict": "confirmed", "reason": "Matches the 10-Q (12,345) and the quote holds the number."},
          "operating_income": {"verdict": "confirmed", "reason": "..."},
          "net_income":       {"verdict": "mismatch",  "reason": "The extract says 1,284 but its quote and the 10-Q say 1,234."},
          "diluted_eps":      {"verdict": "cannot check", "reason": "..."}
        },
        "claims": {
          "M1": {"verdict": "matches", "reason": "Revenue rose 24.2% on a year ago, faster than the 9.0% on the previous quarter."},
          "M2": {"verdict": "does not match", "reason": "..."}
        },
        "tone": {"verdict": "supported", "reason": "..."},
        "ratings": {
          "S1": {"score": 3, "reason": "..."},
          "S2": {"score": 5, "reason": "..."},
          "S3": {"score": 3, "reason": "..."}
        }
      }
    ]

(The numbers above show the shape only.) Give `claims` one entry for each claim in `claims` (an empty object `{}`
when there are none), and `tone` only when the watcher gave one (else `null`). If there is nothing to assess, write
an empty list:

    echo '[]' > /tmp/assess.json

## Step 4 · Save the verdicts
Run:

    python3 tools/earnings.py --save-assess /tmp/assess.json

If it prints `"ok": false`, nothing was saved. Fix `/tmp/assess.json` as `problems` says and run it again. When it
prints `"ok": true`, it has added your verdicts to `data/assessments.json` and this run to `data/runs.json`. It
also prints the `headline` and the `headings` for the brief. If there was nothing to assess, it still records the
run.

## Step 5 · Write the brief
Write the file at `brief_path` (for example `briefs/2026-10-26-assess.md`) in exactly this shape. Lines in angle
brackets come from the summary, from Step 4 or from your `/tmp/assess.json`.

    <brief.title>

    <headline from Step 4>

    ## <company> · <period_label>
    Results filed on <release_date_long> · accession <accession> · [Press release on sec.gov](<press_release_url>)

    | Figure | Extracted | Filed with the SEC | Verdict | Reason |
    |---|---|---|---|---|
    | Revenue | 12,345 USD millions | 12,345 USD millions (10-Q, 2026-07-23) | confirmed | <reason> |
    | Operating income | ... | ... | ... | ... |
    | Net income | ... | ... | ... | ... |
    | Diluted EPS | ... | ... | ... | ... |

    **Fundamentals:**
    <each line of brief.fundamentals_lines for this heading>

    **Management's words against the numbers:**
    | Claim | Verdict | Reason |
    |---|---|---|
    | M1 (revenue): <claim> | matches | <reason> |

    **Tone:** the watcher says <label>; <supported or not supported>. <reason>

    - **S1 Correct:** <score> of 5. <reason>
    - **S2 Complete:** <score> of 5. <reason>
    - **S3 Useful:** <score> of 5. <reason>

    ## Radar check
    <brief.radar_line>

    ## What the analyst should check by hand
    <one line for each mismatch and each figure that cannot be checked: what to open and what to look for>

    ## Sources
    <brief.sources_line>
    <each line of brief.source_failure_lines, if there are any>

Write one company section for each item in `to_assess`, using the `headings` from Step 4. Copy the fundamentals
lines exactly. Leave out the management table when there are no claims, and the Tone line when `tone` is null. Add a
line under "What the analyst should check by hand" for each claim that does not match. In "Filed with the SEC",
write `not filed yet` when there is no filed figure. If the radar check says "They do not agree", add a line under
"What the analyst should check by hand" saying so. When every figure is confirmed and the radar count agrees, the
check-by-hand section says `- Nothing: every figure was confirmed against the 10-Q.` When there was nothing to
assess, leave out the company sections and write `- Nothing new to check today.` there. Write each `|` inside a
reason as `\|`. Report and check the figures and nothing else: no view on the shares, no advice to buy, sell or
hold.

## Step 6 · Record the run
Run:

    python3 tools/earnings.py --record
    python3 tools/earnings.py --check

`--record` checks the brief's title, headings, tables, fundamentals lines, the management table and Tone line,
ratings, the radar line and the lines from the summary, then
prints `"ok": true` and a `commit_message`, for example `earnings: 2026-10-26 · assess · 3 checked`. If it prints
`"ok": false`, fix the brief as `problems` says and run it again. Do not edit anything in `data/` by hand.

## Step 7 · Save to GitHub
The watcher may have pushed since your copy was made, so take its work first. Run these, with the `commit_command`
that `--record` printed in Step 6, exactly as it is:

    git add data briefs
    <commit_command>
    git pull --rebase origin main
    git push origin HEAD:main

The `commit_command` names the repository owner as the only author. Do not change it, and do not add a
Co-Authored-By, Claude-Session or any other line to the commit message. If the push still fails, say so in your
final answer with the error message. Push to `main`. Do not create a `claude/` branch or a pull request.

## Final answer
Write four lines:
1. Sources read: `<sources_ok> of <sources_total>`, and the `detail` of any that failed.
2. What was checked: the headline from Step 4, how many management claims match the numbers, and whether the radar
   count agreed.
3. The brief's path.
4. The push result, or the failure with its error message.
