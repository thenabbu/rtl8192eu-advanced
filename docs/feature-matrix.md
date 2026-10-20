# Driver landscape (RTL8192EU)

| | TP-Link official Linux | Realtek official 5.6.4 | Realtek official 5.11.2.1 (this base) | mainline rtl8xxxu |
|---|---|---|---|---|
| Release | 2015-07 (`v4.3.15_14701`) | 2019-11 | 2021-05 | in-kernel |
| Source of record | TP-Link support zip | Realtek; mirrored (Mange/`realtek-4.4.x` README says 4.4.1 but the code self-reports `v5.6.4_35685.20191108`) | Realtek; mirrored (clnhub `5.11.2.1` branch) | kernel.org |
| AP mode (hostapd) | no (station only) | yes | yes (explicit `CONFIG_AP_MODE=y`) | **no** (why vendor drivers exist) |
| Monitor mode | no | yes (`CONFIG_WIFI_MONITOR=y`) | compiled out; **enabled here via patch 0003** | partial |
| Mesh (802.11s) source | no | yes | yes | — |
| FT / MBO / WNM / RRM / ROC | no | no | **yes** (new in 5.11) | — |
| sw crypto (CCMP/GCMP internal) | no | no | yes | — |
| procfs surface | 156 handlers (source) | 482 handlers (source) | **138 live entries** — 8 global + 128 device + odm/mcc subdirs, measured on the prod AP 2026-10-20 | — |
| Kernel support | ≤ 3.10 | ≤ 6.x (community patches) | ≤ 7.0 (with mirror's compat fixes) | mainline cadence |
| Bugs found here | — | PM-underflow on rmmod | PM-underflow (fixed, patch 0001) + monitor→AP WARN (fixed, patch 0002) | — |

Windows side: TP-Link ships Realtek's `rtwlanu.sys` v1030.2.0731.2015
(see `windows-driver.md`) — same vendor-request family, proprietary ioctls.
