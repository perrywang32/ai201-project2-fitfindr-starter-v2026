# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
The search uses keyword overlap rather than semantic matching, so one query phrased differently from the listing text may miss even when the listing is a reasonable fit.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
This path is a deterministic empty-list check: once search returns no results, the loop exits before either model tool is called.

---

## 3. The selected item reaches the styling tool

**Given a query that matches at least one listing, `suggest_outfit` receives the exact dictionary stored in `session["selected_item"]` in 5 of 5 tries.**



**Why this target:**
The selected item is stored once and passed directly to the next tool, so exact object equality is a reasonable expectation on every run.

---

## 4. Fit card content

**For a matched listing, at least 4 of 5 generated fit cards contain the listing title, price, and platform, and each card has 2–4 sentences.**



**Why this target:**
The model can vary its wording, so allowing one miss accounts for occasional formatting drift while still requiring the item details and caption length most of the time.

---

## 5. The search respects the price ceiling

**For a query with a maximum price, every listing returned by `search_listings` is at or below that price in 5 of 5 tries.**



**Why this target:**
Price filtering is a deterministic comparison in the search tool; the inclusive ceiling should never be exceeded, so all five tries should pass.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->

