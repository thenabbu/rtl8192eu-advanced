# Artifact manifest (sha256, what lives where)

## Upstream inputs (NOT in git — fetched by URL)

| File | URL | sha256 |
|---|---|---|
| Realtek official 5.6.4 tree | `https://github.com/clnhub/rtl8192eu-linux/archive/refs/heads/5.6.4.tar.gz` | `500cfe82533f00c14f3658eb5a82ee23b311741cc5a90fc47153a2c52848dc5b` |
| Realtek official 5.11.2.1 tree (base) | `https://github.com/clnhub/rtl8192eu-linux/archive/refs/heads/5.11.2.1.tar.gz` | `a68052912d44a9791c26d5c4d7d99ec9c52447bf6ddb06fccb5febf23d35715b` |
| TP-Link official Linux v4.3.15 | `https://static.tp-link.com/res/down/soft/TL-WN822N(US)_V4_160315_Linux.zip` | `b9c7b1f1cde9ab3fa49f312079e34b4828abbedca89feb139dc6636ca8227c52` |
| TP-Link official Windows (v4+v5) | `https://static.tp-link.com/TL-WN822N_EU_US_V4_V5_20170726_Wins.zip` | `2ddfe5f5f5a3794767b4d76c17119a4705147ac9ebae927906fe2a742af15fea` |
| Community Mange HEAD (snapshot of 2026-10-19) | `https://github.com/Mange/rtl8192eu-linux-driver` @ `c629cc972a0d878c930d19c4a9309c27c1e61f92` | — (git tree) |

## In git (this repo)

- `captures/usbmon-*.txt` — usbmon textual captures (raw, as produced by
  `/sys/kernel/debug/usb/usbmon/6u`)
- `captures/monitor.pcap` — radiotap pcap from the patched driver in monitor mode
- `captures/*.log`, `captures/dmesg-init-window.txt` — bounce/swap timelines
- `docs/*` — descriptor dump, modinfo, procfs dumps, findings
- `patches/*`, `tools/usbmon_parse.py`

## Not in git (too large / regenerable)

- Extracted official driver trees + Windows payload (~100 MB working dir):
  regenerable from the table above
- `8192eu.ko` builds: build from source + patches instead
