import subprocess
import time
import base64
import frida
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

now = int(time.time())
token = base64.b64encode(f"{now}|LZ".encode('utf-8')).decode('utf-8')
arg = f"--from-launcher={token}"

exe_path = r"G:\Last Z\Game\FarmGame.exe"
work_dir = r"G:\Last Z\Game"

js_sniffer = """
const ws2 = Process.getModuleByName('WS2_32.dll');
const sendFn = ws2.getExportByName('send');

Interceptor.attach(sendFn, {
    onEnter(args) {
        const sock = args[0].toInt32();
        const buf = args[1];
        const len = args[2].toInt32();
        if (len > 0) {
            const bytes = buf.readByteArray(len);
            send({type: 'send', len: len, raw: Array.from(new Uint8Array(bytes))});
        }
    }
});
"""

print("[Full Packet Capture] Starting FarmGame.exe with early Frida injection...")
proc = subprocess.Popen(
    [exe_path, arg, "-screen-width", "640", "-screen-height", "360", "-screen-fullscreen", "0"],
    cwd=work_dir
)

time.sleep(1)
session = frida.attach(proc.pid)
script = session.create_script(js_sniffer)

captured_packets = []
def on_msg(msg, data):
    if msg['type'] == 'send':
        p = msg['payload']
        # If it's an SFS packet (starts with 0x80)
        if p['raw'] and p['raw'][0] == 0x80:
            print(f"[Captured SFS Packet] len={p['len']}")
            captured_packets.append(p['raw'])

script.on('message', on_msg)
script.load()

print("[Full Packet Capture] Listening for 10 seconds...")
time.sleep(10)

session.detach()
proc.terminate()
try:
    proc.wait(timeout=3)
except:
    proc.kill()

print(f"[Full Packet Capture] Total SFS packets captured: {len(captured_packets)}")

if len(captured_packets) >= 2:
    p2 = captured_packets[1]
    print(f"Packet 2 full length: {len(p2)} bytes")
    with open(r"data/cache/packet2_full.bin", "wb") as f:
        f.write(bytes(p2))
    print("Saved scratch/packet2_full.bin successfully!")
