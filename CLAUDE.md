# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project summary

This repository is now a command-driven terminal containment game managed with `uv`.

Current playable content is the first-night prototype of **Threshold Protocol / 门限协议**:
- the player is under a 04:00 deadline
- gameplay revolves around terminal commands, module decisions, evidence capture, and protocol execution
- a senior mentor figure guides the opening flow but may know more than he should
- front-stage gameplay uses looping background music
- endings still use the shared ending audio asset

## Commands

### Sync environment

```bash
uv sync
```

### Run the game

```bash
uv run cligame play
```

Muted run:

```bash
uv run cligame play --mute
```

List playable content:

```bash
uv run cligame list-stories
```

### Tests and lint

```bash
uv run pytest
uv run ruff check .
```

## Architecture

### Runtime flow

- `src/cligame/cli.py` starts the first-night session, starts looping BGM, and switches to ending audio when the session finishes.
- `src/cligame/game.py` contains `FirstNightEngine`, the command-driven state machine.
- `src/cligame/models.py` defines module/task/protocol/game-state models.
- `src/cligame/renderer.py` renders the incident console HUD, command outputs, and ending screen.
- `src/cligame/audio.py` handles Windows audio playback for looping BGM and ending sound, while muted or unsupported environments fall back to a no-op implementation.

### Content layout

- `src/cligame/first_night_data.py` — static first-night definitions (modules, tasks, protocols, mentor lines, relay messages)
- `src/cligame/content/first_night/files/` — readable terminal files for the first night
- `src/cligame/content/audio/bgm/background_loop.mp3` — looping gameplay background music
- `src/cligame/content/audio/endings/shared_ending.mp3` — shared ending audio
- `src/cligame/content/art/endings/*.txt` — ending art assets
- `semantic-library.md` — style/lore phrase bank
- `剧本内容.md` — high-level story/product design reference

## Important design rules

- Prefer command-driven interaction over numeric branching.
- The game is about decision-making under time pressure, not just reading eerie prose.
- Player actions should change time, module state, accessible information, identity state, and available final protocols.
- Keep runtime assets in `src/cligame/content/`.
- Keep `semantic-library.md` as style/source material rather than the primary runtime script format.
- Keep gameplay BGM under `audio/bgm/` and ending sounds under `audio/endings/`.

## Current first-night priorities

- clear opening objective
- senior-led onboarding
- offline recorder as the first key tool
- conflicting information sources
- restore/isolate tradeoffs
- self-sacrifice-heavy protocol endings
- looping BGM during front-stage play with a clean cut to ending audio

If you extend the game, preserve those pillars unless the user explicitly changes direction.
