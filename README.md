# Agentic trade execution analysis: eval archive

Everything from the agent eval behind the blog post
[Agentic trade execution analysis: markouts, TCA and what agents find](https://questdb.com/blog/agentic-trade-execution-analysis-markouts-tca/).

Start with `NOTES.md`: setup, ground truth, every run's scorecard, the
follow-up experiment.

**Spoiler warning:** `reference/answer_key.json` and the ground truth in
`NOTES.md` give away every planted problem. If you rerun the eval, run the
agent with web access off, or it may find this repo and read the answers.

## Reproduce a run from scratch

This folder has the harness, the prompts and the skill version used. The data
generator comes from its public GitHub repo, pinned to the exact commit.

### 1. Prerequisites

- Docker Desktop, and **about 15 GB of free disk**. The data below uses 9.6 GB
  inside the container, and Docker Desktop only returns space to macOS after
  you quit it. A full-scale load (`SCALE=1`, five days) is 19 GB.
- Python 3.12, Node.js (for `npx`), and Chrome.
- Claude Code and Codex CLIs, logged in. Subscriptions are fine; headless runs
  draw on the plan's usage limits.
- Run from a folder where none of your own hooks or global `AGENTS.md` rules
  load extra files; anything they pull in contaminates a run.

### 2. Start QuestDB

```bash
docker run -d --name eqeval-questdb -p 19000:9000 questdb/questdb:10.2.0
curl -sf --retry 30 --retry-delay 1 --retry-all-errors -o /dev/null "http://127.0.0.1:19000/exec?query=SELECT+1"
```

Port 19000 keeps clear of a local QuestDB on 9000. The runs used QuestDB
10.2.0 and MCP server `@questdb/mcp-server-questdb@0.5.0`.

### 3. Generate the data

The generator is the `energy-trading` folder of
[javier/commodities-data-generator](https://github.com/javier/commodities-data-generator),
pinned to commit `0113e8956a3be15a7f9a84ca6a41cce6187cff5f` (2026-10-14,
"Merge pull request #5 from javier/jv/energy_trading"), the version every run
used.

```bash
mkdir work && cd work
git clone https://github.com/javier/commodities-data-generator.git
git -C commodities-data-generator checkout 0113e8956a3be15a7f9a84ca6a41cce6187cff5f
python3 -m venv venv
venv/bin/pip install -q -r ../generator/requirements-frozen.txt
HOST=127.0.0.1:19000 SCALE=0.5 START_TS=2026-11-10T00:00:00Z DEMO_DAY=2026-11-11 \
  PY="$PWD/venv/bin/python" commodities-data-generator/energy-trading/energy_backfill.sh
```

To try a newer generator, skip the `checkout` and use the repo's own
`energy-trading/requirements.txt`, but expect the planted storyline and the
ground truth in `NOTES.md` to differ.

What the original load used, and what to change for a new one:

- **Demo day** `DEMO_DAY`: the weekday the planted storyline is on (2026-11-11,
  a Wednesday). The last planted event is at 11:15 UTC, so load after that day
  is over, or on a later day, so the whole storyline exists.
- **History** `START_TS`: one day before the demo day, so agents can compare
  with the previous day. `END_TS` defaults to now (the original load ran to
  2026-11-12 09:20 UTC).
- **Scale** `SCALE=0.5`: about 1,700 fills a day and 25M quotes a weekday.
  Lower scales thin out the fills until the counterparty and book effects stop
  being statistically visible.
- **Seed** 7, the script's default. Planted events, sizes and counterparties
  are deterministic for a given seed and demo day.
- **Prices are anchored to live Yahoo Finance front-month levels** at load
  time, so absolute prices and some magnitudes will differ from the post. For
  fully repeatable prices, add `--static_anchors true` to the generator command
  inside `energy_backfill.sh` (the script doesn't pass extra arguments through).
- The backfill also rewrites
  `commodities-data-generator/energy-trading/energy_demo_queries.sql` with the
  demo day's dates; `reference/energy_demo_queries.dated-2026-11-11.sql` is the
  original run's version.

### 4. Hide the answer key

```bash
python3 ../harness/hide_answer_key.py --drop
```

It saves `energy_demo_events` to `answer_key.json` in the current folder and
drops the table, so no agent can read it. Do this before any agent connects.
Optionally run `python3 ../harness/disk_guard.py` in the background: it stops
the container if free disk falls below 20 GiB.

Ground truth beyond the answer key table (the counterparty types, the crude
book's foresight, the gasoil spread cost) comes from the generator code, not
its README, which has the counterparty labels backwards. `NOTES.md` lists all
13 planted effects and how each was checked.

### 5. Edit the prompt's date

`harness/prompt.txt` names the session ("yesterday's session, Wednesday 11
November 2026"). Change it to your demo day.

### 6. Run Claude Code

Each run gets its own folder (with the skill as a project skill) and its own
console address, so notebooks from earlier runs stay invisible to it. Any
`<name>.localhost` resolves to your machine in Chrome.

```bash
mkdir -p runs/claude1/.claude/skills
cp -R ../skill-used/questdb-0e6ba28 runs/claude1/.claude/skills/questdb
sed 's#final1.localhost#claude1.localhost#; s#final1.log#claude1.log#' \
  ../harness/mcp-final1.json > ../harness/mcp-claude1.json
MCP_CONFIG=mcp-claude1.json ../harness/run.sh "$PWD/runs/claude1" "$PWD/runs/claude1.jsonl"
```

- A pairing tab opens in your browser: click **Connect** with **Read**
  permission. Only one tab can pair with a server. If you want to pair from a
  different tab, close the auto-opened one without connecting.
- `MODEL=claude-fable-5-1` runs the frontier model; the default was Opus 5.5.
- `--setting-sources project --strict-mcp-config` keeps your `CLAUDE.md`,
  memories, hooks and other MCP servers out. `harness/extra/smoke.sh <run_dir>`
  is the check that proved it (it asks a session what it can see).

### 7. Run Codex

```bash
cp -R ../skill-used/questdb-0e6ba28 ~/.agents/skills/questdb   # or: npx skills add questdb/skills
mkdir -p runs/codex1
CODEX_MODEL=gpt-6-astra ../harness/run-codex.sh "$PWD/runs/codex1" "$PWD/runs/codex1.jsonl" http://codex1.localhost:19000
```

- Make sure there's no old copy in `~/.codex/skills/questdb`: it can shadow
  the one in `~/.agents/skills`.
- The script assumes `~/.codex/config.toml` already defines
  `[mcp_servers.questdb]` (`command = "npx"`,
  `args = ["-y", "@questdb/mcp-server-questdb@0.5.0"]`). It only overrides the
  console address and log path, pre-approves the server's tools (headless
  `codex exec` refuses every MCP call otherwise), and turns off the browser
  and computer-use plugins.
- Leave `CODEX_MODEL` unset for the default (gpt-6.1-sol in the original runs,
  medium reasoning effort from the user config).

### 8. Follow-up prompts (optional)

Continue a finished run with one extra message. Get the session ID from the
transcript (`"session_id"` for Claude Code, `"thread_id"` for Codex):

```bash
../harness/fork-claude.sh "$PWD/runs/claude1" <session_id> ../harness/followup-generic.txt \
  http://claude1-more.localhost:19000 "$PWD/runs/claude1-more.jsonl"
CODEX_RUN_DIR="$PWD/runs/codex1" ../harness/fork-codex.sh <thread_id> \
  ../harness/followup-coverage.txt http://codex1-cov.localhost:19000 "$PWD/runs/codex1-cov.jsonl"
```

### 9. Score a run

```bash
python3 ../harness/progress.py runs/claude1.jsonl 1          # Claude Code
python3 ../harness/progress_codex.py runs/codex1.jsonl       # Codex
python3 ../harness/errors_detail.py runs/claude1.jsonl       # failed queries and fixes
```

Compare the final summary with `NOTES.md` (Ground truth) and `answer_key.json`.
Check every headline against the data before accepting it: `reference/` has
the queries used to confirm or refute claims (`ref_1d.sql` counterparty types,
`crude_edge.sql`, `gasoil_check.sql`, `wti_broker.sql`, `feed_gap.sql`, ...),
runnable with `python3 ../harness/q.py <file.sql>`. The generator's own cell
`1c` divides the HORIZON offset by 1e6 on a nanosecond table, so its
`horizon_s` column is really milliseconds.

### 10. Export the notebooks

```bash
python3 ../harness/extra/notebook_receiver.py "$PWD/notebooks" &
```

Then open each run's console address in Chrome (for example
`http://claude1.localhost:19000/`) and run this in the page console, changing
the name at the end of the URL:

```js
const db = await new Promise((res, rej) => { const r = indexedDB.open('web-console'); r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error); });
const all = await new Promise(res => { const r = db.transaction('buffers').objectStore('buffers').getAll(); r.onsuccess = () => res(r.result); });
const notebooks = all.filter(b => b.notebookViewState);
await fetch('http://127.0.0.1:18765/claude1', {method: 'POST', headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({origin: location.origin, exported_at: new Date().toISOString(), notebooks})});
```

### 11. Clean up

```bash
docker rm -fv eqeval-questdb
docker rmi questdb/questdb:10.2.0   # only if you pulled it for this
```

Then quit Docker Desktop to give the disk space back to macOS.

## Layout

| Path | What it is |
|---|---|
| `NOTES.md` | Full write-up: environment, ground truth, results table for all runs, follow-up experiment |
| `harness/prompt.txt` | The prompt every run received |
| `harness/followup-generic.txt`, `harness/followup-coverage.txt` | The two follow-up prompts |
| `harness/run.sh` | Headless Claude Code run (`MODEL=` for Fable; `MCP_CONFIG=` per console origin) |
| `harness/run-codex.sh` | Headless Codex run (`CODEX_MODEL=` for Astra), MCP tools pre-approved, browser plugins off |
| `harness/fork-claude.sh`, `harness/fork-codex.sh` | Continue a saved session with one follow-up prompt |
| `harness/mcp-*.json` | Per-run MCP configs (each run used its own `*.localhost:19000` console origin) |
| `harness/progress.py`, `harness/progress_codex.py`, `harness/errors_detail.py`, `harness/find_queries.py` | Transcript summarisers used for scoring |
| `harness/hide_answer_key.py`, `harness/disk_guard.py`, `harness/q.py` | Answer-key removal, disk guard, query runner |
| `harness/extra/` | Notebook export receiver, isolation smoke test, pairing helper, Codex query extractors, demo probe |
| `generator/requirements-frozen.txt` | The exact Python packages the generator ran with (the generator itself is cloned from GitHub, see step 3) |
| `transcripts/` | Every run's raw stream (`*.jsonl`) and start/end times (`*.times`) |
| `notebooks/` | Export of every notebook the agents built (see below) |
| `reference/` | Answer key, the generator's reference queries, verification queries, syntax tests |
| `screenshots/` | Dashboard captures; `retake-2x/` holds the sharp sources of the images in the post |
| `skill-used/questdb-0e6ba28/` | The skill version used by every scored run |
| `skill-used/pilot-versions/run1..run8/` | The skill as it was for each pilot run |

## Run names

| Name | Agent and model | Skill |
|---|---|---|
| run1-pilot, run2 .. run8 | Claude Code, Opus 5.5 | pilot versions, improved between runs |
| final1/2/3-claude-opus | Claude Code, Opus 5.5 | 0e6ba28 (scored) |
| fable1 | Claude Code, Fable 5.1 | 0e6ba28 |
| codex1/2/3-gpt61sol | Codex, gpt-6.1-sol, medium | 0e6ba28 (scored) |
| astra1-gpt6astra | Codex, gpt-6-astra, medium | 0e6ba28 |
| final2-followup-*, codex1-followup-* | forks of final2 and codex1 with one follow-up prompt | 0e6ba28 |

## Notebook exports

Each file in `notebooks/` holds the console's own record of the notebook
(the `buffers` entry in the Web Console's IndexedDB `web-console` database):
title, cells with SQL and markdown, chart and grid layout, and variables. It
was read from each run's console origin on 2026-11-13, after the runs
finished, so it reflects the final state, including any edits the agent made
after the first save. Wrapper fields: `origin`, `exported_at`, `notebooks`.

## License

[Apache License 2.0](LICENSE).
