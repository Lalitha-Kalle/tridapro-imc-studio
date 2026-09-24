import json
from pathlib import Path

from flask import Flask, g, jsonify, render_template

from db import DB_PATH, get_connection

app = Flask(__name__)


def get_db():
    if "db" not in g:
        g.db = get_connection()
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chapters")
def api_chapters():
    db = get_db()
    chapters = db.execute("SELECT * FROM chapters ORDER BY position").fetchall()

    result = []
    for ch in chapters:
        slides = db.execute(
            "SELECT * FROM slides WHERE chapter_id=? ORDER BY position", (ch["id"],)
        ).fetchall()
        drills = db.execute(
            "SELECT * FROM drills WHERE chapter_id=? ORDER BY position", (ch["id"],)
        ).fetchall()
        tests = db.execute(
            "SELECT * FROM test_questions WHERE chapter_id=? ORDER BY position", (ch["id"],)
        ).fetchall()

        result.append(
            {
                "id": ch["chapter_key"],
                "name": ch["name"],
                "sub": ch["sub"] or "",
                "deck": ch["deck_url"] or "",
                "slides": [
                    {
                        "k": s["kicker"],
                        "h": s["heading"],
                        "s": s["sub"],
                        "b": json.loads(s["bullets"]),
                        "n": s["note"],
                    }
                    for s in slides
                ],
                "drills": [
                    {
                        "s": d["stem"],
                        "o": json.loads(d["options"]),
                        "c": d["correct_index"],
                        "e": d["explanation"],
                    }
                    for d in drills
                ],
                "test": [
                    {
                        "s": t["stem"],
                        "o": json.loads(t["options"]),
                        "c": t["correct_index"],
                        "e": t["explanation"],
                    }
                    for t in tests
                ],
            }
        )

    return jsonify(result)


if __name__ == "__main__":
    if not Path(DB_PATH).exists():
        print("No database found — run `python seed.py` first.")
    else:
        app.run(debug=True)
