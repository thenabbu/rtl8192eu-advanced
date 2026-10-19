# TX power control surface (RTL8192EU)

Everything the driver exposes for TX power, and what actually does what.
All entries under `/proc/net/rtl8192eu/wlan0/`.

## The formula (from `phy_get_txpwr_target` / dumpers in hal_com_phycfg.c)

```
idx = base + min((by_rate + btc + extra), limit, ulimit) + tpc + tpt + dpd
```

- units: TX gain index, **2 idx = 1 dBm** (`hal_spec->txgi_pdbm = 2`)
- `by_rate` comes from the `tx_power_by_rate` table (CCK 16 / OFDM 14 /
  HT-1SS 13 / HT-2SS 12 dBm on this dongle)
- `limit` = regulatory table — **disabled/unloaded on this build** (shows 63 = uncapped)
- `btc` = BT-coex reduction (no BT present → 0)

## Knobs

| proc entry | write format | effect |
|---|---|---|
| `tx_power_offset` | decimal `0..5` (values >5 reset to 0) | **+N dBm on every rate** — dead code upstream (set+printed, never consumed); **our patch 0004 wires it into `extra`** |
| `tx_power_ext_info` | `default` (or any other string) | reload power tables (from phy files when `CONFIG_LOAD_PHY_PARA_FROM_FILE`), reapplies levels |
| `tx_power_idx` | `ch bw offset` (decimal) | re-dump the formula for another channel/bw (read-only) |
| `tx_power_by_rate`, `target_tx_power`, `tx_power_limit`, `hal_txpwr_info`, `rf_reg_dump`, `kfree_thermal` | — | read-only views |

## Live verification of patch 0004 (2026-10-19)

| offset | CCK_1M idx | dBm | extra term |
|---|---|---|---|
| 0 (baseline) | 37 (0x25) | 16 | 0 |
| 1 | 39 (0x27) | 17 | 2 |
| 4 | 45 (0x2d) | 20 | 8 |
| 0 (restored) | 37 (0x25) | 16 | 0 |

Exact baseline restore, services stayed active, no kernel warnings.

## Safety rails

- The offset knob clamps at 0..5 dBm at parse time.
- `min(..., limit, ulimit)` still bounds the result — enabling a real
  regulatory limit table later re-caps this knob automatically.
- 5 dBm over a 16 dBm table stays well inside the 2.4 GHz ISM band
  allowance and inside the PA's linear range.
