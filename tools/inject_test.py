#!/usr/bin/env python3
"""Inject marker probe-requests on wlan0 (monitor mode). Wire proof via usbmon."""
import socket, struct, time, sys

N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
s.bind(('wlan0', 0))

radiotap = struct.pack('<BBHI', 0, 0, 8, 0)          # ver, pad, len=8, present=0
fc     = struct.pack('<H', 0x0040)                    # mgmt / probe request
dur    = struct.pack('<H', 0)
da     = b'\xff' * 6
sa     = b'\x02\x11\x22\x33\x44\x55'
bssid  = b'\xff' * 6
seq    = struct.pack('<H', 0)
ie     = b'\x00\x04HERMES'                            # SSID IE: "HERMES"
frame  = radiotap + fc + dur + da + sa + bssid + seq + ie

sent = 0
for i in range(N):
    try:
        sent += s.send(frame)
        time.sleep(0.1)
    except OSError as e:
        print("send err:", e)
        break
print(f"sent {sent} bytes ({N} frames, {len(frame)} B each)")
s.close()
