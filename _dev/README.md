# Sample data for the dashboard

This folder lets you see the dashboard before your own first run. Add `?data=_dev` to your dashboard's address,
for example `https://<your-username>.github.io/earnings-extractor-assessor/?data=_dev`. The routines never read
this folder.

## Where it comes from
I made it on Sunday 25 October 2026 from the real SEC answers I saved that morning (`tools/sample_data/`), with
`--offline --now 2026-10-25T06:07` for the watcher and `--now 2026-10-25T06:37` for the assessor:

- `data/radar.json` holds the 37 results filings (8-K, item 2.02) that the radar found for 23 and 24 October 2026.
- `data/extractions.json` holds the figures, two management claims and a tone for Alphabet, Amazon and Meta
  Platforms. Every quote is copied word for word from the companies' real press releases.
- `data/assessments.json`, `data/runs.json` and `briefs/` hold what the two agents saved and wrote that morning.

## One figure is wrong on purpose
**Meta Platforms' revenue says 61,601 USD millions. The press release and the 10-Q both say 64,601.** I changed
one digit so that you can see what a mismatch looks like: a red chip on the dashboard, the assessor's reason, a
lower S1 and S3 rating, and a line under "What the analyst should check by hand". The quote next to the figure is
the real one ("Revenue | $ | 64,601"), which is how the assessor caught it. The other 11 figures are correct.

## One claim does not match the numbers
The watcher also saved what management says, with quotes from the releases, and a tone for each company. The
assessor judged each claim against the fundamentals. **Meta Platforms, claim M1: "Our investments are paying off,
the core business is strong".** The quote is real, but operating income fell 36.8% on a year ago (12,988 against
20,535 USD millions), mostly because of a $9.9 billion legal charge, so the assessor says "does not match", and the
watcher's "positive" tone is "not supported". Nothing was changed by hand here: the claim is management's own, and
the numbers are the filed ones. It shows what a catch of words against numbers looks like.

## The script
`make_sample_data.py` is for the teaching team. It trims a folder of saved SEC answers into `tools/sample_data/`
and checks that the trimmed press releases still give exactly the same text.
