#!/bin/sh
# rtlled - full LED control for TP-Link TL-WN822N v4 (RTL8192EU) via the
# rtl8192eu driver's procfs register interface. No rebuild needed.
#
# usage: sudo rtlled.sh status
#        sudo rtlled.sh on   [reg]   # default reg=4d (LEDCFG1)
#        sudo rtlled.sh off  [reg]
#        sudo rtlled.sh blink [n] [reg]   # n cycles, default 3
#
# Registers: 4c=LEDCFG0 4d=LEDCFG1 4e=LEDCFG2 (see docs/led-control.md)
# Semantics (from hal/rtl8192e/usb/rtl8192eu_led.c): clear bit7 = LED ON,
# set bit7 = LED OFF.
P=${RTLLED_PROC:-/proc/net/rtl8192eu/wlan0}
REG=${2:-4d}
[ -w "$P/read_reg" ] || { echo "need root / driver not loaded"; exit 1; }

rd() { echo "$1 1" > "$P/read_reg"; cat "$P/read_reg" | sed 's/.*=0x//'; }
wr() { echo "$1 $2 1" > "$P/write_reg"; }

cmd=$1
case $cmd in
  status)
    for r in 4c 4d 4e 64; do
      REG=$r; echo "LEDCFG@$r = 0x$(rd $r)"
    done ;;
  on)  v=$(rd $REG); wr $REG $(printf %x $(( 0x$v & ~0x80 ))); echo "$REG -> 0x$(rd $REG) (bit7 clear = ON)" ;;
  off) v=$(rd $REG); wr $REG $(printf %x $(( 0x$v | 0x80 ))); echo "$REG -> 0x$(rd $REG) (bit7 set = OFF)" ;;
  blink)
    n=${2:-3}; REG=${3:-4d}; i=0
    v=$(rd $REG)
    while [ $i -lt $n ]; do
      wr $REG $(printf %x $(( 0x$v & ~0x80 ))); sleep 0.4
      wr $REG $(printf %x $(( 0x$v | 0x80 ))); sleep 0.4
      i=$((i+1))
    done
    echo "blinked $REG x$n, left at 0x$(rd $REG)" ;;
  *) echo "usage: rtlled.sh {status|on|off|blink [n] [reg]}"; exit 1 ;;
esac
