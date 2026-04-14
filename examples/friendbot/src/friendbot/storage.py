import asyncio
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class KnownGroup:
    chat_id: int
    title: str | None
    username: str | None
    first_seen_at: str
    last_seen_at: str


class GroupStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self._lock = asyncio.Lock()
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS known_groups (
                chat_id INTEGER PRIMARY KEY,
                title TEXT,
                username TEXT,
                first_seen_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL
            )
            """
        )
        self.connection.commit()

    async def upsert_group(self, chat_id: int, title: str | None, username: str | None) -> bool:
        now = datetime.now(UTC).isoformat()

        async with self._lock:
            cursor = await asyncio.to_thread(
                self.connection.execute,
                "SELECT 1 FROM known_groups WHERE chat_id = ?",
                (chat_id,),
            )
            existing_row = await asyncio.to_thread(cursor.fetchone)
            await asyncio.to_thread(
                self.connection.execute,
                """
                INSERT INTO known_groups (chat_id, title, username, first_seen_at, last_seen_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(chat_id) DO UPDATE SET
                    title = excluded.title,
                    username = excluded.username,
                    last_seen_at = excluded.last_seen_at
                """,
                (chat_id, title, username, now, now),
            )
            await asyncio.to_thread(self.connection.commit)
            return existing_row is None

    async def list_chat_ids(self) -> list[int]:
        async with self._lock:
            cursor = await asyncio.to_thread(
                self.connection.execute, "SELECT chat_id FROM known_groups ORDER BY first_seen_at"
            )
            rows = await asyncio.to_thread(cursor.fetchall)
            return [row[0] for row in rows]

    async def list_groups(self) -> list[KnownGroup]:
        async with self._lock:
            cursor = await asyncio.to_thread(
                self.connection.execute,
                """
                SELECT chat_id, title, username, first_seen_at, last_seen_at
                FROM known_groups
                ORDER BY first_seen_at
                """,
            )
            rows = await asyncio.to_thread(cursor.fetchall)
            return [KnownGroup(*row) for row in rows]

    async def close(self) -> None:
        async with self._lock:
            await asyncio.to_thread(self.connection.close)
