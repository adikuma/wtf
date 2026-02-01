from pathlib import Path

import pytest

from src.cli import get_commits, format_for_llm
from src.models import Commit, RepoSummary


def test_get_commits_empty(mocker):
    mocker.patch("src.cli.get_git_commits", return_value=None)
    commits = get_commits("/fake/path", "author", "1 day ago")
    assert commits == []


def test_get_commits_parses_correctly(mocker):
    raw = "abc123|fix bug|2025-01-01|2025-01-01T10:00:00"
    mocker.patch("src.cli.get_git_commits", return_value=raw)

    commits = get_commits("/fake/repo", "author", "1 day ago")

    assert len(commits) == 1
    assert commits[0].hash == "abc123"
    assert commits[0].message == "fix bug"
    assert commits[0].date == "2025-01-01"


def test_get_commits_multiple_lines(mocker):
    raw = "abc123|fix bug|2025-01-01|time1\ndef456|add feature|2025-01-02|time2"
    mocker.patch("src.cli.get_git_commits", return_value=raw)

    commits = get_commits("/fake/repo", "author", "1 day ago")

    assert len(commits) == 2


def test_format_for_llm():
    summaries = [
        RepoSummary(
            name="repo1",
            path="/path/repo1",
            commits=[
                Commit(
                    hash="abc",
                    message="commit 1",
                    date="2025-01-01",
                    time="10:00",
                    repo_name="repo1",
                ),
                Commit(
                    hash="def",
                    message="commit 2",
                    date="2025-01-01",
                    time="11:00",
                    repo_name="repo1",
                ),
            ],
        )
    ]

    result = format_for_llm(summaries)

    assert "repo1 (2 commits)" in result
    assert "commit 1" in result
    assert "commit 2" in result
