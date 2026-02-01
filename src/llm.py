import json

import requests

from config import settings

from .models import LLMResponse

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
        },
        "required": ["summary", "roast"],
        "additionalProperties": False,
    },
}

SYSTEM_PROMPT = """You generate standup summaries from git commits.

Rules:
- Summary: 2-3 sentences, professional but casual
- Roast: One witty observation about patterns you notice
- Be brief. No fluff.
- Notice: repeated fixes, vague commits, late night work, scattered focus
"""


def analyze_commits(commits_text: str) -> tuple[LLMResponse, float]:
    # call openrouter with provider routing
    response = requests.post(
        settings.openrouter_url,
        headers={
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.wtf_model,
            "provider": {"order": [settings.wtf_provider]},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": commits_text},
            ],
            "response_format": {"type": "json_schema", "json_schema": SCHEMA},
        },
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
