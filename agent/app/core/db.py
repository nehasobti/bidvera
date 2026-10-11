"""Checkpointer persistence factory for LangGraph workflows.

Supports PostgreSQL (when configured), persistent disk-backed checkpoint storage (default for local development),
and in-memory fallback for isolated unit tests.
"""

from __future__ import annotations

import logging
import pickle
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    ChannelVersions,
    Checkpoint,
    CheckpointMetadata,
)
from langgraph.checkpoint.memory import MemorySaver

from agent.app.core.settings import settings

logger = logging.getLogger(__name__)


class PersistentDiskSaver(MemorySaver):
    """A disk-backed checkpoint saver that supports both synchronous and asynchronous operations.

    It maintains compatibility with LangGraph's sync (`get_state`, `get_tuple`) and async
    (`ainvoke`, `astream`, `aget_tuple`) APIs while persisting state snapshots across server restarts.
    """

    def __init__(self, file_path: Path | str | None = None) -> None:
        super().__init__()
        self.file_path = Path(file_path or (Path.cwd() / "data" / "checkpoints.pkl"))
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        if self.file_path.exists():
            try:
                with open(self.file_path, "rb") as f:
                    storage_dict, writes_dict, blobs_dict = pickle.load(f)
                    self.storage.update(storage_dict)
                    self.writes.update(writes_dict)
                    self.blobs.update(blobs_dict)
                logger.info(f"Loaded existing checkpoints from {self.file_path}")
            except Exception as e:
                logger.warning(f"Could not load checkpoints from {self.file_path}: {e}")

    def _save_to_disk(self) -> None:
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            temp_path = self.file_path.with_suffix(".tmp")
            with open(temp_path, "wb") as f:
                pickle.dump((dict(self.storage), dict(self.writes), dict(self.blobs)), f)
            temp_path.replace(self.file_path)
        except Exception as e:
            logger.warning(f"Could not save checkpoints to {self.file_path}: {e}")

    def put(
        self,
        config: dict[str, Any],
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> dict[str, Any]:
        result = super().put(config, checkpoint, metadata, new_versions)
        self._save_to_disk()
        return result

    async def aput(
        self,
        config: dict[str, Any],
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> dict[str, Any]:
        result = await super().aput(config, checkpoint, metadata, new_versions)
        self._save_to_disk()
        return result

    def put_writes(
        self,
        config: dict[str, Any],
        writes: Sequence[tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        super().put_writes(config, writes, task_id, task_path)
        self._save_to_disk()

    async def aput_writes(
        self,
        config: dict[str, Any],
        writes: Sequence[tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        await super().aput_writes(config, writes, task_id, task_path)
        self._save_to_disk()


_disk_saver: PersistentDiskSaver | None = None


def get_checkpointer() -> BaseCheckpointSaver:
    """Returns a persistent checkpointer.

    1. PostgresSaver if DATABASE_URL is configured.
    2. PersistentDiskSaver in data/checkpoints.pkl (survives app restarts).
    3. MemorySaver as fallback.
    """
    global _disk_saver

    # 1. PostgreSQL Checkpointer
    db_url = settings.database_url
    if db_url and "postgresql" in db_url:
        try:
            from langgraph.checkpoint.postgres import PostgresSaver

            saver = PostgresSaver.from_conn_string(db_url)
            saver.setup()
            logger.info("Successfully connected to PostgreSQL checkpointer.")
            return saver
        except Exception as e:
            logger.warning(
                f"Failed to connect to PostgreSQL checkpointer ({e}). Falling back to PersistentDiskSaver."
            )

    # 2. Persistent Disk Checkpointer (data/checkpoints.pkl)
    try:
        if _disk_saver is None:
            _disk_saver = PersistentDiskSaver()
        return _disk_saver
    except Exception as exc:
        logger.warning(
            f"Failed to initialize PersistentDiskSaver ({exc}). Falling back to MemorySaver."
        )
        return MemorySaver()
