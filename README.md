# rtl8192eu-advanced

A production-grade Linux driver for the **TP-Link TL-WN822N v4** USB WiFi
adapter (Realtek **RTL8192EU**, USB `2357:0108`) — and for any other
RTL8192EU-based adapter.

Base: **Realtek's newest official release (v5.11.2.1, 2021)** — newer than
TP-Link's own Linux driver (v4.3.15, 2015) and the widely-used community
mirror (Mange, v5.6.4-era) — plus original fixes and features, all
reverse-engineered and wire-verified on live hardware.

**Every fix below exists in both the official AND community builds today.**

| Commit / patch | What it changes |
|---|---|
| autopm hold guard | `Runtime PM usage count underflow!` on every `rmmod` — probe's PM get fails on modern kernels, driver still put an unheld reference at remove. Fixed + dyndbg probes |
| MLME monitor no-op | `rtw_warn_on(1)` stack dump on every monitor→AP transition — Realtek added `MLME_IS_MONITOR` but forgot the branch |
| `CONFIG_WIFI_MONITOR=y` | monitor mode — official stock ships it compiled out |
| TX power offset wired | the `tx_power_offset` proc knob (0–5 dBm) was set+printed but **never consumed** — now wired into the TX power target |
| `CONFIG_MONITOR_MODE_XMIT` | TX injection was impossible: carrier never comes up in monitor mode (Realtek's own fix ships commented out) + a hostile `rtap_len == 12` check. Now: monitor RX **and** wire-verified TX injection |
| debug probes | dyndbg-gated `pr_debug` breadcrumbs across the whole monitor TX flow (stock ships every diagnostic compiled out) |

## Build from a clone

```bash
git clone https://github.com/thenabbu/rtl8192eu-advanced.git
cd rtl8192eu-advanced/driver
make KVER=$(uname -r) -j$(nproc)
sudo insmod 8192eu.ko rtw_power_mgnt=0 rtw_enusbss=0   # AP duty: keep both = 0
```

### DKMS (survives kernel upgrades)

```bash
sudo cp -a driver /usr/src/rtl8192eu-1.0
sudo dkms add rtl8192eu/1.0
sudo dkms install rtl8192eu/1.0 -k $(uname -r)
```

Module name stays `8192eu`, so existing `modprobe.d` options and udev
rules keep working. CI builds the tree on Ubuntu 22.04 (5.15) and
24.04 (6.8) on every push.

## Verified on live hardware (2026-10-19)

- AP duty (hostapd): clients re-associate ~9 s after module bounce,
  zero kernel warnings across a full day
- monitor RX: 838 802.11 frames in 8 s (`captures/monitor.pcap`)
- monitor TX: 10/10 injected frames = 72-byte bulk-OUT URBs with
  completion status 0
- TX power: offset 0/1/4 → CCK 16/17/20 dBm, exact restore
- LED: full on/off/blink control (`tools/rtlled.sh`)
- A/B kernel-log proof for every bugfix (old module still warns,
  patched one silent, same log)

## Hardware control surface

- `docs/txpower-control.md` — the TX power formula and every knob
- `docs/led-control.md` — LED registers (`REG_LEDCFG0/1/2`), semantics
- `docs/usb-protocol.md` — the complete wire protocol (vendor request,
  register map, init phases, firmware download)
- `docs/monitor-injection.md` — the injection failure chain + the usbmon
  32-byte TX truncation trap
- `docs/windows-driver.md` — what the official Windows driver exposes
  (OID surface incl. vendor `OID_RT_*` commands)
- `tools/` — LED control, injection test, usbmon parser

## Provenance

Base tree imported verbatim from the official 5.11.2.1 mirror
(see `MANIFEST.md` for hashes); our series is the commit history on top.
GPL-2.0 — see `LICENSE`.
