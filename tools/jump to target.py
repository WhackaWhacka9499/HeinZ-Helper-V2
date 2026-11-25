import sys, os, argparse
tools_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, tools_dir)
import importlib.util

spec = importlib.util.spec_from_file_location("cd", os.path.join(tools_dir, "client discovery.py"))
cd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cd)

def jump_camera(x: int, y: int, srv_id: int = 0, pid: int = None):
    target_pid = pid or cd.resolve_target_pid()
    if not target_pid:
        print("[-] Target game client not found")
        return False
    
    lua = f"""
    local tx = {int(x)}
    local ty = {int(y)}
    local srv = {int(srv_id)}
    
    if SceneManager and SceneManager.IsInWorld and not SceneManager:IsInWorld() then
        local inPve = (LWBattleManager and LWBattleManager.isInBattle) or false
        if not inPve and SceneManager.ChangeToWorld then
            local okW = pcall(function() SceneManager:ChangeToWorld() end)
            if not okW then pcall(SceneManager.ChangeToWorld) end
        end
    end
    
    local jumped = false
    if GoToUtil and GoToUtil.GotoWorldPos then
        if UnityEngine and UnityEngine.Vector2 and UnityEngine.Vector2.New then
            pcall(function() GoToUtil.GotoWorldPos(UnityEngine.Vector2.New(tx, ty), true) end)
            jumped = true
        end
    end
    
    if not jumped then
        local w = SceneManager and SceneManager.World
        if w and w.Camera and w.Lookat and w.TileXYToWorld then
            pcall(function() w:Lookat(w:TileXYToWorld(tx, ty)) end)
            jumped = true
        end
    end
    
    local wpm = DataCenter and DataCenter.WorldPointManager
    if wpm and wpm.DoSendViewRequest then
        pcall(function() wpm:DoSendViewRequest(tx, ty, 1, srv > 0 and srv or nil) end)
    end
    
    return jumped and string.format("JUMP_OK: %d, %d (Server %d)", tx, ty, srv) or "JUMP_FAILED"
    """
    ok, res = cd.frida_eval_lua(target_pid, lua, timeout=6.0)
    print(res if ok else f"[-] Lua error: {res}")
    return ok and "JUMP_OK" in str(res)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("x", type=int)
    parser.add_argument("y", type=int)
    parser.add_argument("--server", type=int, default=0)
    parser.add_argument("--pid", type=int, default=None)
    args = parser.parse_args()
    jump_camera(args.x, args.y, args.server, args.pid)
