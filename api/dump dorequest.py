import frida
import sys

sys.stdout.reconfigure(encoding='utf-8')

session = frida.attach('Survival.exe')
scr = session.create_script('''
const mod = Process.getModuleByName('xlua.dll');
const nf = (name, ret, args) => new NativeFunction(mod.getExportByName(name), ret, args, {scheduling: 'exclusive'});
const top = nf('lua_gettop', 'int', ['pointer']);
const settop = nf('lua_settop', 'void', ['pointer', 'int']);
const loadstring = nf('luaL_loadstring', 'int', ['pointer', 'pointer']);
const pcall = nf('lua_pcall', 'int', ['pointer', 'int', 'int', 'int']);
const str = nf('lua_tolstring', 'pointer', ['pointer', 'int', 'pointer']);
const length = Memory.alloc(8);

let done = false;
Interceptor.attach(mod.getExportByName('lua_pcallk'), {
    onEnter(args) {
        if (done) return;
        const L = args[0];
        const saved = top(L);
        try {
            const luaCode = `
                local helper = package.loaded["Loading.LoginAddrHelper"] or {}
                -- Dump string of DoRequest
                local dumped = string.dump(helper.DoRequest)
                -- Base64 or hex encode dumped bytecode
                local b = {}
                for i = 1, #dumped do
                    table.insert(b, string.format("%02x", string.byte(dumped, i)))
                end
                return table.concat(b, " ")
            `;
            if (loadstring(L, Memory.allocUtf8String(luaCode)) === 0) {
                if (pcall(L, 0, 1, 0) === 0) {
                    const p = str(L, top(L), length);
                    const sz = Number(length.readU64());
                    const output = p.readUtf8String(sz);
                    send({bytecode_hex: output});
                    done = true;
                }
            }
        } catch (e) {
            send({error: String(e)});
        } finally {
            settop(L, saved);
        }
    }
});
''')

res = []
scr.on('message', lambda m, d: res.append(m.get('payload')))
scr.load()
import time; time.sleep(1)
session.detach()

if res and 'bytecode_hex' in res[0]:
    hex_str = res[0]['bytecode_hex']
    raw = bytes.fromhex(hex_str.replace(" ", ""))
    with open(r"data/cache/DoRequest.luac", "wb") as f:
        f.write(raw)
    print(f"Dumped DoRequest.luac ({len(raw)} bytes)")
