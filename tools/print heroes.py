import json
from pathlib import Path

# Load from inspect_hero_names_direct by importing or reading
from inspect_hero_names_direct import data_out

items = list(data_out.values()) if isinstance(data_out, dict) else data_out
print(f"Total heroes: {len(items)}")
for h in items:
    line = h.get("line") or {}
    code_name = line.get("42")
    icon = line.get("31")
    print(f"HeroID: {h.get('heroId')} | CodeName: {code_name} | Icon: {icon} | Lv: {h.get('level')} | Rank: {h.get('curRank')} | Power: {h.get('power')} | Master: {h.get('isMaster')}")
