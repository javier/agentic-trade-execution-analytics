# Agent-driven execution-quality eval

Goal: give "agent-ready" an observable meaning. An agent investigates execution
quality end to end (discover the schema, join trades and quotes, compute
markouts, investigate outliers, leave a reproducible notebook or dashboard),
scored on correctness, completion, interventions and setup effort.

The write-up is the blog post
[Agentic trade execution analysis: markouts, TCA and what agents find](https://questdb.com/blog/agentic-trade-execution-analysis-markouts-tca/),
which walks through the astra1 run.

## Environment

- QuestDB `questdb/questdb:10.2.0` in container `eqeval-questdb`, host port
  19000 (kept clear of a local QuestDB on 9000).
- Data: energy generator (javier/commodities-data-generator, energy-trading)
  cloned fresh, `SCALE=0.5 START_TS=2026-11-10T00:00:00Z DEMO_DAY=2026-11-11`,
  backfill to 2026-11-12 ~09:07 UTC. ~9.6 GB inside the container.
  Scale 1 over 5 days was 19 GB and pushed the Mac below the 12 GB free floor;
  Docker.raw only shrank after quitting Docker Desktop.
- `energy_demo_events` (the answer key) exported to reference/answer_key.json
  and DROPPED before any agent ran.
- MCP: `@questdb/mcp-server-questdb@0.5.0`, Read permission. Each run used a
  fresh browser origin (`evalN.localhost:19000`, `finalN.localhost:19000`) so
  earlier notebooks were invisible to the next agent.
- Agent: headless `claude -p` (Opus 5.5), `--setting-sources project
  --strict-mcp-config --permission-mode dontAsk`, skill installed as a project
  skill in the run folder. Isolation smoke test passed: no CLAUDE.md, memories,
  hooks or user skills visible. See harness/run.sh.
- Prompt: harness/prompt.txt (desk head voice, no hints about markouts or plants).

## Ground truth (what the data really contains)

From answer_key.json plus generator code (not its README, which is wrong in places):
- Voice/broker counterparties: UTILITY_* and INDUSTRIAL_* make the desk LOSE
  (adverse selection); BANK_* and TRADER_* make the desk win; PRODUCER_* neutral.
  The generator README/comment says the reverse; the code's sign convention is
  what the data shows. Reference cell 1d (3 days): industrial n=114 -5.75 bps
  @15m, -9.71 @1h; utility n=137 -4.42 @15m, -6.62 @1h; bank +2.29 @15m, +9.02 @1h.
- CRUDE book trades with foresight: +7.8 bps @15m (ref 1c).
- PRODUCTS (gasoil) always aggressive: flat ~-1.5 bps.
- Cold snap 09:30-09:50 UTC Nov 11: gas/power +6-8%; EU_GAS -4.3 bps, UK_POWER
  -2.6 @15m (positioning, not execution).
- EEX quote feed silent 08:45-08:48 UTC (no ticks at all; ICE_ENDEX keeps going).
- LNG JKM_Dec-26 booked 10x (500k vs 50k), corrected 10:45.
- EU_GAS TTF_Q1-27 broker trade with BANK_02 booked twice, duplicate cancelled 11:00.
- UK_POWER UKPWR_Win-27 voice deal booked 3h45m late; voice bookings generally late.
- Manual mark TTF_Q1-27 +2.50 EUR (trader_11) 08:00-08:30; bad vol mark
  TTF_Mar-27 10:30-10:50; CRUDE limit breach 07:00-10:00 (not execution quality).
- EEX: wider spread, aggressive fills ~2x cost of primary venue.
- Strip (quarter/season) quotes are stale (median 9-16 s, up to 15 min), so
  strip markouts against own quote are an artifact (runs 1, 6, 7, final1 agree).
- Reference cell 1c labels `h.offset / 1000000` as seconds, but energy_fills is
  TIMESTAMP_NS, so the column is milliseconds (generator bug).

## Runs

| Run | Skill | Min | Queries | Failed | Interv. | Headline result |
|---|---|---|---|---|---|---|
| run1 (pilot) | PR #7 initial | 14.6 | 74 | 5 | 0 | found util/industrial; missed cold snap |
| run2 | +TICK/units/IN/UUID/analysis | 8.6 | 56 | 4 | 0 | cold snap; missed counterparty; NBP strip FP |
| run3 | +HORIZON sides, count_distinct | 9.3 | 48 | 1 | 0 | said "no feed outage" (false: 10-min buckets) |
| run4 | +mistakes in SKILL.md, gap rule, derived groups | 13.1 | 72 | 3 | 0 | outage exact 181 s; counterparty diluted by type x channel |
| run5 | +CTE timestamp, window ORDER BY, split rule | 11.5 | 58 | 2 | 0 | UTILITY_02 named but rally-confounded; HORIZON cells lost variables |
| run6 | +TCA method, ON filter fix | 9.3 | 52 | 2 | 0 | EU_GAS NBP probable FP (t -1.7); variables fixed |
| run7 | +hypotheses not dropped, weigh evidence | 10.1 | 55 | 1 | 0 | first CRUDE edge (t 5-10) |
| run8 | +go wide, coarsest grouping first | 8.7 | 55 | 1 | 0 | first full counterparty finding (n=114, t -3.8) |
| **final1** | **0e6ba28** (scored) | 11.4 | 61 | 2 | 0 | counterparty + CRUDE + cold snap + strips + bookings; missed EEX outage, gasoil, marks |

| **final2** | **0e6ba28** (scored) | 10.7 | 71 | 1 | 0 | FIRST to find CRUDE limit breach (3.33M bbl vs 2M, 07:21-08:22); cold snap; strips; bookings; MISSED counterparty (per-name only); attributed Brent gains to own impact (misses the all-days CRUDE edge); missed EEX outage |
| **final3** | **0e6ba28** (scored) | 9.8 | 57 | 2 | 0 | counterparty (industrial t -3.7 over 3 days, utility t -2.1); EEX outage + feed-health chart; EEX routing; cold snap; strips; dup/10x/late; MISSED CRUDE edge, limit breach; hedged gasoil Mar/Apr-27 drift (t~-2, probable noise) |
| codex0 | 0e6ba28 | 0.4 | 0 | – | – | BLOCKED: codex exec refuses MCP calls ("requires approval, but approval policy is never"); fix = `mcp_servers.questdb.default_tools_approval_mode="approve"` |
| **codex1** | **0e6ba28** (scored, gpt-6.1-sol medium) | 7.5 | 60 (+21 validate) | 1 | 0 | FIRST to find champion model failing on winter gas/power and the manual TTF marks; cold snap; late bookings; headline = gasoil Mar/Apr-27 drift (real unplanted effect); counterparty only per-name (UTILITY_02 rally-confounded, UTILITY_10); MISSED segment, CRUDE edge, breach, strips, dup, 10x, EEX outage/routing; dashboard dates FIXED (no variable) |

| **codex2** | **0e6ba28** (scored, gpt-6.1-sol medium) | 9.7 | 98 (+23 validate) | 2 | 0 | champion model + manual marks again; FIRST to read gasoil as half-spread only; cold snap; late bookings; headline WTI broker flow (-6.16 bps @5m) = hedged FP: all cp types negative that day incl. banks (reference/wti_broker.sql); UTILITY_02/10 watchlist; 20-panel notebook, fixed dates |

| **codex3** | **0e6ba28** (scored, gpt-6.1-sol medium) | 14.9 | 124 (+35 validate) | 2 | 0 | WIDEST coverage: limit breach (2.93M bbl, 66.7 min over), EEX outage, FIRST to find the bad vol mark ("four volatility corrections"), champion model, manual marks, gasoil half-spread, late bookings; headline WTI PRODUCER flow (5 trades, -19.5 bps, t -4.26) = FP (producers neutral), hedged; industrials only via gasoil/INDUSTRIAL_08; new error: CASE expression in HORIZON ON unsupported; 24 panels, fixed dates |

| **fable1** | **0e6ba28** (Claude Code, claude-fable-5-1; ran in parallel with codex3) | 15.4 | 80 | 2 | 0 | counterparty segments (industrial via broker t -3.8, utility via OTC t -3.9, banks favourable); gasoil = spread; EEX outage; stale strips; late bookings; noticed every EEX fill has a quote 1 ns earlier at the fill price (generator mechanic); headline frames 09:30 rally as passive offers run over (defensible alternative to "market risk", notes the desk was long 6.7M therms); unverified: UK power aggressive -6 bps ex-spike t -3.1; MISSED CRUDE edge, breach, marks, model, dup, 10x; 17 cells with 4 variables; same new error as codex3 (expression in HORIZON ON) |

| **astra1** | **0e6ba28** (Codex, gpt-6-astra medium, confirmed in ~/.codex session log) | 9.7 | 80 (+20 validate) | 4 | 0 | BEST COVERAGE, NO FALSE HEADLINE: utility counterparties in oil voice flow (32 trades, -6.98 bps vs matched exchange fills); gasoil = spread; cold snap with model attribution; champion model; limit breach; manual mark; vol corrections; EEX outage; late bookings; MISSED CRUDE edge, strips, dup, 10x, EEX routing, industrial segment; errors: CASE in HORIZON ON (x2), BETWEEN on DOUBLE, unexpected token; 20 panels, fixed dates |


### Follow-up experiment (2026-11-13): does one more prompt help?

Forked saved sessions (Claude `--resume --fork-session`, Codex `exec fork`),
fresh console origins, same data. Base runs: final2 (Claude, 4/13) and codex1
(Codex, 4/13). Prompts in harness/followup-*.txt.

| Fork | Planted found | Extra time | New planted | Notes |
|---|---|---|---|---|
| final2 + "keep digging" | 8 | 9.5 min | model, manual mark, vol mark, EEX outage | found feed stop at 09:20 Nov 12 (true, our load end), FX views fall back to 1.0, expiry positions; kept wrong crude "own impact" story |
| codex1 + "keep digging" | 8 | 15 min (incl. a re-pair) | breach, outage, vol, EEX routing (1.05-1.33 bps on split orders) | demoted its own gasoil headline ("reverses by 30m"); live position view caveat |
| final2 + coverage prompt | 7 | 8.8 min | model, manual mark, vol mark | coverage table states "energy_quotes: gaps per hour: no gaps" (FALSE) and "no toxic counterparty" (FALSE); booking-date positions finding; kept crude story |
| codex1 + coverage prompt | 7 | 11.3 min | breach (3.05M with late trades, 74 min), outage, vol | 36-object coverage table with real reconciliations; kept gasoil as headline; no routing |

Takeaways: one follow-up roughly doubles planted coverage (4 -> 7-8) for both
tools, each going to its own blind spots. Wording matters less than asking.
Neither prompt fixed the deep misses (counterparty segments, crude edge) or the
wrong crude explanation. The coverage table makes checks auditable, but it can
also record a too-coarse check as a verified negative.

fork-codex.sh cd's to the run folder and pins sandbox_mode read-only.

Codex harness: harness/run-codex.sh. Overrides only via `-c`: eval CONSOLE_ORIGIN,
pre-approved questdb tools, node_repl + browser/chrome/computer-use plugins
disabled (parity with Claude `--no-chrome`), notify off. Codex loads the skill
from ~/.agents/skills/questdb (0e6ba28), verified; remove any stale copy under
~/.codex/skills first.

Unplanted but real: GASOIL Mar-27/Apr-27 aggressive fills on Nov 11 drift
-7.5 bps (t -4.7) and -10.2 bps (t -3.6) at 5 min; front months normal
(reference/gasoil_check.sql). Generator gives PRODUCTS no foresight, so this is
a back-month pricing side effect; cause not identified. Found by final3 (hedged)
and codex1 (headline). Not a false positive.

CRUDE edge check (reference/crude_edge.sql): +6.9 to +8.2 bps @15m every day,
inside and outside the 07:00-08:30 breach window, so final2's "own impact"
explanation is wrong.

Scored-run details (final1): industrial n=114 -9.5 bps @30m t -3.8; utility
t -3.9; CRUDE +7-9 bps @15m t 4-11; strip quote age 0.03 s months / 9.3 s
quarters / 16 s seasons; dup, 10x, late bookings all found; bonus: book views
default to today. Step 0 half-followed (tables() profile yes, marks/limits/gaps
no), no coverage table. Dashboard: 9 panels + read-me, `@day` and `@hist`.
Screenshots in screenshots/ (counterparty curve chart is the hero image). Raw
floats in tables (1.3900000000000001) would show in print.
