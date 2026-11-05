# -*- coding: utf-8 -*-
"""
TorahNotesOCR - Learning and Memory Engine
Stores user corrections, common Talmudic abbreviations, and OCR error patterns.
Learns automatically from user edits and applies corrections to future scans.
"""

import os
import re
import sqlite3
import difflib
from datetime import datetime
from typing import List, Tuple, Dict, Any

DEFAULT_CORRECTIONS = [
    # Common OCR misreadings of Yeshiva / Torah handwriting
    ("בסייד", "בס\"ד"),
    ("בסיד", "בס\"ד"),
    ("בסד", "בס\"ד"),
    ("שיעורא", "שיעור א'"),
    ("שיעורב", "שיעור ב'"),
    ("שיעורג", "שיעור ג'"),
    ("שיעורד", "שיעור ד'"),
    ("שיעורה", "שיעור ה'"),
    ("שיעורו", "שיעור ו'"),
    ("שיעורז", "שיעור ז'"),
    ("שיעורח", "שיעור ח'"),
    ("רשל", "רגל"),
    ("קוס", "תוס'"),
    ("קוס'", "תוס'"),
    ("תום", "תוס'"),
    ("תוס", "תוס'"),
    ("רסי", "רש\"י"),
    ("רשי", "רש\"י"),
    ("רשלי", "רש\"י"),
    ("רמבם", "רמב\"ם"),
    ("ראבד", "ראב\"ד"),
    ("ריף", "רי\"ף"),
    ("ראס", "רא\"ש"),
    ("ראש", "רא\"ש"),
    ("חנין", "ח\"נ"),
    ("חנ", "ח\"נ"),
    ("ח\"נ'", "ח\"נ"),
    ("נס", "נ\"ש"),
    ("נש", "נ\"ש"),
    ("גש", "נ\"ש"),
    ("נפקמ", "נפק\"מ"),
    ("קמל", "קמ\"ל"),
    ("סדא", "סד\"א"),
    ("ברהר", "ברה\"ר"),
    ("ברחר", "ברה\"ר"),
    ("ברהי", "ברה\"י"),
    ("משאכ", "משא\"כ"),
    ("משא\"ב", "משא\"כ"),
    ("אכ", "א\"כ"),
    ("איכ", "אי\"כ"),
    ("עיש", "עיי\"ש"),
    ("עייש", "עיי\"ש"),
    ("עכד", "עכ\"ד"),
    ("עכ\"ל", "עכ\"ל"),
    ("עכל", "עכ\"ל"),
    ("וכו", "וכו'"),
    ("וגו", "וגו'"),
    ("מנל", "מנ\"ל"),
    ("תר", "ת\"ר"),
    ("יל", "י\"ל"),
    ("צל", "צ\"ל"),
    ("צב", "צ\"ב"),
    ("צב'", "צ\"ב"),
    ("ממנ", "ממ\"נ"),
    ("מהו", "מהו'"),
    ("הגמ", "הגמ'"),
    ("גמ", "גמ'"),
    ("מתנ", "מתנ'"),
    ("מתני", "מתני'"),
    ("דכתי", "דכתיב"),
    ("איפכ", "איפכא"),
    ("כדרכ", "כדרכה"),
    ("פנ\"י", "פנ\"י"),
    ("פני", "פנ\"י"),
    ("הנציב", "הנצי\"ב"),
    ("הנצי\"ב", "הנצי\"ב"),
]

DEFAULT_VOCABULARY = [
    "בבא", "קמא", "מציעא", "בתרא", "כיצד", "הרגל", "מועדת", "להלך", "כדרכה",
    "ולשבר", "שן", "ורגל", "קרן", "צרורות", "חצי", "נזק", "נזק", "שלם", "שינוי",
    "אורחיה", "משונה", "כוחו", "כגופו", "תולדה", "אב", "אבות", "נזיקין",
    "רש\"י", "תוספות", "תוס'", "רמב\"ם", "ראב\"ד", "רי\"ף", "רא\"ש", "מהר\"ם",
    "רבינו", "פרץ", "הגרש\"פ", "הגרי\"ז", "ברכת", "שמואל", "אימרי", "משה",
    "רשות", "הרבים", "היחיד", "חצר", "הניזק", "פטור", "חייב", "הלכתא", "גמירי"
]

class LearningEngine:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to user appdata or local directory
            app_dir = os.path.join(os.path.expanduser("~"), ".torah_notes_ocr")
            os.makedirs(app_dir, exist_ok=True)
            db_path = os.path.join(app_dir, "learned_corrections.db")
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _get_connection(self):
        return self._conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS replacements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    raw_text TEXT UNIQUE COLLATE NOCASE,
                    corrected_text TEXT NOT NULL,
                    count INTEGER DEFAULT 1,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vocabulary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT UNIQUE,
                    frequency INTEGER DEFAULT 1,
                    category TEXT DEFAULT 'general'
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    page_name TEXT,
                    raw_line TEXT,
                    corrected_line TEXT,
                    timestamp TEXT
                )
            """)
            conn.commit()

            # Seed default corrections if table is empty
            cursor.execute("SELECT COUNT(*) FROM replacements")
            if cursor.fetchone()[0] == 0:
                now = datetime.now().isoformat()
                for raw, corr in DEFAULT_CORRECTIONS:
                    cursor.execute("""
                        INSERT OR IGNORE INTO replacements 
                        (raw_text, corrected_text, count, is_active, created_at, updated_at)
                        VALUES (?, ?, 1, 1, ?, ?)
                    """, (raw, corr, now, now))
                conn.commit()

            # Seed vocabulary
            cursor.execute("SELECT COUNT(*) FROM vocabulary")
            if cursor.fetchone()[0] == 0:
                for w in DEFAULT_VOCABULARY:
                    cursor.execute("""
                        INSERT OR IGNORE INTO vocabulary (word, frequency, category)
                        VALUES (?, 5, 'talmud')
                    """, (w,))
                conn.commit()

    def get_all_replacements(self, active_only: bool = True) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT id, raw_text, corrected_text, count, is_active, updated_at FROM replacements"
            if active_only:
                query += " WHERE is_active = 1"
            query += " ORDER BY count DESC, raw_text ASC"
            cursor.execute(query)
            rows = cursor.fetchall()
            return [
                {
                    "id": r[0],
                    "raw_text": r[1],
                    "corrected_text": r[2],
                    "count": r[3],
                    "is_active": bool(r[4]),
                    "updated_at": r[5]
                }
                for r in rows
            ]

    def add_or_update_replacement(self, raw_text: str, corrected_text: str, increment: int = 1) -> bool:
        raw_text = raw_text.strip()
        corrected_text = corrected_text.strip()
        if not raw_text or not corrected_text or raw_text == corrected_text:
            return False

        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO replacements (raw_text, corrected_text, count, is_active, created_at, updated_at)
                VALUES (?, ?, ?, 1, ?, ?)
                ON CONFLICT(raw_text) DO UPDATE SET
                    corrected_text = excluded.corrected_text,
                    count = replacements.count + excluded.count,
                    is_active = 1,
                    updated_at = excluded.updated_at
            """, (raw_text, corrected_text, increment, now, now))
            conn.commit()
        return True

    def delete_replacement(self, replacement_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM replacements WHERE id = ?", (replacement_id,))
            conn.commit()
            return cursor.rowcount > 0

    def toggle_replacement(self, replacement_id: int, active: bool) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE replacements SET is_active = ? WHERE id = ?", (1 if active else 0, replacement_id))
            conn.commit()
            return cursor.rowcount > 0

    def learn_from_corrections(self, raw_text: str, corrected_text: str, page_name: str = "") -> List[Tuple[str, str]]:
        """
        Compares raw OCR text with user-corrected text using word sequence alignment.
        Extracts and stores learned word/phrase substitutions in the database.
        Returns a list of newly learned (raw, corrected) pairs.
        """
        raw_tokens = [w for w in re.split(r'(\s+|[.,:;!?"\'\(\)\[\]])', raw_text) if w and not w.isspace()]
        corr_tokens = [w for w in re.split(r'(\s+|[.,:;!?"\'\(\)\[\]])', corrected_text) if w and not w.isspace()]

        matcher = difflib.SequenceMatcher(None, raw_tokens, corr_tokens)
        learned = []

        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'replace':
                    raw_sub = " ".join(raw_tokens[i1:i2]).strip()
                    corr_sub = " ".join(corr_tokens[j1:j2]).strip()
                    # Learn single words or short phrases up to 3 tokens
                    if 0 < len(raw_tokens[i1:i2]) <= 3 and 0 < len(corr_tokens[j1:j2]) <= 3:
                        if raw_sub and corr_sub and raw_sub != corr_sub:
                            cursor.execute("""
                                INSERT INTO replacements (raw_text, corrected_text, count, is_active, created_at, updated_at)
                                VALUES (?, ?, 1, 1, ?, ?)
                                ON CONFLICT(raw_text) DO UPDATE SET
                                    corrected_text = excluded.corrected_text,
                                    count = replacements.count + 1,
                                    updated_at = excluded.updated_at
                            """, (raw_sub, corr_sub, now, now))
                            learned.append((raw_sub, corr_sub))

            # Record in history
            if page_name or learned:
                cursor.execute("""
                    INSERT INTO history (page_name, raw_line, corrected_line, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (page_name, raw_text[:500], corrected_text[:500], now))

            # Update vocabulary with all words in corrected text
            words = re.findall(r'[\u0590-\u05FF]{2,}', corrected_text)
            for w in set(words):
                cursor.execute("""
                    INSERT INTO vocabulary (word, frequency, category)
                    VALUES (?, 1, 'learned')
                    ON CONFLICT(word) DO UPDATE SET frequency = vocabulary.frequency + 1
                """, (w,))

            conn.commit()

        return learned

    def apply_corrections(self, text: str) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Applies all active learned corrections to the given raw OCR text.
        Sorts replacements by length (longer phrases first) to prevent partial replacements.
        Returns:
            (processed_text, applied_rules_list)
        """
        if not text:
            return "", []

        replacements = self.get_all_replacements(active_only=True)
        # Sort by length descending so longer phrases match before substrings
        replacements.sort(key=lambda r: len(r["raw_text"]), reverse=True)

        applied = []
        result = text

        for rule in replacements:
            raw = rule["raw_text"]
            corr = rule["corrected_text"]

            # If raw contains quotes or special regex chars, escape it
            pattern = re.escape(raw)
            # Match whole word boundaries in Hebrew (boundary: start/end of string, whitespace, or punctuation)
            boundary_pattern = r'(?<![\u0590-\u05FF0-9])' + pattern + r'(?![\u0590-\u05FF0-9])'

            if re.search(boundary_pattern, result):
                result = re.sub(boundary_pattern, corr, result)
                applied.append((raw, corr))

        return result, applied
