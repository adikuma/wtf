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


class LLMResponse(BaseModel):
    summary: str
    roast: str


class StandupResult(BaseModel):
    repos: list[RepoSummary]
    llm_response: LLMResponse
    generated_at: datetime
    cost_usd: float
