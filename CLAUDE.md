# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project summary

This repository contains a Python 3.11 terminal narrative game managed with `uv`.

The current version provides:
- a CLI entrypoint exposed as `cligame`
- one built-in short branching story (`first_story`)
- a JSON-based story loading pipeline
- a dedicated ending presentation flow with per-ending terminal art
- a shared ending audio asset currently used by all endings
- tests, PRD, and a lightweight technical design document

The user wants this repository managed with `uv` for dependency changes and command execution.

## Commands

### Sync environment

```bash
uv sync
```

### Run the game

Play the default built-in story:

```bash
uv run cligame play
```

List built-in stories:

```bash
uv run cligame list-stories
```

Play muted:

```bash
uv run cligame play --mute
```

Load an external story file:

```bash
uv run cligame play --story-file path/to/story.json
```

### Tests and lint

Run all tests:

```bash
uv run pytest
```

Run lint:

```bash
uv run ruff check .
```

## Architecture

### Runtime flow

- `src/cligame/cli.py` parses commands and selects a built-in or external story source.
- `src/cligame/story_loader.py` loads and validates story JSON into typed models.
- `src/cligame/game.py` runs the main loop and switches to a dedicated ending sequence when an ending node is reached.
- `src/cligame/renderer.py` owns terminal presentation through `rich`, including ending art loading and ending-page rendering.
- `src/cligame/audio.py` defines the audio abstraction; Windows currently uses a simple player for the shared ending mp3, while muted or unsupported environments fall back to a no-op implementation.

### Content model

Stories are stored as JSON node graphs under `src/cligame/content/stories/`.

Current format:
- top-level fields: `id`, `title`, `intro`, `start_node`, `nodes`
- non-ending nodes contain `choices`
- ending nodes contain `ending_title`, `ending`, and may contain `ending_art`
- every `next` target must resolve to an existing node id

Keep story content structure-driven. Do not hardcode branching story logic into Python unless there is a strong reason.

### Asset layout

- `src/cligame/content/audio/endings/shared_ending.mp3` — shared ending audio used by all current endings
- `src/cligame/content/art/endings/*.txt` — per-ending terminal art resources
- `semantic-library.md` — root writing corpus and style reference
- `src/cligame/content/corpus/semantic-library.md` — package-local note describing corpus usage

Prefer moving runtime assets into `src/cligame/content/` rather than leaving them in the repository root.

## Important files

- `pyproject.toml` — packaging, script entrypoint, pytest configuration, dev tools
- `main.py` — thin compatibility shim to the package CLI
- `src/cligame/cli.py` — main command entrypoint
- `src/cligame/game.py` — game session loop and ending flow
- `src/cligame/story_loader.py` — story loading and validation
- `src/cligame/models.py` — story data structures
- `src/cligame/content/stories/first_story.json` — first playable story
- `src/cligame/content/audio/endings/shared_ending.mp3` — current ending audio asset
- `src/cligame/content/art/endings/` — ending art assets
- `docs/prd.md` — first-version product requirements
- `docs/technical-design.md` — first-version technical design

## Implementation notes

- Prefer standard-library solutions unless the task clearly benefits from another dependency.
- Keep dependency changes aligned with `uv` usage and lockfile updates.
- For new story content, preserve the separation between corpus/reference material and structured playable story files.
- For new ending effects, prefer resource files and story metadata over hardcoded strings.
- If you add new commands, tests, or tooling, update both `README.md` and this file so the documented workflow stays accurate.
