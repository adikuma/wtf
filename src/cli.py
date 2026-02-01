import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import pyperclip
import typer

from config import settings

from . import formatter, storage
from .git import find_git_repos, get_git_commits, get_git_user
from .llm import analyze_commits
from .models import Commit, RepoSummary, StandupResult

app = typer.Typer(add_completion=False)


@app.command()
def main(
    dir: Optional[Path] = typer.Option(None, "--dir", "-d"),
    here: bool = typer.Option(False, "--here", "-H"),
    days: int = typer.Option(1, "--days", "-n"),
    author: Optional[str] = typer.Option(None, "--author", "-a"),
    copy: bool = typer.Option(False, "--copy", "-c"),
    spending: bool = typer.Option(False, "--spending"),
    history: bool = typer.Option(False, "--history"),
    json_out: bool = typer.Option(False, "--json"),
):
    # handle --spending
    if spending:
        total = storage.get_total_spent()
        formatter.render_spending(total)
        return

    # handle --history
    if history:
        past = storage.load_history()
        for item in past:
            formatter.console.print(f"[dim]{item.generated_at}[/dim]")
            formatter.console.print(item.llm_response.summary)
            formatter.console.print()
        return

    # main flow
    scan_path = str(dir) if dir else "."
    git_author = author or get_git_user() or "unknown"

    # handle monday (show fri-sun)
    if datetime.now().weekday() == 0:
        days = max(days, 3)

    # find repos and commits
    if here:
        repos = [scan_path]
    else:
        repos = find_git_repos(scan_path)

    summaries = []
    for repo_path in repos:
        commits = get_commits(repo_path, git_author, f"{days} days ago")
        if commits:
            summaries.append(
                RepoSummary(name=Path(repo_path).name, path=repo_path, commits=commits)
            )

    if not summaries:
        formatter.console.print("[yellow]No commits found.[/yellow]")
        raise typer.Exit()

    # call llm
    commits_text = format_for_llm(summaries)

    try:
        llm_response, cost = analyze_commits(commits_text)
        storage.add_spending(cost, settings.wtf_model)
    except Exception as e:
        formatter.console.print(f"[red]LLM error: {e}[/red]")
        raise typer.Exit(1)

    # build result
    result = StandupResult(
        repos=summaries,
        llm_response=llm_response,
        generated_at=datetime.now(),
        cost_usd=cost,
    )

    # save to history
    storage.save_standup(result)

    # output
    if json_out:
        print(
            json.dumps(
                {
                    "summary": result.llm_response.summary,
                    "roast": result.llm_response.roast,
                    "repos": [
                        {"name": r.name, "commits": len(r.commits)} for r in summaries
                    ],
                },
                indent=2,
            )
        )
    else:
        formatter.render(result)

    # copy to clipboard
    if copy:
        pyperclip.copy(result.llm_response.summary)
        formatter.render_copied()


def get_commits(repo_path: str, author: str, since: str) -> list[Commit]:
    raw = get_git_commits(repo_path, author, since)
    if not raw:
        return []

    commits = []
    for line in raw.split("\n"):
        if "|" in line:
            parts = line.split("|")
            commits.append(
                Commit(
                    hash=parts[0],
                    message=parts[1],
                    date=parts[2] if len(parts) > 2 else "",
                    time=parts[3] if len(parts) > 3 else "",
                    repo_name=Path(repo_path).name,
                )
            )
    return commits


def format_for_llm(summaries: list[RepoSummary]) -> str:
    lines = []
    for s in summaries:
        lines.append(f"\n{s.name} ({len(s.commits)} commits):")
        for c in s.commits:
            lines.append(f"  - {c.message}")
    return "\n".join(lines)


if __name__ == "__main__":
    app()
