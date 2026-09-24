"""
Populate tridapro.db from:
  1. tridapro-imc-studio.xlsx  -> chapter list (name + PPT filename + the
     Google Slides link attached to the PPT cell as a hyperlink), the real
     UKMT IMC syllabus order used to rename the placeholder chapters.
  2. data/seed_content.json    -> the worked slides/drills/mock-test content
     that used to be hardcoded in index.html, ported as-is onto the first
     three chapters (in the same order they appeared before).

The PPT column's cells are hyperlinked to Google Slides "edit" links; those
get rewritten to Slides' "/embed" form, the same transform the app's own
"Deck link" paste-a-URL feature already does client-side (see urlGo in
templates/index.html). Any chapter with a deck link renders that live deck
instead of the app's placeholder text slides.

Run with:  python seed.py
"""
import json
import re
from pathlib import Path

import openpyxl

from db import init_db, get_connection

BASE_DIR = Path(__file__).resolve().parent
XLSX_PATH = BASE_DIR / "tridapro-imc-studio.xlsx"
SEED_CONTENT_PATH = BASE_DIR / "data" / "seed_content.json"

EMBED_SUFFIX_RE = re.compile(r"/(edit|pub|view)(\?[^#]*)?(#.*)?$")


def to_embed_url(url):
    """Mirror the frontend's urlGo transform: .../edit?... -> .../embed"""
    if not url:
        return ""
    return EMBED_SUFFIX_RE.sub("/embed", url.strip())


def load_excel_chapters():
    wb = openpyxl.load_workbook(XLSX_PATH, data_only=True)
    ws = wb.active
    chapters = []
    for row in ws.iter_rows(min_row=2):
        name_cell, ppt_cell = row[0], row[1]
        if not name_cell.value:
            continue
        ppt = ppt_cell.value.strip() if ppt_cell.value else None
        deck_link = ppt_cell.hyperlink.target if ppt_cell.hyperlink else None
        chapters.append({
            "name": str(name_cell.value).strip(),
            "ppt": ppt,
            "deck": to_embed_url(deck_link),
        })
    return chapters


def load_seed_content():
    with open(SEED_CONTENT_PATH, encoding="utf-8") as f:
        return json.load(f)


def main():
    excel_chapters = load_excel_chapters()
    seed_content = load_seed_content()  # list keyed by original placeholder id: ch1, ch2, ch3

    init_db()
    conn = get_connection()
    cur = conn.cursor()

    seeded_with_content = 0
    seeded_with_deck = 0
    for position, chapter in enumerate(excel_chapters, start=1):
        chapter_key = f"ch{position}"
        content = next((c for c in seed_content if c["id"] == chapter_key), None)
        if content:
            seeded_with_content += 1
        if chapter["deck"]:
            seeded_with_deck += 1
        sub = chapter["ppt"] or "Content coming soon"

        cur.execute(
            "INSERT INTO chapters (chapter_key, position, name, sub, ppt_filename, deck_url) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (chapter_key, position, chapter["name"], sub, chapter["ppt"], chapter["deck"]),
        )
        chapter_id = cur.lastrowid

        if content:
            for i, s in enumerate(content["slides"]):
                cur.execute(
                    "INSERT INTO slides (chapter_id, position, kicker, heading, sub, bullets, note) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (chapter_id, i, s["k"], s["h"], s["s"], json.dumps(s["b"]), s["n"]),
                )
            for i, d in enumerate(content["drills"]):
                cur.execute(
                    "INSERT INTO drills (chapter_id, position, stem, options, correct_index, explanation) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (chapter_id, i, d["s"], json.dumps(d["o"]), d["c"], d["e"]),
                )
            for i, t in enumerate(content["test"]):
                cur.execute(
                    "INSERT INTO test_questions (chapter_id, position, stem, options, correct_index, explanation) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (chapter_id, i, t["s"], json.dumps(t["o"]), t["c"], t["e"]),
                )

    conn.commit()
    conn.close()
    print(f"Seeded {len(excel_chapters)} chapters ({seeded_with_content} with worked content, {seeded_with_deck} with a linked Slides deck).")


if __name__ == "__main__":
    main()
