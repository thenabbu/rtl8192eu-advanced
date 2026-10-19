# LED full control (TL-WN822N v4)

The dongle's LED is driven by the MAC registers `REG_LEDCFG0/1/2`
(`hal_com_reg.h`: 0x004C / 0x004D / 0x004E), with an alternate LED1 path
using 0x0064 BIT1 + 0x004C BIT11/15. Semantics straight from
`hal/rtl8192e/usb/rtl8192eu_led.c` (`SwLedOn/Off_8192EU`):

- **clear bit7 of the LEDCFGn = LED ON** (driver comment: "SW control led1 on")
- **set bit7 = LED OFF**

8192EU has no LED0 — the driver maps LED0 onto LED1's register.

## Why raw register writes are THE control path

The driver's LED stack (`CONFIG_RTW_LED` -> `CONFIG_RTW_SW_LED` in
`include/autoconf.h:150-156`) ships **commented out** in every official and
community build, so nothing in the running driver ever touches the LED and
no `led_config` proc entry exists. The generic register interface stays
available though:

```sh
# read: set args (hex addr, hex len), then cat
echo "4d 1" > /proc/net/rtl8192eu/wlan0/read_reg; cat .../read_reg
# write: hex "addr value len"
echo "4d 02 1" > /proc/net/rtl8192eu/wlan0/write_reg
```

`tools/rtlled.sh` wraps this: `status` / `on` / `off` / `blink n`.

## Observed baseline (AP duty, patched 5.11.2.1 build)

`4c=0x82  4d=0x82  4e=0x62  64=0x06` — restored after every experiment.

## Wire proof (`../captures/usbmon-led-test.txt`)

Every userspace write appears as a vendor request on EP0, e.g. the blink
sequence (20 LED writes total, restore at +7.94 s):

```
+5.51s  wValue=0x004d data=0x02   (ON)
+5.92s  wValue=0x004d data=0x82   (OFF)
+5.52s  wValue=0x004e data=0x62   (ON)
+5.92s  wValue=0x004e data=0xe2   (OFF)
+7.94s  restore: 4c=0x82 4d=0x82 4e=0x62 64=0x06
```

## Roadmap

- Enable `CONFIG_RTW_LED` + `CONFIG_RTW_SW_LED` upstream-style to expose
  the driver's own `led_config` (strategy + iface mask) and link/activity
  blinking behaviors (patch candidate 0004).
- A `/sys/class/leds` class device would make the dongle LED work with
  standard userspace tooling (LedTrigger), needs a small classdev wrapper.
