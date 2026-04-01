#!/usr/bin/env python3
"""
Uptime Kuma CLI wrapper using uptime-kuma-api library.
Requires: `uptime-kuma-api` package

Environment variables:
  UPTIME_KUMA_URL      - Uptime Kuma server URL (e.g., http://localhost:3001)
  UPTIME_KUMA_USERNAME - Username for authentication
  UPTIME_KUMA_PASSWORD - Password for authentication

Inspired by: https://github.com/openclaw/skills/tree/main/skills/msarheed/uptime-kuma
Improved by: https://github.com/vedmaka
"""

import argparse
import json
import os
import sys
from typing import Optional  # noqa: F401
import time

try:
    from uptime_kuma_api import UptimeKumaApi, MonitorType, MaintenanceStrategy
except ImportError:
    print("Error: uptime-kuma-api not installed. Run: pip install uptime-kuma-api", file=sys.stderr)
    sys.exit(1)


def get_env_or_exit(name: str) -> str:
    """Get environment variable or exit with error."""
    value = os.environ.get(name)
    if not value:
        print(f"Error: {name} environment variable not set", file=sys.stderr)
        sys.exit(1)
    return value


def get_api() -> UptimeKumaApi:
    """Create and authenticate API connection."""
    url = get_env_or_exit("UPTIME_KUMA_URL")
    username = get_env_or_exit("UPTIME_KUMA_USERNAME")
    password = get_env_or_exit("UPTIME_KUMA_PASSWORD")
    
    api = UptimeKumaApi(
        url=url,
        timeout=60,
        #ssl_verify=False,
        wait_events=0.2
    )
    api.login(username, password)
    return api


def cmd_list_monitors(args):
    """List all monitors."""
    with get_api() as api:
        monitors = api.get_monitors()
        if args.json:
            print(json.dumps(monitors, indent=2, default=str))
        else:
            for m in monitors:
                status = "🟢" if m.get("active") else "⚫"
                print(f"{status} [{m['id']}] {m['name']} ({m['type']})")


def cmd_get_monitor(args):
    """Get details of a specific monitor."""
    with get_api() as api:
        monitor = api.get_monitor(args.id)
        print(json.dumps(monitor, indent=2, default=str))


# def cmd_add_monitor(args):
#     """Add a new monitor."""
#     monitor_types = {
#         "http": MonitorType.HTTP,
#         "https": MonitorType.HTTP,
#         "port": MonitorType.PORT,
#         "ping": MonitorType.PING,
#         "keyword": MonitorType.KEYWORD,
#         "dns": MonitorType.DNS,
#         "docker": MonitorType.DOCKER,
#         "push": MonitorType.PUSH,
#         "steam": MonitorType.STEAM,
#         "gamedig": MonitorType.GAMEDIG,
#         "mqtt": MonitorType.MQTT,
#         "sqlserver": MonitorType.SQLSERVER,
#         "postgres": MonitorType.POSTGRES,
#         "mysql": MonitorType.MYSQL,
#         "mongodb": MonitorType.MONGODB,
#         "radius": MonitorType.RADIUS,
#         "redis": MonitorType.REDIS,
#         "group": MonitorType.GROUP,
#     }
    
#     monitor_type = monitor_types.get(args.type.lower())
#     if not monitor_type:
#         print(f"Error: Unknown monitor type '{args.type}'. Valid types: {', '.join(monitor_types.keys())}", file=sys.stderr)
#         sys.exit(1)
    
#     kwargs = {
#         "type": monitor_type,
#         "name": args.name,
#     }
    
#     if args.url:
#         kwargs["url"] = args.url
#     if args.hostname:
#         kwargs["hostname"] = args.hostname
#     if args.port:
#         kwargs["port"] = args.port
#     if args.interval:
#         kwargs["interval"] = args.interval
#     if args.keyword:
#         kwargs["keyword"] = args.keyword
    
#     with get_api() as api:
#         result = api.add_monitor(**kwargs)
#         print(json.dumps(result, indent=2, default=str))


#def cmd_delete_monitor(args):
#    """Delete a monitor."""
#    with get_api() as api:
#        result = api.delete_monitor(args.id)
#        print(json.dumps(result, indent=2, default=str))


def cmd_pause_monitor(args):
    """Pause a monitor."""
    with get_api() as api:
        result = api.pause_monitor(args.id)
        print(json.dumps(result, indent=2, default=str))


def cmd_resume_monitor(args):
    """Resume a monitor."""
    with get_api() as api:
        result = api.resume_monitor(args.id)
        print(json.dumps(result, indent=2, default=str))


def cmd_status(args):
    """Get overall status summary."""
    with get_api() as api:
        monitors = api.get_monitors()
        
        total = len(monitors)
        active = sum(1 for m in monitors if m.get("active"))
        paused = total - active
        
        # Get heartbeats for status
        up = 0
        down = 0
        pending = 0
        
        for m in monitors:
            if not m.get("active"):
                continue

            print(f"Fetching beats for monitor: {m.get('name')} url: {m.get('url')} ..")
            time.sleep(0.1)

            beats = api.get_monitor_beats(m["id"], 1)
            if beats:
                status = beats[0].get("status")
                if status == 1:
                    up += 1
                elif status == 0:
                    down += 1
                else:
                    pending += 1
            else:
                pending += 1
        
        if args.json:
            print(json.dumps({
                "total": total,
                "active": active,
                "paused": paused,
                "up": up,
                "down": down,
                "pending": pending
            }, indent=2))
        else:
            print(f"📊 Uptime Kuma Status")
            print(f"   Total monitors: {total}")
            print(f"   Active: {active} | Paused: {paused}")
            print(f"   🟢 Up: {up} | 🔴 Down: {down} | ⏳ Pending: {pending}")


def cmd_heartbeats(args):
    """Get recent heartbeats for a monitor."""
    with get_api() as api:
        beats = api.get_monitor_beats(args.id, args.hours)
        if args.json:
            print(json.dumps(beats, indent=2, default=str))
        else:
            for b in beats[-10:]:  # Show last 10
                status = "🟢" if b.get("status") == 1 else "🔴"
                time = b.get("time", "?")
                ping = b.get("ping", "?")
                print(f"{status} {time} - {ping}ms")


def cmd_notifications(args):
    """List notification channels."""
    with get_api() as api:
        notifications = api.get_notifications()
        if args.json:
            print(json.dumps(notifications, indent=2, default=str))
        else:
            for n in notifications:
                active = "✓" if n.get("active") else "✗"
                print(f"[{active}] [{n['id']}] {n['name']} ({n['type']})")


# --- Maintenance commands ---

MAINTENANCE_STRATEGIES = {
    "manual": MaintenanceStrategy.MANUAL,
    "single": MaintenanceStrategy.SINGLE,
    "cron": MaintenanceStrategy.CRON,
    "recurring-interval": MaintenanceStrategy.RECURRING_INTERVAL,
    "recurring-weekday": MaintenanceStrategy.RECURRING_WEEKDAY,
    "recurring-day-of-month": MaintenanceStrategy.RECURRING_DAY_OF_MONTH,
}


def cmd_list_maintenance(args):
    """List all maintenance windows."""
    with get_api() as api:
        maintenances = api.get_maintenances()
        if args.json:
            print(json.dumps(maintenances, indent=2, default=str))
        else:
            if not maintenances:
                print("No maintenance windows found.")
                return
            for m in maintenances:
                active = "🟢" if m.get("active") else "⚫"
                status = m.get("status", "unknown")
                strategy = str(m.get("strategy", "")).split(".")[-1].split("'")[0]
                print(f"{active} [{m['id']}] {m['title']} ({strategy}) - {status}")


def cmd_get_maintenance(args):
    """Get details of a specific maintenance window."""
    with get_api() as api:
        maintenance = api.get_maintenance(args.id)
        print(json.dumps(maintenance, indent=2, default=str))


def cmd_add_maintenance(args):
    """Add a new maintenance window."""
    strategy = MAINTENANCE_STRATEGIES.get(args.strategy)
    if not strategy:
        print(f"Error: Unknown strategy '{args.strategy}'. Valid: {', '.join(MAINTENANCE_STRATEGIES.keys())}", file=sys.stderr)
        sys.exit(1)

    kwargs = {
        "title": args.title,
        "description": args.description or "",
        "strategy": strategy,
        "active": True,
        "intervalDay": args.interval_day or 1,
        "dateRange": [],
        "weekdays": [],
        "daysOfMonth": [],
    }

    # Date range: start/end for single or recurring strategies
    if args.start:
        kwargs["dateRange"].append(args.start)
    if args.end:
        kwargs["dateRange"].append(args.end)

    # Time range for recurring strategies
    if args.time_start and args.time_end:
        def parse_time(t):
            parts = t.split(":")
            return {"hours": int(parts[0]), "minutes": int(parts[1]), "seconds": int(parts[2]) if len(parts) > 2 else 0}
        kwargs["timeRange"] = [parse_time(args.time_start), parse_time(args.time_end)]

    # Cron-specific
    if args.cron:
        kwargs["cron"] = args.cron
    if args.duration:
        kwargs["durationMinutes"] = args.duration

    # Weekdays (0=Sun, 6=Sat)
    if args.weekdays:
        kwargs["weekdays"] = [int(d) for d in args.weekdays.split(",")]

    # Days of month
    if args.days_of_month:
        kwargs["daysOfMonth"] = [int(d) for d in args.days_of_month.split(",")]

    if args.timezone:
        kwargs["timezoneOption"] = args.timezone

    with get_api() as api:
        result = api.add_maintenance(**kwargs)
        maint_id = result.get("maintenanceID")
        print(json.dumps(result, indent=2, default=str))

        # Attach monitors if specified
        if args.monitors and maint_id:
            monitor_ids = [{"id": int(mid)} for mid in args.monitors.split(",")]
            api.add_monitor_maintenance(maint_id, monitor_ids)
            print(f"Attached monitors: {args.monitors}")


def cmd_delete_maintenance(args):
    """Delete a maintenance window."""
    with get_api() as api:
        result = api.delete_maintenance(args.id)
        print(json.dumps(result, indent=2, default=str))


def cmd_pause_maintenance(args):
    """Pause a maintenance window."""
    with get_api() as api:
        result = api.pause_maintenance(args.id)
        print(json.dumps(result, indent=2, default=str))


def cmd_resume_maintenance(args):
    """Resume a maintenance window."""
    with get_api() as api:
        result = api.resume_maintenance(args.id)
        print(json.dumps(result, indent=2, default=str))


def cmd_maintenance_monitors(args):
    """List or add monitors to a maintenance window."""
    with get_api() as api:
        if args.add:
            monitor_ids = [{"id": int(mid)} for mid in args.add.split(",")]
            result = api.add_monitor_maintenance(args.id, monitor_ids)
            print(json.dumps(result, indent=2, default=str))
        else:
            monitors = api.get_monitor_maintenance(args.id)
            print(json.dumps(monitors, indent=2, default=str))


def main():
    parser = argparse.ArgumentParser(description="Uptime Kuma CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # list
    p_list = subparsers.add_parser("list", help="List all monitors")
    p_list.add_argument("--json", action="store_true", help="Output as JSON")
    p_list.set_defaults(func=cmd_list_monitors)
    
    # get
    p_get = subparsers.add_parser("get", help="Get monitor details")
    p_get.add_argument("id", type=int, help="Monitor ID")
    p_get.set_defaults(func=cmd_get_monitor)
    
    # # add
    # p_add = subparsers.add_parser("add", help="Add a new monitor")
    # p_add.add_argument("--name", required=True, help="Monitor name")
    # p_add.add_argument("--type", required=True, help="Monitor type (http, ping, port, etc.)")
    # p_add.add_argument("--url", help="URL to monitor (for HTTP)")
    # p_add.add_argument("--hostname", help="Hostname (for ping/port)")
    # p_add.add_argument("--port", type=int, help="Port number")
    # p_add.add_argument("--interval", type=int, default=60, help="Check interval in seconds")
    # p_add.add_argument("--keyword", help="Keyword to search (for keyword type)")
    # p_add.set_defaults(func=cmd_add_monitor)
    
    # delete
    #p_del = subparsers.add_parser("delete", help="Delete a monitor")
    #p_del.add_argument("id", type=int, help="Monitor ID")
    #p_del.set_defaults(func=cmd_delete_monitor)
    
    # pause
    p_pause = subparsers.add_parser("pause", help="Pause a monitor")
    p_pause.add_argument("id", type=int, help="Monitor ID")
    p_pause.set_defaults(func=cmd_pause_monitor)
    
    # resume
    p_resume = subparsers.add_parser("resume", help="Resume a monitor")
    p_resume.add_argument("id", type=int, help="Monitor ID")
    p_resume.set_defaults(func=cmd_resume_monitor)
    
    # status
    p_status = subparsers.add_parser("status", help="Get overall status")
    p_status.add_argument("--json", action="store_true", help="Output as JSON")
    p_status.set_defaults(func=cmd_status)
    
    # heartbeats
    p_hb = subparsers.add_parser("heartbeats", help="Get heartbeats for a monitor")
    p_hb.add_argument("id", type=int, help="Monitor ID")
    p_hb.add_argument("--hours", type=int, default=24, help="Hours of history")
    p_hb.add_argument("--json", action="store_true", help="Output as JSON")
    p_hb.set_defaults(func=cmd_heartbeats)
    
    # notifications
    p_notif = subparsers.add_parser("notifications", help="List notification channels")
    p_notif.add_argument("--json", action="store_true", help="Output as JSON")
    p_notif.set_defaults(func=cmd_notifications)

    # --- Maintenance subcommands ---

    # maintenance list
    p_mlist = subparsers.add_parser("maint-list", help="List all maintenance windows")
    p_mlist.add_argument("--json", action="store_true", help="Output as JSON")
    p_mlist.set_defaults(func=cmd_list_maintenance)

    # maintenance get
    p_mget = subparsers.add_parser("maint-get", help="Get maintenance details")
    p_mget.add_argument("id", type=int, help="Maintenance ID")
    p_mget.set_defaults(func=cmd_get_maintenance)

    # maintenance add
    p_madd = subparsers.add_parser("maint-add", help="Add a maintenance window")
    p_madd.add_argument("--title", required=True, help="Maintenance title")
    p_madd.add_argument("--description", help="Maintenance description")
    p_madd.add_argument("--strategy", required=True,
                        choices=list(MAINTENANCE_STRATEGIES.keys()),
                        help="Schedule strategy")
    p_madd.add_argument("--start", help="Start datetime (YYYY-MM-DD HH:MM:SS)")
    p_madd.add_argument("--end", help="End datetime (YYYY-MM-DD HH:MM:SS)")
    p_madd.add_argument("--time-start", help="Daily time start (HH:MM or HH:MM:SS)")
    p_madd.add_argument("--time-end", help="Daily time end (HH:MM or HH:MM:SS)")
    p_madd.add_argument("--cron", help="Cron expression (for cron strategy)")
    p_madd.add_argument("--duration", type=int, help="Duration in minutes (for cron strategy)")
    p_madd.add_argument("--interval-day", type=int, help="Interval in days (for recurring-interval)")
    p_madd.add_argument("--weekdays", help="Comma-separated weekdays 0-6, 0=Sun (for recurring-weekday)")
    p_madd.add_argument("--days-of-month", help="Comma-separated days 1-31 (for recurring-day-of-month)")
    p_madd.add_argument("--timezone", help="Timezone (e.g. Europe/Berlin)")
    p_madd.add_argument("--monitors", help="Comma-separated monitor IDs to attach")
    p_madd.set_defaults(func=cmd_add_maintenance)

    # maintenance delete
    p_mdel = subparsers.add_parser("maint-delete", help="Delete a maintenance window")
    p_mdel.add_argument("id", type=int, help="Maintenance ID")
    p_mdel.set_defaults(func=cmd_delete_maintenance)

    # maintenance pause
    p_mpause = subparsers.add_parser("maint-pause", help="Pause a maintenance window")
    p_mpause.add_argument("id", type=int, help="Maintenance ID")
    p_mpause.set_defaults(func=cmd_pause_maintenance)

    # maintenance resume
    p_mresume = subparsers.add_parser("maint-resume", help="Resume a maintenance window")
    p_mresume.add_argument("id", type=int, help="Maintenance ID")
    p_mresume.set_defaults(func=cmd_resume_maintenance)

    # maintenance monitors (list/add monitors to a maintenance)
    p_mmon = subparsers.add_parser("maint-monitors", help="List or add monitors to a maintenance")
    p_mmon.add_argument("id", type=int, help="Maintenance ID")
    p_mmon.add_argument("--add", help="Comma-separated monitor IDs to attach")
    p_mmon.set_defaults(func=cmd_maintenance_monitors)

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    #try:
    args.func(args)
    #except Exception as e:
    #    print(f"Error: {e}", file=sys.stderr)
    #    sys.exit(1)


if __name__ == "__main__":
    main()
