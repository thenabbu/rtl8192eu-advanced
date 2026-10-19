# Hardware profile (from driver procfs — see `proc-dumps.txt`)

- Chip: RTL8192EU, USB 2.0 HS, **2 RF paths / 2×2 MIMO 2.4 GHz**,
  20/40 MHz, 802.11 b/g/n, txgi_max 63 (2 pdbm steps)
- MAC: `8c:90:2d:95:2a:8d` (pinned to `wlan0` by a udev rule on the lab)
- EFUSE: valid (`0x29` header), mostly unburned; channel plan `0x22`
- Function set: P2P, MIRACAST, TDLS advertised; macid 128, sec cam 64
- Driver control surface: `/proc/net/rtl8192eu/wlan0/` — register
  read/write (`read_reg`/`write_reg`), `efuse_map`, TX power tables
  (`tx_power_by_rate`, `tx_power_limit`, `target_tx_power`), `rate_ctl`,
  `chan_plan`, `country_code`, RF/BB register dumps, per-station stats…

Register pages observed on the wire at init/steady state: 0x00 (MAC/EFUSE),
0x01, 0x02 (BB), 0x04–0x06, 0x08–0x0F (PHY/RF via MAC windows;
`ODM_AFE_SETTING` 0x0818 dominates steady-state traffic), 0x1F.
