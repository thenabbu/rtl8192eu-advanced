#!/usr/bin/env bash
# Installs the rtl8192eu web portal. Generic — works on any Linux host with
# the RTL8192EU adapter, on any distro with python3 + systemd.
# Run as root:  sudo ./install.sh
set -euo pipefail

DEST=/opt/rtl8192eu-portal
SRC="$(cd "$(dirname "$0")" && pwd)"

[ "$(id -u)" = 0 ] || { echo "run as root (sudo ./install.sh)"; exit 1; }
[ -d "$DEST" ] && { echo "$DEST already exists — stop the service and remove it first"; exit 1; }

# --- system deps -----------------------------------------------------------
need_pkgs=()
command -v python3 >/dev/null || need_pkgs+=(python3)
python3 -c 'import ensurepip' 2>/dev/null || need_pkgs+=(python3-venv)
if [ "${#need_pkgs[@]}" -gt 0 ]; then
  if command -v apt-get; then apt-get update -qq && apt-get install -y "${need_pkgs[@]}"
  elif command -v dnf; then dnf install -y "${need_pkgs[@]/python3-venv/python3}"
  elif command -v pacman; then pacman -Sy --noconfirm "${need_pkgs[@]}"
  elif command -v zypper; then zypper -q install "${need_pkgs[@]}"
  else echo "install python3 + python3-venv manually, then re-run"; exit 1; fi
fi

# --- portal files + venv ---------------------------------------------------
mkdir -p "$DEST"
cp "$SRC/portal.py" "$SRC/index.html" "$DEST"/
cp "$SRC/autosense.py" "$DEST"/ 2>/dev/null || true
cp "$SRC/autosense.service" /etc/systemd/system/ 2>/dev/null || true
python3 -m venv "$DEST/venv"
"$DEST/venv/bin/pip" install --quiet fastapi 'uvicorn[standard]' scapy

# --- credentials (generated, file only readable by root) -------------------
PW="$(openssl rand -base64 12 2>/dev/null | tr -d '/+=' | cut -c1-16 || head -c16 /dev/urandom | od -An -tx1 | tr -d ' \n')"
umask 077
cat > "$DEST/portal.env" <<ENV
PORTAL_USER=admin
PORTAL_PASS=$PW
PORTAL_PORT=8080
ENV

# --- service ---------------------------------------------------------------
cp "$SRC/rtl8192eu-portal.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now rtl8192eu-portal
grep -q AS_ENABLE "$DEST/portal.env" || printf "\n# autosense mode daemon (opt-in): 1 = monitor-idle + probe-wake + ethernet failover\nAS_ENABLE=0\nAS_SSID=BlockiNG\nAS_IDLE_SECS=300\nAS_UPSTREAM_SSID=NGJIO\nAS_UPSTREAM_PASS=\nAS_GATEWAY=192.168.29.1\n# TG_BOT_TOKEN=\n# TG_CHAT_ID=\n" >> "$DEST/portal.env"
systemctl daemon-reload
if grep -q "^AS_ENABLE=1" "$DEST/portal.env"; then systemctl enable --now autosense; fi

echo
echo "installed."
echo "  portal:  http://<this-machine>:8080"
echo "  user:    admin"
echo "  pass:    $PW"
echo "  change:  edit $DEST/portal.env then 'systemctl restart rtl8192eu-portal'"
echo
echo "the portal binds all interfaces — keep the password safe; anyone on"
echo "your LAN who reaches :8080 gets a login screen."
