import frida
import json
import os
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

root = Path(__file__).resolve().parent
log_file = root / "observed signals.jsonl"
js_file = root / "passive signal listener.js"

print("Starting passive signal listener...")
session = frida.attach("Survival.exe")
js_code = js_file.read_text(encoding="utf-8")
script = session.create_script(js_code)

def on_message(message, data):
    if message['type'] == 'send':
        p = message['payload']
        kind = p.get('kind')
        if kind == 'attached':
            print(f"[ATTACHED] PID {p.get('pid')}: Passive listener active and waiting for signals.", flush=True)
        elif kind == 'inbound_packet':
            cmd = p.get('command')
            ts = p.get('timestamp')
            pld = p.get('payload', {})
            print(f"[PACKET] {ts} -> {cmd} | UID: {pld.get('uid') or pld.get('targetUid')} | Name: {pld.get('name') or pld.get('userName')} | Score: {pld.get('migratePower')}", flush=True)
            with log_file.open('a', encoding='utf-8') as f:
                f.write(json.dumps(p, ensure_ascii=False) + '\n')
        else:
            print(f"[SEND] {json.dumps(p, ensure_ascii=False)}", flush=True)
    elif message['type'] == 'error':
        print(f"[ERROR] {message.get('description')}", flush=True)

script.on('message', on_message)
script.load()

# Run indefinitely until cancelled or killed
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Detaching listener...")
finally:
    session.detach()
    print("Detached successfully.")
