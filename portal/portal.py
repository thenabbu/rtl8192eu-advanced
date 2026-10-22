#!/usr/bin/env python3
"""rtl8192eu-portal — generic web control panel for Realtek RTL8192EU adapters.

Talks to the driver's procfs surface (/proc/net/<mod>/<iface>/), cfg80211
via `ip`/`iw`, and hostapd/dnsmasq/wpa_supplicant if the host has them.
Nothing here is adapter-config specific: install on any Linux box with the
dongle and the right tabs appear.
"""
import hmac
import os
import re
import shutil
import subprocess
import sys
import time
from collections import deque
from datetime import datetime
from functools import lru_cache
from pathlib import Path

try:
    from fastapi import Depends, FastAPI, HTTPException, Request
    from fastapi.responses import FileResponse
    from fastapi.security import HTTPBasic, HTTPBasicCredentials
except ImportError:
    if len(sys.argv) < 2 or sys.argv[1] != "--selftest":
        raise
    # stubs — --selftest only exercises parse/regex helpers, no server
    class HTTPException(Exception):
        def __init__(self, code, msg, headers=None):
            super().__init__(f"{code}: {msg}")
    class _Stub:
        def __init__(self, *a, **k): pass
        def get(self, *a, **k): return lambda f: f
        def post(self, *a, **k): return lambda f: f
    class FastAPI(_Stub): pass
    class Request: pass
    class FileResponse: pass
    class HTTPBasicCredentials: pass
    def Depends(*a, **k): return None
    def HTTPBasic(*a, **k): return None

# ---------------------------------------------------------------- config

PORTAL_HOME = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORTAL_PORT", "8080"))
USER = os.environ.get("PORTAL_USER", "admin")
PASS = os.environ.get("PORTAL_PASS", "")

PROC_ROOT: Path | None = None
IFACE_DIR: Path | None = None
IFACE = os.environ.get("PORTAL_IFACE", "")

REG_RE = re.compile(r"^0[xX][0-9a-fA-F]{1,6}$")
DANGEROUS = {"write_reg", "read_reg", "sreset"}


def _find_proc_root() -> Path | None:
    """Locate /proc/net/<driver>/<iface>. Works for any rtl/rtw module name."""
    for d in sorted(Path("/proc/net").iterdir()):
        if not d.is_dir():
            continue
        low = d.name.lower()
        if not (("rtl" in low or "rtw" in low) and len(low) <= 16):
            continue
        if any(x.is_dir() for x in d.iterdir()):
            return d
    return None


def init():
    global PROC_ROOT, IFACE_DIR, IFACE
    env_root = os.environ.get("PORTAL_PROC_ROOT")
    if env_root:
        PROC_ROOT = Path(env_root)
    else:
        PROC_ROOT = _find_proc_root()
    if PROC_ROOT is None or not PROC_ROOT.is_dir():
        sys.exit("no rtl8192eu procfs root found under /proc/net — is the driver loaded?")
    subdirs = sorted(x for x in PROC_ROOT.iterdir() if x.is_dir())
    if not subdirs:
        sys.exit(f"no interface dir under {PROC_ROOT}")
    IFACE_DIR = subdirs[0]
    IFACE = IFACE or IFACE_DIR.name


# ---------------------------------------------------------------- helpers

def run(*args, timeout=20):
    """shell=False subprocess; returns (rc, out, err)."""
    try:
        p = subprocess.run(list(args), capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, "", str(e)


def which(name):
    return shutil.which(name)


@lru_cache(maxsize=1)
def driver_version():
    try:
        return (PROC_ROOT / "ver_info").read_text().strip().splitlines()[0]
    except Exception:
        return "unknown"


def proc_read(name):
    if not re.match(r"^[A-Za-z0-9_.-]+$", name):
        raise HTTPException(400, "bad name")
    p = IFACE_DIR / name
    if not p.is_file():
        p = PROC_ROOT / name
    if not p.is_file():
        raise HTTPException(404, f"no such procfs entry: {name}")
    return p.read_text()


def proc_names():
    """name -> writable, for global + iface entries (fresh each call)."""
    out = {}
    for root in (PROC_ROOT, IFACE_DIR):
        for x in sorted(root.iterdir()):
            if x.is_file() and x.name not in out:
                out[x.name] = bool(x.stat().st_mode & 0o200)
    return out


def _own_mac():
    try:
        return Path(f"/sys/class/net/{IFACE}/address").read_text().strip().lower()
    except OSError:
        return None


def parse_sta_info(text, own=None):
    """Split all_sta_info into per-client dicts. Blocks start at a macaddr line."""
    own = own or _own_mac()
    clients, cur = [], None
    for line in text.splitlines():
        m = re.search(r"sta's macaddr:([0-9a-f]{2}(?::[0-9a-f]{2}){5})", line, re.I)
        if m:
            cur = {"mac": m.group(1).lower()}
            clients.append(cur)
            continue
        if cur is None:
            continue
        for key, pat in (
            ("tx_pkts", r"tx_data_pkts=(\d+)"),
            ("rx_pkts", r"rx_data_uc_pkts=(\d+)"),
            ("tx_bytes", r"tx_bytes=(\d+)"),
            ("rx_bytes", r"rx_uc_bytes=(\d+)"),
            ("rx_tp", r"rx_tp =(\d+)"),
        ):
            m2 = re.search(pat, line)
            if m2:
                cur[key] = int(m2.group(1))
        if "wpa2_psk=0x1" in line or "wpa_psk=0x1" in line:
            cur["wpa"] = True
    return [c for c in clients
            if c["mac"] != own
            and not set(c["mac"].replace(":", "")) <= {"f", "0"}]


def current_mode():
    rc, out, _ = run("iw", "dev", IFACE, "info")
    if rc != 0:
        return "unknown"
    m = re.search(r"type (\w+)", out)
    if not m:
        return "unknown"
    t = m.group(1).lower()
    return {"ap": "ap", "managed": "station", "monitor": "monitor"}.get(t, t)


def service_state(name):
    """active / inactive / absent"""
    rc, out, _ = run("systemctl", "is-active", name, timeout=5)
    s = out.strip()
    if s in ("active", "inactive"):
        return s
    rc, _, _ = run("systemctl", "cat", name, timeout=5)
    return "absent" if rc != 0 else s or "unknown"


def parse_hostapd(conf_path):
    try:
        text = Path(conf_path).read_text()
    except OSError:
        return None
    data = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        data[k.strip()] = v.strip()
    data["_path"] = str(conf_path)
    data["_ht_capab"] = "ht_capab" in data
    data.pop("ht_capab", None)
    if "wpa_passphrase" in data:
        data["wpa_passphrase"] = f"set ({len(data['wpa_passphrase'])} chars)"
    return data


def parse_dnsmasq(conf_path):
    try:
        text = Path(conf_path).read_text()
    except OSError:
        return None
    out = {"_path": str(conf_path), "interface": None, "dhcp_range": None, "dns": None}
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            continue
        if line.startswith("interface="):
            out["interface"] = line.split("=", 1)[1]
        elif line.startswith("dhcp-range="):
            out["dhcp_range"] = line.split("=", 1)[1]
        elif line.startswith("dhcp-option=6,"):
            out["dns"] = line.split("=", 1)[1]
    return out


def find_hostapd_conf():
    for p in ("/etc/hostapd/hostapd.conf", "/etc/hostapd.conf",
              "/etc/wpa_supplicant/hostapd.conf"):
        if Path(p).is_file():
            return p
    return None


# ---------------------------------------------------------------- selftest

def selftest():
    sample = """==============================
sta's macaddr:8c:90:2d:95:2a:8d
rtsen=0, cts2slef=0
state=0x15, aid=1, macid=3, raid=1
wpa_psk=0x0
wpa2_psk=0x1
rx_data_uc_pkts=1234
rx_uc_bytes=56789
rx_tp =24000 (Kbps)
tx_data_pkts=99
tx_bytes=1000
==============================
sta's macaddr:ff:ff:ff:ff:ff:ff
rx_data_uc_pkts=0
tx_data_pkts=0
tx_bytes=0
rx_uc_bytes=0
"""
    c = parse_sta_info(sample)
    assert len(c) == 1 and c[0]["mac"] == "8c:90:2d:95:2a:8d", c
    assert c[0]["rx_pkts"] == 1234 and c[0]["tx_pkts"] == 99 and c[0]["wpa"], c
    cfg = "interface=wlan0\nssid=BlockiNG\nchannel=11\n# comment\nwpa_passphrase=AHA@password\nht_capab=[RX-STBC1]\nmax_num_sta=25\n"
    t = re.sub(r"^channel=.*$", "channel=6", cfg, flags=re.M)
    t = re.sub(r"^ssid=.*$", "ssid=Test", t, flags=re.M)
    assert "channel=6" in t and "ssid=Test" in t and "ht_capab=[RX-STBC1]" in t and "max_num_sta=25" in t, t
    assert REG_RE.match("0x424")
    assert not REG_RE.match("0x1234567")
    assert re.match(r"^(0[xX][0-9a-fA-F]{1,6}) (0[xX][0-9a-fA-F]{1,8}) ([124])$", "0x424 0x1234 2")
    assert not re.match(r"^(0[xX][0-9a-fA-F]{1,6}) (0[xX][0-9a-fA-F]{1,8}) ([124])$", "0x424 0x1234 8")
    # own-MAC exclusion: the AP lists its own dongle MAC as a sta entry
    assert parse_sta_info(sample, own="8c:90:2d:95:2a:8d") == []
    print("selftest OK")


# ---------------------------------------------------------------- monitor

frames = deque(maxlen=300)
_sniff_on = False


def _on_pkt(pkt):
    d = {"t": datetime.now().strftime("%H:%M:%S"), "len": len(pkt),
         "ch": "", "rate": "", "sig": "", "type": "?", "subtype": "?",
         "a1": "", "a2": "", "a3": ""}
    rt = pkt.get("Radiotap")
    if rt is not None:
        if rt.getfieldval("dBmAntSignal") is not None:
            d["sig"] = f"{rt.getfieldval('dBmAntSignal')}dBm"
        if rt.getfieldval("Channel") is not None:
            d["ch"] = str(int(rt.getfieldval("Channel")))
        if rt.getfieldval("Rate") is not None:
            d["rate"] = f"{rt.getfieldval('Rate') * 2:.0f}M"
    d11 = pkt.get("Dot11")
    if d11 is not None:
        types = {0: "mgmt", 1: "ctrl", 2: "data"}
        sub = {(0, 0): "beacon", (0, 1): "assoc-req", (0, 2): "assoc-resp",
               (0, 3): "auth", (0, 4): "deauth", (0, 5): "probe-req",
               (0, 8): "probe-resp", (0, 11): "action", (0, 10): "disassoc",
               (0, 12): "reassoc-req", (0, 13): "assoc-req"}
        d["type"] = types.get(d11.type, str(d11.type))
        d["subtype"] = sub.get((d11.type, d11.subtype), str(d11.subtype))
        d["a1"], d["a2"] = d11.addr1, d11.addr2
        if d11.type == 2:
            d["a3"] = d11.addr3
    frames.append(d)


def _sniff_loop():
    global _sniff_on
    from scapy.all import sniff
    while _sniff_on:
        try:
            sniff(iface=IFACE, prn=_on_pkt, store=False, timeout=1)
        except Exception:
            time.sleep(1)


def _start_sniffer():
    global _sniff_on
    import threading
    _sniff_on = True
    threading.Thread(target=_sniff_loop, daemon=True).start()


# ---------------------------------------------------------------- app

app = FastAPI()
basic = HTTPBasic(auto_error=False)


def auth(creds: HTTPBasicCredentials | None = Depends(basic)):
    if not PASS:
        raise HTTPException(500, "PORTAL_PASS not set — refusing to run without auth")
    ok = creds and hmac.compare_digest(creds.username, USER) and hmac.compare_digest(creds.password, PASS)
    if not ok:
        raise HTTPException(401, "unauthorized", headers={"WWW-Authenticate": "Basic realm=portal"})


@app.get("/", response_class=FileResponse)
def index(_=Depends(auth)):
    return FileResponse(PORTAL_HOME / "index.html", media_type="text/html")


@app.get("/api/status", dependencies=[Depends(auth)])
def status():
    stats = {}
    try:
        st = Path(f"/sys/class/net/{IFACE}/statistics")
        for k in ("rx_bytes", "tx_bytes", "rx_packets", "tx_packets"):
            stats[k] = int((st / k).read_text().strip())
    except OSError:
        pass
    rx_signal, ap_info = {}, {}
    try:
        t = proc_read("rx_signal")
        m = re.search(r"rssi:(-?\d+)", t)
        if m:
            rx_signal["rssi"] = int(m.group(1))
    except Exception:
        pass
    try:
        t = proc_read("ap_info")
        for pat, key in ((r"SSID=(\S+)", "ssid"), (r"cur_channel=(\d+)", "channel"),
                         (r"state=(0x[0-9a-f]+)", "state")):
            m = re.search(pat, t)
            if m:
                ap_info[key] = m.group(1)
    except Exception:
        pass
    tools = {n: bool(which(n)) for n in ("hostapd", "wpa_supplicant", "dnsmasq", "iw")}
    rc, out, _ = run("ip", "-4", "-br", "addr", "show", IFACE)
    ip_addr = ""
    if rc == 0:
        m = re.search(r"\d+\.\d+\.\d+\.\d+/\d+", out)
        if m:
            ip_addr = m.group(0)
    try:
        clients = parse_sta_info(proc_read("all_sta_info"))
    except Exception:
        clients = []
    return {
        "iface": IFACE, "mode": current_mode(), "driver": driver_version(),
        "proc_root": str(PROC_ROOT), "ap_info": ap_info, "clients": clients,
        "stats": stats, "rx_signal": rx_signal,
        "country": (proc_read("country_code") or "").strip(),
        "tx_power_offset": (proc_read("tx_power_offset") or "").strip(),
        "fw_info": (proc_read("fw_info") or "").strip()[:400],
        "tools": tools,
        "services": {n: service_state(n) for n in ("hostapd", "dnsmasq")},
        "ip": ip_addr,
    }


@app.get("/api/proc", dependencies=[Depends(auth)])
def proc_list():
    return proc_names()


@app.get("/api/proc/read", dependencies=[Depends(auth)])
def proc_read_api(name: str, reg: str | None = None, len_: int = 4):
    if name == "read_reg" and reg:
        if not REG_RE.match(reg) or len_ not in (1, 2, 4):
            raise HTTPException(400, "reg must be 0x-hex, len one of 1/2/4")
        (IFACE_DIR / "read_reg").write_text(f"{reg} {len_}\n")
        time.sleep(0.05)
        return proc_read("read_reg")
    return proc_read(name)


@app.post("/api/proc/write", dependencies=[Depends(auth)])
async def proc_write_api(req: Request):
    import json as _json
    body = _json.loads((await req.body()) or b"{}")
    name, value = body.get("name", ""), body.get("value", "")
    confirm = body.get("confirm", "")
    if name not in proc_names():
        raise HTTPException(404, f"no such procfs entry: {name}")
    value = value.strip()
    if not value or len(value) > 1024 or "\n" in value or "\x00" in value:
        raise HTTPException(400, "value must be 1..1024 chars, single line, no NUL")
    if name == "write_reg":
        if not re.match(r"^(0[xX][0-9a-fA-F]{1,6}) (0[xX][0-9a-fA-F]{1,8}) ([124])$", value):
            raise HTTPException(400, "write_reg format: 0xADDR 0xVAL 1|2|4")
        if confirm != "DANGER":
            raise HTTPException(400, "raw register write requires confirm='DANGER'")
    elif name == "read_reg":
        if not re.match(r"^0[xX][0-9a-fA-F]{1,6} [124]$", value):
            raise HTTPException(400, "read_reg format: 0xADDR 1|2|4")
        if confirm != "DANGER":
            raise HTTPException(400, "raw register access requires confirm='DANGER'")
    elif name in DANGEROUS and confirm != "DANGER":
        raise HTTPException(400, f"{name} requires confirm='DANGER'")
    target = IFACE_DIR / name if (IFACE_DIR / name).exists() else PROC_ROOT / name
    target.write_text(value + "\n")
    return {"written": name, "value": value}


@app.get("/api/mode", dependencies=[Depends(auth)])
def mode_get():
    return {"mode": current_mode()}


@app.post("/api/mode", dependencies=[Depends(auth)])
async def mode_set(req: Request):
    import json as _json
    body = _json.loads((await req.body()) or b"{}")
    mode = body.get("mode")
    if mode not in ("ap", "station", "monitor"):
        raise HTTPException(400, "mode must be ap|station|monitor")
    if body.get("confirm") != "SWITCH":
        raise HTTPException(400, "confirm='SWITCH' required")
    log = []
    if mode != "ap" and service_state("hostapd") == "active":
        run("systemctl", "stop", "hostapd")
        log.append("stopped hostapd")
    if mode != "station":
        rc, _, _ = run("pkill", "-x", "wpa_supplicant")
        if rc == 0:
            log.append("stopped wpa_supplicant")
    rc, _, _ = run("ip", "link", "set", IFACE, "down")
    log.append(f"ip link set {IFACE} down")
    rc, out, err = run("ip", "link", "set", IFACE, "type", mode)
    if rc != 0:
        run("ip", "link", "set", IFACE, "up")
        raise HTTPException(500, f"switch failed: {err.strip()} (link restored)")
    run("ip", "link", "set", IFACE, "up")
    log.append(f"ip link set {IFACE} up")
    if mode == "ap" and which("hostapd"):
        run("systemctl", "start", "hostapd")
        log.append("started hostapd")
    if mode == "station":
        conf = Path(f"/etc/wpa_supplicant/wpa-{IFACE}.conf")
        if conf.is_file() and which("wpa_supplicant"):
            run("wpa_supplicant", "-i", IFACE, "-c", str(conf), "-B")
            log.append("started wpa_supplicant")
    time.sleep(1.5)
    return {"mode": current_mode(), "log": log}


@app.get("/api/net", dependencies=[Depends(auth)])
def net_get():
    hp = find_hostapd_conf()
    return {
        "hostapd": parse_hostapd(hp) if hp else None,
        "dnsmasq": parse_dnsmasq("/etc/dnsmasq.conf") if Path("/etc/dnsmasq.conf").is_file() else None,
        "tools": {n: bool(which(n)) for n in ("hostapd", "wpa_supplicant", "dnsmasq")},
    }


@app.post("/api/net", dependencies=[Depends(auth)])
async def net_set(req: Request):
    import json as _json
    body = _json.loads((await req.body()) or b"{}")
    if body.get("confirm") != "RESTART":
        raise HTTPException(400, "confirm='RESTART' required")
    conf = find_hostapd_conf()
    if not conf:
        raise HTTPException(404, "no hostapd.conf found — install hostapd first")
    text = Path(conf).read_text()
    fields = {
        "ssid": r"^[a-zA-Z0-9!-~]{1,32}$",
        "channel": r"^([1-9]|1[0-4]|[23][0-9])$",
        "country_code": r"^[a-zA-Z]{2}$",
        "max_num_sta": r"^[1-9][0-9]{0,2}$",
    }
    for k, pat in fields.items():
        if k in body and body[k] not in (None, "") and not re.match(pat, str(body[k])):
            raise HTTPException(400, f"invalid {k}")
    if body.get("passphrase") not in (None, "") and len(body["passphrase"]) < 8:
        raise HTTPException(400, "passphrase must be >= 8 chars (or omit)")
    for k in ("ssid", "channel", "country_code", "max_num_sta"):
        if k in body and body[k] not in (None, ""):
            text = re.sub(rf"^{k}=.*$", f"{k}={body[k]}", text, flags=re.M)
    if body.get("passphrase") not in (None, ""):
        text = re.sub(r"^wpa_passphrase=.*$", f"wpa_passphrase={body['passphrase']}", text, flags=re.M)
    Path(conf).write_text(text)
    hp_bin = which("hostapd") or "/usr/sbin/hostapd"
    rc, out, err = run(hp_bin, "-t", str(conf))
    if rc != 0:
        raise HTTPException(500, f"hostapd -t failed (config not applied): {err.strip() or out.strip()}")
    run("systemctl", "restart", "hostapd")
    time.sleep(2.5)
    st = service_state("hostapd")
    if st != "active":
        raise HTTPException(500, f"hostapd did not come back ({st}) — check journalctl -u hostapd")
    return {"applied": True, "hostapd": st, "conf": str(conf)}


@app.get("/api/scan", dependencies=[Depends(auth)])
def scan():
    rc, out, err = run("iw", "dev", IFACE, "scan", timeout=30)
    if rc != 0:
        raise HTTPException(500, f"scan failed: {err.strip() or out.strip()}")
    nets, cur = [], None
    for line in out.splitlines():
        line = line.strip()
        if line == "BSS ":
            if cur:
                nets.append(cur)
            cur = {"bssid": line.split()[-1]}
        elif cur is not None:
            if line.startswith("SSID:"):
                cur["ssid"] = line[5:].strip()
            elif line.startswith("signal:"):
                m = re.match(r"signal:\s*(-?\d+)", line)
                if m:
                    cur["signal"] = int(m.group(1))
            elif line.startswith("frequency:"):
                m = re.match(r"frequency:\s*(\d+)", line)
                if m:
                    cur["freq"] = int(m.group(1))
    if cur:
        nets.append(cur)
    nets = [n for n in nets if n.get("ssid")]
    nets.sort(key=lambda n: -n.get("signal", -99))
    return nets[:40]


@app.post("/api/station", dependencies=[Depends(auth)])
async def station_connect(req: Request):
    import json as _json
    body = _json.loads((await req.body()) or b"{}")
    ssid, psk = body.get("ssid", ""), body.get("passphrase", "")
    if not re.match(r"^[a-zA-Z0-9!-~]{1,32}$", ssid):
        raise HTTPException(400, "invalid ssid")
    if body.get("confirm") != "CONNECT":
        raise HTTPException(400, "confirm='CONNECT' required")
    confdir = Path("/etc/wpa_supplicant")
    confdir.mkdir(mode=0o755, exist_ok=True)
    conf = confdir / f"wpa-{IFACE}.conf"
    net = 'network={\n\tssid="' + ssid + '"\n'
    net += f'\tpsk="{psk}"\n' if psk else "\tkey_mgmt=NONE\n"
    net += "}\n"
    conf.write_text(net)
    if not which("wpa_supplicant"):
        raise HTTPException(404, "wpa_supplicant not installed")
    run("wpa_supplicant", "-i", IFACE, "-c", str(conf), "-B")
    run("ip", "link", "set", IFACE, "up")
    return {"conf": str(conf), "ssid": ssid}


@app.get("/api/monitor/frames", dependencies=[Depends(auth)])
def monitor_frames():
    mode = current_mode()
    if mode == "monitor" and not _sniff_on:
        _start_sniffer()
    last = list(frames)[-200:]
    counts = {}
    for f in last:
        key = f"{f.get('type')}/{f.get('subtype', '?')}"
        counts[key] = counts.get(key, 0) + 1
    return {"active": _sniff_on, "mode": mode, "frames": last, "counts": counts}


@app.post("/api/monitor/stop", dependencies=[Depends(auth)])
def monitor_stop():
    global _sniff_on
    _sniff_on = False
    return {"active": False}


# ---------------------------------------------------------------- main

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        selftest()
        sys.exit(0)
    init()
    if not PASS:
        sys.exit("PORTAL_PASS not set — set it in the env file, this portal never runs unauthenticated")
    print(f"portal: procfs={PROC_ROOT}/{IFACE} iface={IFACE} port={PORT}", flush=True)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")
