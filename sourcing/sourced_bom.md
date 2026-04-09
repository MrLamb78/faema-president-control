# Faema President Control — Sourced BOM

**Circuit:** `faema_president_control`
**Revision:** Rev.4
**Sourcing date:** 2026-04-09
**Manufacturer target:** JLCPCB PCBA (SMD assembly) — THT and module parts hand-soldered by user
**Sourcing tool:** pcbparts MCP (live JLCPCB/LCSC data) — verified 2026-04-09. Critical LCSC#s confirmed via live query.

> ✅ Key LCSC numbers verified via pcbparts MCP live query. C6 (X2 safety cap) and R8 (snubber resistor) removed — snubber unnecessary given HLK-PM05 internal filter + SSR-40DA zero-crossing type.

---

## Tier Legend

| Tier | Meaning |
|------|---------|
| Basic | Free placement; always in stock; lowest surcharge |
| Preferred | Small surcharge; usually in stock |
| Extended | Manual placement fee ~$3/line; may require lead time |
| Non-LCSC | Hand-soldered by user; not in JLCPCB PCBA scope |

---

## 1. Integrated Circuits and Modules

| Refdes | Function | MPN | LCSC# | Package | Qty | JLCPCB Tier | Est. Stock | Est. Unit Price (USD) | KiCad Footprint | Notes |
|--------|----------|-----|-------|---------|-----|-------------|------------|----------------------|-----------------|-------|
| U1 | MCU module | ESP32-S3-MINI-1-N8 | C2913206 | SMD module 27×15 mm | 1 | Extended | 11.481 | $4,65 | ⚠️ CUSTOM FP NEEDED — see note U1 | Verificado via MCP live. Footprint custom necessário: importar `Espressif_ESP32-S3-MINI-1_27x15mm` da lib oficial Espressif. Single-source: Espressif. |
| U2 | AC/DC 5 V isolated | HLK-PM05 | C2834907 | THT brick | 1 | Non-LCSC | — | ~$3.50 | ⚠️ CUSTOM FP NEEDED — see note U2 | Hand-soldered by user. THT module not in JLCPCB PCBA scope. No standard KiCad footprint exists; user must import Hi-Link footprint from community or manufacturer. |
| U3 | LDO 3.3 V | AMS1117-3.3 | C6186 | SOT-223 | 1 | Basic | >50 000 | ~$0.05 | `Package_TO_SOT_SMD:SOT-223-3_TabPin2` | Basic tier, always in stock. Thermal pour on GND tab required. |
| U4 | RTD-to-digital (boiler) | MAX31865AAP+T | C779509 | SSOP-20-208mil | 1 | Extended | 3.035 | $4,44 | `Package_SO:SSOP-20_5.3x7.2mm_P0.65mm` | Verificado via MCP. Tape & reel (T = ideal para PCBA). Single-source Maxim/ADI. 50 Hz filter. |
| U5 | RTC | DS3231SN# | C131027 | SOIC-16W | 1 | Extended | ~1000–3000 | ~$3.00 | `Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm` | Integrated TCXO ±2 ppm. Extended tier. Verificar estoque antes de pedir. |
| U6 | RTD-to-digital (group) | MAX31865AAP+T | C779509 | SSOP-20-208mil | 1 | Extended | (same as U4) | $4,44 | `Package_SO:SSOP-20_5.3x7.2mm_P0.65mm` | Mesmo PN que U4 — pedir 2 pcs de C779509. Pedir 3-4 como buffer (históricamente some do estoque). |

**Note U1 — ESP32-S3-MINI-1 custom footprint:** The standard KiCad footprint library (tested on KiCad 8.x at `/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/RF_Module.pretty/`) contains ESP32-S3-WROOM-1 but NOT ESP32-S3-MINI-1. The MINI-1 has a different pad layout (27×15 mm vs 18×25.5 mm, castellated holes on all four sides). Use the official Espressif KiCad library: https://github.com/espressif/kicad-libraries — footprint name `Espressif_ESP32-S3-MINI-1_27x15mm`.

**Note U2 — HLK-PM05 custom footprint:** Hi-Link publishes a KiCad footprint package at their website. Community version: `HLK-PM05` in the `Hi-Link` community library. Mechanical drawing: 33.5×20.5×15 mm, 4-pin THT (VIN/GND/VO+/VO-), 15.24 mm row pitch.

---

## 2. Resistors

| Refdes | Value | Tol / TCR | Package | Qty | MPN | LCSC# | JLCPCB Tier | Est. Stock | Est. Unit Price (USD) | KiCad Footprint | Notes |
|--------|-------|-----------|---------|-----|-----|-------|-------------|------------|----------------------|-----------------|-------|
| Rref | 430 Ω | 0.1 % / 25 ppm | 0603 | 1 | TD03G4300BT | C666878 | Extended | 8.666 | $0,027 | `Resistor_SMD:R_0603_1608Metric` | Verificado via MCP (live). Fenghua thin film 25ppm. 0.1% é hard requirement para MAX31865 — NÃO substituir por 1%. |
| Rref2 | 430 Ω | 0.1 % / 25 ppm | 0603 | 1 | TD03G4300BT | C666878 | Extended | (same) | $0,027 | `Resistor_SMD:R_0603_1608Metric` | Mesmo PN que Rref — pedir 2 pcs de C666878. |
| R2 | 4.7 kΩ | 1 % | 0603 | 1 | RC0603FR-074K7L | C23162 | Basic | >100 000 | ~$0.01 | `Resistor_SMD:R_0603_1608Metric` | I2C SDA pull-up |
| R3 | 4.7 kΩ | 1 % | 0603 | 1 | RC0603FR-074K7L | C23162 | Basic | >100 000 | ~$0.01 | `Resistor_SMD:R_0603_1608Metric` | I2C SCL pull-up — same PN as R2 |
| R7 | 100 Ω | 1 % | 0603 | 1 | RC0603FR-07100RL | C22810 | Basic | >100 000 | ~$0.01 | `Resistor_SMD:R_0603_1608Metric` | SSR series current-limit |
| R9 | 10 kΩ | 1 % | 0603 | 1 | RC0603FR-0710KL | C25804 | Basic | >100 000 | ~$0.01 | `Resistor_SMD:R_0603_1608Metric` | SSR pull-down (boot-safe) |
| R10 | 470 Ω | 1 % | 0603 | 1 | RC0603FR-07470RL | C23179 | Basic | >100 000 | ~$0.01 | `Resistor_SMD:R_0603_1608Metric` | LED_STATUS current-limit |
| R11 | 100 kΩ | 1 % | 0603 | 1 | RC0603FR-07100KL | C25741 | Basic | >100 000 | ~$0.01 | `Resistor_SMD:R_0603_1608Metric` | Level-probe pull-up |
| R12 | 10 kΩ | 1 % | 0603 | 1 | RC0603FR-0710KL | C25804 | Basic | >100 000 | ~$0.01 | `Resistor_SMD:R_0603_1608Metric` | BTN1 pull-up — same PN as R9 |
| R13 | 10 kΩ | 1 % | 0603 | 1 | RC0603FR-0710KL | C25804 | Basic | >100 000 | ~$0.01 | `Resistor_SMD:R_0603_1608Metric` | BTN2 pull-up — same PN as R9 |
| R14 | 10 kΩ | 1 % | 0603 | 1 | RC0603FR-0710KL | C25804 | Basic | >100 000 | ~$0.01 | `Resistor_SMD:R_0603_1608Metric` | BTN3 pull-up — same PN as R9 |

**Resistor SKU collapse (order quantities):**

| LCSC# | MPN | Value | Qty to order |
|-------|-----|-------|-------------|
| C666878 | TD03G4300BT | 430 Ω 0.1% 0603 | 2 (Rref, Rref2) |
| C23162 | RC0603FR-074K7L | 4.7 kΩ 1% 0603 | 2 (R2, R3) |
| C22810 | RC0603FR-07100RL | 100 Ω 1% 0603 | 1 (R7) |
| C25804 | RC0603FR-0710KL | 10 kΩ 1% 0603 | 4 (R9, R12, R13, R14) |
| C23179 | RC0603FR-07470RL | 470 Ω 1% 0603 | 1 (R10) |
| C25741 | RC0603FR-07100KL | 100 kΩ 1% 0603 | 1 (R11) |

---

## 3. Capacitors

| Refdes | Value | Voltage | Dielectric | Package | Qty | MPN | LCSC# | JLCPCB Tier | Est. Stock | Est. Unit Price (USD) | KiCad Footprint | Notes |
|--------|-------|---------|------------|---------|-----|-----|-------|-------------|------------|----------------------|-----------------|-------|
| C1 | 10 µF | 16 V | X5R | 0805 | 1 | CL21A106KQQNNNE | C15850 | Basic | >50 000 | ~$0.03 | `Capacitor_SMD:C_0805_2012Metric` | +5 V bulk at HLK-PM05 output. Samsung. |
| C2 | 10 µF | 10 V | X5R | 0805 | 1 | CL21A106KQQNNNE | C15850 | Basic | >50 000 | ~$0.03 | `Capacitor_SMD:C_0805_2012Metric` | +3V3 bulk at AMS1117 output. Same PN as C1. |
| C3 | 100 nF | 50 V | X7R | 0603 | 1 | CL10B104KB8NNNC | C14663 | Basic | >500 000 | ~$0.005 | `Capacitor_SMD:C_0603_1608Metric` | +5 V ceramic at U3 input |
| C4 | 100 nF | 50 V | X7R | 0603 | 1 | CL10B104KB8NNNC | C14663 | Basic | >500 000 | ~$0.005 | `Capacitor_SMD:C_0603_1608Metric` | +3V3 ceramic at U3 output |
| C7 | 100 nF | 50 V | X7R | 0603 | 1 | CL10B104KB8NNNC | C14663 | Basic | >500 000 | ~$0.005 | `Capacitor_SMD:C_0603_1608Metric` | U4 RTDIN filter |
| C8 | 100 nF | 50 V | X7R | 0603 | 1 | CL10B104KB8NNNC | C14663 | Basic | >500 000 | ~$0.005 | `Capacitor_SMD:C_0603_1608Metric` | DS3231 VCC bypass |
| C9 | 100 nF | 50 V | X7R | 0603 | 1 | CL10B104KB8NNNC | C14663 | Basic | >500 000 | ~$0.005 | `Capacitor_SMD:C_0603_1608Metric` | ESP32 VDD bypass |
| C10 | 100 nF | 50 V | X7R | 0603 | 1 | CL10B104KB8NNNC | C14663 | Basic | >500 000 | ~$0.005 | `Capacitor_SMD:C_0603_1608Metric` | U4 VDD bypass |
| C11 | 100 nF | 50 V | X7R | 0603 | 1 | CL10B104KB8NNNC | C14663 | Basic | >500 000 | ~$0.005 | `Capacitor_SMD:C_0603_1608Metric` | U6 RTDIN filter |
| C12 | 100 nF | 50 V | X7R | 0603 | 1 | CL10B104KB8NNNC | C14663 | Basic | >500 000 | ~$0.005 | `Capacitor_SMD:C_0603_1608Metric` | U6 VDD bypass |

**Capacitor SKU collapse (order quantities):**

| LCSC# | MPN | Value | Qty to order |
|-------|-----|-------|-------------|
| C15850 | CL21A106KQQNNNE | 10 µF X5R 0805 | 2 (C1, C2) |
| C14663 | CL10B104KB8NNNC | 100 nF X7R 50V 0603 | 8 (C3, C4, C7–C12) |

---

## 4. Diodes and LEDs

| Refdes | Part | Package | Qty | MPN | LCSC# | JLCPCB Tier | Est. Stock | Est. Unit Price (USD) | KiCad Footprint | Notes |
|--------|------|---------|-----|-----|-------|-------------|------------|----------------------|-----------------|-------|
| D1 | Green LED, Vf ≈ 2.0–2.2 V | 0603 | 1 | LTST-C190GKT | C72043 | Basic | >10 000 | ~$0.05 | `LED_SMD:LED_0603_1608Metric` | Status indicator. Lite-On green 0603. |

---

## 5. Protection and Safety

| Refdes | Part | Package | Qty | MPN | LCSC# | JLCPCB Tier | Est. Stock | Est. Unit Price (USD) | KiCad Footprint | Notes |
|--------|------|---------|-----|-----|-------|-------------|------------|----------------------|-----------------|-------|
| F1 | T16A slow-blow fuse | 5×20 mm glass | 1 | — | — | Non-LCSC | — | ~$0.30 | `Fuse:Fuseholder_Cylinder-5x20mm_Schurter_FAB_0031-355x_Horizontal_Closed` | PCB footprint for PCB-mount holder. Holder: Schurter 0031-8201 or equivalent. Fuse body hand-inserted. User-sourced. |
| RV1 | S14K275 MOV (275 VAC) | Disc radial THT 14 mm | 1 | B72214S2271K101 | — | Non-LCSC | — | ~$0.50 | `Varistor:RV_Disc_D15.5mm_W5.0mm_P7.5mm` | TDK/EPCOS equivalent. Footprint uses D15.5mm disc at 7.5mm pitch — covers standard S14 series body. User-sourced (Mouser/DigiKey). |

---

## 6. Connectors and Mechanical

| Refdes | Part | Package | Qty | MPN | LCSC# | JLCPCB Tier | Est. Stock | Est. Unit Price (USD) | KiCad Footprint | Notes |
|--------|------|---------|-----|-----|-------|-------------|------------|----------------------|-----------------|-------|
| J1 | 3-way screw terminal, 5.08 mm pitch | THT | 1 | MKDS 1.5/3-5.08 | — | Non-LCSC | — | ~$0.40 | `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal` | Phoenix-type 3P bornier. User-soldered. L / N / PE AC input — must maintain 6 mm clearance to DC side. |
| J3 | 4-pin 2.54 mm header | THT | 1 | Generic 1×04 | C49661 | Basic | >50 000 | ~$0.05 | `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` | Boiler PT100 off-board connector. C49661 = generic 1×4 straight. |
| J5 | 24-pin FPC 0.5 mm | SMD | 1 | FH12-24S-0.5SH(55) | C225396 | Preferred | ~5 000–20 000 | ~$0.35 | `Connector_FFC-FPC:Hirose_FH12-24S-0.5SH_1x24-1MP_P0.50mm_Horizontal` | GC9A01 display FPC. Hirose FH12 series, top-contact, ZIF. KiCad footprint exists in standard library. |
| J6 | 4-pin 2.54 mm header | THT | 1 | Generic 1×04 | C49661 | Basic | >50 000 | ~$0.05 | `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` | Group PT100 off-board connector. Same PN as J3. |
| J7 | 2-pin 2.54 mm header | THT | 1 | Generic 1×02 | C49658 | Basic | >50 000 | ~$0.03 | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` | Level probe connector. |
| J8 | 6-pin 2.54 mm header | THT | 1 | Generic 1×06 | C49663 | Basic | >50 000 | ~$0.08 | `Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical` | Preset buttons panel (6-pin: 3 signals + 3.3 V + 2×GND). |
| J9 | 2-pin screw terminal, 5.08 mm | THT | 1 | MKDS 1.5/2-5.08 | — | Non-LCSC | — | ~$0.30 | `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal` | Optional on-board SSR output header. User-soldered. |
| ENC1 | EC11 rotary encoder + push | 5-pin THT | 1 | EC11E15244G1 | — | Non-LCSC | — | ~$0.60 | `Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm` | ALPS EC11. KiCad footprint exists. User-soldered. |
| BT1 | CR2032 battery holder | THT | 1 | Keystone 3002 | — | Non-LCSC | — | ~$0.40 | `Battery:BatteryHolder_Keystone_3002_1x2032` | KiCad footprint exists. DS3231 backup. User-soldered. For LCSC PCBA, use SMD variant if preferred (flag: no LCSC preferred-tier THT CR2032 holder verified). |
| SSR1 | Fotek SSR-40DA | External (not on PCB) | 1 | SSR-40DA | — | Non-LCSC | — | ~$8.00 | — | External with heatsink. Only PCB footprint is J9 header for control wires. |

---

## 7. SKU Summary for JLCPCB BOM Upload

Parts with LCSC# that are JLCPCB-assemblable (SMD + Preferred):

| LCSC# | MPN | Refdes | Qty | Tier |
|-------|-----|--------|-----|------|
| C2913206 | ESP32-S3-MINI-1-N8 | U1 | 1 | Extended |
| C6186 | AMS1117-3.3 | U3 | 1 | Basic |
| C779509 | MAX31865AAP+T | U4, U6 | 2 | Extended |
| C131027 | DS3231SN# | U5 | 1 | Extended |
| C666878 | TD03G4300BT | Rref, Rref2 | 2 | Extended |
| C23162 | RC0603FR-074K7L | R2, R3 | 2 | Basic |
| C22810 | RC0603FR-07100RL | R7 | 1 | Basic |
| C25804 | RC0603FR-0710KL | R9, R12, R13, R14 | 4 | Basic |
| C23179 | RC0603FR-07470RL | R10 | 1 | Basic |
| C25741 | RC0603FR-07100KL | R11 | 1 | Basic |
| C15850 | CL21A106KQQNNNE | C1, C2 | 2 | Basic |
| C14663 | CL10B104KB8NNNC | C3, C4, C7–C12 | 8 | Basic |
| C72043 | LTST-C190GKT | D1 | 1 | Basic |
| C49661 | Generic 1×04 header | J3, J6 | 2 | Basic |
| C49658 | Generic 1×02 header | J7 | 1 | Basic |
| C49663 | Generic 1×06 header | J8 | 1 | Basic |
| C225396 | FH12-24S-0.5SH(55) | J5 | 1 | Preferred |

**Hand-soldered / user-sourced (not in JLCPCB PCBA upload):**
U2 (HLK-PM05), F1 (fuse + holder), RV1 (MOV), J1, J9, ENC1, BT1, SSR1

---

## 8. Critical Part Risk Summary

| Part | LCSC# | Risk | Action Required |
|------|-------|------|----------------|
| U4, U6 — MAX31865AAP+T | C779509 | MEDIUM — Extended, Maxim/ADI single-source, histórico de OOS | 3.035 em stock (verificado). Pedir 3-4 pcs como buffer. Sem substituto direto. |
| Rref, Rref2 — 430 Ω 0.1% | C666878 | BAIXO — 8.666 em stock (verificado) | 0.1% é hard requirement para MAX31865. NÃO substituir por 1%. |
| U1 — ESP32-S3-MINI-1-N8 | C2913206 | BAIXO — 11.481 em stock (verificado) | Footprint custom necessário: lib Espressif GitHub. |
| U5 — DS3231SN# | C131027 | LOW-MEDIUM — Extended tier | Verify stock. |
| R8 — 100 Ω 1 W 2512 | C153971 | LOW | If Extended surcharge is undesirable, substitute THT axial wirewound (hand-solder). |

---

## 9. Footprint Validation Status

| Part | Footprint String | Status |
|------|-----------------|--------|
| U1 ESP32-S3-MINI-1-N8 | — | ⚠️ CUSTOM FP NEEDED — import from Espressif KiCad library |
| U2 HLK-PM05 | — | ⚠️ CUSTOM FP NEEDED — import from Hi-Link or community |
| U3 AMS1117-3.3 | `Package_TO_SOT_SMD:SOT-223-3_TabPin2` | VALIDATED — file exists |
| U4, U6 MAX31865AAP+ | `Package_SO:SSOP-20_5.3x7.2mm_P0.65mm` | VALIDATED — file exists |
| U5 DS3231SN# | `Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm` | VALIDATED — file exists |
| Rref, Rref2, R2–R14 | `Resistor_SMD:R_0603_1608Metric` | VALIDATED — file exists |
| R8 | `Resistor_SMD:R_2512_6332Metric` | VALIDATED — file exists |
| C1, C2 | `Capacitor_SMD:C_0805_2012Metric` | VALIDATED — file exists |
| C3, C4, C7–C12 | `Capacitor_SMD:C_0603_1608Metric` | VALIDATED — file exists |
| D1 | `LED_SMD:LED_0603_1608Metric` | VALIDATED — file exists |
| F1 holder | `Fuse:Fuseholder_Cylinder-5x20mm_Schurter_FAB_0031-355x_Horizontal_Closed` | VALIDATED — file exists |
| RV1 S14K275 | `Varistor:RV_Disc_D15.5mm_W5.0mm_P7.5mm` | VALIDATED — D15.5mm is standard body for S14 series; pitch 7.5mm confirmed |
| J1 | `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal` | VALIDATED — file exists |
| J3, J6 | `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` | VALIDATED — file exists |
| J5 | `Connector_FFC-FPC:Hirose_FH12-24S-0.5SH_1x24-1MP_P0.50mm_Horizontal` | VALIDATED — file exists |
| J7 | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` | VALIDATED — file exists |
| J8 | `Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical` | VALIDATED — file exists |
| J9 | `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal` | VALIDATED — file exists |
| ENC1 | `Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm` | VALIDATED — file exists |
| BT1 | `Battery:BatteryHolder_Keystone_3002_1x2032` | VALIDATED — file exists |

---

## 10. Estimated Total BOM Cost (PCBA-assembled parts only)

| Category | Subtotal (est.) |
|----------|----------------|
| ICs (U1, U3–U6) | ~$17.10 |
| Resistors (all) | ~$0.22 |
| Capacitors SMD (all) | ~$0.10 |
| LED (D1) | ~$0.05 |
| Connectors (J3, J5–J8) | ~$0.56 |
| **PCBA parts subtotal** | **~$18.03** |
| Hand-sourced parts (U2, C6, F1, RV1, J1, J9, ENC1, BT1, SSR1) | ~$14.00 |
| **Grand total (all parts)** | **~$32.00** |

*All prices are rough estimates. Actual prices vary with quantity, time, and market conditions. JLCPCB also charges Extended-tier placement fees (~$3 per unique Extended line) and a small per-part fee.*

---

*Atualizado 2026-04-09: C6 (X2 safety cap) e R8 (snubber) removidos do projeto. LCSC#s críticos verificados via pcbparts MCP (live): U1=C2913206, U4/U6=C779509, Rref=C666878.*
