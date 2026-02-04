import json

import requests

from . import storage
from .models import LLMResponse

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "anthropic/claude-3.5-sonnet"


def get_api_key() -> str:
    # get api key from config
    config = storage.load_config()
    if config and config.get("api_key"):
        return config["api_key"]
    return ""


def get_model() -> str:
    # get model from config
    config = storage.load_config()
    if config and config.get("model"):
        return config["model"]
    return DEFAULT_MODEL


SCHEMA = {
    "name": "standup",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "Standup-ready summary, 2-3 sentences max",
            },
            "roast": {
                "type": "string",
                "description": "One snarky but friendly observation",
            },
            "wip_summary": {
                "type": "string",
                "description": "1 sentence about what uncommitted changes suggest you're working on. Empty string if no diff provided.",
            },
        },
        "required": ["summary", "roast", "wip_summary"],
        "additionalProperties": False,
    },
}

SYSTEM_PROMPT = """You generate standup summaries from git commits.

Rules:
- Summary: 2-3 sentences about committed work, professional but casual
- Roast: One witty observation about patterns you notice
- WIP Summary: If diff/uncommitted changes provided, 1 sentence about what's being worked on. Empty if no diff.
- Be brief. No fluff.
- Notice: repeated fixes, vague commits, late night work, scattered focus
"""


def analyze_commits(
    commits_text: str, diff_text: str | None = None
) -> tuple[LLMResponse, float]:
    # call openrouter
    api_key = get_api_key()
    model = get_model()

    # build user message with commits and optional diff
    user_content = f"COMMITS:\n{commits_text}"
    if diff_text:
        user_content += f"\n\nUNCOMMITTED CHANGES (diff):\n{diff_text}"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "response_format": {"type": "json_schema", "json_schema": SCHEMA},
    }

    # use deepinfra provider for gpt-oss model (cheap + fast)
    if model == "openai/gpt-oss-120b":
        payload["provider"] = {"order": ["DeepInfra"]}

    response = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
    )
    response.raise_for_status()
    data = response.json()

    content = json.loads(data["choices"][0]["message"]["content"])
    usage = data.get("usage", {})
    cost = calc_cost(usage)

    return LLMResponse(**content), cost


def calc_cost(usage: dict) -> float:
    # gpt-oss-120b via deepinfra is very cheap
    prompt = usage.get("prompt_tokens", 0) * 0.0000001
    completion = usage.get("completion_tokens", 0) * 0.0000002
    return prompt + completion
