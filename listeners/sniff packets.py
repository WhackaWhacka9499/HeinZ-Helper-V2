import frida
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

js = """
const ws2 = Process.getModuleByName('WS2_32.dll');
const sendFn = ws2.getExportByName('send');
const wsaSendFn = ws2.getExportByName('WSASend');

Interceptor.attach(sendFn, {
    onEnter(args) {
        const sock = args[0].toInt32();
        const buf = args[1];
        const len = args[2].toInt32();
        if (len > 0 && len < 2000) {
            const bytes = buf.readByteArray(Math.min(len, 64));
            send({type: 'send', len: len, hex: hexdump(bytes, {offset: 0, length: Math.min(len, 32), header: false, ansi: false})});
        }
    }
});

Interceptor.attach(wsaSendFn, {
    onEnter(args) {
        const sock = args[0].toInt32();
        const lpBuffers = args[1];
        const dwBufferCount = args[2].toInt32();
        if (dwBufferCount > 0) {
            // WSABUF structure: u_long len, char *buf
            const len = lpBuffers.readU32();
            const buf = lpBuffers.add(Process.pointerSize === 8 ? 8 : 4).readPointer();
            if (len > 0 && len < 2000) {
                const bytes = buf.readByteArray(Math.min(len, 64));
                send({type: 'WSASend', len: len, hex: hexdump(bytes, {offset: 0, length: Math.min(len, 32), header: false, ansi: false})});
            }
        }
    }
});
"""

session = frida.attach('Survival.exe')
script = session.create_script(js)

def on_msg(msg, data):
    if msg['type'] == 'send':
        p = msg['payload']
        print(f"[{p['type']}] len={p['len']}\n{p['hex']}")

script.on('message', on_msg)
script.load()

print("Listening for 3 seconds...")
time.sleep(3)
session.detach()
print("Done.")
