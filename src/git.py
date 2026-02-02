import os
import subprocess


def find_git_repos(start_path):
    # find all git repositories in directory and subdirectories
    repos = []
    for root, dirs, files in os.walk(start_path):
        if ".git" in dirs:
            repos.append(root)
            # skip searching inside .git folders
            dirs[:] = [d for d in dirs if d != ".git"]
    return repos


def get_git_user():
    # fetch configured git user name
    try:
        user = subprocess.check_output(["git", "config", "user.name"]).decode().strip()
    except subprocess.CalledProcessError:
        user = None
    return user


def get_git_email():
    # fetch configured git user email
    try:
        email = (
            subprocess.check_output(["git", "config", "user.email"]).decode().strip()
        )
    except subprocess.CalledProcessError:
        email = None
    return email


def get_git_branch():
    # fetch current git branch
    try:
        branch = (
            subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            .decode()
            .strip()
        )
    except subprocess.CalledProcessError:
        branch = None
    return branch


def get_git_status():
    # fetch current git status
    try:
        status = (
            subprocess.check_output(["git", "status", "--porcelain"]).decode().strip()
        )
    except subprocess.CalledProcessError:
        status = None
    return status


def get_git_commits(repo_path, author, start_date):
    # fetch git commits for author and date range
    # format: hash|message|date|iso_time
    try:
        commits = (
            subprocess.check_output(
                [
                    "git",
                    "log",
                    "--author",
                    author,
                    "--since",
                    start_date,
                    "--pretty=format:%h|%s|%ad|%aI",
                    "--date=short",
                ],
                cwd=repo_path,
            )
            .decode()
            .strip()
        )
    except subprocess.CalledProcessError:
        commits = None
    return commits


def get_git_diff(repo_path: str) -> str:
    # get uncommitted changes (staged + unstaged)
    try:
        diff = (
            subprocess.check_output(
                ["git", "diff", "HEAD"],
                cwd=repo_path,
                stderr=subprocess.DEVNULL,
            )
            .decode(errors="replace")
            .strip()
        )
    except subprocess.CalledProcessError:
        diff = ""
    return diff


def get_git_diff_stat(repo_path: str) -> list[str]:
    # get file change summary (M/A/D with filenames)
    try:
        status = (
            subprocess.check_output(
                ["git", "status", "--porcelain"],
                cwd=repo_path,
            )
            .decode()
            .strip()
        )
    except subprocess.CalledProcessError:
        return []

    if not status:
        return []

    files = []
    for line in status.split("\n"):
        if line.strip():
            files.append(line.strip())
    return files


def get_current_branch(repo_path: str) -> str:
    # get current branch name
    try:
        branch = (
            subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=repo_path,
            )
            .decode()
            .strip()
        )
    except subprocess.CalledProcessError:
        branch = ""
    return branch


def get_commit_streak(repo_path: str, author: str) -> int:
    # count consecutive days with commits (including today)
    from datetime import datetime, timedelta

    try:
        # get all commit dates for author in last 30 days
        output = (
            subprocess.check_output(
                [
                    "git",
                    "log",
                    "--author",
                    author,
                    "--since",
                    "30 days ago",
                    "--pretty=format:%ad",
                    "--date=short",
                ],
                cwd=repo_path,
            )
            .decode()
            .strip()
        )
    except subprocess.CalledProcessError:
        return 0

    if not output:
        return 0

    # get unique dates
    dates = set(output.split("\n"))
    today = datetime.now().date()

    # count streak from today backwards
    streak = 0
    check_date = today
    while True:
        date_str = check_date.strftime("%Y-%m-%d")
        if date_str in dates:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    return streak
