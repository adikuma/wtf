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
