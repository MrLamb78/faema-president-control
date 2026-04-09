# Faema President Control — IC Selection

**Circuit:** `faema_president_control`
**Revision:** Rev.4 (SKiDL migration)

All locked refdes from SPEC §5 are preserved. For each block below, 2–3 candidates are considered. Final recommendation column is what the skeleton BOM will carry. JLCPCB tier (Basic / Preferred / Extended / non-LCSC) and in-stock status will be verified live by the part-sourcer in the next pipeline stage — this document captures the architect's intent and the "why".

---

## U1 — MCU module (ESP32-S3 Mini)

| Candidate | Package | Flash/PSRAM | Native USB | LCSC / JLC tier | Notes |
|-----------|---------|-------------|------------|-----------------|-------|
| **Espressif ESP32-S3-MINI-1-N8** (chosen) | SMD module, 27x15 mm | 8 MB flash, no PSRAM | Yes | LCSC C2913201, typically Extended (module) — allowed because it is specifically required by the SPEC | MicroPython-friendly, Wi-Fi+BT, enough GPIOs for 21 pins assigned |
| ESP32-S3-MINI-1-N8R2 | same | 8 MB flash + 2 MB PSRAM | Yes | Extended | More RAM but not needed for firmware scope in SPEC §6 |
| ESP32-S3-WROOM-1-N8 | SMD module, 18x25.5 mm | 8 MB flash | Yes | Basic/Preferred | Bigger footprint; would require KiCad symbol swap. Not chosen because Rev.4 KiCad uses MINI and we are migrating as-is. |

**Final:** `ESP32-S3-MINI-1-N8` (U1). Single-source risk: Espressif only — accepted because the whole design targets this chip.

---

## U2 — Isolated AC/DC 5 V

| Candidate | Package | Vout / Iout | Isolation | LCSC / JLC tier | Notes |
|-----------|---------|-------------|-----------|-----------------|-------|
| **Hi-Link HLK-PM05** (chosen) | Brick, THT | 5 V / 600 mA | 3 kV AC | LCSC C2834907 (non-LCSC assembly — THT module soldered manually per SPEC) | SPEC §3.1 explicitly names it. Known-good for espresso machine mains. |
| MeanWell IRM-03-5 | THT | 5 V / 600 mA | 3 kV | Non-LCSC | More expensive; equivalent spec; no functional gain |
| TRACO TMLM 05105 | THT | 5 V / 1 A | 3 kV | Non-LCSC | Overspec, larger footprint |

**Final:** `HLK-PM05` (U2). THT, soldered by user after JLCPCB PCBA. Non-LCSC is explicitly allowed by SPEC §7.

---

## U3 — 3.3 V LDO

| Candidate | Package | Vout / Iout | Dropout | LCSC / JLC tier | Notes |
|-----------|---------|-------------|---------|-----------------|-------|
| **AMS1117-3.3** (chosen) | SOT-223 | 3.3 V / 1 A | 1.3 V @ 1A | LCSC C6186 **Basic** | Cheap, always in stock, exact part from SPEC §5. Burns ~1 W at 500 mA — thermal pour on SOT-223 GND required. |
| Diodes Inc AP2127K-3.3 | SOT-25 | 3.3 V / 300 mA | 0.25 V | Extended | Lower dropout but current-limited — 300 mA is marginal vs 500 mA budget. Rejected. |
| TI TLV75733P | SOT-23-5 | 3.3 V / 1 A | 0.23 V | Extended | Low-dropout, better efficiency, higher cost, different package than current Rev.4 KiCad. Not chosen because we are migrating as-is. |

**Final:** `AMS1117-3.3` (U3). Decision drivers: SPEC-locked ref-des, JLC **Basic** tier (always in stock), familiar thermal behaviour. Ensure layout has 150 mm^2 GND copper around SOT-223 tab.

---

## U4, U6 — RTD-to-digital converters (MAX31865)

| Candidate | Package | Channels | SPI | LCSC / JLC tier | Notes |
|-----------|---------|----------|-----|-----------------|-------|
| **MAX31865AAP+** (chosen) | SSOP-20 | 1 (per IC) | Mode 1/3, <= 5 MHz | LCSC C38945 — Extended but almost always in stock, ~$5 each | SPEC mandates MAX31865 as direct IC (not breakout). Two instances needed — one per PT100. |
| MAX31865ATP+ | TQFN-20 | 1 | same | LCSC Extended | Smaller footprint but TQFN harder to hand-rework. Rejected. |
| ADS1220 + external ref + matching network | TSSOP-16 | 1 (PGA 24-bit delta-sigma) | yes | Basic | Much cheaper but requires significant external circuitry (bias, filter, linearization in firmware). 4x the board area. Rejected — SPEC locks MAX31865. |

**Final:** `MAX31865AAP+` for both U4 and U6. The part-sourcer must confirm current stock for 2 pcs minimum.

Reference resistor `Rref / Rref2`:
- **430 Ω 0.1 % 25 ppm/°C, 0603** (e.g. Yageo RT0603BRD07430RL, LCSC C218997, Preferred tier).
- Two pcs. Tolerance is critical — 0.1 % is a hard requirement from the MAX31865 datasheet for best accuracy; 1 % would degrade PT100 readout.

---

## U5 — Real-time clock (DS3231)

| Candidate | Package | Accuracy | Backup | LCSC / JLC tier | Notes |
|-----------|---------|----------|--------|-----------------|-------|
| **DS3231SN#** (chosen) | SOIC-16W (300 mil) | ±2 ppm | VBAT pin | LCSC C131027 — Extended, typically in stock | Integrated crystal + TCXO. Matches SPEC §3.5 exactly. |
| DS3231MZ+ | SOIC-8 | ±5 ppm | VBAT | Extended | Smaller/cheaper but ±5 ppm; SPEC §3.5 specifies ±2 ppm. Rejected. |
| PCF8563 | SOIC-8 | External crystal needed | yes | Basic | Cheap but needs 32.768 kHz crystal + 2 caps; worse accuracy; drift over temperature. Rejected. |
| RV-3028-C7 | SON-8 | ±1 ppm | super-cap | Extended | Very low power, very accurate, but not on Rev.4 KiCad. Future option. Not chosen this revision. |

**Final:** `DS3231SN#` (U5). Pull-ups R2/R3 = 4.7 kOhm to +3V3; bypass C8 = 100 nF.

Backup battery `BT1`: CR2032 holder, THT — e.g. **Linx Technologies BAT-HLD-001** or Keystone 1066. The part-sourcer will pick the LCSC-stocked equivalent (likely Keystone 3002 or SMD BAT-HLD-001-SMT if a surface-mount variant is desired). Recommendation: keep THT because the current KiCad Rev.4 uses a THT holder.

---

## Discrete / passive decisions (highlights)

These are not ICs but warrant justification:

### R7 — SSR series 100 Ω
- **Rationale:** SSR-40DA requires 3–32 V DC / 7.5 mA minimum. At 3.3 V, (3.3 – V_LED_internal) / 100 Ω ≈ 21 mA. Comfortable margin, stays under 50 mA abs max, no thermal concerns on 0603 (P < 50 mW).
- **Part:** Any 100 Ω 0603 ±1 %, JLC Basic (e.g. RC0603FR-07100RL, LCSC C22810).

### R9 — SSR pull-down 10 kΩ
- **Rationale:** ESP32-S3 GPIOs are high-Z during boot. Pull-down guarantees 0 V on SSR+ until firmware actively drives HIGH. Prevents boiler from energising on reset/crash.
- **Part:** 10 kΩ 0603 ±1 % JLC Basic (RC0603FR-0710KL, LCSC C25804).

### R10 — LED current limit 470 Ω
- **Rationale:** Green LED Vf ≈ 2.1 V at 3.3 V rail → I = (3.3 − 2.1)/470 = 2.55 mA. Visible without wasting current. 0603 OK.
- **Part:** 470 Ω 0603 JLC Basic (LCSC C23179).

### R11 — Level-probe pull-up 100 kΩ
- **Rationale:** Weak pull-up so that conductivity probe current is ~33 µA max (reduces electrolysis on the boiler wall probe). Firmware pulses reads further to minimise DC bias on probe.
- **Part:** 100 kΩ 0603 JLC Basic (LCSC C25741).

### R2, R3 — I2C pull-ups 4.7 kΩ
- **Rationale:** Standard DS3231 I2C at 100 kHz; 4.7 kΩ is textbook.
- **Part:** 4.7 kΩ 0603 JLC Basic (LCSC C23162).

### R12, R13, R14 — Button pull-ups 10 kΩ
- **Rationale:** Active-LOW buttons with firm external pull-up (don't rely on ESP32 internal pull-up because the buttons run off-board via J8 with ~20 cm cable — noise margin).
- **Part:** 10 kΩ 0603 JLC Basic (same PN as R9).

### R8 + C6 — SSR RC snubber
- R8 = 100 Ω **1 W** — must be either 2512 thick-film or a THT axial wirewound. SPEC §5 allows 2512. Candidate: Vishay CRCW2512100RFKEG (LCSC C153971, Extended, in stock). Thermal dissipation at ~10 A AC across snubber is < 100 mW steady-state, pulses are absorbed.
- C6 = 100 nF **400 V X1/X2** — must be a safety-rated capacitor, no generic X7R. Candidate: Kemet C0603C104K4RAC... is WRONG (too low voltage). Correct: Würth WE-CSSA 890334023031 or Vishay VY2102M49Y5US63L5 (X1/Y2 rated, 300 VAC, 0.1 uF). These are THT/radial disc or box. **Non-LCSC-Basic** but justifiable for safety.

### C1 — 5 V bulk 10 µF 0805
- Multilayer ceramic, 10 V or 16 V, X5R/X7R. JLC Basic (LCSC C15850 — Samsung CL21A106KQQNNNE).

### C2 — 3.3 V bulk 10 µF 0805
- Same as above.

### C3, C4, C7, C8, C9, C10, C11, C12 — 100 nF 0603 ceramic
- X7R, 50 V, JLC Basic (LCSC C14663 — Samsung CL10B104KB8NNNC). Use one SKU for all.

### F1 — T16A fuse
- 5×20 mm glass or ceramic slow-blow. Holder is THT (e.g. Schurter FUP 031.3508 or cheaper Bel Fuse). Non-LCSC, user-soldered.

### RV1 — S14K275 MOV
- TDK/EPCOS B72214S2271K101 or equivalent. Disc/radial THT. Non-LCSC likely. Protects HLK-PM05 input from surges.

### D1 — Status LED
- Green 0603, 2.0–2.2 V Vf. Any JLC Basic (e.g. Lite-On LTST-C190GKT, LCSC C72043). Preferred over blue to reduce eye strain in an espresso-machine environment.

### ENC1 — EC11 encoder
- ALPS EC11E15244G1 or generic equivalent; 15 pulses per rev, switch, 5-pin THT. Non-LCSC (mechanical part).

### J1, J3, J5, J6, J7, J8 — connectors
- J1: 3-way screw terminal (THT, 5.08 mm pitch, e.g. Phoenix MKDS 1.5/3).
- J3, J6: 4-pin 2.54 mm header (PT100 off-board).
- J5: 24-pin 0.5 mm FPC (GC9A01 ribbon). LCSC Preferred (e.g. Amphenol FH12).
- J7: 2-pin 2.54 mm header (level probe).
- J8: 6-pin 2.54 mm header (buttons panel).

---

## Summary of single-source / Extended-tier risks

| Part | Reason for Extended/non-LCSC | Risk level |
|------|------------------------------|------------|
| U1 ESP32-S3-MINI-1 | Espressif-only module | Low (stable product line) |
| U2 HLK-PM05 | THT AC/DC, non-LCSC | Low (user-soldered, easy to substitute brand) |
| U4/U6 MAX31865 | Maxim-only, Extended tier | Medium (has occasionally gone out of stock) |
| U5 DS3231 | Extended tier, Maxim part | Low-medium |
| R8 snubber 100Ω 1W | 2512 or axial wirewound | Low |
| C6 snubber 100 nF 400 V X1/X2 | Safety-rated, typically non-LCSC | Low (user-soldered THT) |
| SSR1 | External, not on BOM for PCBA | N/A |

The part-sourcer is instructed to escalate if U4/U6 (MAX31865) is out of stock — there is no acceptable drop-in substitute without re-architecture.
