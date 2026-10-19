# USB wire protocol (RTL8192EU via rtl8192eu vendor driver)

All evidence: usbmon text captures in `../captures/`, correlated against
driver source (`os_dep/linux/usb_ops_linux.c`, `hal/rtl8192e/`).

## Endpoints (lsusb, docs/lsusb-full.txt)

| EP | Type | Role |
|---|---|---|
| 0x04 IN | bulk | RX (32 KiB URBs) |
| 0x05 OUT | bulk | TX |
| 0x06 OUT | bulk | TX |
| 0x07 IN | interrupt | (unused by this driver at runtime — 0 submits observed) |
| 0x08 OUT | bulk | TX |
| 0x00 | control | ALL register I/O |

## Vendor request (the entire register protocol)

```
bmRequestType 0x40 (OUT) / 0xC0 (IN), bRequest 0x05, wValue = register address,
wIndex = 0, wLength = 1 | 2 | 4 (register width) or 254 (block upload)
```

Source: `REALTEK_USB_VENQT_CMD_REQ`/`REALTEK_USB_VENQT_WRITE` in
`usb_ops_linux.c:109,172`. No other vendor request exists in steady state.

## Init sequence (captured across a controlled module bounce)

30 phases, ~12 000 control ops over 43 s (5.6.4) / ~9 400 ops (5.11.2.1):

1. teardown burst (hostapd stop → interface down)
2. rmmod → usbcore device reset on unbind: descriptor re-reads +
   `SET_CONFIGURATION` appear mid-capture (this is the reset, not a second device)
3. probe: MAC-page register sweep + EFUSE read via `REG_EFUSE_CTRL_8192E`
   (0x0030–0x0033 protocol), ~1 424 ops
4. **firmware download**: 126 × 254-byte control writes
   (`MAX_REG_BOLCK_SIZE`, `rtl8192e_hal_init.c`) ≈ 32 KiB + 8-byte tail writes
5. PHY/RF calibration (~1 599 ops: pages 0x08/0x09/0x0D/0x0E) + TXAGC tables
6. steady state: periodic poll, ~100 register ops every ~2.05 s (PhyDM
   dynamic mechanism: AFE 0x0818, 0x0DF4, TXAGC readbacks…)

## Version differences (5.6.4 vs 5.11.2.1 on the wire)

- Same protocol, same FWDL structure, same poll cadence
- 5.6.4 re-downloads the firmware a **second** time at every interface-up
  (+3 700 ops + another 32 KiB flash); 5.11.2.1 does a 76-op ifup path
- 5.11.2.1 adds ~1 858 ops of extra RF configuration at probe

## Steady state (20 s idle AP)

1 322 register ops (735 reads / 587 writes), all bRequest 0x05; pages
touched: 0x08 (45 %), 0x01, 0x0D, 0x0A, 0x0C, 0x0F. RX: 21 × 32 KiB bulk IN.
