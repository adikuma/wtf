from datetime import datetime

from pydantic import BaseModel


class Commit(BaseModel):
    hash: str
    message: str
    date: str
    time: str
    repo_name: str


class RepoSummary(BaseModel):
    name: str
    path: str
    commits: list[Commit]
    branch: str = ""


class WipSummary(BaseModel):
    repo_name: str
    files_changed: list[str]
    diff_preview: str


class TimeStats(BaseModel):
    total_commits: int = 0
    late_night_commits: int = 0
    early_morning_commits: int = 0
    estimated_hours: float = 0.0


class LLMResponse(BaseModel):
    summary: str
    roast: str
    wip_summary: str | None = None


class StandupResult(BaseModel):
    repos: list[RepoSummary]
    llm_response: LLMResponse
    generated_at: datetime
    cost_usd: float
    wip: list[WipSummary] = []
    time_stats: TimeStats | None = None
    streak: int = 0
