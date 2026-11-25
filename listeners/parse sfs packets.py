import re
import json

log_path = r"data/logs/traffic.log"

with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

entries = re.split(r'(\[(?:send|recv)\]\s+len=\d+)', text)

sfs_packets = []

for i in range(1, len(entries), 2):
    header = entries[i].strip()
    body = entries[i+1] if i+1 < len(entries) else ""
    
    # Parse hex bytes
    hex_bytes = []
    ascii_chars = []
    for line in body.split('\n'):
        line = line.strip()
        if re.match(r'^[0-9a-f]{8}\s+', line):
            parts = line.split()
            # offset parts[0]
            # hex parts[1..16]
            # ascii parts[-1]
            for p in parts[1:17]:
                if len(p) == 2 and re.match(r'^[0-9a-f]{2}$', p):
                    hex_bytes.append(int(p, 16))
    
    if hex_bytes and hex_bytes[0] == 0x80:
        # Check action / command
        sfs_packets.append({
            'dir': 'send' if 'send' in header else 'recv',
            'len': len(hex_bytes),
            'raw_bytes': hex_bytes
        })

print(f"Total SFS packets found (starting with 0x80): {len(sfs_packets)}")
for idx, p in enumerate(sfs_packets):
    b = p['raw_bytes']
    # SFS header: 0x80, len_hi, len_lo
    # followed by SFSObject (0x12)
    # Search for ascii strings inside b
    s_chars = "".join([chr(x) if 32 <= x <= 126 else "." for x in b])
    print(f"\nPacket #{idx+1} [{p['dir'].upper()}] len={p['len']}")
    print(s_chars[:120])
