# wtf-dev

A CLI tool that tells you what you worked on - with personality.

## Install

```bash
pip install wtf-dev
```

## Setup

```bash
wtf setup
```

This will prompt for your OpenRouter API key and let you pick a model.

## Usage

```bash
# what did I do today?
wtf

# look back N days
wtf --days 3

# only current repo
wtf --here

# copy to clipboard
wtf --copy
```

## Features

- **Standup summary** - LLM-generated summary of your commits
- **WIP tracking** - Shows uncommitted changes + what you're currently working on
- **Streak counter** - Track your commit streak
- **Late night detection** - Spots those 2am coding sessions
- **Branch context** - Shows which branches you touched
- **History** - View past standups with `wtf --history`
- **Cost tracking** - Track API spending with `wtf --spending`

## Output

```
PREVIOUSLY ON YOUR CODE...  Feb 02, 2026
  * 5 day streak
────────────────────────────────────────────────────────────

   ai-platform (main) ─── 2 commits
  ├─ feat(sdr): add langsmith tracing
  └─ feat(sdr): add automatic follow-up

   [wip]
   ai-platform ─── 3 files changed
  ├─ M src/api/routes.py
  └─ A src/new_feature.py

────────────────────────────────────────────────────────────

  Added LangSmith tracing and automatic follow-up for stale
  conversations in the SDR pipeline.

  Currently working on: Adding new API routes for validation.

  Two features down, infinite bugs to go.
```

## Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--dir PATH` | `-d` | Scan a specific directory |
| `--here` | `-H` | Only current repo |
| `--days N` | `-n` | Look back N days (default: 1) |
| `--author NAME` | `-a` | Filter by author |
| `--copy` | `-c` | Copy to clipboard |
| `--history` | | View past standups |
| `--spending` | | Show API costs |
| `--json` | | Output as JSON |
