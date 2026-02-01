import io
import sys
from datetime import datetime

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .models import RepoSummary, StandupResult

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
    # header
    date_str = datetime.now().strftime("%b %d, %Y")
    header = Panel(
        Text("PREVIOUSLY ON YOUR CODE...", style="bold")
        + Text(f"                 {date_str}", style="dim"),
        box=box.DOUBLE,
        border_style="bright_white",
        padding=(0, 1),
    )
    console.print(header)
    console.print()

    # repos as trees
    for repo in result.repos:
        render_repo(repo)

    # summary box
    summary_text = f"\n{result.llm_response.summary}\n\n{result.llm_response.roast}\n"
    summary = Panel(
        summary_text, box=box.DOUBLE, border_style="bright_white", padding=(1, 2)
    )
    console.print(summary)


def render_repo(repo: RepoSummary):
    # repo header line
    commit_count = len(repo.commits)
    header_line = (
        f"  {repo.name} " + "-" * (40 - len(repo.name)) + f" {commit_count} commits"
    )
    console.print(header_line, style="bold")

    # tree of commits
    for i, commit in enumerate(repo.commits):
        is_last = i == len(repo.commits) - 1
        prefix = "  +-- " if is_last else "  |-- "
        console.print(f"{prefix}{commit.message}", style="dim")

    console.print()


def render_spending(total: float):
    console.print(
        Panel(f"Total API spending: ${total:.6f}", title="Spending", box=box.ROUNDED)
    )


def render_copied():
    console.print("[dim]copied to clipboard[/dim]")
