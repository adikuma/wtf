import requests
from InquirerPy import inquirer
from rich.console import Console
from rich.prompt import Prompt

from . import storage

console = Console()

# popular models to show in selection (cheap + fast first)
POPULAR_MODELS = [
    "openai/gpt-oss-120b",
    "anthropic/claude-sonnet-4",
    "anthropic/claude-3.5-sonnet",
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "google/gemini-2.0-flash-001",
    "meta-llama/llama-3.3-70b-instruct",
    "deepseek/deepseek-chat-v3-0324",
    "deepseek/deepseek-r1",
    "qwen/qwen-2.5-72b-instruct",
    "mistralai/mistral-large-2411",
]


def fetch_models(api_key: str) -> list[dict]:
    # fetch models from openrouter api
    response = requests.get(
        "https://openrouter.ai/api/v1/models",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    response.raise_for_status()
    return response.json().get("data", [])


def filter_models(models: list[dict]) -> list[dict]:
    # filter to popular models and sort by our preferred order
    model_map = {m["id"]: m for m in models}
    filtered = []
    for model_id in POPULAR_MODELS:
        if model_id in model_map:
            filtered.append(model_map[model_id])
    return filtered


def format_price(pricing: dict) -> str:
    # format pricing as $X/$Y (input/output per 1M tokens)
    prompt = float(pricing.get("prompt", 0)) * 1_000_000
    completion = float(pricing.get("completion", 0)) * 1_000_000
    return f"${prompt:.2f}/${completion:.2f}"


def run_setup():
    # main setup flow
    console.print("\n[bold]wtf setup[/bold]\n")

    # prompt for api key
    console.print("Get your API key from: [link]https://openrouter.ai/keys[/link]\n")
    api_key = Prompt.ask("Enter your OpenRouter API key", password=True)

    if not api_key.strip():
        console.print("[red]API key cannot be empty.[/red]")
        return

    # validate by fetching models
    console.print("\n[dim]Validating...[/dim]", end=" ")
    try:
        models = fetch_models(api_key)
        console.print("[green]done[/green]\n")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            console.print("[red]invalid key[/red]")
        else:
            console.print(f"[red]error: {e}[/red]")
        return
    except Exception as e:
        console.print(f"[red]error: {e}[/red]")
        return

    # filter to popular models
    filtered = filter_models(models)
    if not filtered:
        filtered = models[:15]

    # build choices for interactive picker
    choices = []
    for model in filtered:
        price = format_price(model.get("pricing", {}))
        label = f"{model['id']:<42} {price}"
        choices.append({"name": label, "value": model["id"]})

    # interactive model picker with arrow keys
    selected_model = inquirer.select(
        message="Select a model:",
        choices=choices,
        default=choices[0]["value"],
        pointer="›",
    ).execute()

    # save config
    storage.save_config(api_key, selected_model)

    console.print(
        f"\n[green]Setup complete![/green] Using [bold]{selected_model}[/bold]"
    )
    console.print("[dim]Run `wtf` to get started.[/dim]\n")
