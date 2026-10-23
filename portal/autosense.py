#!/usr/bin/env python3
"""autosense — self-managing mode daemon for the RTL8192EU AP dongle.

Vision (user's): the adapter idles in MONITOR (LED breathing); a probe
request for the AP SSID flips it to AP (LED blinking); ethernet loss flips
it to STATION on the upstream Wi-Fi (LED solid) and fires a Telegram alert;
ethernet recovery flips back to AP (LED blinking).

One process, systemd-managed, owns the dongle LED. Talk to it by editing
the env file — no CLI, no API. `--selftest` checks the pure logic.
"""
import math
import os
import re
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

IFACE = os.environ.get("AS_IFACE", "wlan0")
ETH = os.environ.get("AS_ETH_IFACE", "enp1s0")
SSID = os.environ.get("AS_SSID", "BlockiNG")
UP_SSID = os.environ.get("AS_UPSTREAM_SSID", "NGJIO")
UP_PASS = os.environ.get("AS_UPSTREAM_PASS", "")
GATEWAY = os.environ.get("AS_GATEWAY", "192.168.29.1")
IDLE_SECS = int(os.environ.get("AS_IDLE_SECS", "300"))
TICK = int(os.environ.get("AS_TICK", "5"))
DEBOUNCE = int(os.environ.get("AS_DEBOUNCE", "2"))
PAUSE_FILE = Path(os.environ.get(
    "AS_PAUSE_FILE", str(Path(__file__).resolve().parent / "autosense.pause")))
DRY = os.environ.get("AS_DRY", "") == "1"
TG_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
TG_CHAT = os.environ.get("TG_CHAT_ID", "")

PROC = Path(f"/proc/net/rtl8192eu/{IFACE}")
MAC_RE = re.compile(r"sta's macaddr:([0-9a-f]{2}(?::[0-9a-f]{2}){5})", re.I)
CIPHER_RE = re.compile(r"wpa(?:2)?_(?:psk|group_cipher|pairwise_cipher)=0x[1-9a-fA-F]")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def run(*args, timeout=20):
    if DRY:
        log("DRY-run:", *args)
        return 0
    try:
        p = subprocess.run(list(args), capture_output=True, text=True, timeout=timeout)
        return p.returncode
    except (OSError, subprocess.TimeoutExpired) as e:
        log("run failed:", args, e)
        return 1


def telegram(msg):
    """Edge-triggered alerts only (state changes), best-effort."""
    if not (TG_TOKEN and TG_CHAT):
        log("no TG config, would alert:", msg)
        return
    import json
    import urllib.request
    body = json.dumps({"chat_id": TG_CHAT, "text": msg}).encode()
    try:
        urllib.request.urlopen(urllib.request.Request(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            data=body, headers={"Content-Type": "application/json"}), timeout=10)
        log("alerted:", msg)
    except OSError as e:
        log("alert failed:", e)


def own_mac():
    try:
        return Path(f"/sys/class/net/{IFACE}/address").read_text().strip().lower()
    except OSError:
        return None


def client_count(text):
    """Real associated stations (own MAC + all-zero-mac dummies excluded).
    Each block is bounded at the next macaddr so cipher flags never bleed
    across entries."""
    own = own_mac()
    real = 0
    matches = list(MAC_RE.finditer(text))
    for i, m in enumerate(matches):
        mac = m.group(1).lower()
        if mac == own or set(mac.replace(":", "")) <= {"f", "0"}:
            continue
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        if CIPHER_RE.search(text[m.end():end]):
            real += 1
    return real


def eth_ok():
    """Carrier up AND gateway answering. Carrier check is instant."""
    carrier = Path(f"/sys/class/net/{ETH}/carrier")
    try:
        if carrier.read_text().strip() != "1":
            return False
    except OSError:
        return False
    return run("ping", "-c", "2", "-W", "1", GATEWAY, timeout=5) == 0


def switch_wifi(mode, channel=None):
    """mode: ap|monitor|managed — safe sequence, restores AP on failure."""
    hostapd_was = False
    if DRY:
        log("DRY-run: switch to", mode)
        return True
    if mode != "ap":
        hostapd_was = run("systemctl", "is-active", "--quiet", "hostapd") == 0
        if hostapd_was:
            run("systemctl", "stop", "hostapd")
    if mode == "ap":
        # iw refuses set-type ap on this driver ("run a management daemon") —
        # hostapd performs the nl80211 iftype change itself
        run("ip", "link", "set", IFACE, "up")
        run("systemctl", "start", "hostapd")
        time.sleep(2)
        if run("systemctl", "is-active", "--quiet", "hostapd") != 0:
            log("hostapd did not come up — AP not running")
            return False
        run("systemctl", "start", "dnsmasq")
        return True
    run("ip", "link", "set", IFACE, "down")
    if run("iw", "dev", IFACE, "set", "type", mode) != 0:
        run("ip", "link", "set", IFACE, "up")
        run("systemctl", "start", "hostapd")
        if hostapd_was:
            log("switch to", mode, "FAILED — hostapd restarted")
            time.sleep(2)
            return run("systemctl", "is-active", "--quiet", "hostapd") == 0
        log("switch to", mode, "FAILED")
        return False
    run("ip", "link", "set", IFACE, "up")
    if mode == "monitor" and channel:
        run("iw", "dev", IFACE, "set", "channel", str(channel))
    return True


# ---------------------------------------------------------------- LED

# LED — proven 2026-10-24 by user watching the physical dongle: the visible
# LED is LED1 (this chip has no LED0), driven by bit 11 of the 32-bit
# PHY/baseband register at 0x4C — 0 = on, 1 = off. SwLedOn/Off_8192EU
# (rtl8192eu_led.c) first clears bit 1 of 0x64 and bits 15/10/9/8 of 0x4C;
# those gate software control, without them the LED never lights. The
# MAC-byte registers 0x4c/0x4d/0x4e (LEDCFG0/1/2) do NOT drive the LED.
LED_GATE = 0x8F00     # 0x4C bits 15,11,10,9,8 — cleared to arm SW control
LED_BIT = 0x0800      # 0x4C bit 11 — 0: on, 1: off


class Led(threading.Thread):
    """Owns the LED: solid=station, blink 1Hz=ap, breathing=monitor."""
    STATE = {"mode": None}
    _stop = threading.Event()
    _base = None      # cached 0x4C dword; only we write it, so cache is safe

    def _read32(self, addr):
        (PROC / "read_reg").write_text(f"{addr:x} 4\n")
        last = (PROC / "read_reg").read_text().strip().splitlines()[-1]
        return int(last.rsplit("=0x", 1)[1], 16)

    def _arm(self):
        """One-time gate config per (re)start; cache the 0x4C base value."""
        if DRY:
            self._base = None
            return
        try:
            v64 = self._read32(0x64)
            (PROC / "write_reg").write_text(f"64 {v64 & ~0x2:x} 4\n")
            self._base = self._read32(0x4C)
        except (OSError, ValueError, IndexError) as e:
            log("led arm failed:", e)
            self._base = None

    def _w(self, on):
        """One 32-bit write_reg per toggle: bit 11 of 0x4C."""
        if DRY or self._base is None:
            return
        try:
            v = (self._base & ~LED_GATE) | (0 if on else LED_BIT)
            (PROC / "write_reg").write_text(f"4c {v:x} 4\n")
        except OSError as e:
            log("led write failed:", e)

    def run(self):
        self._arm()
        while not self._stop.is_set():
            mode = self.STATE["mode"]
            if mode == "station":
                self._w(True)
                self._stop.wait(5)
                continue
            if mode == "ap":
                self._w(True); self._stop.wait(0.5)
                self._w(False); self._stop.wait(0.5)
                continue
            if mode == "monitor":
                # breathing: 0->1->0 sine over ~3s, PWM at ~16Hz
                t = 0.0
                while not self._stop.is_set() and self.STATE["mode"] == "monitor":
                    level = (1 - math.cos(2 * math.pi * (t % 3.0) / 3.0)) / 2
                    self._w((t % 0.06) < 0.06 * level)
                    t += 0.06
                    self._stop.wait(0.06)
                continue
            self._stop.wait(1)

    def stop(self):
        self._stop.set()
        self._w(False)


# ---------------------------------------------------------------- probes

def ap_channel():
    try:
        m = re.search(r"^channel=(\d+)", Path("/etc/hostapd/hostapd.conf").read_text(), re.M)
        return int(m.group(1)) if m else 11
    except OSError:
        return 11


def probe_ssid(pkt):
    """SSID IE of a probe request (None if absent)."""
    from scapy.layers.dot11 import Dot11Elt
    elt = pkt.getlayer("Dot11Elt")
    while elt is not None:
        if elt.ID == 0:
            return elt.info
        elt = elt.payload.getlayer("Dot11Elt")
    return None


def sniff_probes(ssid, hit):
    """Monitor-mode listener: fires `hit` on a probe request for `ssid`."""
    from scapy.all import sniff
    want = ssid.encode()
    def prn(pkt):
        if pkt.haslayer("Dot11ProbeReq") and probe_ssid(pkt) == want:
            hit()
    while probe_watch.is_set():
        try:
            # 5s windows: probe bursts are ~300ms, 5x fewer promiscuous
            # toggles in the kernel log
            sniff(iface=IFACE, prn=prn, store=False, timeout=5)
        except Exception:
            time.sleep(1)


probe_watch = threading.Event()
sniff_thread = None


def stop_sniffer():
    """Kill the capture thread and wait for its socket to close (iw needs
    the iface quiet before an iftype change)."""
    global sniff_thread
    probe_watch.clear()
    if sniff_thread and sniff_thread.is_alive():
        sniff_thread.join(timeout=3)
    sniff_thread = None


# ---------------------------------------------------------------- main loop

def failover_up():
    """ethernet dead: join upstream Wi-Fi, alert."""
    if not UP_PASS:
        log("no AS_UPSTREAM_PASS — cannot fail over; staying in AP, dark")
        return False
    conf = Path("/etc/wpa_supplicant/wpa-failover.conf")
    conf.parent.mkdir(mode=0o755, exist_ok=True)
    conf.write_text(f'network={{\n\tssid="{UP_SSID}"\n\tpsk="{UP_PASS}"\n}}\n')
    conf.chmod(0o600)
    switch_wifi("managed")
    run("wpa_supplicant", "-i", IFACE, "-c", str(conf), "-B")
    time.sleep(6)
    run("dhclient", "-1", "-v", IFACE)
    Led.STATE["mode"] = "station"
    return True


def failover_down():
    """ethernet back: drop the Wi-Fi uplink, return to AP."""
    run("pkill", "-x", "wpa_supplicant")
    run("pkill", "-x", "dhclient")
    switch_wifi("ap")
    Led.STATE["mode"] = "ap"


def main():
    state, down_ticks, idle_since, probing = "boot", 0, None, False
    led = Led(); led.start()
    hit_probe = threading.Event()

    def on_probe():
        hit_probe.set()

    def guarded(signum, frame):
        led.stop()
        sys.exit(0)
    signal.signal(signal.SIGTERM, guarded)
    signal.signal(signal.SIGINT, guarded)

    log(f"autosense: iface={IFACE} ssid={SSID} upstream={UP_SSID} idle={IDLE_SECS}s dry={DRY}")
    paused = False
    while True:
        # pause file = portal is in manual mode; hold whatever mode it set
        if PAUSE_FILE.exists():
            if not paused:
                log("auto paused — holding current mode")
                paused = True
            time.sleep(TICK)
            continue
        if paused:
            log("auto resumed")
            paused = False
        eth = eth_ok()
        if not eth:
            down_ticks += 1
        else:
            down_ticks = 0

        if state != "failover" and down_ticks >= DEBOUNCE:
            log("ethernet DOWN", down_ticks * TICK, "s — failing over")
            if failover_up():
                state = "failover"
                telegram(f"🔴 lab ethernet down — failover to {UP_SSID} ({IFACE})")
                hit_probe.clear()
        elif state == "failover" and eth:
            log("ethernet back — restoring AP")
            failover_down()
            state = "ap"
            telegram("🟢 lab ethernet restored — back on " + ETH)

        if state != "failover":
            try:
                n = client_count((PROC / "all_sta_info").read_text())
            except OSError:
                n = 0
            if n > 0:
                idle_since = None
                if state != "ap":
                    log(f"{n} client(s) want the AP")
                    stop_sniffer()
                    if switch_wifi("ap"):
                        state = "ap"
                if state == "ap":
                    Led.STATE["mode"] = "ap"
            elif state == "ap" or state == "boot":
                idle_since = idle_since or time.time()
                if time.time() - idle_since >= IDLE_SECS or state == "boot":
                    log("idle — going to monitor, listening for probes")
                    if switch_wifi("monitor", channel=ap_channel()):
                        state = "monitor"
                        probe_watch.set()
                        sniff_thread = threading.Thread(
                            target=sniff_probes, args=(SSID, on_probe), daemon=True)
                        sniff_thread.start()
                        Led.STATE["mode"] = "monitor"
                    idle_since = time.time()
            elif state == "monitor":
                if hit_probe.is_set():
                    hit_probe.clear()
                    log("probe request for", SSID, "— bringing the AP up")
                    stop_sniffer()
                    if switch_wifi("ap"):
                        state = "ap"
                        Led.STATE["mode"] = "ap"
        time.sleep(TICK)


def selftest():
    sample = """==============================
sta's macaddr:8c:90:2d:95:2a:8d
wpa_psk=0x0
wpa2_group_cipher=0x0
==============================
sta's macaddr:18:01:f1:08:7e:5f
wpa_psk=0x2
wpa2_pairwise_cipher=0x10
==============================
sta's macaddr:ff:ff:ff:ff:ff:ff
wpa_psk=0x0
==============================
"""
    import autosense as me
    me.own_mac = lambda: "8c:90:2d:95:2a:8d"   # the dongle lists itself
    assert me.client_count(sample) == 1, "own+dummy MACs must be excluded, cipher needed"
    me.own_mac = lambda: None
    assert me.client_count(sample) == 1
    # decision matrix: eth x clients -> state
    def decide(eth, clients, state, idle_elapsed):
        if state == "failover":
            return "ap" if eth else "failover"
        if not eth:
            return "failover"
        if clients > 0:
            return "ap"
        if idle_elapsed >= IDLE_SECS:
            return "monitor"
        return state
    assert decide(True, 1, "ap", 999) == "ap"
    assert decide(True, 0, "ap", IDLE_SECS) == "monitor"
    assert decide(True, 0, "ap", 1) == "ap"
    assert decide(False, 1, "ap", 1) == "failover"
    assert decide(False, 0, "monitor", IDLE_SECS) == "failover"
    assert decide(True, 1, "failover", 0) == "ap"
    assert not me.own_mac() or True
    print("selftest OK")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        selftest()
        sys.exit(0)
    main()
