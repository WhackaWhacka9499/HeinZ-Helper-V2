import frida
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

js = """
const ws2 = Process.getModuleByName('WS2_32.dll');
const recvFn = ws2.getExportByName('recv');

Interceptor.attach(recvFn, {
    onEnter(args) {
        this.buf = args[1];
    },
    onLeave(retval) {
        const len = retval.toInt32();
        if (len > 50 && len < 4000) {
            const bytes = this.buf.readByteArray(len);
            send({type: 'recv', len: len, hex: hexdump(bytes, {offset: 0, length: Math.min(len, 128), header: false, ansi: false})});
        }
    }
});

const mod = Process.getModuleByName('xlua.dll');
const nf = (name, ret, args) => new NativeFunction(mod.getExportByName(name), ret, args, {scheduling: 'exclusive'});
const loadstring = nf('luaL_loadstring', 'int', ['pointer', 'pointer']);
const pcall = nf('lua_pcall', 'int', ['pointer', 'int', 'int', 'int']);

let sent = false;
Interceptor.attach(mod.getExportByName('lua_pcallk'), {
    onEnter(args) {
        if (sent) return;
        const L = args[0];
        sent = true;
        const code = Memory.allocUtf8String("return SFSNetwork.SendMessage(MsgDefines.GetNewUserInfo, '1556702503000694')");
        if (loadstring(L, code) === 0) {
            pcall(L, 0, 0, 0);
            send({type: 'lua_sent'});
        }
    }
});
"""

session = frida.attach('Survival.exe')
script = session.create_script(js)

def on_msg(msg, data):
    if msg['type'] == 'send':
        p = msg['payload']
        print(f"[{p['type']}] len={p.get('len')}\n{p.get('hex')}")

script.on('message', on_msg)
script.load()

time.sleep(2)
session.detach()
