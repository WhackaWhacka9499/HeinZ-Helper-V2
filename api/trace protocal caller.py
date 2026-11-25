import frida
import sys

sys.stdout.reconfigure(encoding='utf-8')

session = frida.attach('Survival.exe')
scr = session.create_script('''
const mod = Process.getModuleByName('xlua.dll');
const nf = (name, ret, args) => new NativeFunction(mod.getExportByName(name), ret, args, {scheduling: 'exclusive'});
const top = nf('lua_gettop', 'int', ['pointer']);
const str = nf('lua_tolstring', 'pointer', ['pointer', 'int', 'pointer']);
const ptrfn = nf('lua_topointer', 'pointer', ['pointer', 'int']);
const length = Memory.alloc(8);

let handler = null;
let found = false;

Interceptor.attach(mod.getExportByName('lua_pcallk'), {
    onEnter(args) {
        if (found) return;
        const L = args[0];
        const nargs = args[1].toInt32();
        if (nargs !== 2) return;
        
        const saved = top(L);
        try {
            // Read command string
            const p = str(L, saved - 1, length);
            const sz = Number(length.readU64());
            if (sz > 0 && sz < 80) {
                const cmd = p.readUtf8String(sz);
                if (cmd && cmd.length > 2) {
                    found = true;
                    const bt = Thread.backtrace(this.context, Backtracer.ACCURATE)
                        .map(DebugSymbol.fromAddress)
                        .map(s => s.toString());
                    send({cmd: cmd, backtrace: bt});
                }
            }
        } catch (e) {
        }
    }
});
''')

res = []
scr.on('message', lambda m, d: res.append(m.get('payload')))
scr.load()
import time; time.sleep(3)
session.detach()

if res:
    print(f"Captured caller of GameMain.Protocal [{res[0].get('cmd')}]:")
    for l in res[0].get('backtrace', []):
        print("  ", l)
