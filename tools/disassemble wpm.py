import struct

OP54 = [
    "MOVE","LOADI","LOADF","LOADK","LOADKX","LOADFALSE","LFALSESKIP","LOADTRUE","LOADNIL",
    "GETUPVAL","SETUPVAL","GETTABUP","GETTABLE","GETI","GETFIELD","SETTABUP","SETTABLE","SETI","SETFIELD",
    "NEWTABLE","SELF","ADDI","ADDK","SUBK","MULK","MODK","POWK","DIVK","IDIVK","BANDK","BORK","BXORK",
    "SHLI","SHRI","ADD","SUB","MUL","MOD","POW","DIV","IDIV","BAND","BOR","BXOR","SHL","SHR",
    "MMBIN","MMBINI","MMBINK","UNM","BNOT","NOT","LEN","CONCAT","CLOSE","TBC","JMP","EQ","LT","LE",
    "EQK","EQI","LTI","LEI","GTI","GEI","TEST","TESTSET","CALL","TAILCALL","RETURN","RETURN0","RETURN1",
    "FORLOOP","FORPREP","TFORPREP","TFORCALL","TFORLOOP","SETLIST","CLOSURE","VARARG","VARARGPREP","EXTRAARG"
]

def parse54(data):
    pos = 33
    def r_byte():
        nonlocal pos
        b = data[pos]; pos += 1; return b
    def r_varint():
        nonlocal pos
        x = 0
        while True:
            b = data[pos]; pos += 1
            x = (x << 7) | (b & 0x7F)
            if b & 0x80: return x
    def r_str():
        nonlocal pos
        sz = r_varint()
        if sz == 0: return ""
        s = data[pos:pos+sz-1].decode("utf-8", errors="replace")
        pos += sz - 1
        return s
    def r_proto():
        nonlocal pos
        src = r_str()
        linedef = r_varint()
        lastline = r_varint()
        nparams = r_byte()
        is_vararg = r_byte()
        maxstack = r_byte()
        ncode = r_varint()
        code = [struct.unpack_from("<I", data, pos + i*4)[0] for i in range(ncode)]
        pos += ncode * 4
        nk = r_varint()
        consts = []
        for _ in range(nk):
            t = r_byte()
            if t == 0: consts.append(None)
            elif t == 1: consts.append(False)
            elif t == 17: consts.append(True)
            elif t == 3:
                consts.append(struct.unpack_from("<q", data, pos)[0]); pos += 8
            elif t == 19:
                consts.append(struct.unpack_from("<d", data, pos)[0]); pos += 8
            elif t in (4, 20):
                consts.append(r_str())
            else:
                consts.append(f"?t={t}")
        nup = r_varint()
        for _ in range(nup): pos += 3
        np = r_varint()
        for _ in range(np): r_proto()
        nline = r_varint()
        pos += nline
        nabs = r_varint()
        for _ in range(nabs): r_varint(); r_varint()
        nloc = r_varint()
        locs = [(r_str(), r_varint(), r_varint()) for _ in range(nloc)]
        nupn = r_varint()
        upns = [r_str() for _ in range(nupn)]
        return {"linedef": linedef, "lastline": lastline, "code": code, "consts": consts, "locs": locs, "upns": upns}
    return r_proto()

def disasm54(name, p):
    print(f"\n- {name} (L{p['linedef']}-{p['lastline']}) -")
    print("  Locals:", [f"R{i}:{l[0]}(pc {l[1]}..{l[2]})" for i, l in enumerate(p["locs"])])
    print("  Upvals:", [f"U{i}:{u}" for i, u in enumerate(p["upns"])])
    print("  Consts:", [f"K{i}:{repr(c)}" for i, c in enumerate(p["consts"])])
    for pc, ins in enumerate(p["code"]):
        op = ins & 0x7F
        A = (ins >> 7) & 0xFF
        k = (ins >> 15) & 0x1
        B = (ins >> 16) & 0xFF
        C = (ins >> 24) & 0xFF
        Bx = (ins >> 15) & 0x1FFFF
        sBx = Bx - 65535
        sJ = (ins >> 7) - 16777215
        opname = OP54[op] if op < len(OP54) else f"OP_{op}"
        def kc(idx):
            return f"K{idx}({repr(p['consts'][idx])})" if idx < len(p["consts"]) else f"K{idx}"
        desc = f"A={A} B={B} C={C} k={k}"
        if opname == "LOADK": desc = f"R{A} := {kc(Bx)}"
        elif opname == "LOADI": desc = f"R{A} := {sBx}"
        elif opname in ("GETTABUP",): desc = f"R{A} := U{B}[{kc(C)}]"
        elif opname in ("SETTABUP",): desc = f"U{A}[{kc(B)}] := {kc(C) if k else f'R{C}'}"
        elif opname in ("GETFIELD",): desc = f"R{A} := R{B}.{kc(C)}"
        elif opname in ("SETFIELD",): desc = f"R{A}.{kc(B)} := {kc(C) if k else f'R{C}'}"
        elif opname in ("SELF",): desc = f"R{A+1} := R{B}; R{A} := R{B}:{kc(C)}"
        elif opname in ("GETUPVAL",): desc = f"R{A} := U{B}({p['upns'][B] if B < len(p['upns']) else B})"
        elif opname in ("JMP",): desc = f"goto {pc + 1 + sJ}"
        elif opname in ("CALL",): desc = f"R{A}(nargs={B-1}, nret={C-1})"
        print(f"  {pc:03d} {opname:<10} {desc}")

with open(r"data/cache/wpm_bytecode.txt") as f:
    lines = dict(l.strip().split(":", 1) for l in f if ":" in l)

for name in ["GetViewLevelRange", "GetViewBounds", "GetServerLod", "UpdateViewRequest", "SendViewRequest", "DoSendViewRequest", "BuildAsync", "CalcOutOfViewZones"]:
    p = parse54(bytes.fromhex(lines[name]))
    disasm54(name, p)
