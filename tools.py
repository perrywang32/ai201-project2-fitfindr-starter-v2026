"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    listings = load_listings()
    requested = {
        word.casefold()
        for word in re.findall(r"[a-zA-Z0-9]+", description)
        if len(word) > 1
    }

    def size_tokens(value) -> set[str]:
        # Treat slash sizes as alternatives: M matches S/M and M/L, but S
        # does not accidentally match XL and "s" does not match "US 9".
        parts = re.findall(r"[a-zA-Z]+\d*(?:/[a-zA-Z]+\d*)*|\d+(?:\.\d+)?", str(value))
        return {
            part.casefold()
            for token in parts
            for part in token.split("/")
        }

    matches = []
    for listing in listings:
        try:
            price = float(listing.get("price"))
        except (TypeError, ValueError):
            continue
        if max_price is not None and price > float(max_price):
            continue
        if size and not (size_tokens(size) & size_tokens(listing.get("size", ""))):
            continue

        def words(value) -> set[str]:
            if isinstance(value, list):
                value = " ".join(map(str, value))
            return {word.casefold() for word in re.findall(r"[a-zA-Z0-9]+", str(value))}

        # A title match should count more than a passing keyword in a long
        # description, so the agent's first result is a useful top match.
        score = (
            3 * len(requested & words(listing.get("title", "")))
            + 2 * len(requested & words(listing.get("style_tags", [])))
            + len(requested & words(listing.get("description", "")))
            + len(requested & words(listing.get("category", "")))
            + len(requested & words(listing.get("colors", [])))
            + len(requested & words(listing.get("brand") or ""))
        )
        if score:
            matches.append((score, listing))

    matches.sort(key=lambda pair: (-pair[0], float(pair[1].get("price", 0))))
    return [listing for _, listing in matches[: config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    owned_items = wardrobe.get("items", []) if isinstance(wardrobe, dict) else []
    item_details = (
        f"{new_item.get('title', 'the item')} ({new_item.get('category', 'clothing')}, "
        f"size {new_item.get('size', 'unspecified')}, ${new_item.get('price', 'unknown')})"
    )
    if owned_items:
        wardrobe_lines = []
        for item in owned_items:
            name = item.get("name", item.get("title", "wardrobe item"))
            details = []
            for field in ("category", "colors", "style_tags", "notes"):
                value = item.get(field)
                if value:
                    if isinstance(value, list):
                        value = ", ".join(map(str, value))
                    details.append(f"{field.replace('_', ' ')}: {value}")
            suffix = f" ({'; '.join(details)})" if details else ""
            wardrobe_lines.append(f"- {name}{suffix}")
        wardrobe_text = "\n".join(wardrobe_lines)
        prompt = (
            f"Suggest one or two wearable outfits around {item_details}. "
            "Use specific pieces from the user's wardrobe and explain briefly why they work. "
            "Do not invent wardrobe items.\n\nWardrobe:\n" + wardrobe_text
        )
    else:
        prompt = (
            f"Give practical general styling advice for {item_details}. "
            "Suggest one or two outfit combinations using common basics, and make clear "
            "that the user has not provided a wardrobe list."
        )
    response = generate(
        prompt,
        system="You are a practical personal stylist. Keep suggestions specific, concise, and wearable.",
    )
    return response.strip() or f"Try pairing {item_details} with simple neutral basics and comfortable shoes."


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not outfit or not outfit.strip():
        return "I couldn't create a fit card because no outfit suggestion was provided."

    prompt = (
        "Write a natural social caption in 2 to 4 sentences for this thrift find. "
        "Mention the item title, its price, and its marketplace exactly once each; "
        "capture a specific vibe without sounding like a product listing.\n\n"
        f"Item: {new_item.get('title', 'Thrift find')}\n"
        f"Price: ${new_item.get('price', 'unknown')}\n"
        f"Platform: {new_item.get('platform', 'unknown')}\n"
        f"Outfit idea: {outfit}"
    )
    response = generate(
        prompt,
        system="Write only the finished caption. Do not add a heading or quotation marks.",
    )
    return response.strip() or (
        f"Found {new_item.get('title', 'a thrift find')} for ${new_item.get('price', 'unknown')} "
        f"on {new_item.get('platform', 'a marketplace')}. The look feels easy and personal."
    )
