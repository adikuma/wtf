import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import pyperclip
import typer

from . import formatter, storage
from .git import (
    find_git_repos,
    get_commit_streak,
    get_current_branch,
    get_git_commits,
    get_git_diff,
    get_git_diff_stat,
    get_git_user,
)
from .llm import analyze_commits, get_model
from .models import Commit, RepoSummary, StandupResult, TimeStats, WipSummary

app = typer.Typer(add_completion=False, invoke_without_command=True)


@app.command()
def setup():
    from .setup import run_setup

    run_setup()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    dir: Optional[Path] = typer.Option(None, "--dir", "-d"),
    here: bool = typer.Option(False, "--here", "-H"),
    days: int = typer.Option(1, "--days", "-n"),
    author: Optional[str] = typer.Option(None, "--author", "-a"),
    copy: bool = typer.Option(False, "--copy", "-c"),
    spending: bool = typer.Option(False, "--spending"),
    history: bool = typer.Option(False, "--history"),
    json_out: bool = typer.Option(False, "--json"),
):
    # if a subcommand was invoked, skip main logic
    if ctx.invoked_subcommand is not None:
        return

    # check if configured, run setup if not
    if not storage.is_configured():
        formatter.console.print("[yellow]First time? Let's set up wtf.[/yellow]")
        from .setup import run_setup

        run_setup()
        return

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
    wip_summaries = []
    all_commits = []

    for repo_path in repos:
        commits = get_commits(repo_path, git_author, f"{days} days ago")
        branch = get_current_branch(repo_path)

        if commits:
            summaries.append(
                RepoSummary(
                    name=Path(repo_path).name,
                    path=repo_path,
                    commits=commits,
                    branch=branch,
                )
            )
            all_commits.extend(commits)

        # gather wip (uncommitted changes)
        diff_stat = get_git_diff_stat(repo_path)
        if diff_stat:
            diff = get_git_diff(repo_path)
            wip_summaries.append(
                WipSummary(
                    repo_name=Path(repo_path).name,
                    files_changed=diff_stat,
                    diff_preview=diff[:2000],
                )
            )

    if not summaries and not wip_summaries:
        formatter.console.print("[yellow]No commits found.[/yellow]")
        raise typer.Exit()

    # calculate time stats
    time_stats = calculate_time_stats(all_commits)

    # get streak
    streak = get_commit_streak(scan_path, git_author) if summaries else 0

    # call llm
    commits_text = format_for_llm(summaries) if summaries else "No commits."
    diff_text = format_wip_for_llm(wip_summaries) if wip_summaries else None

    try:
        llm_response, cost = analyze_commits(commits_text, diff_text)
        storage.add_spending(cost, get_model())
    except Exception as e:
        formatter.console.print(f"[red]LLM error: {e}[/red]")
        raise typer.Exit(1)

    # build result
    result = StandupResult(
        repos=summaries,
        llm_response=llm_response,
        generated_at=datetime.now(),
        cost_usd=cost,
        wip=wip_summaries,
        time_stats=time_stats,
        streak=streak,
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


def format_wip_for_llm(wip_summaries: list[WipSummary]) -> str:
    lines = []
    for wip in wip_summaries:
        lines.append(f"\n{wip.repo_name} ({len(wip.files_changed)} files changed):")
        for f in wip.files_changed[:10]:
            lines.append(f"  {f}")
        if wip.diff_preview:
            lines.append(f"\nDiff preview:\n{wip.diff_preview[:1500]}")
    return "\n".join(lines)


def calculate_time_stats(commits: list[Commit]) -> TimeStats:
    if not commits:
        return TimeStats()

    late_night = 0
    early_morning = 0

    for c in commits:
        if c.time:
            try:
                # time is in ISO format like 2026-02-02T23:45:00+05:30
                hour = int(c.time[11:13])
                if hour >= 22 or hour < 5:
                    late_night += 1
                elif hour < 7:
                    early_morning += 1
            except (ValueError, IndexError):
                pass

    # estimate hours: rough heuristic (15 min per commit minimum)
    estimated_hours = len(commits) * 0.25

    return TimeStats(
        total_commits=len(commits),
        late_night_commits=late_night,
        early_morning_commits=early_morning,
        estimated_hours=estimated_hours,
    )


if __name__ == "__main__":
    app()
