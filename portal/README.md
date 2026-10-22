# rtl8192eu portal

A router-style web control panel for Realtek RTL8192EU USB adapters running
this driver. One page for the whole control surface the driver exposes:

- **Dashboard** — live mode, SSID/channel/country, RSSI, connected clients
  with per-client traffic, rx/tx totals, tx power offset, firmware info.
- **Modes** — switch the adapter between **AP**, **station (client)** and
  **monitor**, with setup forms for each:
  - AP: SSID / passphrase / channel / country / max clients (edits
    `hostapd.conf`, validates with `hostapd -t`, restarts hostapd)
  - Station: scan nearby networks, pick one, connect via wpa_supplicant
  - Monitor: pure radio capture of everything in the air
- **Monitor** — live human-readable frame table (beacons, probes, data,
  handshakes, …) with per-type counts.
- **Advanced** (collapsed) — every procfs entry the driver exposes
  (130+), readable in place, writable where the driver allows, plus
  direct register read/write (behind a typed `DANGER` confirm).

## How it works

The portal is a **separate root process** (Python + FastAPI) that talks to
the driver through `/proc/net/<driver>/<iface>/` and to the network stack
through `ip` / `iw` / `hostapd` / `wpa_supplicant` / `dnsmasq` — whatever is
installed on the host. Zero driver changes: killing the portal never
affects the radio, and a misbehaving portal can't panic the kernel.
Config for what's present is auto-detected (a clean box without hostapd
just shows "not installed" hints in the Modes tab).

## Install

Requires: the driver loaded (`lsusb` shows `2357:0108` or your RTL8192EU
variant, interface up), python3 + systemd.

```sh
sudo -S -p '' ./install.sh
```

Prints a generated password. Portal at `http://<machine>:8080` (change
`PORTAL_PORT` in `/opt/rtl8192eu-portal/portal.env`).

Env vars (all optional, in `/opt/rtl8192eu-portal/portal.env`):
`PORTAL_USER`, `PORTAL_PASS` (required — the portal refuses to start
without one), `PORTAL_PORT`, `PORTAL_IFACE` (default: first adapter iface),
`PORTAL_PROC_ROOT` (default: auto-detected).

## Security

- HTTP basic auth, TLS **not** included — run it on a trusted LAN or put a
  TLS proxy in front.
- Register writes and mode switches require explicit typed confirms in the
  UI and a confirm token in the API. A bad register write can take the
  radio down until reboot/reload — that's a hardware property, not a bug.

## Uninstall

```sh
sudo systemctl disable --now rtl8192eu-portal
sudo rm -rf /opt/rtl8192eu-portal /etc/systemd/system/rtl8192eu-portal.service
sudo systemctl daemon-reload
```

## Self-check

```sh
python3 portal.py --selftest
```
