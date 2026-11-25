import frida
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

js = """
const ws2 = Process.getModuleByName('WS2_32.dll');
const sendFn = ws2.getExportByName('send');

Interceptor.attach(sendFn, {
    onEnter(args) {
        const sock = args[0].toInt32();
        const buf = args[1];
        const len = args[2].toInt32();
        if (len > 5 && len < 2000) {
            const bytes = buf.readByteArray(len);
            send({type: 'send', len: len, hex: hexdump(bytes, {offset: 0, length: len, header: false, ansi: false})});
        }
    }
});

const mod = Process.getModuleByName('xlua.dll');
const nf = (name, ret, args) => new NativeFunction(mod.getExportByName(name), ret, args, {scheduling: 'exclusive'});
const top = nf('lua_gettop', 'int', ['pointer']);
const settop = nf('lua_settop', 'void', ['pointer', 'int']);
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
