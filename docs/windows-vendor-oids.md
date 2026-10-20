# Windows vendor OIDs (0xff81xxxx) — rtwlanu.sys

Vendor OID dispatch in the official TP-Link Windows driver for the TL-WN822N v4
(RTL8192EU). These OIDs have no names in the standard NDIS OID table — see
`windows-oid-table.txt` for the 143 standard OIDs.

## Provenance

- Binary: `rtwlanu.sys` v1030.2 (2,829,312 bytes), extracted from the TP-Link
  Windows installer `TL-WN822N_EU_US_V4_V5_20170726_Wins.zip` (InstallShield cabinet).
- Analysis: Ghidra 12.1.4 on the WSL laptop via REA MCP.
- Run: fan-out `deleg_c96e46f4` (2026-10-20), interrupted before final synthesis.
  This doc distills that run's raw evidence; full transcript at
  `/opt/data/cache/delegation/live/deleg_c96e46f4/task-1.log`.
- Raw evidence: `raw/disasm-FUN_140019850.txt`, `raw/disasm-FUN_140015fc0.txt`,
  `raw/pseudo-FUN_140019850.txt` (plus spill IDs cited per section).
  Handler-2 pseudocode (FUN_140015fc0) captured live via REA MCP on
  2026-10-20 (REA evidence id `ev_3866b99078f9a677`); table-helper
  pseudocode preserved in `raw/pseudo-FUN_1401294e4.txt` /
  `raw/pseudo-FUN_140129ce8.txt`.

## Dispatcher

All vendor OIDs are handled inside one function: **FUN_140019850** (entry
0x140019850, 1069 instructions). Observed conventions from the prologue and
case bodies (inferences marked as such):

| reg | role (observed) |
|---|---|
| `RDI` | adapter context pointer (heavily indexed, e.g. `[RDI+0xc40]`) — inference |
| `RSI` | input buffer from NDIS — inference |
| `R15D` | input buffer length (checked by `CMP R15D, 0xNN`) — inference |
| `R12` | pointer to output-length field (bodies write sizes there) — inference |
| `RBX` | OID value (compared in the switch) — observed |

Each case typically checks the input length, reads the input via `RSI`, writes
an expected output size into `[R12]`, and calls a helper.

## Case table — handler 1 (FUN_140019850), decoded

33 cases total (the fan-out run captured 31; the xref pass recovered
`0xff816802` and `0xff816818`, which sit in the first-stage switch).

| OID | body entry | decoded semantics |
|---|---|---|
| `0xff816802` | `0x14001991e` | **ADC sampler start/stop**: `[main+0x762648]=in[0]`, `[0x65cb71]=0`, call `adc_smp_set(main_ctx, 0, 0)` (FUN_140130190) |
| `0xff816808` | `0x14001a2d9` | store `in[0]` → `[0x4d0f98]` (flag) |
| `0xff816818` | `0x1400199e6` | **ADC sampler config apply**: needs 13 B; stores 10 B `{u16,u16,u32,u8,u8}` → `[sec+0x38..41]` + `[main+0x76d4b0..b9]`; `[per-if(0x1c0)+0x25]=1`; `sampler_cfg_apply` (FUN_14012f2c4); on fail → `sampler_if_tick` (FUN_14012f32c) |
| `0xff81684d` | `0x140019cb7` | **blob setter (2 sizes)**: 36 B → FUN_1400ab0c8, 68 B → FUN_1400a9954 |
| `0xff8168f1` | `0x140019c08` | **toggle**: in=0 → `hal_write_trigger(0x18f)` (+`0x190` if trace bit 0x8); in=1 → `hal_write_trigger(0x191)`; `[0x65ca65]=in`, `[0x65cb70]=in?1:0` |
| `0xff8168f2` | `0x140019bb6` | needs 18 B, `in[0]==0`; `sampler_mode_dispatch(mode=0)` (FUN_14012dbd8); success flag in R13B |
| `0xff8168f3` | `0x14001a975` | **true no-op** → `0x10001` |
| `0xff8168f5` | `0x14001a04f` | **blob setter**: needs 66 B → FUN_1400a9e2c |
| `0xff8168fc` | `0x140019f91` | **toggle**: in==1 → `[0x65c616]=1` + gated `hal_write_trigger(0x198)`; else `[0x65c616]=0` + gated `0x199` |
| `0xff8168fd` | `0x140019f02` | `hal_write_trigger(0x18d)`; needs 68 B → FUN_1400ab01c (blob setter) |
| `0xff8168fe` | `0x140019e4f` | **toggle**: in==1 → `[0x65cb70]=1` + gated `0x19b`; else `[0x65cb70]=0` + gated `0x19c` |
| `0xff819000` | `0x140019dab` | `[sec+0xb8]=in[0]`; if in[0]==1: in[1]≤0x77 required, `[sec+0xbc]=in[1]&7`, `[sec+0xbd]=(in[1]>>4)&7` (mirrored to second sec-ctx if present) |
| `0xff819001` | `0x14001a0a1` | **mode/channel config**: `[sec+0xc0]=in[0]` (0..3); 1..3: in[1]=band 0..6, in[2..3]=u16 channel (band 0 ⇒ nonzero), band→const map `{1:0xeff, 2:0xf37, 3:0x1eff, 4:0x1f37, 5:0x2cbe}`, `[sec+0xc6]=in[4]` (mode 3 ⇒ in[4]≥1); in[0]>3: drain 8-entry list at `RDI+0xfd8` (lock/unlock FUN_140260958/FUN_140261074, unlink + FUN_1400d7854 per entry) |
| `0xff819003` | `0x14001a3b3` | `[sec+0x24]=in[0]` (0..2) |
| `0xff819006` | `0x14001a398` | variadic blob → FUN_1400a66c8; nonzero return → error `0xc0010014` |
| `0xff819007` | `0x14001a2c4` | **collect pending results**: in[0] must be 1; walks list at `RDI+0x668` (≤64 iterations, FUN_1400a40f8 per entry, entries with `[e+0x15]!=0` appended via FUN_1400cf18c); empty list → append default entry `[0x4af1c]`; finalize FUN_1400cf254 |
| `0xff81900c` | `0x14001a22e` | **work-queue control**: in=0 → start queue at `RDI+0x540`; in=1 → start queue at `RDI+0x598` (both via FUN_14002d844); in>1 → `hal_write_trigger(0x17c)` (+`0x17d` if trace bit 0x8) |
| `0xff819011` | `0x14001a522` | **rate/config setter + queue drain**: in[0]==1, 3 B: in[1] 1..0x40 → `[sec+0xfb]=in[1]`, `[sec+0xfc]=in[2]`; else drain per-IF queue at `0x646348` (list at `[RSI+0x108]`, FUN_14002c07c/FUN_1400b67e4/FUN_14003c878 per element), `[sec+0xfa]=0` then `2` |
| `0xff819020` | `0x14001a4ab` | **toggle**: in=0 → `hal_write_trigger(0x181)`, `[0x655feb]=0`; else `0x182`, `[0x655feb]=1` |
| `0xff819023` | `0x14001a48a` | `[main+0x762638]=in[0]` + DbgPrint(fmt `0x140264f00`) |
| `0xff819024` | `0x14001a46f` | `[main+0x762640]=in[0]` + DbgPrint(`0x140264f20`) |
| `0xff819025` | `0x14001a454` | `[main+0x762641]=in[0]` + DbgPrint(`0x140264f40`) |
| `0xff819026` | `0x14001a60e` | `[main+0x762642]=in[0]` (u16, mirrored `[R13+0x115c]`) + DbgPrint(`0x140264f80`) |
| `0xff819036` | `0x14001a78f` | store `in[0]` → `[0x656119]` (flag) |
| `0xff81903d` | `0x14001a6fd` | needs ≥1 B; in==1 → gated `hal_write_trigger(0x187)`; `[0x6562da]=1`; `out[0]=inlen` |
| `0xff81903e` | `0x14001a674` | `[0x6562dc]=in[0]`; `hal_write32(0x189, in[0])` (FUN_14000c990); `out[0]=inlen` |
| `0xff81903f` | `0x14001a66f` | **true no-op** → `0x10001` |
| `0xff819040` | `0x14001a79c` | `[sec+0x100]=in[0]`; `hal_write32(0x180, in[0])` |
| `0xff819044` | `0x14001a8f7` | **toggle**: in==1 → `[0x655f64]=1` + gated `hal_write_trigger(0x185)`; else `[0x655f64]=0` |
| `0xff819045` | `0x14001a87d` | **toggle**: in=0 → `[0x655f65]=1` + `hal_write_trigger(0x183)`; else `0x184` + `[0x655f65]=0`; `[0x655f66]=1` |
| `0xff81904a` | `0x14001a86a` | variadic blob → FUN_1400a7488 |
| `0xff81904b` | `0x14001a84c` | `[main+0x762644]=in[0]` (u16, mirrored `[R13+0x1160]`) |
| `0xff81904c` | `0x14001a82e` | `[main+0x762646]=in[0]` (u16, mirrored `[R13+0x1162]`) |
| `0xff819052` | `0x14001a945` | variadic → FUN_1400d03d8 |
| `0xff819054` | `0x14001a9d8` | `[0x839145]=in[0]`; FUN_1400d021c(pDevice) |
| `0xff819056` | `0x14001a9cb` | variadic → FUN_1400d03b4 |
| `0xff819057` | `0x14001a9b8` | variadic → FUN_1400a7298; fail → error path |
| `0xff819064` | `0x14001a97d` | `[0x65d802]=in[0..1]` (u16); `hal_write32(0x18a, in u16)` |

### JNZ-stub correction (supersedes commit d68400b)

The switch arms use the pattern

```asm
CMP EBX, 0xff81xxxx ; JNZ 0x14001a975
<real body: store / helper call>
```

The `JNZ 0x14001a975` is the **non-match fallback** to the `0x10001` stub —
i.e. "if this is *not* the OID, return the ack and do nothing". The **match
path falls through** into the real body. The earlier reading (six OIDs are
no-op acks) was backwards. Corrected classification:

- **true no-ops** (match path lands directly on the stub): `0xff8168f3`,
  `0xff81903f`.
- **real work via fall-through**: `0xff819000` (2-field config),
  `0xff81900c` (work-queue start / 0x17c-0x17d HAL writes), `0xff819025`
  (store + DbgPrint), `0xff81904c` (u16 store at `main+0x762646`).

The stub itself:

```asm
0x14001a975: MOV R14D, 0x10001
0x14001a97b: JMP 0x14001a9e8
0x14001a9e8: MOV EAX, R14D          ; return value in EAX
0x14001a9eb: MOV RCX, [RBP-8]; XOR RCX, RSP; CALL 0x140059560   ; canary check
```

`0x10001` = standard "success, nothing to return" ack for the ack-only path.

### Context layout notes (handler 1)

- `RDI` = pDevice (adapter context); `[RDI+0xc40]` = main HW/state ctx;
  `[RDI+0x5e01a0]` = secondary (per-IF or second device) ctx;
  `[RDI+0x2000]` = per-interface ctx (index byte at `+0x118`).
- `main+0x762638..0x762648` = **diagnostics config block** (8 sub-fields;
  4 of them DbgPrint-ed on set — the Windows utility's diagnostics page).
- `main+0x76d4xx` = **ADC sampler block** (config at 0x76d488, data cfg at
  0x76d4b0, mode at 0x762648).
- `[0x140292000]` = global debug/trace ctx: `+0x18`/`+0x58` = trace
  sub-contexts, `+0x29` = log level, `+0x2c` = mask, `+0x69`/`+0x6c` =
  second gate. `FUN_1400021ac`/`FUN_14000c990` writes here are **trace
  events** (cmd 0x2b, event ids 0x17c-0x19c), not device register writes —
  the cmd 0x2b id matches the usbmon write-command capture.

## Block bodies

### body @ 0x140019cb7  (OIDs: `0xff81684d`)

```asm
0x140019cb7: CMP R15D, 0x24
0x140019cbb: JNC 0x140019cf7
0x140019cbd: MOV R8D, 0x42
0x140019cc3: MOV dword ptr [R12], R8D
0x140019cc7: MOV RCX, qword ptr [0x140292000]
0x140019cce: CMP RCX, R9
0x140019cd1: JZ 0x140019e02
0x140019cd7: CMP byte ptr [RCX + 0x29], 0x4
0x140019cdb: JC 0x140019e02
0x140019ce1: MOV EAX, dword ptr [RCX + 0x2c]
0x140019ce4: TEST R10B, AL
0x140019ce7: JZ 0x140019e02
0x140019ced: MOV EDX, 0x18c
0x140019cf2: JMP 0x140019b1d
0x140019cf7: MOV R8D, R15D
0x140019cfa: MOV RDX, RSI
0x140019cfd: MOV RCX, RDI
0x140019d00: CALL 0x1400ab0c8    ; CALL -> <indirect>
0x140019d05: JMP 0x14001a9e8
0x140019d0a: MOV R8D, 0x44
0x140019d10: CMP R15D, R8D
0x140019d13: JNC 0x140019d49
0x140019d15: MOV dword ptr [R12], R8D
0x140019d19: MOV RCX, qword ptr [0x140292000]
0x140019d20: CMP RCX, R9
0x140019d23: JZ 0x140019e02
0x140019d29: CMP byte ptr [RCX + 0x29], 0x4
0x140019d2d: JC 0x140019e02
0x140019d33: MOV EAX, dword ptr [RCX + 0x2c]
0x140019d36: TEST R10B, AL
0x140019d39: JZ 0x140019e02
0x140019d3f: MOV EDX, 0x195
0x140019d44: JMP 0x140019b1d
0x140019d49: MOV R8D, R15D
0x140019d4c: MOV RDX, RSI
0x140019d4f: MOV RCX, RDI
0x140019d52: CALL 0x1400a9954    ; CALL -> <indirect>
0x140019d57: JMP 0x14001a9e8
0x140019d5c: MOV EAX, 0xff819001
0x140019d61: CMP EBX, EAX
0x140019d63: JA 0x14001a1fe
0x140019d69: JZ 0x14001a0a1
0x140019d6f: CMP EBX, 0xff8168f5
0x140019d75: JZ 0x14001a04f
0x140019d7b: CMP EBX, 0xff8168fc
0x140019d81: JZ 0x140019f91
0x140019d87: CMP EBX, 0xff8168fd
0x140019d8d: JZ 0x140019f02
0x140019d93: CMP EBX, 0xff8168fe
0x140019d99: JZ 0x140019e4f
0x140019d9f: CMP EBX, 0xff819000
0x140019da5: JNZ 0x14001a975
0x140019dab: MOV RCX, qword ptr [RDI + 0x668]
0x140019db2: MOV RCX, qword ptr [RCX]
0x140019db5: CALL 0x14007f924    ; CALL -> <indirect>
0x140019dba: MOV RDX, qword ptr [RDI + 0x5e01a0]
0x140019dc1: MOV R8, R14
0x140019dc4: TEST RAX, RAX
0x140019dc7: JZ 0x140019dd0
0x140019dc9: MOV R8, qword ptr [RAX + 0x5e01a0]
0x140019dd0: MOVZX EAX, byte ptr [RSI]
0x140019dd3: MOV dword ptr [RDX + 0xb8], EAX
0x140019dd9: TEST R8, R8
0x140019ddc: JZ 0x140019de5
0x140019dde: MOV byte ptr [R8 + 0xbc], AL
0x140019de5: MOV ECX, dword ptr [RDX + 0xb8]
0x140019deb: SUB ECX, 0x1
0x140019dee: JNZ 0x14001a9e8
0x140019df4: CMP R15D, 0x2
0x140019df8: JNC 0x140019e0c
0x140019dfa: MOV dword ptr [R12], 0x2
0x140019e02: MOV EAX, 0xc0010014
0x140019e07: JMP 0x14001a9eb
0x140019e0c: MOV AL, byte ptr [RSI + 0x1]
0x140019e0f: CMP AL, 0x77
0x140019e11: JA 0x140019ad9
0x140019e17: MOV CL, AL
0x140019e19: SHR AL, 0x4
0x140019e1c: AND AL, 0x7
0x140019e1e: AND CL, 0x7
0x140019e21: MOV byte ptr [RDX + 0xbc], CL
0x140019e27: MOV byte ptr [RDX + 0xbd], AL
0x140019e2d: TEST R8, R8
0x140019e30: JZ 0x14001a9e8
0x140019e36: MOV byte ptr [R8 + 0xbc], CL
0x140019e3d: MOV AL, byte ptr [RDX + 0xbd]
0x140019e43: MOV byte ptr [R8 + 0xbd], AL
0x140019e4a: JMP 0x14001a9e8
```

### body @ 0x140019c08  (OIDs: `0xff8168f1`)

```asm
0x140019c08: MOV RCX, qword ptr [0x140292000]
0x140019c0f: CMP RCX, R9
0x140019c12: JZ 0x140019c41
0x140019c14: CMP byte ptr [RCX + 0x29], 0x4
0x140019c18: JC 0x140019c41
0x140019c1a: MOV EAX, dword ptr [RCX + 0x2c]
0x140019c1d: TEST R10B, AL
0x140019c20: JZ 0x140019c41
0x140019c22: MOV RCX, qword ptr [RCX + 0x18]
0x140019c26: MOV EDX, 0x18f
0x140019c2b: MOV R8, R11
0x140019c2e: CALL 0x1400021ac    ; CALL -> <indirect>
0x140019c33: MOV RCX, qword ptr [0x140292000]
0x140019c3a: LEA R9, [0x140292000]
0x140019c41: CMP byte ptr [RSI], R14B
0x140019c44: JNZ 0x140019c80
0x140019c46: CMP RCX, R9
0x140019c49: JZ 0x140019c6d
0x140019c4b: CMP byte ptr [RCX + 0x29], 0x4
0x140019c4f: JC 0x140019c6d
0x140019c51: MOV EAX, dword ptr [RCX + 0x2c]
0x140019c54: TEST AL, 0x8
0x140019c56: JZ 0x140019c6d
0x140019c58: MOV RCX, qword ptr [RCX + 0x18]
0x140019c5c: LEA R8, [0x140278de0]
0x140019c63: MOV EDX, 0x190
0x140019c68: CALL 0x1400021ac    ; CALL -> <indirect>
0x140019c6d: MOV byte ptr [RDI + 0x65ca65], R14B
0x140019c74: MOV byte ptr [RDI + 0x65cb70], R14B
0x140019c7b: JMP 0x14001a9e8
0x140019c80: CMP RCX, R9
0x140019c83: JZ 0x140019ca7
0x140019c85: CMP byte ptr [RCX + 0x29], 0x4
0x140019c89: JC 0x140019ca7
0x140019c8b: MOV EAX, dword ptr [RCX + 0x2c]
0x140019c8e: TEST AL, 0x8
0x140019c90: JZ 0x140019ca7
0x140019c92: MOV RCX, qword ptr [RCX + 0x18]
0x140019c96: LEA R8, [0x140278de0]
0x140019c9d: MOV EDX, 0x191
0x140019ca2: CALL 0x1400021ac    ; CALL -> <indirect>
0x140019ca7: MOV EBX, 0x1
0x140019cac: MOV byte ptr [RDI + 0x65ca65], BL
0x140019cb2: JMP 0x14001a9e8
```

### body @ 0x140019bb6  (OIDs: `0xff8168f2`)

```asm
0x140019bb6: MOV R8D, 0x12
0x140019bbc: CMP R15D, R8D
0x140019bbf: JNC 0x140019bf5
0x140019bc1: MOV dword ptr [R12], R8D
0x140019bc5: MOV RCX, qword ptr [0x140292000]
0x140019bcc: CMP RCX, R9
0x140019bcf: JZ 0x140019e02
0x140019bd5: CMP byte ptr [RCX + 0x29], 0x4
0x140019bd9: JC 0x140019e02
0x140019bdf: MOV EAX, dword ptr [RCX + 0x2c]
0x140019be2: TEST R10B, AL
0x140019be5: JZ 0x140019e02
0x140019beb: MOV EDX, 0x193
0x140019bf0: JMP 0x140019b1d
0x140019bf5: MOV R8D, R15D
0x140019bf8: MOV RDX, RSI
0x140019bfb: MOV RCX, RDI
0x140019bfe: CALL 0x1400a9cf8    ; CALL -> <indirect>
0x140019c03: JMP 0x14001a9e8
```

### body @ 0x14001a975  (OIDs: `0xff8168f3`, `0xff819000`, `0xff81900c`, `0xff819025`, `0xff81903f`, `0xff81904c`)

```asm
0x14001a975: MOV R14D, 0x10001
0x14001a97b: JMP 0x14001a9e8
```

### body @ 0x14001a04f  (OIDs: `0xff8168f5`)

```asm
0x14001a04f: MOV R8D, 0x42
0x14001a055: CMP R15D, R8D
0x14001a058: JNC 0x14001a08e
0x14001a05a: MOV dword ptr [R12], R8D
0x14001a05e: MOV RCX, qword ptr [0x140292000]
0x14001a065: CMP RCX, R9
0x14001a068: JZ 0x140019e02
0x14001a06e: CMP byte ptr [RCX + 0x29], 0x4
0x14001a072: JC 0x140019e02
0x14001a078: MOV EAX, dword ptr [RCX + 0x2c]
0x14001a07b: TEST R10B, AL
0x14001a07e: JZ 0x140019e02
0x14001a084: MOV EDX, 0x196
0x14001a089: JMP 0x140019b1d
0x14001a08e: MOV R8D, R15D
0x14001a091: MOV RDX, RSI
0x14001a094: MOV RCX, RDI
0x14001a097: CALL 0x1400a9e2c    ; CALL -> <indirect>
0x14001a09c: JMP 0x14001a9e8
0x14001a0a1: MOV RDX, qword ptr [RDI + 0x5e01a0]
0x14001a0a8: MOVZX ECX, byte ptr [RSI]
0x14001a0ab: MOV RAX, RDX
0x14001a0ae: MOV dword ptr [RDX + 0xc0], ECX
0x14001a0b4: MOV R9D, dword ptr [RDX + 0xc0]
0x14001a0bb: MOV ECX, R9D
0x14001a0be: TEST R9D, R9D
0x14001a0c1: JZ 0x14001a199
0x14001a0c7: SUB ECX, 0x1
0x14001a0ca: JZ 0x14001a0de
0x14001a0cc: SUB ECX, 0x1
0x14001a0cf: JZ 0x14001a199
0x14001a0d5: SUB ECX, 0x1
0x14001a0d8: JNZ 0x14001a9e8
0x14001a0de: CMP R15D, 0x5
0x14001a0e2: JNC 0x14001a0f1
0x14001a0e4: MOV dword ptr [R12], 0x5
0x14001a0ec: JMP 0x140019e02
0x14001a0f1: MOV CL, byte ptr [RSI + 0x1]
0x14001a0f4: CMP CL, 0x6
0x14001a0f7: JA 0x140019ad9
0x14001a0fd: MOVZX R8D, byte ptr [RSI + 0x2]
0x14001a102: MOVZX EAX, byte ptr [RSI + 0x3]
0x14001a106: SHL R8W, 0x8
0x14001a10b: OR R8W, AX
0x14001a10f: TEST CL, CL
0x14001a111: JNZ 0x14001a11d
0x14001a113: TEST R8W, R8W
0x14001a117: JZ 0x140019ad9
0x14001a11d: MOVZX ECX, CL
0x14001a120: TEST ECX, ECX
0x14001a122: JZ 0x14001a171
0x14001a124: SUB ECX, 0x1
0x14001a127: JZ 0x14001a163
0x14001a129: SUB ECX, 0x1
0x14001a12c: JZ 0x14001a15c
0x14001a12e: SUB ECX, 0x1
0x14001a131: JZ 0x14001a155
0x14001a133: SUB ECX, 0x1
0x14001a136: JZ 0x14001a14e
0x14001a138: CMP ECX, 0x1
0x14001a13b: JZ 0x14001a147
0x14001a13d: MOV word ptr [RDX + 0xc4], R14W
0x14001a145: JMP 0x14001a179
0x14001a147: MOV EAX, 0x2cbe
0x14001a14c: JMP 0x14001a168
0x14001a14e: MOV EAX, 0x1f37
0x14001a153: JMP 0x14001a168
0x14001a155: MOV EAX, 0xf37
0x14001a15a: JMP 0x14001a168
0x14001a15c: MOV EAX, 0x1eff
0x14001a161: JMP 0x14001a168
0x14001a163: MOV EAX, 0xeff
0x14001a168: MOV word ptr [RDX + 0xc4], AX
0x14001a16f: JMP 0x14001a179
0x14001a171: MOV word ptr [RDX + 0xc4], R8W
0x14001a179: MOV AL, byte ptr [RSI + 0x4]
0x14001a17c: CMP R9D, 0x3
0x14001a180: JNZ 0x14001a18e
0x14001a182: LEA EBX, [R9 + -0x2]
0x14001a186: CMP AL, BL
0x14001a188: JC 0x140019ad9
0x14001a18e: MOV byte ptr [RDX + 0xc6], AL
0x14001a194: JMP 0x14001a9e8
0x14001a199: MOV EBX, 0x1
0x14001a19e: MOV RCX, RDI
0x14001a1a1: MOV EDX, EBX
0x14001a1a3: CALL 0x140260958    ; CALL -> <indirect>
0x14001a1a8: LEA R15, [RDI + 0x1068]
0x14001a1af: LEA RSI, [RDI + 0xfd8]
0x14001a1b6: LEA R12D, [RBX + 0x8]
0x14001a1ba: JMP 0x14001a1dd
0x14001a1bc: MOV RDX, qword ptr [RSI]
0x14001a1bf: CMP RDX, RSI
0x14001a1c2: JZ 0x14001a1e2
0x14001a1c4: MOV RCX, qword ptr [RDX]
0x14001a1c7: MOV RAX, qword ptr [RDX + 0x8]
0x14001a1cb: MOV qword ptr [RAX], RCX
0x14001a1ce: MOV qword ptr [RCX + 0x8], RAX
0x14001a1d2: MOV RCX, RDI
0x14001a1d5: DEC dword ptr [R15]
0x14001a1d8: CALL 0x1400d7854    ; CALL -> <indirect>
0x14001a1dd: CMP qword ptr [RSI], R14
0x14001a1e0: JNZ 0x14001a1bc
0x14001a1e2: ADD RSI, 0x10
0x14001a1e6: ADD R15, 0x4
0x14001a1ea: SUB R12, RBX
0x14001a1ed: JNZ 0x14001a1dd
0x14001a1ef: MOV EDX, EBX
0x14001a1f1: MOV RCX, RDI
0x14001a1f4: CALL 0x140261074    ; CALL -> <indirect>
0x14001a1f9: JMP 0x14001a9e8
0x14001a1fe: CMP EBX, 0xff819003
0x14001a204: JZ 0x14001a3b3
0x14001a20a: CMP EBX, 0xff819006
0x14001a210: JZ 0x14001a398
0x14001a216: CMP EBX, 0xff819007
0x14001a21c: JZ 0x14001a2c4
0x14001a222: CMP EBX, 0xff81900c
0x14001a228: JNZ 0x14001a975
0x14001a22e: MOV AL, byte ptr [RSI]
0x14001a230: TEST AL, AL
0x14001a232: JNZ 0x14001a242
0x14001a234: LEA RCX, [RDI + 0x540]
0x14001a23b: CALL 0x14002d844    ; CALL -> <indirect>
0x14001a240: JMP 0x14001a283
0x14001a242: MOV EBX, 0x1
0x14001a247: CMP AL, BL
0x14001a249: JNZ 0x14001a254
0x14001a24b: LEA RCX, [RDI + 0x598]
0x14001a252: JMP 0x14001a23b
0x14001a254: MOV RCX, qword ptr [0x140292000]
0x14001a25b: CMP RCX, R9
0x14001a25e: JZ 0x14001a9e8
0x14001a264: CMP byte ptr [RCX + 0x29], 0x4
0x14001a268: JC 0x14001a291
0x14001a26a: MOV EAX, dword ptr [RCX + 0x2c]
0x14001a26d: TEST R10B, AL
0x14001a270: JZ 0x14001a291
0x14001a272: MOV RCX, qword ptr [RCX + 0x18]
0x14001a276: MOV EDX, 0x17c
0x14001a27b: MOV R8, R11
0x14001a27e: CALL 0x1400021ac    ; CALL -> <indirect>
0x14001a283: MOV RCX, qword ptr [0x140292000]
0x14001a28a: LEA R9, [0x140292000]
0x14001a291: CMP RCX, R9
0x14001a294: JZ 0x14001a9e8
0x14001a29a: CMP byte ptr [RCX + 0x29], 0x4
0x14001a29e: JC 0x14001a9e8
0x14001a2a4: MOV EAX, dword ptr [RCX + 0x2c]
0x14001a2a7: TEST AL, 0x8
0x14001a2a9: JZ 0x14001a9e8
0x14001a2af: MOV EDX, 0x17d
0x14001a2b4: LEA R8, [0x140278de0]
0x14001a2bb: MOV RCX, qword ptr [RCX + 0x18]
0x14001a2bf: JMP 0x140019ef8
```

### body @ 0x140019f91  (OIDs: `0xff8168fc`)

```asm
0x140019f91: CMP R15D, 0x4
0x140019f95: JNC 0x140019fd7
0x140019f97: MOV dword ptr [R12], 0x4
0x140019f9f: MOV RCX, qword ptr [0x140292000]
0x140019fa6: CMP RCX, R9
0x140019fa9: JZ 0x140019e02
0x140019faf: CMP byte ptr [RCX + 0x29], 0x4
0x140019fb3: JC 0x140019e02
0x140019fb9: MOV EAX, dword ptr [RCX + 0x2c]
0x140019fbc: TEST R10B, AL
0x140019fbf: JZ 0x140019e02
0x140019fc5: MOV EDX, 0x197
0x140019fca: MOV dword ptr [RSP + 0x20], 0x4
0x140019fd2: JMP 0x14001a73a
0x140019fd7: MOV EBX, 0x1
0x140019fdc: CMP dword ptr [RSI], EBX
0x140019fde: JNZ 0x14001a017
0x140019fe0: MOV byte ptr [RDI + 0x65c616], BL
0x140019fe6: MOV RCX, qword ptr [0x140292000]
0x140019fed: CMP RCX, R9
0x140019ff0: JZ 0x14001a9e8
0x140019ff6: CMP byte ptr [RCX + 0x69], 0x4
0x140019ffa: JC 0x14001a9e8
0x14001a000: TEST dword ptr [RCX + 0x6c], 0x400
0x14001a007: JZ 0x14001a9e8
0x14001a00d: MOV EDX, 0x198
0x14001a012: JMP 0x140019ef1
0x14001a017: MOV byte ptr [RDI + 0x65c616], R14B
0x14001a01e: MOV RCX, qword ptr [0x140292000]
0x14001a025: CMP RCX, R9
0x14001a028: JZ 0x14001a9e8
0x14001a02e: CMP byte ptr [RCX + 0x69], 0x4
0x14001a032: JC 0x14001a9e8
0x14001a038: TEST dword ptr [RCX + 0x6c], 0x400
0x14001a03f: JZ 0x14001a9e8
0x14001a045: MOV EDX, 0x199
0x14001a04a: JMP 0x140019ef1
```

### body @ 0x140019f02  (OIDs: `0xff8168fd`)

```asm
0x140019f02: MOV RCX, qword ptr [0x140292000]
0x140019f09: CMP RCX, R9
0x140019f0c: JZ 0x140019f34
0x140019f0e: CMP byte ptr [RCX + 0x29], 0x4
0x140019f12: JC 0x140019f34
0x140019f14: MOV EAX, dword ptr [RCX + 0x2c]
0x140019f17: TEST R10B, AL
0x140019f1a: JZ 0x140019f34
0x140019f1c: MOV RCX, qword ptr [RCX + 0x18]
0x140019f20: MOV EDX, 0x18d
0x140019f25: MOV R8, R11
0x140019f28: CALL 0x1400021ac    ; CALL -> <indirect>
0x140019f2d: LEA R9, [0x140292000]
0x140019f34: MOV R8D, 0x44
0x140019f3a: CMP R15D, R8D
0x140019f3d: JNC 0x140019f7e
0x140019f3f: MOV dword ptr [R12], R8D
0x140019f43: MOV RCX, qword ptr [0x140292000]
0x140019f4a: CMP RCX, R9
0x140019f4d: JZ 0x140019e02
0x140019f53: CMP byte ptr [RCX + 0x29], 0x4
0x140019f57: JC 0x140019e02
0x140019f5d: MOV EAX, dword ptr [RCX + 0x2c]
0x140019f60: TEST AL, 0x8
0x140019f62: JZ 0x140019e02
0x140019f68: MOV dword ptr [RSP + 0x20], R8D
0x140019f6d: MOV EDX, 0x18e
0x140019f72: LEA R8, [0x140278de0]
0x140019f79: JMP 0x14001a73d
0x140019f7e: MOV R8D, R15D
0x140019f81: MOV RDX, RSI
0x140019f84: MOV RCX, RDI
0x140019f87: CALL 0x1400ab01c    ; CALL -> <indirect>
0x140019f8c: JMP 0x14001a9e8
```

### body @ 0x140019e4f  (OIDs: `0xff8168fe`)

```asm
0x140019e4f: CMP R15D, 0x4
0x140019e53: JNC 0x140019e81
0x140019e55: MOV dword ptr [R12], 0x4
0x140019e5d: MOV RCX, qword ptr [0x140292000]
0x140019e64: CMP RCX, R9
0x140019e67: JZ 0x140019e02
0x140019e69: CMP byte ptr [RCX + 0x29], 0x4
0x140019e6d: JC 0x140019e02
0x140019e6f: MOV EAX, dword ptr [RCX + 0x2c]
0x140019e72: TEST R10B, AL
0x140019e75: JZ 0x140019e02
0x140019e77: MOV EDX, 0x19a
0x140019e7c: JMP 0x140019fca
0x140019e81: MOV EBX, 0x1
0x140019e86: CMP dword ptr [RSI], EBX
0x140019e88: JNZ 0x140019ebe
0x140019e8a: MOV byte ptr [RDI + 0x65cb70], BL
0x140019e90: MOV RCX, qword ptr [0x140292000]
0x140019e97: CMP RCX, R9
0x140019e9a: JZ 0x14001a9e8
0x140019ea0: CMP byte ptr [RCX + 0x69], 0x4
0x140019ea4: JC 0x14001a9e8
0x140019eaa: TEST dword ptr [RCX + 0x6c], 0x400
0x140019eb1: JZ 0x14001a9e8
0x140019eb7: MOV EDX, 0x19b
0x140019ebc: JMP 0x140019ef1
0x140019ebe: MOV byte ptr [RDI + 0x65cb70], R14B
0x140019ec5: MOV RCX, qword ptr [0x140292000]
0x140019ecc: CMP RCX, R9
0x140019ecf: JZ 0x14001a9e8
0x140019ed5: CMP byte ptr [RCX + 0x69], 0x4
0x140019ed9: JC 0x14001a9e8
0x140019edf: TEST dword ptr [RCX + 0x6c], 0x400
0x140019ee6: JZ 0x14001a9e8
0x140019eec: MOV EDX, 0x19c
0x140019ef1: MOV RCX, qword ptr [RCX + 0x58]
0x140019ef5: MOV R8, R11
0x140019ef8: CALL 0x1400021ac    ; CALL -> <indirect>
0x140019efd: JMP 0x14001a9e8
```

### body @ 0x14001a3b3  (OIDs: `0xff819003`)

```asm
0x14001a3b3: MOV AL, byte ptr [RSI]
0x14001a3b5: CMP AL, 0x2
0x14001a3b7: JA 0x140019ad9
0x14001a3bd: MOVZX ECX, AL
0x14001a3c0: MOV RAX, qword ptr [RDI + 0x5e01a0]
0x14001a3c7: MOV dword ptr [RAX + 0x24], ECX
0x14001a3ca: JMP 0x14001a9e8
0x14001a3cf: MOV qword ptr [RDI + 0x496d8], R14
0x14001a3d6: MOV qword ptr [RDI + 0x496e0], R14
0x14001a3dd: MOV qword ptr [RDI + 0x496e8], R14
0x14001a3e4: MOV qword ptr [RDI + 0x496c0], R14
0x14001a3eb: MOV qword ptr [RDI + 0x496c8], R14
0x14001a3f2: MOV qword ptr [RDI + 0x496d0], R14
0x14001a3f9: JMP 0x14001a9e8
0x14001a3fe: MOV EAX, 0xff819040
0x14001a403: CMP EBX, EAX
0x14001a405: JA 0x14001a7eb
0x14001a40b: JZ 0x14001a79c
0x14001a411: MOV EAX, 0xff819026
0x14001a416: CMP EBX, EAX
0x14001a418: JA 0x14001a643
0x14001a41e: JZ 0x14001a60e
0x14001a424: CMP EBX, 0xff819011
0x14001a42a: JZ 0x14001a522
0x14001a430: CMP EBX, 0xff819020
0x14001a436: JZ 0x14001a4ab
0x14001a438: CMP EBX, 0xff819023
0x14001a43e: JZ 0x14001a48a
0x14001a440: CMP EBX, 0xff819024
0x14001a446: JZ 0x14001a46f
0x14001a448: CMP EBX, 0xff819025
0x14001a44e: JNZ 0x14001a975
0x14001a454: MOVZX ECX, byte ptr [RSI]
0x14001a457: MOV RAX, qword ptr [RDI + 0xc40]
0x14001a45e: MOV EDX, ECX
0x14001a460: MOV byte ptr [RAX + 0x762641], CL
0x14001a466: LEA RCX, [0x140264f40]
0x14001a46d: JMP 0x14001a4a1
```

### body @ 0x14001a398  (OIDs: `0xff819006`)

```asm
0x14001a398: MOV R8D, R15D
0x14001a39b: MOV RDX, RSI
0x14001a39e: MOV RCX, RDI
0x14001a3a1: CALL 0x1400a66c8    ; CALL -> <indirect>
0x14001a3a6: TEST EAX, EAX
0x14001a3a8: JZ 0x14001a9e8
0x14001a3ae: JMP 0x140019ad9
```

### body @ 0x14001a2c4  (OIDs: `0xff819007`)

```asm
0x14001a2c4: MOV R15B, byte ptr [RSI]
0x14001a2c7: MOV RAX, qword ptr [RDI + 0x668]
0x14001a2ce: MOV RSI, qword ptr [RAX]
0x14001a2d1: TEST R15B, 0xfc
0x14001a2d5: JNZ 0x140019ad9
0x14001a2db: CMP R15B, 0x2
0x14001a2df: JZ 0x140019ad9
0x14001a2e5: TEST RSI, RSI
0x14001a2e8: JZ 0x14001a30b
0x14001a2ea: MOV RCX, RSI
0x14001a2ed: CALL 0x1400bebd0    ; CALL -> <indirect>
0x14001a2f2: TEST EAX, EAX
0x14001a2f4: JG 0x14001a306
0x14001a2f6: MOV RCX, RSI
0x14001a2f9: CALL 0x14007f924    ; CALL -> <indirect>
0x14001a2fe: MOV RSI, RAX
0x14001a301: TEST RAX, RAX
0x14001a304: JNZ 0x14001a2ea
0x14001a306: TEST RSI, RSI
0x14001a309: JNZ 0x14001a315
0x14001a30b: MOV RAX, qword ptr [RDI + 0x668]
0x14001a312: MOV RSI, qword ptr [RAX]
0x14001a315: MOV RCX, RSI
0x14001a318: CALL 0x1400bebd0    ; CALL -> <indirect>
0x14001a31d: MOV R8B, R15B
0x14001a320: TEST EAX, EAX
0x14001a322: JLE 0x14001a379
0x14001a324: LEA RDX, [RBP + -0x10]
0x14001a328: MOV dword ptr [RBP + -0x10], 0xffffffff
0x14001a32f: MOV RCX, RSI
0x14001a332: MOV word ptr [RBP + -0xc], 0xffff
0x14001a338: CALL 0x1400cf18c    ; CALL -> <indirect>
0x14001a33d: MOV DIL, R14B
0x14001a340: MOV EBX, 0x1
0x14001a345: MOVZX EDX, DIL
0x14001a349: MOV RCX, RSI
0x14001a34c: CALL 0x1400a40f8    ; CALL -> <indirect>
0x14001a351: TEST RAX, RAX
0x14001a354: JZ 0x14001a374
0x14001a356: CMP byte ptr [RAX + 0x15], R14B
0x14001a35a: JZ 0x14001a36b
0x14001a35c: LEA RDX, [RAX + 0x3]
0x14001a360: MOV R8B, R15B
0x14001a363: MOV RCX, RSI
0x14001a366: CALL 0x1400cf18c    ; CALL -> <indirect>
0x14001a36b: ADD DIL, BL
0x14001a36e: CMP DIL, 0x40
0x14001a372: JC 0x14001a345
0x14001a374: MOV RCX, RSI
0x14001a377: JMP 0x14001a38b
0x14001a379: LEA RDX, [RDI + 0x4af1c]
0x14001a380: MOV RCX, RDI
0x14001a383: CALL 0x1400cf18c    ; CALL -> <indirect>
0x14001a388: MOV RCX, RDI
0x14001a38b: MOV DL, R15B
0x14001a38e: CALL 0x1400cf254    ; CALL -> <indirect>
0x14001a393: JMP 0x14001a9e8
```

### body @ 0x14001a522  (OIDs: `0xff819011`)

```asm
0x14001a522: MOV EBX, 0x1
0x14001a527: CMP byte ptr [RSI], BL
0x14001a529: JNZ 0x14001a581
0x14001a52b: CMP R15D, 0x3
0x14001a52f: JNC 0x14001a53e
0x14001a531: MOV dword ptr [R12], 0x3
0x14001a539: JMP 0x140019e02
0x14001a53e: MOV CL, byte ptr [RSI + 0x1]
0x14001a541: CMP CL, 0x40
0x14001a544: JA 0x140019ad9
0x14001a54a: MOV DL, byte ptr [RSI + 0x2]
0x14001a54d: TEST CL, CL
0x14001a54f: JZ 0x140019ad9
0x14001a555: MOV RAX, qword ptr [RDI + 0x5e01a0]
0x14001a55c: MOV byte ptr [RAX + 0xfa], BL
0x14001a562: MOV RAX, qword ptr [RDI + 0x5e01a0]
0x14001a569: MOV byte ptr [RAX + 0xfb], CL
0x14001a56f: MOV RAX, qword ptr [RDI + 0x5e01a0]
0x14001a576: MOV byte ptr [RAX + 0xfc], DL
0x14001a57c: JMP 0x14001a9e8
0x14001a581: LEA R12, [RDI + 0x646348]
0x14001a588: MOV EDX, 0x2
0x14001a58d: MOV RSI, qword ptr [R12]
0x14001a591: MOV RCX, RDI
0x14001a594: CALL 0x140260958    ; CALL -> <indirect>
0x14001a599: JMP 0x14001a5ee
0x14001a59b: LEA RDX, [RSI + 0x118]
0x14001a5a2: CALL 0x14002c07c    ; CALL -> <indirect>
0x14001a5a7: MOV byte ptr [RSI + 0x102], R14B
0x14001a5ae: LEA R15, [RSI + 0x108]
0x14001a5b5: JMP 0x14001a5e6
0x14001a5b7: MOV RBX, qword ptr [R15]
0x14001a5ba: MOV RCX, qword ptr [RBX]
0x14001a5bd: MOV RAX, qword ptr [RBX + 0x8]
0x14001a5c1: MOV qword ptr [RAX], RCX
0x14001a5c4: MOV qword ptr [RCX + 0x8], RAX
0x14001a5c8: MOV RCX, RDI
0x14001a5cb: DEC dword ptr [RSI + 0x21c]
0x14001a5d1: MOV RDX, qword ptr [RBX + 0x18]
0x14001a5d5: CALL 0x1400b67e4    ; CALL -> <indirect>
0x14001a5da: MOV RDX, qword ptr [RBX + 0x18]
0x14001a5de: MOV RCX, RDI
0x14001a5e1: CALL 0x14003c878    ; CALL -> <indirect>
0x14001a5e6: CMP qword ptr [R15], R15
0x14001a5e9: JNZ 0x14001a5b7
0x14001a5eb: MOV RSI, qword ptr [RSI]
0x14001a5ee: MOV RCX, RDI
0x14001a5f1: CMP RSI, R12
0x14001a5f4: JNZ 0x14001a59b
0x14001a5f6: MOV RAX, qword ptr [RDI + 0x5e01a0]
0x14001a5fd: MOV EDX, 0x2
0x14001a602: MOV byte ptr [RAX + 0xfa], R14B
0x14001a609: JMP 0x14001a1f4
0x14001a60e: MOVZX ECX, byte ptr [RSI]
0x14001a611: MOV RAX, qword ptr [RDI + 0xc40]
0x14001a618: MOV R8D, ECX
0x14001a61b: MOV word ptr [R13 + 0x115c], CX
0x14001a623: MOV word ptr [RAX + 0x762642], CX
0x14001a62a: LEA RCX, [0x140264f80]
0x14001a631: MOVZX EDX, word ptr [R13 + 0x115c]
0x14001a639: CALL 0x140059620    ; CALL -> <indirect>
0x14001a63e: JMP 0x14001a9e8
0x14001a643: CMP EBX, 0xff819036
0x14001a649: JZ 0x14001a78f
0x14001a64f: CMP EBX, 0xff81903d
0x14001a655: JZ 0x14001a6fd
0x14001a65b: CMP EBX, 0xff81903e
0x14001a661: JZ 0x14001a674
0x14001a663: CMP EBX, 0xff81903f
0x14001a669: JNZ 0x14001a975
0x14001a66f: JMP 0x14001a9e8
```

### body @ 0x14001a4ab  (OIDs: `0xff819020`)

```asm
0x14001a4ab: CMP byte ptr [RSI], R14B
0x14001a4ae: JNZ 0x14001a4e7
0x14001a4b0: MOV RCX, qword ptr [0x140292000]
0x14001a4b7: CMP RCX, R9
0x14001a4ba: JZ 0x14001a4db
0x14001a4bc: CMP byte ptr [RCX + 0x29], 0x4
0x14001a4c0: JC 0x14001a4db
0x14001a4c2: MOV EAX, dword ptr [RCX + 0x2c]
0x14001a4c5: TEST R10B, AL
0x14001a4c8: JZ 0x14001a4db
0x14001a4ca: MOV RCX, qword ptr [RCX + 0x18]
0x14001a4ce: MOV EDX, 0x181
0x14001a4d3: MOV R8, R11
0x14001a4d6: CALL 0x1400021ac    ; CALL -> <indirect>
0x14001a4db: MOV byte ptr [RDI + 0x655feb], R14B
0x14001a4e2: JMP 0x14001a9e8
0x14001a4e7: MOV RCX, qword ptr [0x140292000]
0x14001a4ee: CMP RCX, R9
0x14001a4f1: JZ 0x14001a512
0x14001a4f3: CMP byte ptr [RCX + 0x29], 0x4
0x14001a4f7: JC 0x14001a512
0x14001a4f9: MOV EAX, dword ptr [RCX + 0x2c]
0x14001a4fc: TEST R10B, AL
0x14001a4ff: JZ 0x14001a512
0x14001a501: MOV RCX, qword ptr [RCX + 0x18]
0x14001a505: MOV EDX, 0x182
0x14001a50a: MOV R8, R11
0x14001a50d: CALL 0x1400021ac    ; CALL -> <indirect>
0x14001a512: MOV EBX, 0x1
0x14001a517: MOV byte ptr [RDI + 0x655feb], BL
0x14001a51d: JMP 0x14001a9e8
```

### body @ 0x14001a48a  (OIDs: `0xff819023`)

```asm
0x14001a48a: MOV RAX, qword ptr [RDI + 0xc40]
0x14001a491: LEA RCX, [0x140264f00]
0x14001a498: MOVZX EDX, byte ptr [RSI]
0x14001a49b: MOV dword ptr [RAX + 0x762638], EDX
0x14001a4a1: CALL 0x140059620    ; CALL -> <indirect>
0x14001a4a6: JMP 0x14001a9e8
```

### body @ 0x14001a46f  (OIDs: `0xff819024`)

```asm
0x14001a46f: MOVZX ECX, byte ptr [RSI]
0x14001a472: MOV RAX, qword ptr [RDI + 0xc40]
0x14001a479: MOV EDX, ECX
0x14001a47b: MOV byte ptr [RAX + 0x762640], CL
0x14001a481: LEA RCX, [0x140264f20]
0x14001a488: JMP 0x14001a4a1
```

### body @ 0x14001a78f  (OIDs: `0xff819036`)

```asm
0x14001a78f: MOV AL, byte ptr [RSI]
0x14001a791: MOV byte ptr [RDI + 0x656119], AL
0x14001a797: JMP 0x14001a9e8
0x14001a79c: MOV RAX, qword ptr [RDI + 0x5e01a0]
0x14001a7a3: MOV DL, byte ptr [RSI]
0x14001a7a5: MOV byte ptr [RAX + 0x100], DL
0x14001a7ab: MOV RCX, qword ptr [0x140292000]
0x14001a7b2: CMP RCX, R9
0x14001a7b5: JZ 0x14001a9e8
0x14001a7bb: CMP byte ptr [RCX + 0x29], 0x4
0x14001a7bf: JC 0x14001a9e8
0x14001a7c5: MOV EAX, dword ptr [RCX + 0x2c]
0x14001a7c8: TEST R10B, AL
0x14001a7cb: JZ 0x14001a9e8
0x14001a7d1: MOV RCX, qword ptr [RCX + 0x18]
0x14001a7d5: MOV R8, R11
0x14001a7d8: MOVZX R9D, DL
0x14001a7dc: MOV EDX, 0x180
0x14001a7e1: CALL 0x14000c990    ; CALL -> <indirect>
0x14001a7e6: JMP 0x14001a9e8
0x14001a7eb: MOV EAX, 0xff819052
0x14001a7f0: CMP EBX, EAX
0x14001a7f2: JA 0x14001a955
0x14001a7f8: JZ 0x14001a945
0x14001a7fe: CMP EBX, 0xff819044
0x14001a804: JZ 0x14001a8f7
0x14001a80a: CMP EBX, 0xff819045
0x14001a810: JZ 0x14001a87d
0x14001a812: CMP EBX, 0xff81904a
0x14001a818: JZ 0x14001a86a
0x14001a81a: CMP EBX, 0xff81904b
0x14001a820: JZ 0x14001a84c
0x14001a822: CMP EBX, 0xff81904c
0x14001a828: JNZ 0x14001a975
0x14001a82e: MOV RCX, qword ptr [RDI + 0xc40]
0x14001a835: MOVZX EAX, byte ptr [RSI]
0x14001a838: MOV word ptr [R13 + 0x1162], AX
0x14001a840: MOV word ptr [RCX + 0x762646], AX
0x14001a847: JMP 0x14001a9e8
```

### body @ 0x14001a6fd  (OIDs: `0xff81903d`)

```asm
0x14001a6fd: MOV EBX, 0x1
0x14001a702: CMP R15D, EBX
0x14001a705: JNC 0x14001a74e
0x14001a707: MOV dword ptr [R12], EBX
0x14001a70b: MOV RCX, qword ptr [0x140292000]
0x14001a712: CMP RCX, R9
0x14001a715: JZ 0x140019e02
0x14001a71b: CMP byte ptr [RCX + 0x29], 0x4
0x14001a71f: JC 0x140019e02
0x14001a725: MOV EAX, dword ptr [RCX + 0x2c]
0x14001a728: TEST R10B, AL
0x14001a72b: JZ 0x140019e02
0x14001a731: MOV EDX, 0x186
0x14001a736: MOV dword ptr [RSP + 0x20], EBX
0x14001a73a: MOV R8, R11
0x14001a73d: MOV RCX, qword ptr [RCX + 0x18]
0x14001a741: MOV R9D, R15D
0x14001a744: CALL 0x140030db0    ; CALL -> <indirect>
0x14001a749: JMP 0x140019e02
0x14001a74e: CMP byte ptr [RSI], BL
0x14001a750: JNZ 0x14001a787
0x14001a752: MOV RCX, qword ptr [0x140292000]
0x14001a759: CMP RCX, R9
0x14001a75c: JZ 0x14001a781
0x14001a75e: CMP byte ptr [RCX + 0x29], 0x4
0x14001a762: JC 0x14001a781
0x14001a764: MOV EAX, dword ptr [RCX + 0x2c]
0x14001a767: TEST R10B, AL
0x14001a76a: JZ 0x14001a781
0x14001a76c: MOV RCX, qword ptr [RCX + 0x18]
0x14001a770: MOV EDX, 0x187
0x14001a775: MOV R8, R11
0x14001a778: CALL 0x1400021ac    ; CALL -> <indirect>
0x14001a77d: MOV RDX, qword ptr [RBP + -0x10]
0x14001a781: MOV byte ptr [RDI + 0x6562da], BL
0x14001a787: MOV dword ptr [RDX], R15D
0x14001a78a: JMP 0x14001a9e8
```

### body @ 0x14001a674  (OIDs: `0xff81903e`)

```asm
0x14001a674: MOV EBX, 0x1
0x14001a679: CMP R15D, EBX
0x14001a67c: JNC 0x14001a6b2
0x14001a67e: MOV dword ptr [R12], EBX
0x14001a682: MOV RCX, qword ptr [0x140292000]
0x14001a689: CMP RCX, R9
0x14001a68c: JZ 0x140019e02
0x14001a692: CMP byte ptr [RCX + 0x29], 0x4
0x14001a696: JC 0x140019e02
0x14001a69c: MOV EAX, dword ptr [RCX + 0x2c]
0x14001a69f: TEST R10B, AL
0x14001a6a2: JZ 0x140019e02
0x14001a6a8: MOV EDX, 0x188
0x14001a6ad: JMP 0x14001a736
0x14001a6b2: MOVZX EAX, byte ptr [RSI]
0x14001a6b5: CMP AL, BL
0x14001a6b7: MOV EDX, EAX
0x14001a6b9: CMOVC EDX, EBX
0x14001a6bc: MOV byte ptr [RDI + 0x6562dc], DL
0x14001a6c2: MOV RCX, qword ptr [0x140292000]
0x14001a6c9: CMP RCX, R9
0x14001a6cc: JZ 0x14001a6f1
0x14001a6ce: CMP byte ptr [RCX + 0x29], 0x4
0x14001a6d2: JC 0x14001a6f1
0x14001a6d4: MOV EAX, dword ptr [RCX + 0x2c]
0x14001a6d7: TEST R10B, AL
0x14001a6da: JZ 0x14001a6f1
0x14001a6dc: MOV RCX, qword ptr [RCX + 0x18]
0x14001a6e0: MOV R8, R11
0x14001a6e3: MOVZX R9D, DL
0x14001a6e7: MOV EDX, 0x189
0x14001a6ec: CALL 0x14000c990    ; CALL -> <indirect>
0x14001a6f1: MOV RAX, qword ptr [RBP + -0x10]
0x14001a6f5: MOV dword ptr [RAX], R15D
0x14001a6f8: JMP 0x14001a9e8
```

### body @ 0x14001a8f7  (OIDs: `0xff819044`)

```asm
0x14001a8f7: MOV EBX, 0x1
0x14001a8fc: CMP byte ptr [RSI], BL
0x14001a8fe: JNZ 0x14001a939
0x14001a900: MOV byte ptr [RDI + 0x655f64], BL
0x14001a906: MOV RCX, qword ptr [0x140292000]
0x14001a90d: CMP RCX, R9
0x14001a910: JZ 0x14001a9e8
0x14001a916: CMP byte ptr [RCX + 0x29], 0x4
0x14001a91a: JC 0x14001a9e8
0x14001a920: MOV EAX, dword ptr [RCX + 0x2c]
0x14001a923: TEST R10B, AL
0x14001a926: JZ 0x14001a9e8
0x14001a92c: MOV EDX, 0x185
0x14001a931: MOV R8, R11
0x14001a934: JMP 0x14001a2bb
0x14001a939: MOV byte ptr [RDI + 0x655f64], R14B
0x14001a940: JMP 0x14001a9e8
0x14001a945: MOV RDX, RSI
0x14001a948: MOV RCX, RDI
0x14001a94b: CALL 0x1400d03d8    ; CALL -> <indirect>
0x14001a950: JMP 0x14001a9e8
0x14001a955: CMP EBX, 0xff819054
0x14001a95b: JZ 0x14001a9d8
0x14001a95d: CMP EBX, 0xff819056
0x14001a963: JZ 0x14001a9cb
0x14001a965: CMP EBX, 0xff819057
0x14001a96b: JZ 0x14001a9b8
0x14001a96d: CMP EBX, 0xff819064
0x14001a973: JZ 0x14001a97d
```

### body @ 0x14001a87d  (OIDs: `0xff819045`)

```asm
0x14001a87d: MOV EBX, 0x1
0x14001a882: CMP byte ptr [RSI], R14B
0x14001a885: JNZ 0x14001a8ba
0x14001a887: MOV byte ptr [RDI + 0x655f65], BL
0x14001a88d: MOV RCX, qword ptr [0x140292000]
0x14001a894: CMP RCX, R9
0x14001a897: JZ 0x14001a8ec
0x14001a899: CMP byte ptr [RCX + 0x29], 0x4
0x14001a89d: JC 0x14001a8ec
0x14001a89f: MOV EAX, dword ptr [RCX + 0x2c]
0x14001a8a2: TEST R10B, AL
0x14001a8a5: JZ 0x14001a8ec
0x14001a8a7: MOV RCX, qword ptr [RCX + 0x18]
0x14001a8ab: MOV EDX, 0x183
0x14001a8b0: MOV R8, R11
0x14001a8b3: CALL 0x1400021ac    ; CALL -> <indirect>
0x14001a8b8: JMP 0x14001a8ec
0x14001a8ba: MOV RCX, qword ptr [0x140292000]
0x14001a8c1: CMP RCX, R9
0x14001a8c4: JZ 0x14001a8e5
0x14001a8c6: CMP byte ptr [RCX + 0x29], 0x4
0x14001a8ca: JC 0x14001a8e5
0x14001a8cc: MOV EAX, dword ptr [RCX + 0x2c]
0x14001a8cf: TEST R10B, AL
0x14001a8d2: JZ 0x14001a8e5
0x14001a8d4: MOV RCX, qword ptr [RCX + 0x18]
0x14001a8d8: MOV EDX, 0x184
0x14001a8dd: MOV R8, R11
0x14001a8e0: CALL 0x1400021ac    ; CALL -> <indirect>
0x14001a8e5: MOV byte ptr [RDI + 0x655f65], R14B
0x14001a8ec: MOV byte ptr [RDI + 0x655f66], BL
0x14001a8f2: JMP 0x14001a9e8
```

### body @ 0x14001a86a  (OIDs: `0xff81904a`)

```asm
0x14001a86a: MOV R8B, R15B
0x14001a86d: MOV RDX, RSI
0x14001a870: MOV RCX, RDI
0x14001a873: CALL 0x1400a7488    ; CALL -> <indirect>
0x14001a878: JMP 0x14001a9e8
```

### body @ 0x14001a84c  (OIDs: `0xff81904b`)

```asm
0x14001a84c: MOV RCX, qword ptr [RDI + 0xc40]
0x14001a853: MOVZX EAX, byte ptr [RSI]
0x14001a856: MOV word ptr [R13 + 0x1160], AX
0x14001a85e: MOV word ptr [RCX + 0x762644], AX
0x14001a865: JMP 0x14001a9e8
```

### body @ 0x14001a9d8  (OIDs: `0xff819054`)

_Last body in the function; boundary = function end (approx).

```asm
0x14001a9d8: MOV CL, byte ptr [RSI]
0x14001a9da: MOV byte ptr [RDI + 0x839145], CL
0x14001a9e0: MOV RCX, RDI
0x14001a9e3: CALL 0x1400d021c    ; CALL -> <indirect>
0x14001a9e8: MOV EAX, R14D
0x14001a9eb: MOV RCX, qword ptr [RBP + -0x8]
0x14001a9ef: XOR RCX, RSP
0x14001a9f2: CALL 0x140059560    ; CALL -> <indirect>
0x14001a9f7: MOV RBX, qword ptr [RSP + 0x88]
0x14001a9ff: ADD RSP, 0x40
0x14001aa03: POP R15
0x14001aa05: POP R14
0x14001aa07: POP R13
0x14001aa09: POP R12
0x14001aa0b: POP RDI
0x14001aa0c: POP RSI
0x14001aa0d: POP RBP
0x14001aa0e: RET
```

### body @ 0x14001a9cb  (OIDs: `0xff819056`)

```asm
0x14001a9cb: MOV RDX, RSI
0x14001a9ce: MOV RCX, RDI
0x14001a9d1: CALL 0x1400d03b4    ; CALL -> <indirect>
0x14001a9d6: JMP 0x14001a9e8
```

### body @ 0x14001a9b8  (OIDs: `0xff819057`)

```asm
0x14001a9b8: MOV R8D, R15D
0x14001a9bb: MOV RDX, RSI
0x14001a9be: MOV RCX, RDI
0x14001a9c1: CALL 0x1400a7298    ; CALL -> <indirect>
0x14001a9c6: JMP 0x14001a3a6
```

### body @ 0x14001a97d  (OIDs: `0xff819064`)

```asm
0x14001a97d: MOVZX EDX, word ptr [RSI]
0x14001a980: MOV word ptr [RDI + 0x65d802], DX
0x14001a987: MOV RCX, qword ptr [0x140292000]
0x14001a98e: CMP RCX, R9
0x14001a991: JZ 0x14001a9e8
0x14001a993: CMP byte ptr [RCX + 0x29], 0x4
0x14001a997: JC 0x14001a9e8
0x14001a999: MOV EAX, dword ptr [RCX + 0x2c]
0x14001a99c: TEST R10B, AL
0x14001a99f: JZ 0x14001a9e8
0x14001a9a1: MOV RCX, qword ptr [RCX + 0x18]
0x14001a9a5: MOV R8, R11
0x14001a9a8: MOVZX R9D, DX
0x14001a9ac: MOV EDX, 0x18a
0x14001a9b1: CALL 0x14000c990    ; CALL -> <indirect>
0x14001a9b6: JMP 0x14001a9e8
```

## Handler 2 — FUN_140015fc0 (read/query family), decoded

Same call shape `(pDevice, OID, inBuf, inLen, outBuf, outLen)` but the
opposite direction: **reads and queries**, including raw chip register
access. 20 observed cases; default → `0x10001` ack. Each case is wrapped in
paired trace events `FUN_1400021ac(trace_ctx, 0xbc..0xd9)` (debug ring, not
device).

| OID | semantics |
|---|---|
| `0xff0101cb` / `0xff8180a2` | **device-info block** (8 B out): `[0..3]=0x10ec0211` (tag: Realtek USB VID `0x10ec` + `0x0211`), `[4..5]` = class code mapped from hw-rev byte `[p1+0xc50]` (`0x0f→0x8188`, `0x18→0x8812`, `0x19/0x1b→0x8821`, `0x11..0x13→0x8192e`, else 0), then two descriptor queries via `*DAT_140443a40` (sizes 0x648/0x650); last byte = `read_chip_reg32(res>>1)` (byte/word by bit 0) or `0x20000000\|(res2&0xffff)` |
| `0xff010408` | generic vendor query → FUN_1402640b4 |
| `0xff0111c2` | generic vendor query → FUN_140263fc8 |
| `0xff0111c9` | **raw register read**: in = `{u32 reg = *p3 & 0xfffff (20-bit), u32 shift = p3[1]>>4}`; out[0] = `read_chip_reg32(reg) >> shift` (byte/word width by bit 0) |
| `0xff8168fa` | 4 B out: u32 at `[p1+0x5fb900]` (status) |
| `0xff8168fb` | 4 B out: bool from FUN_1400bf7b4(p1) (status) |
| `0xff81801a` | **operation mode** (4 B out): hw-mode byte `[p1+0xc52]` mapped `0x04→3, 0x06→1, 0x08→2, else 0` |
| `0xff81801c` | 6 B out: hw-info bytes `[p1+0xc59..0xc5e]` |
| `0xff818022` | **register read (explicit)**: in = `{u32 reg, u32 width}`; reg = `*p3>>1`, width `p3[1]` 1 (byte) or 2 (u16), LSB/MSB by `*p3 & 1`; via FUN_14012ce80 |
| `0xff818040` | survey subsystem → FUN_140135db4 |
| `0xff818041` | survey subsystem → FUN_140135c70 |
| `0xff818042` | survey subsystem → FUN_140135ca0 (global ctx re-root) |
| `0xff818045` | **table read + validity bitmap**: in = `{u32 idx, u32 mode∈{1,2,4}}`; `table_read_bitmap(main_ctx, mode, idx, &out32)` (FUN_1401294e4): reads 1/2/4-byte entry at `[main+0x2ce+idx]`, then ORs validity bits `FUN_14012b44c(idx+i)<<8i` for i<mode |
| `0xff818047` | vtable call `[p1+0x9e8](p1, 0x14, &res8)` |
| `0xff818049` | vtable call `[p1+0x9e8](p1, 0x16, &res8)` |
| `0xff818051` | **bounded table read**: in = `{u32 idx, u32 mode∈{1,2,4}}`; byte at `[main+0x20e5+idx]`, bounds = u16 `[main+0x38f4]` (OOB → 0xff); mode 2/4 → FUN_14012c3e4 / FUN_14012c424 (FUN_140129ce8) |
| `0xff818053` | trace-only (event 0xd4), returns success, no data |
| `0xff818083` | 4 B out: byte `[p1+0x5e2328]` (status) |
| `0xff8180a1` | getter → FUN_140121c04(p1, p5, ...) → out[0] |
| `0xff818780` | **station/IF info dump** (220 B out): `[0]=([p1+0x7b0]==0?1:0)` valid flag, `[4..15]` = u32s from `[0x7c0..0x7cc]`, `[16..219]` = 219 B blob from per-IF ctx `+0x2000` (memcpy FUN_14002d210) |
| `0xff818782` | **set+readback 7-bit control**: in = `{u32 val&0x7f, u32 dir}`; `write_chip_reg32(0x1bf, (dir!=1)<<24 \| val)` (FUN_14003e614); out[2] = `read_chip_reg8(0x1bf)` (FUN_14003db90); 12 B out |

### Named helpers (decompiled 2026-10-20 pass)

| function | inferred name | role |
|---|---|---|
| `FUN_1400021ac` | `hal_write_trigger` | 1-byte command write (cmd 0x2b) to a sub-context (device or trace ctx); no payload |
| `FUN_14000c990` | `hal_write32` | 4-byte payload write, cmd 0x2b (ctx, subidx, value) |
| `FUN_14012ce80` | `read_chip_reg32` | 20-bit-index chip register read → u32 |
| `FUN_14003e614` | `write_chip_reg32` | chip register write (idx, value, flags) |
| `FUN_14003db90` | `read_chip_reg8` | single-byte chip register read |
| `FUN_14012b44c` | `entry_valid` | bool validity query, table at `main+0x2ce` |
| `FUN_1401294e4` | `table_read_bitmap` | size 1/2/4 entry read at `main+0x2ce+idx` OR'd with validity bits |
| `FUN_140129ce8` | `table_read_bounded` | byte read at `main+0x20e5+idx`, bounded by u16 `[main+0x38f4]`; u16/u32 siblings FUN_14012c3e4/FUN_14012c424 |
| `FUN_140130190` | `adc_smp_set` | ADC sampler config: state/trig-sig/trig-sig-sel/dma-data-sig at `main+0x76d488`; on start → `adc_smp_start` |
| `FUN_1401303b4` | `adc_smp_stop` | sampler state → 0 |
| `FUN_14012ff20` | `adc_smp_start` | stop old sampler, then WDF DMA queue start (FUN_14002d844) |
| `FUN_14012f2c4` | `sampler_cfg_apply` | store 10-byte config block at `main+0x8c90`, apply via FUN_14012f754 |
| `FUN_14012f32c` | `sampler_if_tick` | per-IF state machine (per-IF ctx `+0x118` index; saturating 50-attempt counter at `+0x11a` with reset via FUN_14012e210; states 2/3/4) |
| `FUN_14012dbd8` | `sampler_mode_dispatch` | mode 0..3 → FUN_14012ddf8 / FUN_14012f704+FUN_14012e9c4 / FUN_14012f0cc; state at `main+0x764440` |
| `FUN_14012f754` | `work_apply` | generic apply/notify dispatch (xrefs from both sampler helpers + 4 other subsystems) |
| `FUN_14002d844` | `wdf_queue_start` | work-queue / DMA transfer start (xrefs from 0xff81900c + sampler start) |

The two OIDs that drive the **ADC hardware sampler** end-to-end:
`0xff816818` (13-byte config + apply) and `0xff816802` (start/stop).
The 10-byte config block `{u16, u16, u32, u8, u8}` is mirrored into both the
secondary ctx and `main+0x76d4b0` — consistent with a
`{rate, window, mask, sig, flags}` style sampling configuration.

## Unresolved questions (record_unknown from the run)

1. **Who issues the private OIDs?** What external user-mode component (TP-Link
   utility? WDI/IHV service?) issues `OID_WDI_IHV_REQUEST` and the 0xff8168xx
   private OIDs, and what input/output schema does it use at the NDIS boundary?
2. **Linux parity gap.** Does the Linux RTL8192EU driver expose equivalents for
   every Windows-only 0xff8168xx vendor-control and WDI-IHV state path, in
   particular the private blob/config setters and the 0xff8190xx AMPDU controls?

## Handler dispatch chain (registration cross-check, 2026-10-20)

Xref pass (live REA, ev ids `ev_91536ed0…`, `ev_86490902…`): each vendor
handler has **exactly two** references — one call site and one
pointer-table entry. There is no third handler and no NdisM OID-range
registration; routing is a **fall-through chain**:

- **Write/command router `FUN_1400185e0`** (0x1400185e0–0x14001984d):
  `FUN_14003b7d4` → `FUN_1400365e0` → `FUN_140021134` → `FUN_14001fc48` →
  **`FUN_140019850`** (vendor, 33 cases) → `FUN_14001e464` →
  `FUN_14001aa10` → inline tail (explicit `0xe010189`/`0xe01018a+`
  media-info cases). Each link returns `0x10001`
  (`NDIS_STATUS_NOT_SUPPORTED`) to hand the OID to the next link.
- **Read/query router `FUN_14000fdfc`** (0x14000fdfc–0x140012027): single
  call site for **`FUN_140015fc0`** (vendor, 20 cases) at 0x14000fea4,
  preceded by trace event `0xda`.

So vendor OIDs reach the two decoded handlers only after every earlier
standard NDIS/802.11 chain link passes (those links are the 143-value
mapping in `windows-driver.md`). The 53 decoded OIDs (33 + 20) are the
**complete vendor set** — a single call site per handler proves nothing
else dispatches into them.

## Blob setters and survey helpers (decoded 2026-10-20)

Six utility-blob setters (36/66/68-byte and larger config blobs). All
store into driver-internal context — none writes raw chip registers,
except the HW-apply sub-case noted. Raw decompilation: `docs/raw/`.

| Fun | blob | role |
|---|---|---|
| `FUN_1400a9954` | 36B | LE u16 pair → ctx `+0x65ca6a/6c`; clears 0x40B payload buf `+0x65caec`; copies `in[4..4+u16]` into it. 2-param + payload store. Trace 0xb1/0xb2 |
| `FUN_1400a9e2c` | 66B | Same shape, single u16 → `+0x65ca6e`, payload buf `+0x65cb2c`, copy `in[2..]`. Trace 0xb3 |
| `FUN_1400a66c8` | 68B | **Per-PHY feature mask**: 6-bit mask from `in[0]` (bits 0-2 → each PHY ctx `+0x25`, bits 4-6 → `+0x2a`); two getter calls (vtable idx 0x26/0x27) gate bits 0x02/0x04; mask also stored at `*(ctx+0x658)+0x1250`; walks every PHY context via `FUN_14007f924` next-link |
| `FUN_1400a7488` | TLV | **Master HW-config TLV** — `in[0]` = subcommand: `01/03` antenna bits (+0x104/05), `06` 2-bit pair (+0x108/09), `07` var (a7298), `08` **bandwidth 20/40/80MHz** (DbgPrint, +0x20), `0c/0d` (+0xb5/b6), `11/8d` var (a5ae4), `13` u32+enable (+0xa8/ac), `14` (+0xb7/b8, 0→3), `15` u16 (+0xb9/ba), `17/18` global flag bits 0/1 (+0x65d833), `81` lookup (b4888/b5748), `87` (+0xed1), `88` u32+enable → **HW apply** (1023e4+7ba50), `89` mode table entry 0x3001 (+0x655fd8), `8b/8c` (+0x106/07). Length mismatch → trace 0x99 |
| `FUN_1400ab01c` | — | Copies u32 `in+0x40` → `+0x65cbf4`; reinit struct `+0x65cbb1` (2d210); apply (cd9d4) |
| `FUN_1400ab0c8` | — | **Record composer**: 0x20+ byte descriptor at `+0x65c65f` — 6B sig `0x3aaaa`, ID bytes from `+0x4af1c..21` and `+0xc59..5e`, 6B user data `in[0..5]`, variable payload `in+0xe` (len `inlen-0xe`), optional 0x18B extended region + `0x4000` flag; total len → `+0x65ca60` |

Survey helpers `FUN_140135c70` / `FUN_140135db4` / `FUN_140135ca0`
(OIDs `0xff818040/41/42`): decoded live — utility plumbing for the
survey/statistics export path. No Linux port needed: the nl80211 survey
API already provides the equivalent on the Linux side.

## Linux procfs parity (conclusion, 2026-10-20)

Every Windows vendor surface maps to something the Linux driver already
has — **no new driver code is required**:

| Windows surface | Linux equivalent | status |
|---|---|---|
| `0xff0111c9` / `0xff818022` raw register read | `/proc/net/rtl8192eu/wlan0/read_reg` (handler in `core/rtw_debug.c`) | **verified live on lab**: `rtw_read8(0x1c)=0x0`, `rtw_read16(0x10)=0xeb03` |
| `0xff818782` set + readback (reg 0x1bf) | `write_reg` + `read_reg` pair | exists |
| `0xff818780` 220-byte station/IF dump | existing sta/phy debug proc entries (128 live entries) | exists |
| `a7488` sub `08` bandwidth 20/40/80 | cfg80211 `chandef` (native mac80211 path) | native |
| `a66c8` per-PHY feature mask | phydm-internal, hw-init owned | native |
| `0xff816802` ADC sampler start/stop, `0xff816818` 13-byte sampler config | **no port** — Windows-only Realtek diagnostic channel; exposing it as a procfs knob would mean shipping unverified hardware behavior on the production AP. Add only after hardware verification on a spare dongle | intentionally skipped |

## Next pass

Done in this pass (2026-10-20, live REA session):
- Decoded all 33 handler-1 bodies (semantics column in the case table).
- Decoded all 20 handler-2 cases (read/query family, incl. raw register
  reads `0xff0111c9` / `0xff818022`).
- Placed and named 16 helpers (xref pass: all five previously unplaced
  helpers now have call sites; ADCSmp set/stop/apply/tick/dispatch chain
  complete).
- Corrected the JNZ-stub interpretation (d68400b was backwards).
- **Dispatch-chain cross-check**: single call site + pointer-table entry
  per vendor handler; 0x10001 fall-through chain; 53 OIDs = complete
  vendor set (new section above).
- **Decoded all 6 blob setters** + 3 survey helpers (new section above).
- **Linux parity concluded**: register surface already exists and is
  verified live; ADC sampler intentionally not ported (Windows-only
  diagnostic).
- `OID_WDI_IHV_REQUEST` issuer: closed deliberately — the issuer is a
  Windows user-mode component and cannot be resolved from the driver
  binary; the OID functions as an IHV pass-through channel and nothing
  on the Linux side requires it.

Remaining: nothing on the RE/docs track. The Windows decode is complete
end-to-end.

