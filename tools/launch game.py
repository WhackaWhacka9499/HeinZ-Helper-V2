import subprocess
import time
import base64
import os
import sys

now = int(time.time())
token = base64.b64encode(f"{now}|LZ".encode("utf-8")).decode("utf-8")
arg = f"--from-launcher={token}"

exe = r"G:\Last Z_AppData\Game\Survival.exe"
work_dir = r"G:\Last Z_AppData\Game"

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

p = subprocess.Popen(
    [exe, arg],
    cwd=work_dir,
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
    close_fds=True
)

print(f"Launched Survival.exe with PID: {p.pid}")
