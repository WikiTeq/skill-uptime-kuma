---
name: uptime-kuma
description: Interact with Uptime Kuma monitoring server. Use for checking monitor status, adding/removing maintenances, pausing/resuming checks, viewing heartbeat history. Triggers on mentions of Uptime Kuma, server monitoring, uptime checks, or service health monitoring.
---

# Uptime Kuma Skill

Manage Uptime Kuma monitors/maintenances via CLI wrapper around the Socket.IO API.

## Setup

Requires `uptime-kuma-api` Python package that can be installed via `pip install uptime-kuma-api`

The packages might be already preinstalled in your venv environment at `/home/node/.venv` which you
need to activate before running the script.

Environment variables:
- `UPTIME_KUMA_URL` - Server URL (e.g., `http://localhost:3001`)
- `UPTIME_KUMA_USERNAME` - Login username
- `UPTIME_KUMA_PASSWORD` - Login password

## Usage

Script location relative to the skill directory: `scripts/kuma.py`

### Commands

```bash
# Overall status summary (expensive)
python scripts/kuma.py status

# List all monitors
python scripts/kuma.py list
python scripts/kuma.py list --json

note: if you did not find the monitor user asked for in the list, or you're not sure it matches then
ask the user to confirm/clarify, do not make assumptions.

# Get specific monitor details
python scripts/kuma.py get <id>

# Pause/resume monitors
python scripts/kuma.py pause <id>
python scripts/kuma.py resume <id>

# View heartbeat history
python scripts/kuma.py heartbeats <id> --hours 24

# List notification channels
python scripts/kuma.py notifications
```

### Monitor Types

- `http` - HTTP/HTTPS endpoint
- `ping` - ICMP ping
- `port` - TCP port check
- `keyword` - HTTP + keyword search
- `dns` - DNS resolution
- `docker` - Docker container
- `push` - Push-based (passive)
- `mysql`, `postgres`, `mongodb`, `redis` - Database checks
- `mqtt` - MQTT broker
- `group` - Monitor group

### Common Workflows

**Check what's down:**
```bash
python scripts/kuma.py list  # Look for 🔴
# or
python scripts/kuma.py list --json
```

### Maintenance Commands

```bash
# List all maintenance windows
python scripts/kuma.py maint-list
# or
python scripts/kuma.py maint-list --json

# Get maintenance details
python scripts/kuma.py maint-get <id>

# Create a one-time (single) maintenance window
python scripts/kuma.py maint-add --title "Deploy v2.0" --strategy single \
  --start "2026-04-05 02:00:00" --end "2026-04-05 04:00:00" --timezone "UTC"

# Create a manual maintenance (activate/deactivate by hand)
python scripts/kuma.py maint-add --title "Emergency patch" --strategy manual

# Create a cron-based recurring maintenance (every day at 03:00 for 60min)
python scripts/kuma.py maint-add --title "Nightly backup" --strategy cron \
  --cron "0 3 * * *" --duration 60 --timezone "UTC" \
  --start "2026-04-01 00:00:00" --end "2026-12-31 23:59:59"

# Create a recurring-interval maintenance (every 7 days, 02:00-03:00)
python scripts/kuma.py maint-add --title "Weekly reboot" --strategy recurring-interval \
  --interval-day 7 --timezone "UTC" --time-start 02:00 --time-end 03:00 \
  --start "2026-04-01 00:00:00" --end "2026-12-31 23:59:59"

# Create maintenance and attach monitors in one step
python scripts/kuma.py maint-add --title "DB maintenance" --strategy single \
  --start "2026-04-05 02:00:00" --end "2026-04-05 04:00:00" --timezone "UTC" --monitors 1,3,5

# Pause/resume a maintenance window
python scripts/kuma.py maint-pause <id>
python scripts/kuma.py maint-resume <id>

# Delete a maintenance window
python scripts/kuma.py maint-delete <id>

# List monitors attached to a maintenance
python scripts/kuma.py maint-monitors <id>

# Attach monitors to an existing maintenance
python scripts/kuma.py maint-monitors <id> --add 1,2,3
```

Important: due to bug in Kuma Socket API prefer creating maintenance and then attaching a monitor in separate steps

### Maintenance Strategies

- `manual` - Activate/deactivate by hand
- `single` - One-time window with start/end
- `cron` - Cron expression + duration
- `recurring-interval` - Every N days with time range
- `recurring-weekday` - Specific weekdays with time range
- `recurring-day-of-month` - Specific days of month with time range

### Common Maintenance Workflows

**Schedule a maintenance window for specific monitors:**
```bash
python scripts/kuma.py maint-add --title "Deploy v2.0" --strategy single \
  --start "2026-04-05 02:00:00" --end "2026-04-05 04:00:00" \
  --monitors 1,2,3 --timezone "UTC"
```

**Timezone consideration:**

Check user timzeone using `date` command, always use `UTC` timezone for the API

