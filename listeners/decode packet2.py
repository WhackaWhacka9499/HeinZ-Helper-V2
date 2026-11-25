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
    hex_bytes = []
    for line in body.split('\n'):
        line = line.strip()
        if re.match(r'^[0-9a-f]{8}\s+', line):
            parts = line.split()
            for p in parts[1:17]:
                if len(p) == 2 and re.match(r'^[0-9a-f]{2}$', p):
                    hex_bytes.append(int(p, 16))
    if hex_bytes and hex_bytes[0] == 0x80 and 'send' in header:
        sfs_packets.append(hex_bytes)

p2 = sfs_packets[1]
print(f"Packet 2 total bytes: {len(p2)}")

# Let's decode SFSObject
# SmartFoxServer 2X binary format:
# Data types:
# 0x00: NULL
# 0x01: BOOL (1 byte)
# 0x02: BYTE (1 byte)
# 0x03: SHORT (2 bytes, big-endian)
# 0x04: INT (4 bytes, big-endian)
# 0x05: LONG (8 bytes, big-endian)
# 0x06: FLOAT (4 bytes, IEEE 754)
# 0x07: DOUBLE (8 bytes, IEEE 754)
# 0x08: UTF_STRING (2 bytes len + string)
# 0x09: BOOL_ARRAY (2 bytes len + bytes)
# 0x0A: BYTE_ARRAY (4 bytes len + bytes)
# 0x0B: SHORT_ARRAY (2 bytes len + shorts)
# 0x0C: INT_ARRAY (2 bytes len + ints)
# 0x0D: LONG_ARRAY (2 bytes len + longs)
# 0x0E: FLOAT_ARRAY (2 bytes len + floats)
# 0x0F: DOUBLE_ARRAY (2 bytes len + doubles)
# 0x10: UTF_STRING_ARRAY (2 bytes len + strings)
# 0x11: SFS_ARRAY (2 bytes count + elements)
# 0x12: SFS_OBJECT (2 bytes count + (key: utf_string, type: byte, val))

class SFSDecoder:
    def __init__(self, data):
        self.data = bytearray(data)
        self.pos = 0

    def read_byte(self):
        b = self.data[self.pos]
        self.pos += 1
        return b

    def read_short(self):
        v = (self.data[self.pos] << 8) | self.data[self.pos+1]
        self.pos += 2
        return v

    def read_int(self):
        v = (self.data[self.pos] << 24) | (self.data[self.pos+1] << 16) | (self.data[self.pos+2] << 8) | self.data[self.pos+3]
        self.pos += 4
        if v >= 0x80000000:
            v -= 0x100000000
        return v

    def read_long(self):
        v = 0
        for _ in range(8):
            v = (v << 8) | self.data[self.pos]
            self.pos += 1
        return v

    def read_utf(self):
        length = self.read_short()
        s = self.data[self.pos:self.pos+length].decode('utf-8', errors='ignore')
        self.pos += length
        return s

    def decode_value(self, type_id):
        if type_id == 0x00:
            return None
        elif type_id == 0x01:
            return self.read_byte() != 0
        elif type_id == 0x02:
            return self.read_byte()
        elif type_id == 0x03:
            return self.read_short()
        elif type_id == 0x04:
            return self.read_int()
        elif type_id == 0x05:
            return self.read_long()
        elif type_id == 0x08:
            return self.read_utf()
        elif type_id == 0x10: # UTF_STRING_ARRAY
            count = self.read_short()
            return [self.read_utf() for _ in range(count)]
        elif type_id == 0x11: # SFS_ARRAY
            count = self.read_short()
            arr = []
            for _ in range(count):
                elem_type = self.read_byte()
                arr.append(self.decode_value(elem_type))
            return arr
        elif type_id == 0x12: # SFS_OBJECT
            count = self.read_short()
            obj = {}
            for _ in range(count):
                key = self.read_utf()
                val_type = self.read_byte()
                obj[key] = self.decode_value(val_type)
            return obj
        else:
            return f"UNSUPPORTED_TYPE_{hex(type_id)}"

    def decode_packet(self):
        # Header: 0x80 (1 byte flag), 2 bytes length
        flag = self.read_byte()
        length = self.read_short()
        obj_type = self.read_byte()
        if obj_type != 0x12:
            raise ValueError(f"Expected SFS_OBJECT (0x12), got {hex(obj_type)}")
        return self.decode_value(0x12)

dec = SFSDecoder(p2)
res = dec.decode_packet()
print(json.dumps(res, indent=2))
