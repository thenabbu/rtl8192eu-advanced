# 8192eu — install guide

Builds on kernels 5.x → 7.0 (CI-verified on Ubuntu 22.04 / 5.15 and 24.04 / 6.8).

**Monitor mode** is enabled in this tree (`CONFIG_WIFI_MONITOR = y`).

## Prerequisites

```bash
# Debian / Ubuntu / Mint
sudo -S -p '' apt install linux-headers-generic build-essential dkms git
# Fedora
sudo -S -p '' dnf groupinstall "C Development Tools and Libraries" && sudo -S -p '' dnf install dkms git
# RHEL / CentOS
sudo -S -p '' yum groupinstall "Development Tools" && sudo -S -p '' yum install dkms git
# Arch / Manjaro
sudo -S -p '' pacman -S base-devel dkms git
# openSUSE
sudo -S -p '' zypper install -t pattern devel_C_C++ && zypper install dkms git
```

Non-x86: set `CONFIG_PLATFORM_I386_PC = n` and your platform in the `Makefile` (e.g. `CONFIG_PLATFORM_ARM_RPI = y` for 32-bit ARM, `CONFIG_PLATFORM_ARM_AARCH64 = y` for 64-bit).

## Quick install

```bash
sudo -S -p '' ./install_wifi.sh          # add + install via DKMS
sudo -S -p '' ./uninstall_wifi.sh        # remove
```

## Manual install

```bash
# remove any existing 8192eu / competing driver
sudo -S -p '' rmmod 8192eu
sudo -S -p '' rmmod rtl8xxxu
sudo -S -p '' dkms remove -m rtl8192eu -v 1.0

# blacklist the in-tree fallback (rtl8xxxu on Ubuntu)
echo "blacklist rtl8xxxu" | sudo -S -p '' tee /etc/modprobe.d/blacklist-rtl8xxxu.conf

# build + install
sudo -S -p '' cp -ar . /usr/src/rtl8192eu-1.0
sudo -S -p '' dkms add -m rtl8192eu -v 1.0
sudo -S -p '' dkms install -m rtl8192eu -v 1.0
sudo -S -p '' modprobe 8192eu
```

For AP duty, keep power management off:

```bash
sudo -S -p '' modprobe 8192eu rtw_power_mgnt=0 rtw_enusbss=0
```

## Secure Boot

With Secure Boot in deployed mode, enroll the MOK key shown during install once:

```bash
sudo -S -p '' mokutil --import [public_key]   # then reboot and confirm
```

(Or switch to BIOS audit mode to use it without enrolling.)

## Troubleshooting

Before opening an issue, post:

1. kernel version + distro name/version
2. tail of `make.log` if it doesn't compile
3. `lsusb` and `lsmod | grep 8192eu` if it compiles but doesn't work
4. `sudo dmesg | grep -i 8192eu` (limited)
