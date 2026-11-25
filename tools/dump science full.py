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
                            if count > 500 then break end
                            table.insert(parts, string.format("%q:%s", tostring(k), enc(v, depth + 1)))
                        end
                        return "{" .. table.concat(parts, ",") .. "}"
                    end
                    return string.format('"%s"', tostring(val))
                end

                local sciTpls = {}
                if DataCenter.ScienceTemplateManager and DataCenter.ScienceTemplateManager.scienceTemplateDic then
                    for id, tpl in pairs(DataCenter.ScienceTemplateManager.scienceTemplateDic) do
                        local nameId = tpl.name or tpl.scienceName
                        local tabId = tpl.tabId or tpl.tab
                        local maxLv = tpl.maxLevel or tpl.maxLv or tpl.limitLevel
                        local line = tpl._lineData
                        
                        sciTpls[tostring(id)] = {
                            id = id,
                            nameId = nameId,
                            tabId = tabId,
                            maxLv = maxLv,
                            line = line
                        }
                    end
                end

                -- Also let's check all user sciences with full details
                local userSci = {}
                if DataCenter.ScienceDataManager and DataCenter.ScienceDataManager.allScience then
                    for id, s in pairs(DataCenter.ScienceDataManager.allScience) do
                        local lv = s.level or s.lv or (type(s) == "number" and s) or 0
                        local tpl = DataCenter.ScienceTemplateManager and DataCenter.ScienceTemplateManager.scienceTemplateDic and DataCenter.ScienceTemplateManager.scienceTemplateDic[id]
                        userSci[tostring(id)] = {
                            id = id,
                            level = lv,
                            tabId = tpl and (tpl.tabId or tpl.tab),
                            nameId = tpl and (tpl.name or tpl.scienceName)
                        }
                    end
                end

                return enc({
                    tpls = sciTpls,
                    userSci = userSci
                })
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

if isinstance(data_out, dict):
    from pathlib import Path
    out_p = Path(r"data/cache/science_tpls_and_user.json")
    out_p.write_text(json.dumps(data_out, indent=2, ensure_ascii=False), encoding='utf-8')
    print("Saved science tpls & user to:", out_p)
    print(f"Total science templates: {len(data_out.get('tpls', {}))}")
    print(f"Total user sciences: {len(data_out.get('userSci', {}))}")
else:
    print("Raw output:", str(data_out)[:500])
