# Bugs found (both shipping in official *and* community drivers)

## 1. Runtime-PM usage-count underflow on every rmmod (fixed — patch 0001)

`rtl8192eu 6-2:1.0: Runtime PM usage count underflow!` on every module
unload, on 5.6.4 and 5.11.2.1 alike.

Root cause (proved with a dyndbg probe in our patch): probe calls
`usb_autopm_get_interface()` — which **fails with usage=0** on modern
kernels (runtime PM not yet enabled for the interface during probe) — then
unconditionally sets the driver's `autopm_cnt = 1`. Remove trusts that
counter and puts a hold that was never taken → usage goes negative.

Fix: only claim the hold that was actually taken (`autopm_cnt = 0` on get
failure). A/B proof in one kernel log: the unpatched module still
underflows, the patched one is silent. Bonus: the patch adds
`pr_debug` probes on both sides (enable via
`echo "file os_dep/linux/usb_intf.c +p" > /sys/kernel/debug/dynamic_debug/control`).

## 2. WARN stack dump on every monitor→AP transition (fixed — patch 0002)

`WARNING: CPU: … rtw_mlmeext_disconnect+0x138/0x1c0` whenever the interface
returns from monitor mode to AP duty.

Root cause: `rtw_mlmeext_disconnect()` handles AP/MESH/STA/ADHOC states and
falls into `rtw_warn_on(1)` for everything else — Realtek added
`WIFI_MONITOR_STATE`/`MLME_IS_MONITOR` (rtw_mlme.h:88) but never added the
branch. Fix: monitor is a documented no-op (no MLME link to disconnect),
keeping the rest of the function identical to the previous warn path.

## 3. Double firmware download at every interface-up (inherited fix, 5.11)

The 5.6.4 base re-uploads the ~32 KiB firmware (126×254-byte control
writes) at probe *and* again at every interface-up — observed directly in
the usbmon captures. 5.11.2.1 downloads once at probe; ifup is a 76-op
path. Visible as a faster/simpler AP bring-up after module bounce.
