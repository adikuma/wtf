# WTF - What The (F)iles Did I Work On?

A CLI tool that tells you what you worked on yesterday - with personality.

## What It Does

`wtf` scans your git repositories, finds your recent commits, and generates a standup-ready summary with snarky commentary. No more staring at `git log` trying to remember what you did.

## Installation

```bash
# local development
uv sync
uv run wtf

# or install globally
uv pip install -e .
wtf
```

## Usage

```bash
# basic - scan current directory for all repos
wtf

# only current repo (not recursive)
wtf --here

# scan specific directory
wtf --dir ~/projects

# look back N days
wtf --days 3

# filter by author
wtf --author "Your Name"

# copy standup to clipboard
wtf --copy

# view past standups
wtf --history

# show cumulative API spending
wtf --spending

# output as JSON
wtf --json
```

## Configuration

Set your API key in `.env`:

```bash
OPENROUTER_API_KEY=your-key-here
```

Optional settings:

```bash
WTF_MODEL=openai/gpt-oss-120b
WTF_PROVIDER=deepinfra/fp4
OPENROUTER_URL=https://openrouter.ai/api/v1/chat/completions
```

## Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--dir PATH` | `-d` | Scan a specific directory |
| `--here` | `-H` | Only scan current repo, not subdirectories |
| `--days N` | `-n` | Look back N days (default: 1) |
| `--author NAME` | `-a` | Filter by author (default: git config user.name) |
| `--copy` | `-c` | Copy standup summary to clipboard |
| `--history` | | View past standups |
| `--spending` | | Show cumulative API costs |
| `--json` | | Output as JSON |
