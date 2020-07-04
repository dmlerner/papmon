import os
import subprocess
import argparse
 
def kill_pids(pids):
    for pid in pids:
        cmd = f"/mnt/c/Windows/System32/taskkill.exe '/PID' {pid}" 
        status, output = subprocess.getstatusoutput(cmd)

def kill(pattern):
    pids = get_pids(pattern)
    kill_pids(pids)

def get_pids(pattern):
    cmd = f"/mnt/c/Windows/System32/tasklist.exe | rg '{pattern}\S*\s+(\d+)' -r '$1' -o" 
    status, output = subprocess.getstatusoutput(cmd)
    return set(map(int, output.split()))

def main():
    ap = argparse.ArgumentParser(description='Kills a process matching a given pattern.\nUseful for killing Windows processes from WSL')
    ap.add_argument('pattern', nargs='?')
    args = ap.parse_args()
    if args.pattern:
        kill(args.pattern)

if __name__ == '__main__':
    main()
