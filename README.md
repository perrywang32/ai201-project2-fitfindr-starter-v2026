# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

FitFindr takes a plain-language request for a secondhand clothing item, such as a vintage graphic tee under $30 in size M. It searches the listings by keywords, size, and maximum price, then chooses the highest-scoring match. It uses the shopper's wardrobe to suggest outfit combinations and writes a short social caption for the find. If no listing matches, it stops and tells the shopper which parts of the request to change.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Filters clothing listings by price and size, then ranks remaining listings by weighted keyword overlap. Title matches have the most weight, followed by style tags.
- **Inputs:** `description` (`str`), `size` (`str | None`), `max_price` (`float | None`). A slash size such as `S/M` is treated as containing either size.
- **Returns:** A list of matching listing dictionaries. Each dictionary has `id`, `title`, `description`, `category`, `style_tags` (list), `size`, `condition`, `price` (float), `colors` (list), `brand` (string or `None`), and `platform`. Results are ordered by keyword score and capped at `config.SEARCH_RESULT_LIMIT`.
- **When it has nothing:** An empty list (`[]`) when no listing meets the filters and has at least one description keyword match.

### `suggest_outfit`

- **What it does:** Uses the model to suggest one or two outfits around the selected thrift item, using wardrobe pieces when available.
- **Inputs:** `new_item` (`dict` with listing fields such as `title`, `category`, `size`, and `price`); `wardrobe` (`dict` with an `items` list).
- **Returns:** A non-empty styling suggestion string. With wardrobe items, it names pieces from that wardrobe; with an empty wardrobe, it gives general advice.
- **When it has nothing:** It returns a general styling fallback if the model responds with an empty string; model connection failures are surfaced by the model adapter.



### `create_fit_card`

- **What it does:** Uses the model to write a social caption for the selected item and outfit suggestion.
- **Inputs:** `outfit` (`str`); `new_item` (`dict` with `title`, `price`, and `platform`).
- **Returns:** A non-empty caption intended to be two to four sentences and mention the item, price, platform, and outfit vibe.
- **When it has nothing:** If `outfit` is empty or whitespace, it returns an explanatory message without calling the model; an empty model response gets a short fallback caption.


---

## Planning Loop

**Branch rule:** If `search_listings` returns an empty list, the agent stores a message suggesting the shopper change the keywords, size, or maximum price and stops before calling `suggest_outfit`. Otherwise it saves the first result as `selected_item`, sends that item and the wardrobe to `suggest_outfit`, then sends the suggestion and same item to `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regular expressions extract a `size` phrase and a dollar amount/price ceiling; the remaining words become the description. The implementation is deterministic and does not use a model to parse.

**What moves through the session:** `parsed` → `search_results` → `selected_item` and `wardrobe` → `outfit_suggestion` → `fit_card`. If search is empty, `error` is populated and the later fields remain `None`.

---

## Sample Run

The listings and wardrobe loader are now included, and search and loop checks were run against the real 40-listing dataset. This execution environment does not have the project's `python-dotenv` or `google-genai` packages installed, so the model-backed tools could only be checked with a local mock response. The output below is still waiting for a run with the real model; do not submit mock text as model output. After setup, run the commands and paste their actual output here.

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'
[Paste the actual terminal output here after running the command.]
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; import json; print(json.dumps(search_listings('2003 tour bootleg', max_price=30), ensure_ascii=False, indent=2))"
[
  {
    "id": "lst_006",
    "title": "Graphic Tee — 2003 Tour Bootleg Style",
    "description": "Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.",
    "category": "tops",
    "style_tags": ["graphic tee", "vintage", "grunge", "streetwear", "band tee"],
    "size": "L",
    "condition": "good",
    "price": 24.0,
    "colors": ["black"],
    "brand": null,
    "platform": "depop"
  }
]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
[Paste actual output here.]
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
[Paste actual output here.]
```

---

## How I Used AI

**Moment 1**

- *What I asked for:* Help implementing `search_listings` from the starter specification, including size matching and the empty-list case.
- *What came back:* A keyword-overlap search with explicit size-token matching so a small-size request does not match `XL` or a shoe size like `US 9`.
- *What I changed:* I used token matching for slash sizes, applied price and size filters before ranking, and kept the required empty result as `[]`.

**Moment 2**

- *What I asked for:* Help completing the loop while following the acceptance-criteria instructions about branch and session state.
- *What came back:* A deterministic query parser and a sequence that stores each tool result in the session before using it in the next step.
- *What I changed:* I made the no-results branch return a concrete message before the styling tool runs, and the first selected listing is passed to both later tools.

---

## Run Log — Before

**Status: pending the required five real trials per criterion.** I did not mark
these rows PASS or FAIL because this workspace has no MCP SDK, `python-dotenv`,
`google-genai`, or configured model key. The local checks below used stubs and
are not substitutes for `python run_eval.py --label before`.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---:|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4/5 | Not run | Not run | Not run | Not run | Not run | Pending |
| 2. Impossible query stops before second tool | 5/5 | Not run | Not run | Not run | Not run | Not run | Pending |
| 3. Selected item reaches styling tool | 5/5 | Not run | Not run | Not run | Not run | Not run | Pending |
| 4. Fit card content | 4/5 | Not run | Not run | Not run | Not run | Not run | Pending |
| 5. Search respects price ceiling | 5/5 | Not run | Not run | Not run | Not run | Not run | Pending |

**Local implementation checks (mocked; not the five-trial run):** a controlled
Python harness substituted the MCP client's return value and model tools. It
verified the happy path completed, the empty-search branch skipped later tools,
the exact selected listing object was passed to `suggest_outfit`, all four
search results for a `$25` ceiling were at or below `$25`, and a forced
`ModelUnavailable` exception produced a session error instead of a traceback.
These checks establish basic control flow only; they do not measure real MCP or
model behavior.

**Real `run_eval.py` output:** not available yet. After installing
`requirements.txt`, setting up `.env`, and confirming `python test.py` passes,
run `python run_eval.py --label before`, then copy its table and selected raw
output here. Commit the generated file under `results/`.

---

## Verdicts and Diagnoses

No criterion has an official verdict yet because the required five live trials
have not been run. The local checks above are not counted toward the targets.

| # | Criterion | Target | Verdict | How I decided |
|---|---|---:|---|---|
| 1 | Matching query completes all three tools | 4/5 | Pending | Requires five real agent runs. |
| 2 | Impossible query stops before second tool | 5/5 | Pending | The mocked branch check passed once; the five-trial target remains unmeasured. |
| 3 | Selected item reaches styling tool | 5/5 | Pending | The identity check passed once with a local spy; the five-trial target remains unmeasured. |
| 4 | Fit card content | 4/5 | Pending | Requires real model-generated cards to assess content and sentence count. |
| 5 | Search respects price ceiling | 5/5 | Pending | The mocked local search check passed once; the five-trial target remains unmeasured. |

**Diagnoses:** pending the real run log. No measured misses can be diagnosed
honestly until the five trials for each criterion are recorded.

---

## Loop Trace

The trace hooks are in `agent.py::run_agent`. The following is a control-flow
check made with a stubbed MCP client and stubbed model tools; it is **not** a
trace from a live MCP connection or model run. Run
`python app.py ask 'vintage graphic tee under $30' --trace` after local setup and
replace these examples with the terminal output.

**Happy path (stubbed):**

```
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey, Vintage Graphic Hoodie — Faded Black … +7 more
[3] suggest_outfit
      in:  dict with keys: selected_item, wardrobe
      out: jeans and white sneakers
[4] create_fit_card
      in:  dict with keys: outfit, selected_item
      out: Graphic Tee — 2003 Tour Bootleg Style costs $24.0 on depop. Easy streetwear.
```

**Empty search (stubbed):**

```
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[3] empty_search_branch
      out: I couldn't find a listing that matches. Try changing the item keywords, size, or maximum price.
      →    no results; later tools skipped
```

**On the MCP move:** `mcp_server.py` now registers `search_listings`, and
`agent.py` calls it through `mcp_client.call_tool`. The code path was exercised
with a local replacement for `call_tool`, but the MCP protocol connection could
not be tested here because the MCP SDK is not installed. Confirm it on your
machine with `python mcp_client.py` and then capture a live `--trace` run.

---

## The Improvement

The agent now catches `ModelUnavailable` from either model-backed tool, records
a user-readable error in the session, and stops before trying the next step.
A forced exception in a local stub check confirmed this path returns cleanly.
This implementation change was made before the required baseline evaluation,
so it has not yet been selected from a measured diagnosis or evaluated as the
assignment's one improvement.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---:|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4/5 | Not run | Not run | Not run | Not run | Not run | Pending |
| 2. Impossible query stops before second tool | 5/5 | Not run | Not run | Not run | Not run | Not run | Pending |
| 3. Selected item reaches styling tool | 5/5 | Not run | Not run | Not run | Not run | Not run | Pending |
| 4. Fit card content | 4/5 | Not run | Not run | Not run | Not run | Not run | Pending |
| 5. Search respects price ceiling | 5/5 | Not run | Not run | Not run | Not run | Not run | Pending |

**Did it help, and how do I know:** not measured. Run and save the baseline,
choose one change based on its diagnoses, then run
`python run_eval.py --label after` and compare the two actual logs.

---

## What's Still Broken

- The live MCP server/client connection still needs to be checked locally.
- The three failure modes and the five criteria still need real runs; only the
  empty-search and forced model-unavailable paths were exercised with stubs.
- The before/after logs, final verdicts, evidence-based diagnoses, and measured
  improvement are pending those runs.


<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
