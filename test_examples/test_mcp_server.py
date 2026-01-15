#!/usr/bin/env python3
import sys, time, json
print("MCP Server Starting...", file=sys.stderr)
time.sleep(0.2)
print("MCP Server Ready!", file=sys.stderr)
print(json.dumps({"status": "running", "type": "stdio"}))
sys.stdout.flush()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopped", file=sys.stderr)
