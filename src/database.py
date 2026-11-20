import sqlite3
import json

from pathlib import Path
from datetime import datetime


# Lokasi database
BASE_DIR = Path(__file__).resolve().parents[1]
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "aruna.db"


def get_connection():
    DB_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS assessment_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,

                emotional REAL NOT NULL,
                social REAL NOT NULL,
                psychological REAL NOT NULL,

                overall_profile TEXT NOT NULL,
                pattern_profile TEXT NOT NULL,

                recommendation_profile TEXT,
                summary TEXT,
                focus TEXT,
                recommendations TEXT,
                disclaimer TEXT
            )
        """)


def save_assessment(result):
    dimension_scores = result["dimension_scores"]
    recommendation = result["recommendation"]

    created_at = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO assessment_history (
                created_at,
                emotional,
                social,
                psychological,
                overall_profile,
                pattern_profile,
                recommendation_profile,
                summary,
                focus,
                recommendations,
                disclaimer
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            created_at,
            dimension_scores["Emotional"],
            dimension_scores["Social"],
            dimension_scores["Psychological"],
            result["overall_profile"],
            result["pattern_profile"],
            recommendation["profile_name"],
            recommendation["summary"],
            recommendation["focus"],
            json.dumps(
                recommendation["recommendations"],
                ensure_ascii=False
            ),
            recommendation["disclaimer"]
        ))

        return cursor.lastrowid


def get_assessment_history(limit=100):
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT *
            FROM assessment_history
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()

    history = []

    for row in rows:
        item = dict(row)

        item["recommendations"] = json.loads(
            item["recommendations"] or "[]"
        )

        history.append(item)

    return history


def get_assessment_by_id(assessment_id):
    with get_connection() as connection:
        row = connection.execute("""
            SELECT *
            FROM assessment_history
            WHERE id = ?
        """, (assessment_id,)).fetchone()

    if row is None:
        return None

    result = dict(row)
    result["recommendations"] = json.loads(
        result["recommendations"] or "[]"
    )

    return result