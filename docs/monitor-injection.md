# Monitor-mode TX injection (RTL8192EU)

Working, wire-verified injection on the patched driver. The stock driver
cannot inject at all — here is the full failure chain we walked, in order.

## Root causes (stock driver)

1. **No carrier in monitor mode -> qdisc drops everything silently.**
   `send()` returns success, nothing leaves. Realtek's own fix exists —
   `rtw_indicate_connect()` on monitor iftype in
   `cfg80211_rtw_change_iface()` — but sits behind
   `CONFIG_MONITOR_MODE_XMIT`, commented out in `include/drv_conf.h:190`.
   **Patch 0005 enables it.** After the fix: `/sys/class/net/wlan0/carrier` = 1.

2. **`rtw_monitor_xmit_entry()` demands `rtap_len == 12` exactly** (its own
   RTW_INFO even says "should be 14") and drops everything else — every
   standard radiotap TX header (aireplay-ng, scapy defaults) fails this.
   **Patch 0005 accepts any well-formed radiotap header.**

3. **All RTW_INFO diagnostics are compiled out** (`CONFIG_RTW_DEBUG is
   disabled`), so every drop above is invisible. **Patch 0006 adds
   `pr_debug` probes** at the frame flow: monitor xmit -> dump_mgntframe
   gate -> dump_xframe entry -> write_port result. Enable at runtime:
   ```sh
   echo "file core/rtw_xmit.c +p" > /sys/kernel/debug/dynamic_debug/control
   echo "file core/rtw_mlme_ext.c +p" >> /sys/kernel/debug/dynamic_debug/control
   echo "file hal/rtl8192e/usb/rtl8192eu_xmit.c +p" >> /sys/kernel/debug/dynamic_debug/control
   ```

## Test harness

`tools/inject_test.py` — sends N radiotap + probe-request frames with
SSID "HERMES" on a monitor-mode wlan0 (12-byte radiotap).

## Verification — and a usbmon trap

usbmon's **textual API truncates TX payloads to the first 32 bytes**, and a
Realtek TX URB starts with a 32-byte TX descriptor — so the frame body is
*never* visible in the text stream. Grepping for your payload marker finds
nothing even on a perfect transmission. Verify by URB **size + completion
status** instead:

```
S Bo:6:002:5 -115 72 = <TXDESC 32B...     # submit: 32 TXDESC + 40 frame
C Bo:6:002:5 0 72                          # completion: status 0 = transmitted
```

Test-5 capture (`captures/usbmon-inject-test5.txt`): **10/10 72-byte
submits, 10/10 completions with status 0** — all injected frames hit the air.
Driver-side breadcrumbs for the same 10 frames:

```
8192eu: monitor xmit dumping len=32 rate=2 qsel=18
8192eu: monitor-path dump_xframe entry qsel=18 len=32
8192eu: dump_xframe write_port ret=1 w_sz=72      (ret=1 = _SUCCESS)
```

## Frame flow (for reference)

```
socket(AF_PACKET) -> qdisc [carrier!] -> rtw_xmit_entry
  -> (fwstate WIFI_MONITOR_STATE) -> rtw_monitor_xmit_entry
     [radiotap len check] -> alloc_mgtxmitframe -> dump_mgntframe
     [RTW_CANNOT_RUN gate] -> rtw_hal_mgnt_xmit -> rtl8192eu_mgnt_xmit
  -> rtw_dump_xframe [update_txdesc] -> rtw_write_port -> bulk EP5/6
```
