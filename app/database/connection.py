import sqlite3
from pathlib import Path
from typing import Optional, Set
from app.config.settings import get_profile_db_path, DATABASE_PATH, ensure_directories_exist
from app.database.models import CREATE_TABLES_SQL

_INITIALIZED_DBS: Set[str] = set()

def get_db_connection(profile_id: Optional[str] = None) -> sqlite3.Connection:
    ensure_directories_exist()
    if profile_id:
        db_path = get_profile_db_path(profile_id)
    else:
        from app.profiles.profile_manager import profile_manager
        active_id = profile_manager.get_active_profile_id()
        db_path = get_profile_db_path(active_id) if active_id else DATABASE_PATH

    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")

    path_str = str(db_path)
    if path_str not in _INITIALIZED_DBS:
        try:
            with conn:
                conn.executescript(CREATE_TABLES_SQL)
            _INITIALIZED_DBS.add(path_str)
        except Exception:
            _INITIALIZED_DBS.add(path_str)

    return conn

def init_profile_database(profile_id: str) -> None:
    ensure_directories_exist()
    conn = get_db_connection(profile_id=profile_id)
    try:
        with conn:
            conn.executescript(CREATE_TABLES_SQL)
    finally:
        conn.close()

def init_database() -> None:
    ensure_directories_exist()
    conn = sqlite3.connect(str(DATABASE_PATH), check_same_thread=False)
    try:
        with conn:
            conn.executescript(CREATE_TABLES_SQL)
    finally:
        conn.close()
