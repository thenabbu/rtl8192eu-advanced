# rtl8192eu-advanced

Advanced Linux driver for the **TP-Link TL-WN822N v4** USB WiFi adapter
(Realtek **RTL8192EU**, USB `2357:0108`), plus the complete USB
reverse-engineering campaign behind it.

The driver is the **newest official Realtek base (v5.11.2.1)** — newer than
both TP-Link's own Linux release (v4.3.15, 2015) and the widely-used
community mirror (Mange/rtl8192eu-linux-driver) — plus original fixes found
by RE-ing the live device on the wire:

| Patch | What it fixes |
|---|---|
| `0001-usb-autopm-hold-guard` | Runtime-PM usage-count underflow on every `rmmod` (present in official *and* community drivers): probe takes a PM hold, silently fails on modern kernels, driver still puts it at remove |
| `0002-mlme-disconnect-monitor-noop` | `rtw_warn_on(1)` + full stack dump on every monitor→AP transition — Realtek added `MLME_IS_MONITOR` but forgot the branch in `rtw_mlmeext_disconnect()` |
| `0003-enable-wifi-monitor-mode` | `CONFIG_WIFI_MONITOR=y` — official stock ships monitor mode compiled out |
| `0004-wire-tx-power-offset-knob` | `tx_power_offset` proc knob was dead code upstream (never consumed) — now adds +N dBm (0-5) to every rate, verified on the wire/dumps |
| `0005-monitor-injection-fixes` | TX injection was impossible on stock builds: carrier never comes up in monitor mode (Realtek's own `CONFIG_MONITOR_MODE_XMIT` fix ships commented out) + a hostile `rtap_len == 12` check drops standard radiotap headers |
| `0006-monitor-xmit-debug-probes` | dyndbg-gated `pr_debug` probes across the whole TX flow (all stock RTW_INFO diagnostics are compiled out) |

Verified on Linux 6.8 (Ubuntu 24.04) with live AP duty (hostapd), live
monitor capture, and A/B kernel-log proof for each fix (see `docs/`).

## Build

```bash
# 1. fetch the official base (sha256 in MANIFEST.md)
curl -LO https://github.com/clnhub/rtl8192eu-linux/archive/refs/heads/5.11.2.1.tar.gz
tar -xzf 5.11.2.1.tar.gz && cd rtl8192eu-linux-5.11.2.1

# 2. apply this repo's patches
for p in /path/to/rtl8192eu-advanced/patches/*.patch; do patch -p1 < "$p"; done

# 3. build for the running kernel
make KVER=$(uname -r) -j$(nproc)
sudo insmod 8192eu.ko rtw_power_mgnt=0 rtw_enusbss=0   # AP use: keep both = 0
```

DKMS: copy the patched tree to `/usr/src/rtl8192eu-1.0`, then
`dkms add/install rtl8192eu/1.0`. Module name stays `8192eu`, so existing
`modprobe.d` options and udev rules keep working.

## RE artifacts

- `captures/usbmon-init-5.6.4.txt`, `usbmon-init-5.11.2.1.txt` — full driver
  bring-up on the wire (12k/9k control transfers, 30 phases)
- `captures/usbmon-runtime.txt` — steady-state polling
- `captures/monitor.pcap` — 802.11 frames captured with the patched driver
  in monitor mode (radiotap, LINKTYPE 127)
- `docs/lsusb-full.txt` — full USB descriptor
- `docs/proc-dumps.txt` — EFUSE/EEPROM map, hardware capability profile
- `tools/usbmon_parse.py` — capture parser (handles the usbmon text-format traps)
- Findings: `docs/usb-protocol.md`, `docs/feature-matrix.md`,
  `docs/hardware-profile.md`, `docs/bugs-found.md`, `docs/windows-driver.md`

## Status

Running as the house AP driver on the lab host since 2026-10-19: hostapd
(AP mode), monitor mode, client re-association ~9 s after module bounce,
zero kernel warnings. LED control (`tools/rtlled.sh`), real TX power offset (patch 0004), and
wire-verified monitor-mode TX injection (patches 0005/0006, see
`docs/monitor-injection.md`) all shipped. Roadmap: `led_config` strategy
build flag, Windows `rtwlanu.sys` comparison (Ghidra).

## Provenance & license

Base driver sources are Realtek's GPL-licensed kernel driver releases,
redistributed upstream (see `MANIFEST.md` for exact URLs and hashes). This
repo contains only original documentation, tooling and patches; the patches
are provided under the same terms as the driver source they apply to.
