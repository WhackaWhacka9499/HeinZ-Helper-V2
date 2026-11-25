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

                local items = {}
                if DataCenter.ItemData and DataCenter.ItemData.ItemInfos then
                    for uuid, item in pairs(DataCenter.ItemData.ItemInfos) do
                        local iId = item.itemId or item.id
                        local tpl = DataCenter.ItemTemplateManager and DataCenter.ItemTemplateManager.itemDic and DataCenter.ItemTemplateManager.itemDic[tonumber(iId)]
                        local nameKey = tpl and (tpl.name or tpl.itemName)
                        local itemType = tpl and (tpl.itemType or tpl.type)
                        local quality = tpl and tpl.quality
                        local descKey = tpl and tpl.desc

                        table.insert(items, {
                            uuid = tostring(uuid),
                            itemId = tonumber(iId),
                            count = item.count or item.num or item.itemNum,
                            nameKey = nameKey and tostring(nameKey) or "",
                            descKey = descKey and tostring(descKey) or "",
                            itemType = itemType,
                            quality = quality
                        })
                    end
                end

                return enc(items)
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
    out_p = Path(r"data/cache/heinzy_all_inventory_items.json")
    out_p.write_text(json.dumps(data_out, indent=2, ensure_ascii=False), encoding='utf-8')
    items = list(data_out.values()) if isinstance(data_out, dict) else data_out
    print(f"Saved {len(items)} inventory items to {out_p}")
    for it in items[:15]:
        print(f"Item {it.get('itemId')} | Count: {it.get('count')} | NameKey: {it.get('nameKey')} | Type: {it.get('itemType')}")
