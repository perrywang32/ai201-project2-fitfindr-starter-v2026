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

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



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
