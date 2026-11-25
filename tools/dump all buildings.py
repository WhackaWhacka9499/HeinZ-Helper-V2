import frida
import json
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

js = r"""
const mod = Process.getModuleByName('xlua.dll');
const nf = (name, ret, args) => new NativeFunction(mod.getExportByName(name), ret, args);
const top = nf('lua_gettop', 'int', ['pointer']);
const settop = nf('lua_settop', 'void', ['pointer', 'int']);
const loadstring = nf('luaL_loadstring', 'int', ['pointer', 'pointer']);
const pcall = nf('lua_pcall', 'int', ['pointer', 'int', 'int', 'int']);
const str = nf('lua_tolstring', 'pointer', ['pointer', 'int', 'pointer']);
const length = Memory.alloc(8);

function getString(L, index) {
    const p = str(L, index, length);
    const sz = Number(length.readU64());
    return sz === 0 ? '' : p.readUtf8String(sz);
}

let done = false;
Interceptor.attach(mod.getExportByName('lua_pcallk'), {
    onEnter(args) {
        if (done) return;
        done = true;
        const L = args[0];
        const saved = top(L);
        try {
            const code = `
                local function enc(val, depth)
                    depth = depth or 0
                    if depth > 4 then return '"[max]"' end
                    local t = type(val)
                    if t == "number" then return tostring(val) end
                    if t == "boolean" then return val and "true" or "false" end
                    if t == "string" then return string.format("%q", val) end
                    if t == "table" then
                        local parts = {}
                        local count = 0
                        for k, v in pairs(val) do
                            count = count + 1
                            if count > 200 then break end
                            table.insert(parts, string.format("%q:%s", tostring(k), enc(v, depth + 1)))
                        end
                        return "{" .. table.concat(parts, ",") .. "}"
                    end
                    return string.format('"%s"', tostring(val))
                end

                local buildings = {}
                if DataCenter.BuildManager and DataCenter.BuildManager.allBuilding then
                    for uuid, b in pairs(DataCenter.BuildManager.allBuilding) do
                        local itemId = b.itemId or b.buildId
                        local tpl = DataCenter.BuildTemplateManager and DataCenter.BuildTemplateManager.buildDesTemplateDic and DataCenter.BuildTemplateManager.buildDesTemplateDic[itemId]
                        local nameId = tpl and (tpl.name or tpl.buildName)
                        local line = tpl and tpl._lineData
                        local bType = tpl and tpl.type

                        table.insert(buildings, {
                            uuid = tostring(uuid),
                            itemId = itemId,
                            level = b.level,
                            state = b.state,
                            pos = b.pos,
                            nameId = nameId,
                            type = bType,
                            line = line
                        })
                    end
                end

                return enc(buildings)
            `;

            const cstr = Memory.allocUtf8String(code);
            if (loadstring(L, cstr) === 0) {
                if (pcall(L, 0, 1, 0) === 0) {
                    const res = getString(L, -1);
                    send({status: 'ok', data: res});
                } else {
                    send({status: 'pcall_err', err: getString(L, -1)});
                }
            } else {
                send({status: 'load_err', err: getString(L, -1)});
            }
        } catch(e) {
            send({status: 'exception', err: e.toString()});
        } finally {
            settop(L, saved);
        }
    }
});
"""

session = frida.attach(33632)
script = session.create_script(js)

data_out = None
def on_message(message, data):
    global data_out
    if message['type'] == 'send':
        payload = message['payload']
        if payload.get('status') == 'ok':
            try:
                data_out = json.loads(payload['data'])
            except Exception as e:
                data_out = payload['data']
        else:
            print("Error payload:", payload)

script.on('message', on_message)
script.load()

for _ in range(50):
    if data_out:
        break
    time.sleep(0.1)

session.detach()

if data_out:
    from pathlib import Path
    out_p = Path(r"data/cache/heinzy_all_buildings.json")
    out_p.write_text(json.dumps(data_out, indent=2, ensure_ascii=False), encoding='utf-8')
    b_list = list(data_out.values()) if isinstance(data_out, dict) else data_out
    print(f"Total buildings: {len(b_list)}")
