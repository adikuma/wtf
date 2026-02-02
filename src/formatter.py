import io
import sys
from datetime import datetime

from rich.console import Console

from .models import RepoSummary, StandupResult, WipSummary

# force utf-8 for windows (skip during tests)
if sys.platform == "win32" and "pytest" not in sys.modules:
    try:
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
    except Exception:
        pass

console = Console(force_terminal=True)


def render(result: StandupResult):
    # header - clean, no box
    date_str = datetime.now().strftime("%b %d, %Y")
    console.print()
    console.print(
        f"[bold cyan]PREVIOUSLY ON YOUR CODE...[/bold cyan]  [dim]{date_str}[/dim]"
    )

    # streak
    if result.streak > 1:
        console.print(f"  [yellow]* {result.streak} day streak[/yellow]")

    console.print("[dim]" + "─" * 60 + "[/dim]")
    console.print()

    # repos as trees
    for repo in result.repos:
        render_repo(repo)

    # wip section
    if result.wip:
        render_wip(result.wip)

    # branches
    branches = list(set(r.branch for r in result.repos if r.branch))
    if len(branches) > 1:
        console.print(f"   [dim]branches: {', '.join(branches)}[/dim]")
        console.print()

    # time stats
    if result.time_stats and result.time_stats.late_night_commits > 0:
        console.print(
            f"   [dim]* {result.time_stats.late_night_commits} late night commits[/dim]"
        )
        console.print()

    # summary - clean, no box
    console.print("[dim]" + "─" * 60 + "[/dim]")
    console.print()
    console.print(f"  {result.llm_response.summary}")

    # wip summary from llm
    if result.llm_response.wip_summary:
        console.print()
        console.print(
            f"  [magenta]Currently working on:[/magenta] {result.llm_response.wip_summary}"
        )

    console.print()
    console.print(f"  [dim italic]{result.llm_response.roast}[/dim italic]")
    console.print()


def render_repo(repo: RepoSummary):
    # repo header line
    commit_count = len(repo.commits)
    branch_str = f" ({repo.branch})" if repo.branch else ""
    console.print(
        f"   [bold]{repo.name}[/bold]{branch_str} [dim]─── {commit_count} commits[/dim]"
    )

    # tree of commits
    for i, commit in enumerate(repo.commits):
        is_last = i == len(repo.commits) - 1
        prefix = "  └─" if is_last else "  ├─"
        console.print(f"  {prefix} [dim]{commit.message}[/dim]")

    console.print()


def render_wip(wip_list: list[WipSummary]):
    console.print("   [bold magenta][wip][/bold magenta]")
    for wip in wip_list:
        console.print(
            f"   {wip.repo_name} [dim]─── {len(wip.files_changed)} files changed[/dim]"
        )
        for i, f in enumerate(wip.files_changed[:5]):
            is_last = i == len(wip.files_changed[:5]) - 1
            prefix = "  └─" if is_last else "  ├─"
            console.print(f"  {prefix} [dim]{f}[/dim]")
        if len(wip.files_changed) > 5:
            console.print(f"  [dim]   ... and {len(wip.files_changed) - 5} more[/dim]")
    console.print()


def render_spending(total: float):
    console.print(f"[dim]Total API spending: ${total:.6f}[/dim]")


def render_copied():
    console.print("[dim]copied to clipboard[/dim]")
