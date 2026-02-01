import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from src.git import find_git_repos, get_git_commits, get_git_user


def test_find_git_repos_empty_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        repos = find_git_repos(tmpdir)
        assert repos == []


def test_find_git_repos_with_git_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        # create a fake .git directory
        git_dir = Path(tmpdir) / ".git"
        git_dir.mkdir()

        repos = find_git_repos(tmpdir)
        assert len(repos) == 1
        assert repos[0] == tmpdir


def test_find_git_repos_nested():
    with tempfile.TemporaryDirectory() as tmpdir:
        # create nested repos
        repo1 = Path(tmpdir) / "repo1"
        repo1.mkdir()
        (repo1 / ".git").mkdir()

        repo2 = Path(tmpdir) / "subdir" / "repo2"
        repo2.mkdir(parents=True)
        (repo2 / ".git").mkdir()

        repos = find_git_repos(tmpdir)
        assert len(repos) == 2


def test_get_git_commits_invalid_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = get_git_commits(tmpdir, "anyone", "1 day ago")
        assert result is None


def test_get_git_user_returns_string_or_none():
    result = get_git_user()
    assert result is None or isinstance(result, str)
