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
