"""Sync all 16 bracket states (689-704) to Google Drive Native Spreadsheets."""

import argparse
import importlib.util
from pathlib import Path
import sys

if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

TOOLS_DIR = Path(__file__).resolve().parent


def _load_sync_module():
    path = TOOLS_DIR / "sync bracket drive sheets.py"
    spec = importlib.util.spec_from_file_location("sync_bracket_drive_sheets", str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync all 16 bracket states (689-704) to Google Drive.")
    parser.add_argument("--states", nargs="*", default=["all"], help="Specific state IDs or 'all' (default: all 689-704)")
    parser.add_argument("--refresh-live", "--live", action="store_true", help="Refresh live rankings/rosters from game before pushing to Drive")
    parser.add_argument("--refresh-profiles", action="store_true", help="Refresh deep profiles whose power changed significantly")
    parser.add_argument("--pid", type=int, default=None, help="Target Last Z client PID")
    args = parser.parse_args()

    mod = _load_sync_module()
    if not args.states or (len(args.states) == 1 and str(args.states[0]).lower() == "all"):
        states = list(mod.ALL_BRACKET_STATES)
    else:
        states = [int(s) for s in args.states]

    summary = mod.sync_states(
        states=states,
        refresh_live=args.refresh_live,
        refresh_profiles=args.refresh_profiles,
        pid=args.pid,
    )
    print(f"Bracket Sync Complete: {summary['synced_count']} synced, {summary['error_count']} errors.")
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
