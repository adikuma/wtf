import json
from unittest.mock import MagicMock, patch

import pytest

from src.llm import analyze_commits, calc_cost


def test_calc_cost():
    usage = {
        "prompt_tokens": 1000,
        "completion_tokens": 500,
    }
    cost = calc_cost(usage)
    expected = 1000 * 0.0000001 + 500 * 0.0000002
    assert cost == pytest.approx(expected)


def test_calc_cost_empty():
    cost = calc_cost({})
    assert cost == 0.0


def test_analyze_commits_success(mocker):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "summary": "test summary",
                            "roast": "test roast",
                        }
                    )
                }
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
        },
    }
    mock_response.raise_for_status = MagicMock()

    mocker.patch("src.llm.requests.post", return_value=mock_response)
    mocker.patch("src.llm.settings.openrouter_api_key", "test-key")
    mocker.patch("src.llm.settings.openrouter_url", "https://test.com")
    mocker.patch("src.llm.settings.wtf_model", "test-model")
    mocker.patch("src.llm.settings.wtf_provider", "test-provider")

    response, cost = analyze_commits("test commits")

    assert response.summary == "test summary"
    assert response.roast == "test roast"
    assert cost > 0
