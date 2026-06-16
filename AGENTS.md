# AGENTS.md

Telegram bot that monitors free doctor appointment slots at 12th Minsk City Clinical Dental Polyclinic (`https://12gksp.medtalon.by`).

## Architecture

Single Docker container running `main.py` — aiogram polling loop + background asyncio monitor task.

```
main.py → starts aiogram polling + background asyncio task
            ├── monitor_loop() runs every CHECK_INTERVAL seconds
            │     ├── ClinicClient.get_schedule(date) → GET /api/talonbriefs/{DD.MM.YYYY}
            │     ├── checks isFree for target doctor IDs
            │     └── sends Telegram via notify_free_slots()
            └── /status command → runs check on demand
```

## Key Commands

```bash
# Local dev with UV
uv sync                    # create .venv and install deps
uv run python app/main.py  # run with .venv

# Docker
docker compose up -d --build   # build & run
docker compose logs -f         # view logs
docker compose down            # stop
```

## API Surface (discovered by inspecting site JS bundles)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `POST /` | — | Accept agreement, get session cookies |
| `GET /api/talonbriefs/{DD.MM.YYYY}` | JSON | All doctors' slots for a date |
| `GET /api/doctors` | JSON | Doctor list |
| `GET /api/talons` | JSON | Talons (needs params) |
| `GET /api/lookups/all` | JSON | Specializations |

Schedule response per doctor entry contains `hasFree` (bool) and arrays `morningTalonTimes`, `afternoonTalonTimes`, `eveningTalonTimes` with slots having `isFree` flag.

## Session Flow

1. `POST /` (empty body) → server sets `.ASPXAUTH` + `ASP.NET_SessionId` cookies
2. Include cookies in subsequent `GET /api/talonbriefs/{date}` requests
3. On 401 → re-accept agreement and retry

## Config (env vars)

| Var | Default | Description |
|-----|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | — | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | — | Target chat for notifications |
| `DOCTOR_IDS` | `1437` | Comma-separated doctor IDs |
| `DAYS_TO_SCAN` | `5` | How many future days to check |
| `CHECK_INTERVAL` | `3600` | Seconds between checks |

## Files

| File | Role |
|------|------|
| `app/config.py` | pydantic-settings, loads from env |
| `app/clinic_api.py` | Async HTTP client for clinic (httpx) |
| `app/monitor.py` | Check logic + state.json persistence |
| `app/bot.py` | aiogram router, /start, /status, notify |
| `app/main.py` | Entry point, start polling + background loop |
| `pyproject.toml` | Project metadata + deps (UV source of truth) |
| `.python-version` | Python version pin for UV |
| `state.json` | Persisted on Docker volume (`/app/data/`) |

## State

`state.json` tracks notified slot `talonDateTime` values per doctor to prevent duplicate alerts. Stored on Docker volume, survives restarts.
