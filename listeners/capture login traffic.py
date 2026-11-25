import subprocess
import time
import base64
import frida
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
const recvFn = ws2.getExportByName('recv');

Interceptor.attach(sendFn, {
    onEnter(args) {
        const sock = args[0].toInt32();
        const buf = args[1];
        const len = args[2].toInt32();
        if (len > 0) {
            const bytes = buf.readByteArray(len);
            send({type: 'send', len: len, hex: hexdump(bytes, {offset: 0, length: Math.min(len, 256), header: false, ansi: false})});
        }
    }
});

Interceptor.attach(recvFn, {
    onEnter(args) {
        this.buf = args[1];
    },
    onLeave(retval) {
        const len = retval.toInt32();
        if (len > 0) {
            const bytes = this.buf.readByteArray(len);
            send({type: 'recv', len: len, hex: hexdump(bytes, {offset: 0, length: Math.min(len, 256), header: false, ansi: false})});
        }
    }
});
"""

print("Starting FarmGame.exe with early Frida injection...")
proc = subprocess.Popen(
    [exe_path, arg, "-screen-width", "640", "-screen-height", "360", "-screen-fullscreen", "0"],
    cwd=work_dir
)

# Attach immediately
time.sleep(1)
session = frida.attach(proc.pid)
script = session.create_script(js_sniffer)

packets = []
def on_msg(msg, data):
    if msg['type'] == 'send':
        p = msg['payload']
        print(f"[{p['type']}] len={p['len']}")
        print(p['hex'])
        packets.append(p)

script.on('message', on_msg)
script.load()

print("Sniffing network traffic for 12 seconds...")
time.sleep(12)

session.detach()
proc.terminate()
try:
    proc.wait(timeout=3)
except:
    proc.kill()

print(f"Done. Captured {len(packets)} packets.")
