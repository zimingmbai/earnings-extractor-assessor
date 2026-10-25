# US market earnings watcher and assessor

Two Claude cloud routines share this repository. Every morning at 6:07 AM Singapore time the **watcher** lists
every US company that filed results with the SEC since its last run (the earnings radar). For the companies in
your watchlist (Alphabet, Amazon and Meta Platforms to start with), and for two more that it picks at random each
morning from the companies that have just reported, it reads the press release and writes down four headline
figures (revenue, operating income, net income and diluted earnings per share), the company's guidance, two to
four things management says and the release's tone, each with the exact words it comes from. At 6:37 AM the
**assessor** checks every figure against the press release and against the figures the company filed with the SEC,
builds a table of how the fundamentals changed from a year ago and from the previous quarter, judges whether
management's words match those numbers, and rates the watcher's work. Both write a dated brief, and a dashboard
on GitHub Pages shows the results.

A small GitHub Action in this repository, **SEC fetch**, asks the SEC for the data at 5:10 AM and 5:40 AM and keeps
the answers in `sec_cache/`. Claude's cloud is often not allowed to reach the SEC (it answers `CONNECT 403`), but it
can always reach GitHub, so the routines read the SEC's answers from this repository.

The reader is an equity analyst at a Singapore fund who covers these three companies. Before the 8:30 AM
morning meeting, the analyst needs their latest results, checked, and wants to know who else reported overnight.
The briefs report results and check them. They never recommend buying, selling or holding a share, and they are
not investment advice.

MGMT 6110, Problem Set 6. Please allow about an hour, as the step-by-step guide says, much of it waiting for runs and for GitHub Pages.

## Why two agents
The assessor is the first check on the watcher, and you are the second. It is the same thing you do in your own
self-assessment: one piece of work, checked against evidence by someone who did not do it. The assessor never
changes the watcher's figures. It only judges them, so you can see the figures and its verdicts side by side and
decide. The dashboard shows the assessor's scores under **Assessor agent's ratings**, ready for you to copy into
your self-assessment form.

## How it works
0. **SEC fetch, 5:10 AM and 5:40 AM (GitHub Actions).** `.github/workflows/sec-fetch.yml` runs
   `python3 tools/earnings.py fetch`. It makes exactly the requests the next watch and assess need (the radar, each
   watchlist company's filings list, any new press release, the company facts), trims the answers to the words the
   tool reads, and commits them to `sec_cache/` (`sec-fetch: <date> <time> · 24 of 24 answers`). It also starts by
   itself whenever you save `config.json`, and you can run it at any time from the **Actions** tab: **SEC fetch** →
   **Run workflow**. Until `config.json` holds your username and email, it fetches nothing and says so.
1. **Watcher, 6:07 AM.** `tools/earnings.py watch` reads the SEC's answers from `sec_cache/` when the fetch filled
   it in the last 20 hours (`cache_max_hours` in `config.json`), and asks the SEC directly only for anything the
   cache does not hold. The radar lists every 8-K with item 2.02 (results of operations) filed since the last run
   and keeps the new ones in `data/radar.json`. For each watchlist company, and for the two random picks from the
   radar (seeded by your GitHub username, so classmates get different companies), it finds the newest results,
   saves the press release (exhibit 99.1) as `sources/<CIK>-<accession>.txt`, and Claude writes the four figures,
   the guidance, what management says and the tone, each with its quote. `--save-extract` refuses any quote that
   is not in the saved text. Earnings call transcripts are not filed with the SEC, so what management says comes
   from the CEO and CFO commentary and the outlook in the press release.
2. **Assessor, 6:37 AM.** `tools/earnings.py assess` checks that each quote is in the saved text, compares each
   figure with the company's quarterly report (the 10-Q, from the SEC's XBRL company facts), builds the
   fundamentals table (revenue, operating income, net income, diluted EPS, operating margin and net margin, this
   quarter against a year ago and the previous quarter), and checks the radar count. Claude gives each figure a
   verdict (`confirmed`, `mismatch` or `cannot check`), judges each thing management says against the numbers
   (`matches`, `does not match` or `cannot check`) and whether the tone is supported, and rates the watcher's work
   from 1 to 5 on S1 Correct, S2 Complete and S3 Useful.
3. Each routine writes its brief in `briefs/`, records the run in `data/runs.json`, and pushes to `main`.
   `index.html` shows the latest figures with the verdicts as coloured chips, the assessor agent's ratings, a table
   of who reported since the last run with a filter box, both agents' runs on one timeline, and every brief.

## Set it up
The step-by-step guide shows every click. In short:
1. In Finder, press **Command-Shift-.** (full stop) to show hidden files, so that `.github` and `.nojekyll` are
   uploaded too. On GitHub, click **+** → **New repository**, name it `earnings-extractor-assessor`, choose
   **Public**, and click **Create repository**. Upload everything inside this folder, not the folder itself, and
   check that the file list shows `.github` and `.nojekyll`. If eLearn gives a template link, you may use **Use this
   template** → **Create a new repository** instead.
2. In your copy, edit `config.json`: your GitHub username in `github_username` and `dashboard_url`, and an email
   address in `contact_email`. The SEC asks every program that reads EDGAR to give one, and the fetch refuses to run
   without it. Please use your SMU or a personal address. It is visible in your public repository.
3. In **Settings** → **Pages**, choose **Deploy from a branch**, branch `main`, folder `/ (root)`, and **Save**.
   Your dashboard will be at `https://<your-username>.github.io/earnings-extractor-assessor/`. To see it with
   sample data before your first run, add `?data=_dev` to that address.
4. Saving `config.json` starts the SEC fetch by itself. Open the **Actions** tab: after about a minute its run shows a
   green tick, and the repository has a new commit that starts with `sec-fetch:`. If no run appears, click **SEC
   fetch** → **Run workflow** → **Run workflow**.
5. Give Claude access to the repository: open https://github.com/apps/claude, click **Install** (or **Configure**),
   choose **Only select repositories**, pick `earnings-extractor-assessor`, and click **Install** (or **Save**). Your
   routines copy the repository and push their work through Claude's GitHub App.
6. In the Claude desktop app, open the **Code** tab and click **Scheduled** in the sidebar (older versions call it
   **Routines**). Create two tasks with **Set up manually**:

| Setting | Watcher | Assessor |
|---|---|---|
| Name | `PS6: Earnings watcher` | `PS6: Earnings assessor` |
| Instructions | `Read PROMPT_WATCH.md and CLAUDE.md in this repository and do the job in PROMPT_WATCH.md. Push your changes to main.` | `Read PROMPT_ASSESS.md and CLAUDE.md in this repository and do the job in PROMPT_ASSESS.md. Push your changes to main.` |
| Repository | your copy of this repository | the same repository |
| Cloud environment | leave it as it is (the Default environment is fine; the SEC fetch does the network part) | the same |
| Trigger | **Schedule**, daily, **6:07 AM** | **Schedule**, daily, **6:37 AM** |
| Connectors | remove every connector | remove every connector |

7. Press **Run now** on the watcher and wait until its run has finished and GitHub shows a commit such as
   `earnings: 2026-10-26 · watch · 5 new`. Then press **Run now** on the assessor. Please read both runs, not only
   the green dot: a green run means only that nothing broke on Anthropic's side, and the job itself may still have
   failed. Run now is limited to 30 runs an hour for each task.

If the brief's Sources section says `sec_cache/` is old or empty, the SEC fetch did not run today: open the Actions
tab, read the latest **SEC fetch** run, fix what it says (usually `contact_email`), press **Run workflow**, and then
**Run now** on the watcher. If a Sources line says `blocked_by_routine_network`, the tool asked the SEC directly for
something the cache did not hold, and Claude's cloud refused it; the fix is the same.

## What I tested
When I tested this on the morning of Sunday 25 October 2026, from my Mac, with a test address in
`contact_email`:
- With `contact_email` still `YOUR_EMAIL_ADDRESS`, `watch` and `assess` refused to run and sent no request.
- The watch at 9:25 AM made 10 requests and took 3 seconds. The radar searched 23 and 24 October (US dates) and
  read 43 hits in one page: 37 different 8-Ks with item 2.02, all filed on Friday 23 October, none from the
  watchlist. Among them were American Express (AXP), SLB (SLB), Autoliv (ALV), Gentex (GNTX) and Booz Allen
  Hamilton (BAH). Several Federal Home Loan Banks and a private credit fund were on the list too, with no ticker.
- It found and saved the three press releases (exhibit 99.1): Alphabet's of Wednesday 22 July 2026
  (`googexhibit991q22026.htm`, 26,127 characters of text, headed "Alphabet Announces Second Quarter 2026
  Results"), Amazon's of Thursday 30 July 2026 (`amzn-20260630xex991.htm`, 41,015 characters, headed "AMAZON.COM
  ANNOUNCES SECOND QUARTER RESULTS") and Meta Platforms' of Wednesday 21 October 2026
  (`meta-09302026xexhibit991.htm`, 25,409 characters, headed "Meta Reports Third Quarter 2026 Results"). Meta's 8-K
  also covers items 1.01 and 8.01, but its exhibit 99.1 is still the results release. The agreement is exhibit
  10.1.
- I read the three releases and wrote the 12 figures and their quotes myself, as the watcher would.
  `--save-extract` accepted them. It refused the same file with one quote changed, named the figure and saved
  nothing.
- The assess at 9:26 AM made 3 requests (the company facts, 3 to 4 MB each) and took 1 second. All 12 figures
  matched the 10-Q exactly, and the radar check agreed (37 in the brief, 37 saved). One figure looked odd at first:
  Alphabet's net income for the June quarter, 112,193 USD millions, is larger than its operating income (40,770).
  The release gives the same figure. Other income that quarter was 97,983 USD millions, mostly gains on equity
  securities. The 10-Q figure covers 1 April to 30 June 2026 (91 days), not the half year, whose net income was
  174,771. Amazon's net income (62,647) is high for a similar reason. The assessor shows the dates of every filed
  figure, so you can see which period it compared.
- A second watch at 9:27 AM read Saturday 24 October again, found 0 new filings and said "no new results since"
  each company's date. In all, these tests sent 18 requests to the SEC, at least 0.25 seconds apart.
- I ran three mornings in a row with saved copies (`--offline --now`), a blocked host, an unreachable host, a
  damaged `data/radar.json`, and a brief whose radar count I changed by hand (the assessor said "They do not
  agree"). The dashboard worked on a laptop and at phone width, with the filter box and the watchlist rows.

The full run of each routine in Claude's cloud is the one step I could not do from my Mac, so please read your first
runs with extra care.

## What to expect
- **The timeline for Problem Set 6.** Set the task up by Monday 26 October. Your first Run now reads last week's
  results: on its first run the radar looks back seven days (`radar_first_run_days` in `config.json`), so it lists
  every company that reported in the previous week (366 from Monday 19 to Friday 23 October in my test), and the
  watcher reads two of them, picked at random, in full. Then the 6:07 AM run on Tuesday 27 October reads the
  companies that reported on Monday in the US, and the 6:37 AM assessor checks them. Wednesday's runs are the last
  before the deadline.
- If a company picked at random has no press release the tool can read (no exhibit 99.1, a PDF, almost no text),
  the tool tries the next one in your random order, up to four more, and names the skipped ones in the brief.
- In the results season (late January, April, July and October) the radar lists dozens of companies each weekday
  morning. On Monday mornings in Singapore it covers Saturday and Sunday in the US, which are usually empty. Banks,
  funds and the Federal Home Loan Banks file results too, so not every name has a ticker.
- The radar finds an 8-K through the words "Results of Operations and Financial Condition", the heading of item
  2.02, and keeps only filings whose items include 2.02. It reads at most 20 pages of 100 hits a run.
- Your watchlist companies report four times a year, so most mornings say "No new results" and "Nothing to assess"
  for them. The dashboard keeps showing their latest results.
- Results usually come out after the US market closes, which is about 4 AM to 5 AM in Singapore, and the 10-Q often
  follows a day later. So on the morning of new results the assessor will often say "cannot check" for every
  figure. It checks those results again each morning for up to 10 days (`recheck_days` in `config.json`) until the
  10-Q is filed.
- Figures for the December quarter are in the annual report (10-K), which gives figures for the whole year, so the
  assessor will usually say "cannot check" for them. That is a limit of the filing check, not a fault.
- The filing check allows 0.5 per cent, so a wrong last digit can still pass it. That is why the assessor also
  checks whether the quote holds the number, and why you remain the second check.
- A second run on the same day writes over that day's brief. GitHub keeps the earlier version in the history.

## Other companies
You may replace a company in `config.json` with another one. Use its CIK, which you can find on SEC EDGAR:
- Apple, CIK `320193`. Its year ends in late September, so its September quarter is in its 10-K and cannot be
  checked against a quarterly figure.
- NVIDIA, CIK `1045810`. Its year ends in late January.
- Netflix, CIK `1065280`. Some companies give their tables in thousands of dollars. The watcher converts them to
  millions.
- Microsoft, CIK `789019`. Its year ends on 30 June, so its June quarter sits in a 10-K and the assessor may not
  find a quarterly filing figure for it.

If a company names its press release file differently, the tool reads the filing's index page to find exhibit
99.1, which takes one more request.

## Files
| File | What it is |
|---|---|
| `PROMPT_WATCH.md` | The watcher's job, step by step (read by every watcher run). |
| `PROMPT_ASSESS.md` | The assessor's job, step by step (read by every assessor run). |
| `CLAUDE.md` | The house rules both agents follow. |
| `config.json` | Your username, dashboard address, contact email, the companies, the SEC addresses and the check settings. |
| `tools/earnings.py` | The tool (Python 3.9 or later, standard library only): `fetch` (GitHub only), `watch`, `assess`, `--save-extract`, `--save-assess`, `--record`, `--check`. |
| `tools/sample_data/` | Trimmed copies of the SEC's answers from my test on 25 October 2026 (the radar, the filings lists, the filing indexes, the three press releases and the company facts), for `--offline` tests. |
| `data/radar.json` | Every results filing the radar has seen in the last 120 days, keyed by accession. Written only by the tool. |
| `data/extractions.json` | Every result the watcher saved: the figures, units and quotes. Written only by the tool. |
| `data/assessments.json` | Every verdict and rating the assessor gave. Written only by the tool. |
| `data/runs.json` | One entry per run of either agent. Written only by the tool. |
| `sources/` | The saved press releases, as plain text. The assessor checks quotes against them. |
| `briefs/` | One watch brief and one assessment brief per day. |
| `index.html` | The dashboard. |
| `.nojekyll` | Tells GitHub Pages to serve the files as they are. |
| `.github/workflows/sec-fetch.yml` | The SEC fetch on GitHub Actions, at 5:10 AM and 5:40 AM Singapore time and on demand. |
| `sec_cache/` | The SEC's answers from the latest fetch, trimmed, with `manifest.json` (when, how many answered). Written only by the SEC fetch. |
| `_dev/` | Sample data from my test, for previewing the dashboard with `?data=_dev`, and the script that made `tools/sample_data/`. The routines do not use it. The quotes are real, and one Meta Platforms figure is wrong on purpose to show a mismatch. `_dev/README.md` says which. |

## Run it on your own computer

    python3 tools/earnings.py --check
    python3 tools/earnings.py watch --offline --now 2026-10-25T06:07
    python3 tools/earnings.py watch
    python3 tools/earnings.py assess

The first line checks the data files. The second reads the saved copies in `tools/sample_data/` instead of the
network, so it works before you fill in `contact_email`. It saves three texts in `sources/`, so please delete them
before you commit. The last two make the same requests as the routines and need your `contact_email`. Please run
them sparingly, as the SEC asks. To see the dashboard, run `python3 -m http.server 8000` in this folder and open
`http://localhost:8000/`.
