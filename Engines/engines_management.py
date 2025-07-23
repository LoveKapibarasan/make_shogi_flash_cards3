import re
import subprocess
import time
import os
from dotenv import load_dotenv


def initialize_engine():
    load_dotenv()
    ENGINE_PATH = os.getenv("ENGINE_PATH")
    SETTING_FILE_PATH = os.getenv("SETTING_FILE_PATH")
    cwd = os.path.dirname(ENGINE_PATH)
    executable = os.path.basename(ENGINE_PATH)
    print("[DEBUG] cwd:", cwd)
    print("[DEBUG] Full Engine Path:", ENGINE_PATH)
    print("[DEBUG] Executable Name:", executable)
    
    process = subprocess.Popen(
        [f"./{executable}"], 
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=os.path.dirname(ENGINE_PATH)
    )
    try:
        with open(SETTING_FILE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                process.stdin.write(line.strip() + '\n')
                process.stdin.flush()
                time.sleep(1)
    except Exception as e:
        raise RuntimeError(f"Initialization error: {e}")
    return process

def read_output(proc, command, timeout=180.0):
    proc.stdin.write(command + '\n')
    proc.stdin.write("go\n")
    proc.stdin.flush()
    cp = nodes = pv = None
    start_time = time.time()
    while True:
        time.sleep(2)
        if time.time() - start_time > timeout:
            raise ValueError("timeout")
        line = proc.stdout.readline()
        print("[DEBUG] Output:", line.strip())
        if not parse_line(line) is None:
            cp, nodes, pv =  parse_line(line)
        if line.startswith("bestmove"):
            break
    return cp, nodes, pv



def parse_line(line):
    mpv_match = re.search(r'multipv\s+(\d+)', line)
    if mpv_match and mpv_match.group(1) != '1':
        return None

    match = re.search(r'cp\s+(-?\d+).*?nodes\s+(\d+).*?pv\s+(.*)', line)
    if match:
        cp = int(match.group(1))
        nodes = int(match.group(2))
        pv = match.group(3).strip()
        return cp ,nodes, pv
    return None