# 12stom-talon

Telegram bot that monitors free doctor appointment slots at 12th Minsk City Clinical Dental Polyclinic ([12gksp.medtalon.by](https://12gksp.medtalon.by)).

## How it works

- Runs as a single Docker container (or directly via UV)
- Polls the clinic's API every `CHECK_INTERVAL` seconds for future days (up to `DAYS_TO_SCAN`)
- Detects free slots (online booking or via registry) for configured doctor IDs
- Sends Telegram notifications for new slots — deduplicates via a persisted `state.json`
- Exposes `/start` and `/status` bot commands

## Configuration

All via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | — | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | — | Target chat/group ID for notifications |
| `CLINIC_BASE_URL` | `https://12gksp.medtalon.by` | Clinic site base URL |
| `DOCTOR_IDS` | `1437` | Comma-separated doctor IDs to monitor |
| `DAYS_TO_SCAN` | `5` | Number of future days to check |
| `CHECK_INTERVAL` | `3600` | Seconds between checks |
| `STATE_FILE_PATH` | `state.json` | Path to state file for deduplication |

## Quick start

### Local (UV)

```bash
uv sync
uv run python app/main.py
```

### Docker

```bash
docker compose up -d --build
```

View logs:

```bash
docker compose logs -f
```

Stop:

```bash
docker compose down
```

## Project structure

```
├── app/
│   ├── __init__.py
│   ├── main.py         # Entry point — polling + background monitor loop
│   ├── bot.py          # aiogram router (/start, /status, notify)
│   ├── clinic_api.py   # Async HTTP client for the clinic API
│   ├── config.py       # pydantic-settings config
│   └── monitor.py      # Check logic + state.json persistence
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── .env.example
```
