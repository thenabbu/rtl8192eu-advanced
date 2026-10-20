# Windows driver extraction (rtwlanu.sys)

TP-Link's Windows package (`TL-WN822N_EU_US_V4_V5_20170726_Wins.zip`,
sha256 in MANIFEST.md) is an NSIS installer wrapping an **InstallShield
2014** setup whose payload is itself a merged single-file container.

Extraction path (no Windows needed):

1. `7zz x Setup.exe` → NSIS layer (`$PLUGINSDIR/Driver Files/Setup.exe`, plugins)
2. The InstallShield "Driver Files/Setup.exe" embeds a `Disk1/` set as
   `name\0path\0version\0size\0 + data` records starting right after the PE
   stub — walk the records to carve `data1.cab` (962 076 B), `data1.hdr`
   (21 946 B), `data2.cab` (14 227 901 B), `ISSetup.dll`, `setup.exe/inx/ini`
3. `unshield x data1.hdr` on the carved set → per-OS driver dirs

Yields `Driver_RTL_8192EU_TL-WN822N_V4_{XP,Win7,Win8,Win8.1,Win10}_{32,64}/`
each with `rtwlanu.sys` (~3.8 MB), `netrtwlanu*.inf/.cat`, `rtlCoInst.dll`.
`rtwlanu.sys` (Win10 x64) self-reports **v1030.2.0731.2015**, PDB path
`rtwlanu.pdb`. Next: Ghidra/REA pass to map its ioctl surface vs the Linux
driver's procfs knobs.

## Ghidra/REA analysis (2026-10-19, first pass)

Target: `rtwlanu.sys` Win10 x64 (sha256 de091b0b…), PE x86_64, image base
`0x140000000`, 6 925 procedures, 3 113 strings, 10 segments — including a
`tdb` segment (the WDI task database). PDB `rtwlanu.pdb` referenced but not
shipped (no symbols; functions recovered as `FUN_*`).

### The OID surface, fully mapped

The driver contains a complete OID→name pretty-printer
(`FUN_140034560`); its entire switch was extracted to
`windows-oid-table.txt` — **143 unique OID value→name pairs**:
standard NDIS GEN (0x101xx), 802.11 (0xd0101xx / shown 0xe0101xx),
power-management (0xfd0101xx), and the Realtek vendor block:

| Value | OID |
|---|---|
| 0xff0101cb | OID_RT_DEVICE_ID_INFO |
| 0xff010401 | OID_RT_MOTOR_BT_802_11_PAL |
| 0xff818780 | OID_RT_PRO8187_WI_POLL |

The vendor SET/QUERY dispatcher (`FUN_140019850`, reached via the
`OID_RT_AMPDU_BURST_MODE: %d` debug strings) decodes a private command
block around `0xff8190xx`:

| Value | Command |
|---|---|
| 0xff819023 | OID_RT_AMPDU_BURST_MODE |
| 0xff819024 | OID_RT_AMPDU_BURST_NUM |
| 0xff819025 | OID_RT_AUTO_AMPDU_BURST_ENABLE |
| 0xff819026 | OID_RT_AUTO_AMPDU_BURST_THRESHOLD |

plus an unmapped `0xff8168xx` vendor block (0x…84d, 0x…8f1/2/4/5/c/d/e)
reserved for deeper decoding. Registry-backed parameters live under
`HKLM\SYSTEM\...\Services\RtlWlans\Parameters`.

### WDI layer

The driver is a Microsoft **WDI** miniport: the standard task set
(OID_WDI_TASK_OPEN/CLOSE/SCAN/CONNECT/START_AP/STOP_AP/ROAM/…) is
registered via the `tdb` segment, and vendor passthrough happens
through `OID_WDI_IHV_REQUEST` (consumed by Realtek's user-mode
`RtlIhvOid.dll`, shipped in the TP-Link installer).

### Comparison verdict

The Windows "full control" surface reduces to: standard WDI tasks +
a small vendor OID block (AMPDU burst tuning, BT-PAL, device info) +
registry parameters. **The Linux driver's procfs surface (588 handlers:
register R/W, EFUSE, TX power tables, rate control, channel plans,
per-station stats) is materially richer than anything the Windows driver
exposes.** There is no Windows-only control we are missing for the
functions this adapter performs; remaining unknowns are the
`0xff8168xx` block and deeper WDI TLV internals.

## Follow-up (2026-10-20): vendor 0xff81xxxx dispatch

The 143-name table above covers the OIDs the driver pretty-prints; the **vendor
switch** in `FUN_140019850` (31 cases: 9× 0xff8168xx + 22× 0xff8190xx) has no
names — it is now mapped in `windows-vendor-oids.md` (case table, per-body
disassembly, open questions), with full raw disassembly/pseudocode in `docs/raw/`.
