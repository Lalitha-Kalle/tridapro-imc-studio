DROP TABLE IF EXISTS drills;
DROP TABLE IF EXISTS test_questions;
DROP TABLE IF EXISTS slides;
DROP TABLE IF EXISTS chapters;

CREATE TABLE chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_key TEXT UNIQUE NOT NULL,
    position INTEGER NOT NULL,
    name TEXT NOT NULL,
    sub TEXT,
    ppt_filename TEXT,
    deck_url TEXT NOT NULL DEFAULT ''
);

CREATE TABLE slides (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    kicker TEXT,
    heading TEXT,
    sub TEXT,
    bullets TEXT NOT NULL,
    note TEXT
);

CREATE TABLE drills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    stem TEXT NOT NULL,
    options TEXT NOT NULL,
    correct_index INTEGER NOT NULL,
    explanation TEXT
);

CREATE TABLE test_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    stem TEXT NOT NULL,
    options TEXT NOT NULL,
    correct_index INTEGER NOT NULL,
    explanation TEXT
);

CREATE INDEX idx_slides_chapter ON slides(chapter_id);
CREATE INDEX idx_drills_chapter ON drills(chapter_id);
CREATE INDEX idx_test_chapter ON test_questions(chapter_id);
