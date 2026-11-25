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
                local lines = {}
                for k, v in pairs(CS.NetWorkAssistant) do
                    table.insert(lines, "CS.NetWorkAssistant." .. tostring(k) .. " = " .. tostring(v))
                end
                
                local inst = CS.NetWorkAssistant.Instance
                for k, v in pairs(inst) do
                    table.insert(lines, "inst." .. tostring(k) .. " = " .. tostring(v))
                end
                
                return table.concat(lines, string.char(10))
            `;
            if (loadstring(L, Memory.allocUtf8String(luaCode)) === 0) {
                if (pcall(L, 0, 1, 0) === 0) {
                    const p = str(L, top(L), length);
                    const sz = Number(length.readU64());
                    const output = p.readUtf8String(sz);
                    send({output: output});
                    done = true;
                } else {
                    const err = str(L, top(L), length).readUtf8String();
                    send({call_err: err});
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

print(res)
