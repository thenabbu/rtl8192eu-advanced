#!/bin/sh
# rtlled - full LED control for TP-Link TL-WN822N v4 (RTL8192EU) via the
# rtl8192eu driver's procfs register interface. No rebuild needed.
#
# usage: sudo rtlled.sh status
#        sudo rtlled.sh on
#        sudo rtlled.sh off
#        sudo rtlled.sh blink [n]   # n cycles, default 3
#
# Proven 2026-10-24 (user-verified on the physical dongle): the visible
# LED is LED1 (this chip has no LED0) = bit 11 of the 32-bit
# PHY/baseband register 0x4C (0 = ON, 1 = OFF), gated by clearing
# 0x64 bit 1 and 0x4C bits 15/10/9/8. Byte writes to MAC 0x4c/0x4d/0x4e
# do NOT light the LED. See docs/led-control.md.
P=${RTLLED_PROC:-/proc/net/rtl8192eu/wlan0}
[ -w "$P/write_reg" ] || { echo "need root / driver not loaded"; exit 1; }

r32() { echo "$1 4" > "$P/read_reg"; cat "$P/read_reg" | tail -1 | sed 's/.*=0x//'; }
w32() { echo "$1 $2 4" > "$P/write_reg"; }
arm() { # one-time gate config; caches 0x4C dword with gates cleared
  v64=$(r32 64); w32 64 $(printf %x $(( 0x$v64 & ~0x2 )))
  BASE=$(( 0x$(r32 4c) & ~0x8f00 ))
}

cmd=$1
case $cmd in
  status)
    v64=$(r32 64); v4c=$(r32 4c)
    echo "0x64 = 0x$v64 (bit1 = $(( (0x$v64 >> 1) & 1 )))"
    echo "0x4c = 0x$v4c (bit11 = $(( (0x$v4c >> 11) & 1 )) : 0=ON 1=OFF)"
    echo "gate bits 15/10/9/8 = 0x$(( 0x$v4c & 0x8700 ))"
    ;;
  on)  arm; w32 4c $(printf %x $BASE);             echo "ON  0x4c=0x$(r32 4c)" ;;
  off) arm; w32 4c $(printf %x $((BASE | 0x800))); echo "OFF 0x4c=0x$(r32 4c)" ;;
  blink)
    n=${2:-3}; i=0; arm
    while [ $i -lt $n ]; do
      w32 4c $(printf %x $BASE); sleep 0.4
      w32 4c $(printf %x $((BASE | 0x800))); sleep 0.4
      i=$((i+1))
    done
    echo "blinked $n x, left OFF (0x4c = 0x$(r32 4c))"
    ;;
  *) echo "usage: rtlled.sh {status|on|off|blink [n]}"; exit 1 ;;
esac
