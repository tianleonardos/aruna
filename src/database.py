"""Modul Manajemen Database SQLite ARUNA.

Menangani:
1. Autentikasi Pengguna & Hak Akses (Admin vs Mahasiswa).
2. Penyimpanan Asesmen Mahasiswa dengan Kode Unik (unique_code).
3. Manajemen Konten Website (CRUD) untuk Pengumuman, Kontak Bantuan, dan FAQ Edukasi.
"""

from __future__ import annotations

import hashlib
import json
import random
import secrets
import sqlite3
import string
from datetime import datetime
from pathlib import Path
from typing import Any

# Lokasi penyimpanan database SQLite
BASE_DIR = Path(__file__).resolve().parents[1]
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "aruna.db"


def get_connection() -> sqlite3.Connection:
    """Membuka koneksi ke database SQLite dan memastikan direktori tersedia."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def hash_password(password: str) -> str:
    """Melakukan hashing password menggunakan SHA-256."""
    salt = "aruna_pbl_tek1302_salt"
    return hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()


def generate_unique_code() -> str:
    """Menghasilkan kode unik acak untuk asesmen mahasiswa (contoh: ARN-7B2X9F)."""
    chars = string.ascii_uppercase + string.digits
    # Hilangkan karakter yang membingungkan seperti 0/O atau 1/I
    clean_chars = "".join([c for c in chars if c not in "0O1I"])
    random_part = "".join(random.choices(clean_chars, k=6))
    return f"ARN-{random_part}"


# ===========================================================================
# 1. INISIALISASI & MIGRASI DATABASE
# ===========================================================================

def initialize_database() -> None:
    """Membuat tabel-tabel utama dan melakukan migrasi kolom jika diperlukan."""
    with get_connection() as conn:
        # Tabel Pengguna (Akun Mahasiswa & Admin)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'student')),
                nim TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # Tabel Riwayat Asesmen
        conn.execute("""
            CREATE TABLE IF NOT EXISTS assessment_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unique_code TEXT UNIQUE,
                user_id INTEGER,
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
                disclaimer TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Migrasi kolom unique_code & user_id jika belum ada
        cursor = conn.execute("PRAGMA table_info(assessment_history)")
        columns = [row["name"] for row in cursor.fetchall()]

        if "unique_code" not in columns:
            conn.execute("ALTER TABLE assessment_history ADD COLUMN unique_code TEXT")
        if "user_id" not in columns:
            conn.execute("ALTER TABLE assessment_history ADD COLUMN user_id INTEGER")

        # Tabel CRUD Website: Pengumuman
        conn.execute("""
            CREATE TABLE IF NOT EXISTS website_announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Tabel CRUD Website: Kontak Bantuan & Konseling
        conn.execute("""
            CREATE TABLE IF NOT EXISTS support_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                phone TEXT NOT NULL,
                description TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            )
        """)

        # Tabel CRUD Website: FAQ Edukasi
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mental_health_faqs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                category TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            )
        """)

        # Seed Akun Admin Default jika belum ada
        admin_exists = conn.execute(
            "SELECT 1 FROM users WHERE username = 'admin'"
        ).fetchone()

        if not admin_exists:
            now_iso = datetime.now().astimezone().isoformat(timespec="seconds")
            conn.execute("""
                INSERT INTO users (username, password_hash, full_name, role, nim, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                "admin",
                hash_password("admin123"),
                "Administrator Aruna",
                "admin",
                "ADMIN-001",
                now_iso,
            ))

        # Seed data awal kontak bantuan jika masih kosong
        contact_count = conn.execute("SELECT COUNT(*) FROM support_contacts").fetchone()[0]
        if contact_count == 0:
            now_iso = datetime.now().astimezone().isoformat(timespec="seconds")
            conn.execute("""
                INSERT INTO support_contacts (name, category, phone, description, is_active, created_at)
                VALUES 
                ('Layanan Konseling Sebaya Kampus', 'Konseling Kampus', '0812-3456-7890', 'Layanan bimbingan dan konseling gratis untuk mahasiswa aktif.', 1, ?),
                ('Yayasan Pulih (Dukungan Trauma & Mental)', 'Layanan Nasional', '021-78842580', 'Konseling psikologis daring dan luring untuk pemulihan emosional.', 1, ?),
                ('Hotline Kemenkes RI (Sejiwa)', 'Layanan Darurat', '119 ext 8', 'Layanan pertolongan pertama krisis psikologis 24 jam gratis.', 1, ?)
            """, (now_iso, now_iso, now_iso))

        # Seed data awal FAQ jika masih kosong
        faq_count = conn.execute("SELECT COUNT(*) FROM mental_health_faqs").fetchone()[0]
        if faq_count == 0:
            now_iso = datetime.now().astimezone().isoformat(timespec="seconds")
            conn.execute("""
                INSERT INTO mental_health_faqs (question, answer, category, is_active, created_at)
                VALUES
                ('Apakah hasil asesmen Aruna merupakan diagnosis medis?', 'Bukan. Aruna adalah instrumen skrining dan refleksi kesejahteraan mental berdasarkan Unsupervised Learning. Hasilnya menggambarkan pola psikososial dan bukan label penyakit klinis.', 'Umum', 1, ?),
                ('Bagaimana privasi dan kerahasiaan jawaban saya?', 'Semua jawaban Anda dienkripsi dan disimpan secara lokal pada database. Identitas unik hanya Anda yang memiliki kodenya.', 'Privasi', 1, ?),
                ('Apa yang harus saya lakukan jika profil saya berada pada kategori rentan?', 'Anda dapat memanfaatkan rekomendasi yang disediakan di aplikasi dan menghubungi layanan konseling kampus atau kontak bantuan yang tercantum.', 'Bantuan', 1, ?)
            """, (now_iso, now_iso, now_iso))


# ===========================================================================
# 2. SISTEM AKUN & AUTENTIKASI (ADMIN & MAHASISWA)
# ===========================================================================

def register_user(
    username: str,
    password: str,
    full_name: str,
    role: str = "student",
    nim: str | None = None,
) -> dict[str, Any]:
    """Mendaftarkan akun baru (mahasiswa atau admin)."""
    username_clean = username.strip().lower()
    if not username_clean or not password.strip():
        raise ValueError("Username dan password tidak boleh kosong.")

    now_iso = datetime.now().astimezone().isoformat(timespec="seconds")
    p_hash = hash_password(password.strip())

    with get_connection() as conn:
        try:
            cursor = conn.execute("""
                INSERT INTO users (username, password_hash, full_name, role, nim, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                username_clean,
                p_hash,
                full_name.strip(),
                role,
                nim.strip() if nim else None,
                now_iso,
            ))
            user_id = cursor.lastrowid
            return {
                "id": user_id,
                "username": username_clean,
                "full_name": full_name.strip(),
                "role": role,
                "nim": nim,
            }
        except sqlite3.IntegrityError:
            raise ValueError(f"Username '{username_clean}' sudah digunakan. Silakan gunakan yang lain.")


def authenticate_user(username: str, password: str) -> dict[str, Any] | None:
    """Memverifikasi kredensial login pengguna. Mengembalikan info user jika valid."""
    username_clean = username.strip().lower()
    p_hash = hash_password(password.strip())

    with get_connection() as conn:
        row = conn.execute("""
            SELECT id, username, full_name, role, nim, created_at
            FROM users
            WHERE username = ? AND password_hash = ?
        """, (username_clean, p_hash)).fetchone()

        if row:
            return dict(row)
        return None


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    """Mengambil informasi pengguna berdasarkan ID."""
    with get_connection() as conn:
        row = conn.execute("SELECT id, username, full_name, role, nim, created_at FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


# ===========================================================================
# 3. PENYIMPANAN ASESMEN DENGAN KODE UNIK
# ===========================================================================

def save_assessment(result: dict[str, Any], user_id: int | None = None) -> tuple[int, str]:
    """Menyimpan hasil asesmen mahasiswa ke SQLite dengan kode unik transaksi."""
    dimension_scores = result["dimension_scores"]
    recommendation = result["recommendation"]

    created_at = datetime.now().astimezone().isoformat(timespec="seconds")
    unique_code = generate_unique_code()

    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO assessment_history (
                unique_code,
                user_id,
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            unique_code,
            user_id,
            created_at,
            dimension_scores["Emotional"],
            dimension_scores["Social"],
            dimension_scores["Psychological"],
            result["overall_profile"],
            result["pattern_profile"],
            recommendation["profile_name"],
            recommendation["summary"],
            recommendation["focus"],
            json.dumps(recommendation["recommendations"], ensure_ascii=False),
            recommendation["disclaimer"],
        ))

        return cursor.lastrowid, unique_code


def get_assessment_history(limit: int = 100, user_id: int | None = None) -> list[dict[str, Any]]:
    """Mengambil riwayat asesmen (bisa difilter per user_id)."""
    with get_connection() as conn:
        if user_id is not None:
            rows = conn.execute("""
                SELECT * FROM assessment_history
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM assessment_history
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,)).fetchall()

    history = []
    for row in rows:
        item = dict(row)
        item["recommendations"] = json.loads(item["recommendations"] or "[]")
        if not item.get("unique_code"):
            item["unique_code"] = f"ARN-LEGACY-{item['id']}"
        history.append(item)
    return history


def get_assessment_by_unique_code(unique_code: str) -> dict[str, Any] | None:
    """Mencari data asesmen berdasarkan kode unik (misal: ARN-7B2X9F)."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM assessment_history WHERE unique_code = ?",
            (unique_code.strip().upper(),),
        ).fetchone()

        if row:
            item = dict(row)
            item["recommendations"] = json.loads(item["recommendations"] or "[]")
            return item
        return None


def get_assessment_by_id(assessment_id: int) -> dict[str, Any] | None:
    """Mengambil data asesmen berdasarkan primary key ID."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM assessment_history WHERE id = ?",
            (assessment_id,),
        ).fetchone()

        if row:
            item = dict(row)
            item["recommendations"] = json.loads(item["recommendations"] or "[]")
            return item
        return None


# ===========================================================================
# 4. CRUD KONTEN WEBSITE (CMS ADMIN)
# ===========================================================================

# --- PENGUMUMAN ---
def get_announcements(active_only: bool = False) -> list[dict[str, Any]]:
    """Mengambil daftar pengumuman."""
    with get_connection() as conn:
        query = "SELECT * FROM website_announcements"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY created_at DESC"
        rows = conn.execute(query).fetchall()
        return [dict(r) for r in rows]


def add_announcement(title: str, content: str, is_active: bool = True) -> int:
    """Menambahkan pengumuman baru."""
    now_iso = datetime.now().astimezone().isoformat(timespec="seconds")
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO website_announcements (title, content, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (title.strip(), content.strip(), 1 if is_active else 0, now_iso, now_iso))
        return cursor.lastrowid


def update_announcement(announcement_id: int, title: str, content: str, is_active: bool) -> None:
    """Memperbarui pengumuman."""
    now_iso = datetime.now().astimezone().isoformat(timespec="seconds")
    with get_connection() as conn:
        conn.execute("""
            UPDATE website_announcements
            SET title = ?, content = ?, is_active = ?, updated_at = ?
            WHERE id = ?
        """, (title.strip(), content.strip(), 1 if is_active else 0, now_iso, announcement_id))


def delete_announcement(announcement_id: int) -> None:
    """Menghapus pengumuman."""
    with get_connection() as conn:
        conn.execute("DELETE FROM website_announcements WHERE id = ?", (announcement_id,))


# --- KONTAK BANTUAN ---
def get_support_contacts(active_only: bool = False) -> list[dict[str, Any]]:
    """Mengambil daftar kontak bantuan."""
    with get_connection() as conn:
        query = "SELECT * FROM support_contacts"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY id ASC"
        rows = conn.execute(query).fetchall()
        return [dict(r) for r in rows]


def add_support_contact(name: str, category: str, phone: str, description: str, is_active: bool = True) -> int:
    """Menambahkan kontak bantuan baru."""
    now_iso = datetime.now().astimezone().isoformat(timespec="seconds")
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO support_contacts (name, category, phone, description, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name.strip(), category.strip(), phone.strip(), description.strip(), 1 if is_active else 0, now_iso))
        return cursor.lastrowid


def update_support_contact(contact_id: int, name: str, category: str, phone: str, description: str, is_active: bool) -> None:
    """Memperbarui kontak bantuan."""
    with get_connection() as conn:
        conn.execute("""
            UPDATE support_contacts
            SET name = ?, category = ?, phone = ?, description = ?, is_active = ?
            WHERE id = ?
        """, (name.strip(), category.strip(), phone.strip(), description.strip(), 1 if is_active else 0, contact_id))


def delete_support_contact(contact_id: int) -> None:
    """Menghapus kontak bantuan."""
    with get_connection() as conn:
        conn.execute("DELETE FROM support_contacts WHERE id = ?", (contact_id,))


# --- FAQ EDUKASI ---
def get_faqs(active_only: bool = False) -> list[dict[str, Any]]:
    """Mengambil daftar FAQ."""
    with get_connection() as conn:
        query = "SELECT * FROM mental_health_faqs"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY id ASC"
        rows = conn.execute(query).fetchall()
        return [dict(r) for r in rows]


def add_faq(question: str, answer: str, category: str, is_active: bool = True) -> int:
    """Menambahkan FAQ baru."""
    now_iso = datetime.now().astimezone().isoformat(timespec="seconds")
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO mental_health_faqs (question, answer, category, is_active, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (question.strip(), answer.strip(), category.strip(), 1 if is_active else 0, now_iso))
        return cursor.lastrowid


def update_faq(faq_id: int, question: str, answer: str, category: str, is_active: bool) -> None:
    """Memperbarui FAQ."""
    with get_connection() as conn:
        conn.execute("""
            UPDATE mental_health_faqs
            SET question = ?, answer = ?, category = ?, is_active = ?
            WHERE id = ?
        """, (question.strip(), answer.strip(), category.strip(), 1 if is_active else 0, faq_id))


def delete_faq(faq_id: int) -> None:
    """Menghapus FAQ."""
    with get_connection() as conn:
        conn.execute("DELETE FROM mental_health_faqs WHERE id = ?", (faq_id,))
