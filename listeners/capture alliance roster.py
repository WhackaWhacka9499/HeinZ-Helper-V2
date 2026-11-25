import frida
import json
import sys
import threading
from pathlib import Path

pid = int(sys.argv[1]) if len(sys.argv) > 1 else 4220
root = Path(__file__).parent
done = threading.Event()
roster_data = None
session = None

print(f"Attaching to Survival.exe (PID {pid})...")
try:
    session = frida.attach(pid)
    js_code = (root / "capture_alliance_roster.js").read_text(encoding="utf-8")
    script = session.create_script(js_code)

    def on_message(message, data):
        global roster_data
        if message['type'] == 'send':
            payload = message['payload']
            print(f"Received message kind: {payload.get('kind')}")
            if payload.get('kind') == 'alliance_roster':
                roster_data = payload
                print(f"Captured {payload.get('count')} alliance members!")
                done.set()
        elif message['type'] == 'error':
            print(f"Script Error: {message.get('description')}")
            done.set()

    script.on('message', on_message)
    script.load()

    if not done.wait(15):
        print("Timeout waiting for Lua callback. Please ensure the Alliance Members screen is open/interacted with.")
finally:
    if session:
        session.detach()
        print("Detached from process.")

if roster_data:
    out_file = root / "vs33_alliance_roster.json"
    out_file.write_text(json.dumps(roster_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved roster to {out_file}")
    
    # Also print a concise summary table
    members = roster_data.get('members', [])
    alliance = roster_data.get('alliance', {})
    print(f"\nAlliance: [{alliance.get('abbr')}] {alliance.get('name')} (Server {alliance.get('serverId')})")
    print(f"Total Members: {len(members)}\n")
    
    # Sort by total power descending
    members.sort(key=lambda m: m.get('power') or 0, reverse=True)
    print(f"{'#':<3} | {'Rank':<4} | {'HQ':<3} | {'Player Name':<20} | {'Total Power':<12} | {'Arena Power':<12} | {'UID'}")
    print("-" * 85)
    for idx, m in enumerate(members[:30], 1):
        name = (m.get('name') or '')[:18]
        rank_str = f"R{m.get('rank')}" if m.get('rank') else "R?"
        hq = m.get('mainCityLv') or '?'
        power = f"{m.get('power'):,}" if m.get('power') else "0"
        arena = f"{m.get('arenaPower'):,}" if m.get('arenaPower') else "N/A"
        uid = m.get('uid') or ''
        print(f"{idx:<3} | {rank_str:<4} | {hq:<3} | {name:<20} | {power:<12} | {arena:<12} | {uid}")
    if len(members) > 30:
        print(f"... and {len(members) - 30} more members.")
