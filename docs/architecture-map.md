# Driver architecture map (Realtek 5.11.2.1 base)

Source-level map of the `8192eu` module: what is where, how a probe flows
to the air, and where every control surface lives. All `file:line` refs
verified against this tree (2026-10-20).

## Tree

```
driver/
├── core/             vendor core (45 .c) — platform-independent
│   ├── rtw_mlme*.c   802.11 state machine (rtw_mlme_ext.c: 16 282 lines)
│   ├── rtw_ap.c      AP mode (5 955)          rtw_sta_mgt.c  station mode
│   ├── rtw_xmit.c / rtw_recv.c                TX/RX data path (6 374 / 4 943)
│   ├── rtw_io.c      register I/O             rtw_odm.c  ODM (PhyDM) glue
│   ├── rtw_rf.c      RF config                rtw_pwrctrl.c  power ctrl
│   ├── rtw_p2p.c rtw_ft.c rtw_mbo.c rtw_wnm.c rtw_tdls.c rtw_roch.c
│   ├── mesh/ rtw_rm*.c                        802.11s
│   ├── monitor/      rtw_radiotap.c — radiotap pack/unpack (monitor mode)
│   ├── crypto/       software CCMP/GCMP       efuse/  wds/
│   └── rtw_mp.c      MP (production test) mode
├── hal/              chip + board abstraction
│   ├── rtl8192e/     RTL8192EU: rtl8192e_hal_init.c, _phycfg.c, _rf6052.c,
│   │                 hal8192e_fw.c (FW download), Hal8192EPwrSeq.c
│   │   └── usb/      usb_halinit.c, usb_ops_linux.c (vendor vendor-request
│   │                 protocol), rtl8192eu_led.c, _recv.c, _xmit.c
│   ├── phydm/        PhyDM dynamic mechanism (~30 files: AFE, TXAGC, LNA,
│   │                 path-div, CCK-PD, …) — the ~2 s poller on the wire
│   └── btc/ led/ efuse/ hal_hci/
├── os_dep/linux/     Linux glue (24 .c)
│   ├── usb_intf.c    USB probe/remove (rtw_drv_init @1237, .probe @299)
│   ├── rtw_proc.c    the entire procfs surface (5 995 lines)
│   ├── ioctl_cfg80211.c / xmit_linux.c / recv_linux.c / mlme_linux.c
│   └── wifi_regd.c, nlrtw.c, os_intfs.c, custom_gpio_linux.c
├── include/          260 .h — autoconf.h (build switches), hal headers
└── platform/         platform glue
```

## Init → data path

```
usbcore probe
 └─ rtw_drv_init                        os_dep/linux/usb_intf.c:1237
     ├─ rtw_hal_data_init               :670
     ├─ rtw_hal_set_hwreg (USB mode)    :661
     ├─ rtw_hal_inirp_init              :764   (URBs: bulk EP5/6 out, EP4 in)
     └─ hal init  hal/rtl8192e/usb/usb_halinit.c
         ├─ MAC/EFUSE page sweep (0x00–0x1F)          [usb-protocol.md]
         ├─ FW download 126 × 254 B   hal8192e_fw.c
         └─ PHY/RF cal + ODM start    rtl8192e_phycfg.c, hal/phydm/

rx:  bulk EP4 IN → core/rtw_recv.c  (rtw_recv_entry → filter → cfg80211)
tx:  cfg80211 → xmit_linux.c → rtw_xmit_entry (core/rtw_xmit.c)
     → dump_xframe → rtw_write_port → bulk EP5/6
     (monitor path: rtw_monitor_xmit_entry — monitor-injection.md)
```

## Control surface — procfs (all of it in `os_dep/linux/rtw_proc.c`)

```
/proc/net/rtl8192eu/
├── global (8 entries)   ver_info, log_level, drv_cfg, chplan_*,
│    country_chplan_map, global_op_class
│                        ← drv_proc_hdls[]  rtw_proc.c:222, registered :328
└── wlan0/ (128 live entries — measured on the production AP, 2026-10-20)
    ├── read_reg / write_reg        rtw_proc.c:4953-4 — raw register path
    ├── tx_power_* / rf_reg_dump    TX power surface  → txpower-control.md
    ├── chan_plan / country_code    channel plan      → hardware-profile.md
    ├── all_sta_info / ap_info      per-station / AP state
    ├── btreg_read / btreg_write    BTC (BT-coex) registers
    └── odm/  mcc/                  PhyDM + MCC subdirs (rtw_proc.c:5669/5837)
```

271 handler macros in source; 138 live entries (8 global + 128 device +
odm/mcc subdirs). The difference is #ifdef'd-out features (MP, HALMAC,
DBG_MEM_ALLOC) plus dynamically created per-station entries.

## This tree's patches (on top of the official base)

| # | patch | what it does |
|---|---|---|
| 0001 | `usb-autopm-hold-guard` | kills the Runtime-PM underflow on rmmod |
| 0002 | `mlme-disconnect-monitor-noop` | kills the WARN dump on monitor → AP |
| 0003 | `enable-wifi-monitor-mode` | monitor mode compiles in |
| 0004 | `wire-tx-power-offset-knob` | `tx_power_offset` actually changes power |
| 0005 | `monitor-injection-fixes` | carrier + radiotap accept → injection works |
| 0006 | `monitor-xmit-debug-probes` | quiet dyndbg breadcrumbs on the TX path |

Each has A/B kernel-log proof in `bugs-found.md`.

## Where each topic is documented

| topic | doc |
|---|---|
| USB wire protocol, register map, init phases | `usb-protocol.md` |
| Windows vendor OID surface (53 OIDs, decoded) | `windows-vendor-oids.md` |
| Windows driver extraction + WDI layer | `windows-driver.md` |
| monitor injection, usbmon trap | `monitor-injection.md` |
| TX power formula + knobs | `txpower-control.md` |
| LED registers + wire proof | `led-control.md` |
| bugs with before/after proof | `bugs-found.md` |
| hardware profile from procfs | `hardware-profile.md` |
| official vs community vs this driver | `feature-matrix.md` |
