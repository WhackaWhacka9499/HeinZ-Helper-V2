import frida
import sys

sys.stdout.reconfigure(encoding='utf-8')

js = """
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
                local net = require("Net.SFSNetwork")
                local mgr = require("Net.NetworkManager")
                local lines = {}
                table.insert(lines, "=== SFSNetwork ===")
                for k, v in pairs(net) do
                    table.insert(lines, "SFS." .. tostring(k) .. " = " .. tostring(v))
                end
                table.insert(lines, "=== NetworkManager ===")
                for k, v in pairs(mgr) do
                    table.insert(lines, "NM." .. tostring(k) .. " = " .. tostring(v))
                end
                return table.concat(lines, "\\n")
            `;
            if (loadstring(L, Memory.allocUtf8String(luaCode)) === 0) {
                if (pcall(L, 0, 1, 0) === 0) {
                    const p = str(L, top(L), length);
                    const sz = Number(length.readU64());
                    const output = p.readUtf8String(sz);
                    send({output: output});
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
"""

session = frida.attach('Survival.exe')
script = session.create_script(js)
res = []
script.on('message', lambda m, d: res.append(m))
script.load()

import time; time.sleep(1)
session.detach()

if res and res[0].get('payload', {}).get('output'):
    print(res[0]['payload']['output'])
else:
    print(res)
