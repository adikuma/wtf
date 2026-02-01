import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from src import storage
from src.models import Commit, LLMResponse, RepoSummary, StandupResult


def make_standup_result():
    return StandupResult(
        repos=[
            RepoSummary(
                name="test-repo",
                path="/path/to/repo",
                commits=[
                    Commit(
                        hash="abc123",
                        message="test commit",
                        date="2025-01-01",
                        time="10:00",
                        repo_name="test-repo",
                    )
                ],
            )
        ],
        llm_response=LLMResponse(
            summary="test summary",
            roast="test roast",
        ),
        generated_at=datetime.now(),
        cost_usd=0.001,
    )


def test_save_and_load_standup():
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(storage, "WTF_DIR", Path(tmpdir)):
            with patch.object(storage, "HISTORY_DIR", Path(tmpdir) / "history"):
                with patch.object(
                    storage, "SPENDING_FILE", Path(tmpdir) / "spending.json"
                ):
                    result = make_standup_result()
                    storage.save_standup(result)

                    history = storage.load_history()
                    assert len(history) == 1
                    assert history[0].llm_response.summary == "test summary"


def test_spending_tracking():
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(storage, "WTF_DIR", Path(tmpdir)):
            with patch.object(storage, "HISTORY_DIR", Path(tmpdir) / "history"):
                with patch.object(
                    storage, "SPENDING_FILE", Path(tmpdir) / "spending.json"
                ):
                    storage.add_spending(0.001, "test-model")
                    storage.add_spending(0.002, "test-model")

                    total = storage.get_total_spent()
                    assert total == pytest.approx(0.003)


def test_load_spending_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(storage, "SPENDING_FILE", Path(tmpdir) / "nonexistent.json"):
            records = storage.load_spending()
            assert records == []
