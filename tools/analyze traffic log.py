import re
import json

log_path = r"data/logs/traffic.log"

with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

entries = re.split(r'(\[(?:send|recv)\]\s+len=\d+)', text)
print(f"Total entries: {len(entries)}")

recvs = []
sends = []

for i in range(1, len(entries), 2):
    header = entries[i].strip()
    body = entries[i+1] if i+1 < len(entries) else ""
    if 'recv' in header:
        recvs.append((header, body))
    else:
        sends.append((header, body))

print(f"Total sends: {len(sends)}, Total recvs: {len(recvs)}")

# Check first 10 recvs
print("\nFirst 10 recvs:")
for h, b in recvs[:10]:
    first_line = b.strip().split('\n')[0] if b.strip() else ""
    print(f"{h}: {first_line}")

# Check any recv that contains recognizable strings
print("\nSearching recvs for keywords like 'APS', 'ReadyGo', '2066965117000694', 'session', 'user':")
for idx, (h, b) in enumerate(recvs):
    if any(k in b for k in ['APS', 'ReadyGo', '206696', 'al.rank', 'success', 'cmd']):
        print(f"Recv #{idx+1} ({h}):")
        lines = b.strip().split('\n')
        for l in lines[:5]:
            print(f"  {l}")
