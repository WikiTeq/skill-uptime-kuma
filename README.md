# skill-uptime-kuma

Claude Code skill for interacting with [Uptime Kuma](https://github.com/louislam/uptime-kuma) monitoring server.

Check monitor status, manage maintenances, pause/resume checks, view heartbeat history — all from your agent.

> Monitor add/edit/delete actions are intentionally disabled for safety.

## Install

```bash
npx skills add -g git@github.com:WikiTeq/skill-uptime-kuma.git
```

## Setup

Requires `uptime-kuma-api` Python package:

```bash
pip install uptime-kuma-api
```

Set environment variables:

- `UPTIME_KUMA_URL` — Server URL (e.g. `http://localhost:3001`)
- `UPTIME_KUMA_USERNAME` — Login username
- `UPTIME_KUMA_PASSWORD` — Login password

## What it can do

- List and inspect monitors
- Pause/resume monitors
- View heartbeat history
- List notification channels
- Create, pause, resume, delete maintenance windows
- Attach monitors to maintenance windows
