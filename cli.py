#!/usr/bin/env python3
"""
Simple CLI to interact with the credit application API.
Usage:
  python cli.py list
  python cli.py set-status <application_id> <status>
"""
import sys
import json
import urllib.request
import urllib.error
from argparse import ArgumentParser

BASE_URL = "http://127.0.0.1:5000"


def api_get(path):
    url = f"{BASE_URL}{path}"
    try:
        with urllib.request.urlopen(url) as resp:
            data = resp.read().decode()
            return json.loads(data)
    except urllib.error.HTTPError as e:
        print(f"Error {e.code}: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def api_patch(path, data):
    url = f"{BASE_URL}{path}"
    data_json = json.dumps(data).encode()
    req = urllib.request.Request(
        url,
        data=data_json,
        headers={"Content-Type": "application/json"},
        method="PATCH",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            resp_data = resp.read().decode()
            return json.loads(resp_data)
    except urllib.error.HTTPError as e:
        print(f"Error {e.code}: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def cmd_list(_):
    apps = api_get("/api/applications")
    if not apps:
        print("No applications found.")
        return
    # Print header
    print(f"{'ID':>4} {'Name':<20} {'Amount':>10} {'Term':>5} {'Status':<12} {'Created'}")
    print("-" * 80)
    for a in apps:
        print(
            f"{a['id']:>4} {a['name']:<20} {a['amount']:>10.2f} {a['term']:>5} {a['status']:<12} {a['created_at']}"
        )


def cmd_set_status(args):
    app_id = args.id
    status = args.status
    if status not in ("в ожидании", "одобрено", "отклонено"):
        print("Status must be one of: 'в ожидании', 'одобрено', 'отклонено'", file=sys.stderr)
        sys.exit(1)
    result = api_patch(f"/api/applications/{app_id}/status", {"status": status})
    print(f"Updated application {app_id}: status = {result['status']}")


def main():
    parser = ArgumentParser(description="Credit application CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List all applications")
    list_parser.set_defaults(func=cmd_list)

    set_status_parser = subparsers.add_parser(
        "set-status", help="Set status of an application"
    )
    set_status_parser.add_argument("id", type=int, help="Application ID")
    set_status_parser.add_argument(
        "status", help="New status (в ожидании, одобрено, отклонено)"
    )
    set_status_parser.set_defaults(func=cmd_set_status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()