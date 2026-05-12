# TJM Home Task

A desktop automation pipeline that fetches posts from a REST API and writes each one into Notepad using GUI automation — locating the Notepad icon on the desktop via a vision-language model (VLM) grounding system instead of hardcoded coordinates.

---
## Annotated Screenshots

- [Top Left](screenshots/annotated_top_left.png)
- [Bottom Right](screenshots/annotated_bottom_right.png)
- [Center 1](screenshots/annotated_center_1.png)
- [Center 2](screenshots/annotated_center_2.png)

---

## Project Structure

```
tmj-home-task/
│
├── main.py                    # Entry point — orchestrates the full pipeline
├── config.py                  # Project-wide paths and constants
├── pyproject.toml             # Dependencies (uv)
├── posts.json                 # Cached posts (fallback when API is unavailable)
├── screenshots/               # Annotated debug screenshots (auto-created)
│
└── src/
    ├── builder.py             # Factory functions for clients and strategies
    ├── data_source.py         # Fetches posts from API, falls back to cache
    ├── screen.py              # Screenshot capture and annotated image saving
    ├── notepad_driver.py      # Notepad GUI automation (type, save, close)
    ├── window_validator.py    # Polls for window focus / window disappearance
    │
    └── grounder/              # VLM-based GUI element grounding subsystem
        ├── prompts.py         # Prompt templates for the grounding model
        ├── types.py           # BBox and Viewport data classes
        │
        ├── providers/         # Model client abstraction layer
        │   ├── base.py        # Abstract ModelClient, ModelRequest, ModelResponse
        │   ├── openrouter.py  # OpenRouter implementation
        │   ├── openai.py      # OpenAI implementation
        │   └── _common.py     # Shared utility: base64 image encoding
        │
        ├── roles/
        │   └── grounder.py    # Calls the provider, parses JSON bbox, denormalize coords
        │
        └── strategies/        # Pluggable grounding algorithms
            ├── base.py        # Abstract GroundingStrategy
            ├── direct.py      # Single-pass grounding
            └── reground.py    # Two-pass grounding: full screen ground → model optimal res precise reground
```

---

## Configuration

`config.py` defines all shared paths:

| Constant | Value |
|---|---|
| `POSTS_API_URL` | `https://jsonplaceholder.typicode.com/posts` |
| `POSTS_CACHE_PATH` | `posts.json` (repo root) |
| `PROJECT_DIR` | `~/Desktop/tjm-project/` |
| `ANNOTATION_DIR` | `screenshots/` (repo root) |

Environment variables (`.env`):

| Variable | Purpose |
|---|---|
| `OPENROUTER_API_KEY` | API key for OpenRouter |

---

## Pipeline Overview

```
fetch_posts()
    │
    ▼
process_post(post)
    │
    ├── captureScreenshot()          # PIL Image of the full desktop
    │
    ├── build_strategy('reground')   # Selects grounding algorithm
    │       └── Grounder(client)     # Wraps the VLM provider
    │
    ├── strategy.ground(screenshot, target_description)
    │       └── returns BBox (pixel coords on screen)
    │
    ├── save_annotated_screenshot()  # Saves debug PNG to screenshots/
    │
    ├── moveTo(x, y) + doubleClick() # Open Notepad
    │
    ├── type_post_content()          # Paste title + body
    │
    └── save_as() + close()          # Save .txt file, close window
```

---

## Grounding Subsystem

The grounding subsystem locates a UI element on a screenshot by asking a vision-language model to return a bounding box, then converts that to screen pixel coordinates.

### Layer Architecture

```
GroundingStrategy          (strategies/)
    │  Defines how to approach the given image
    │
    ▼
Grounder                   (roles/grounder.py)
    │  Formats the prompt, calls the provider, parses the JSON response,
    │  and denormalises the 0-1000 bbox into pixel coordinates
    │
    ▼
ModelClient                (providers/)
    │  Handles the actual HTTP call to the VLM API
    │  Returns raw ModelResponse(text, parsed_json)
    │
    ▼
VLM API (OpenRouter)
```

---

### Grounding Strategies

#### Direct (`strategies/direct.py`)

Single model call on the full screenshot. Fast, less precise for small icons.

```
screenshot ──► Grounder.ground() ──► BBox
```

#### Reground (`strategies/reground.py`)

Two-pass approach for higher precision on small targets:

1. **First Pass** — run `Grounder` on the full screenshot to get an approximate center.
2. **Crop** — extract a `crop_size × crop_size` (default 1024 px) window centred on that point.
3. **Fine pass** — run `Grounder` again on the crop (larger apparent target → better bbox).
4. **Translate** — use `Viewport.to_screen()` to convert the local crop bbox back to full-screen coordinates.

---

### Provider: OpenRouter (`providers/openrouter.py`)


- Image encoded as base64 PNG and sent as `image_url` content part.
- Model response expected as a JSON object: `{"bbox": [x1, y1, x2, y2]}` in 0–1000 normalised space.
- `ModelClient.execute()` retries up to 3 times on failure.

Default model: `qwen/qwen3-vl-32b-instruct`

---

### Prompt (`prompts.py`)

The model is instructed to return only a JSON object:

```
{"bbox": [x1, y1, x2, y2]}   — target found
{"bbox": null}                 — target not visible
```

---

## Debug Annotations

After each grounding call, `save_annotated_screenshot()` writes a PNG to `screenshots/post_{id}_annotated.png` showing:

- **Red rectangle** — the predicted bounding box
- **Red circle** — the computed click point (bbox center)

---


## Setup

```bash
# Install dependencies (requires uv)
uv sync

# Copy and fill in your API key
cp .env.example .env

# Run
uv run main.py
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `openai` | Chat Completions client (used against OpenRouter) |
| `pillow` | Screenshot annotation (ImageDraw) |
| `pyautogui` | Screenshot capture, mouse/keyboard automation |
| `pygetwindow` | Window title polling |
| `pyperclip` | Clipboard-based text input into Notepad |
| `python-dotenv` | `.env` loading |
| `requests` | Posts API fetch |
