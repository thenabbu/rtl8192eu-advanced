# LED full control (TL-WN822N v4)

**Proven 2026-10-24 — user verified the physical light.** The visible
LED is LED1 (this chip has no LED0). It is driven by **bit 11 of the
32-bit PHY/baseband register at 0x4C**, set up by the sequence in
`SwLedOn/Off_8192EU` (`hal/rtl8192e/usb/rtl8192eu_led.c`):

| Register bit | Role |
|---|---|
| `0x4C` bit 11 | LED on/off — **0 = ON, 1 = OFF** |
| `0x4C` bits 15/10/9/8 | SW-control gate — must be cleared first |
| `0x64` bit 1 | SW-control gate — must be cleared first |

- **ON** = clear `0x64` bit 1, clear `0x4C` bits 15/10/9/8/11
- **OFF** = set `0x4C` bit 11 (gates stay cleared)
- Measured: ON `0x4C = 0x06620082`, `0x64 = 0x30430004`
  OFF `0x4C = 0x06620882`

## What does NOT light the LED (tested dark)

Byte writes to the MAC registers 0x4C/0x4D/0x4E (`REG_LEDCFG0/1/2`),
every value tried — including the vendor MP-blink `4d 02`: **dark**.
They read back fine but are not wired to the visible LED on this
chip. The earlier "bit 7 of LEDCFG1" theory was wrong.

## Control path (no driver changes)

`read_reg`/`write_reg` take a width column; `4` = 32-bit access:

```sh
W=/proc/net/rtl8192eu/wlan0
echo "4c 4" > $W/read_reg && tail -1 $W/read_reg    # read dword
echo "4c 6620082 4" > $W/write_reg                  # 32-bit write
```

`tools/rtlled.sh` wraps the proven sequence: `status` / `on` / `off` /
`blink n`. `portal/autosense.py` uses the same writes for its mode
indication: **breathing = monitor, 1 Hz blink = AP, solid = station**
(NGJIO failover).

## Evidence chain (2026-10-24)

- Byte holds `4d 02 1` (+ `4c 82 1`), 02:44 and 03:38: user saw dark
- 32-bit sequence hold, window 03:58:53–04:08:53: **user saw the light**
- `captures/usbmon-led-test.txt`: byte writes do reach the chip on EP0
  (wValue=0x004d) — the chip simply ignores them for the LED

## Roadmap

- Enable `CONFIG_RTW_LED` + `CONFIG_RTW_SW_LED` upstream-style to
  expose the driver's own `led_config` (strategy + iface mask) and
  link/activity blinking behaviors (patch candidate 0004).
- A `/sys/class/leds` class device would make the dongle LED work with
  standard userspace tooling (LedTrigger); needs a small classdev
  wrapper.
