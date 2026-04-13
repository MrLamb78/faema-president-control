# Faema President Temperature Controller — SPEC

**Circuit name:** `faema_president_control`
**Revision:** Rev.5
**Source:** Rev.4 + editorial review (2026-04-12)
**Target manufacturer:** JLCPCB with PCBA (LCSC parts, prefer Basic/Preferred tier)
**Target board size:** ~90 x 80 mm

> **⚠ Display module not yet selected.** J5 FPC footprint (pin count, pitch, pinout) must be
> frozen before starting PCB layout. Do not route display connections until confirmed.

---

## 1. Purpose

Replace the mechanical pressostat in a Faema President espresso machine (manual group)
with an electronic PID temperature controller featuring:
- PID control of the boiler heating resistor
- Round IPS display with analog gauge UI
- Real-time clock scheduling (on/off heating by time of day)
- Adaptive setpoint based on group head temperature
- Dry-boiler protection via conductivity level sensor
- 3 physical preset buttons (extraction / boost / steam)

## 2. System overview

```
220 VAC (bifásica L1+L2)  ──► F1+F2+RV1 ──► HLK-PM05 (isolated SMPS) ──► 5 V rail
                                          │
                                          ├──► AMS1117-3.3 ──► 3.3 V rail
                                          │                     │
                                          │                     ├──► ESP32-S3 Mini (MCU)
                                          │                     ├──► 2 x MAX31865 (SPI)
                                          │                     ├──► DS3231 RTC (I2C)
                                          │                     ├──► GC9A01 display (SPI + FPC)
                                          │                     └──► 3 preset buttons, encoder, level probe, LED
                                          │
                                          └──► Q1 (2N7002) gate drive from GPIO4
                                                     │
                                                     └─ Q1 drain → SSR-40DA input (−)
                                                        R7 from +5V → SSR-40DA input (+)
                                                        SSR-40DA switches 220 VAC to boiler resistor (external)
```

## 3. Electrical requirements

### 3.1 Power
| Rail | Source | Current budget | Notes |
|------|--------|----------------|-------|
| 220 VAC | Mains (bifásica L1+L2) | ~11 A peak (boiler) | F1+F2 T16A slow-blow (um por fase), MOV S14K275 across L1–L2 após fusíveis, 6 mm creepage min |
| +5 V    | HLK-PM05 (AC/DC isolated, 3 kV) | ~1 A | powers AMS1117 + SSR gate drive |
| +3.3 V  | AMS1117-3.3 (SOT-223 LDO) | ~500 mA | ESP32 peak ~300 mA + peripherals |

- AMS1117-3.3 dissipates ~1 W (5 V → 3.3 V at 500 mA); generous copper pour on SOT-223 GND pad required.
- HLK-PM05 and SSR are THT/external — all other parts are SMD suitable for PCBA.

### 3.2 Microcontroller
- **ESP32-S3 Mini module** (MicroPython), native USB, Wi-Fi + BT, 3.3 V logic.

### 3.3 Temperature sensing
Two independent channels, both using MAX31865 (SSOP-20, direct IC not breakout):

| Channel | IC | Rref | Filter caps | DRDY | CS | Config |
|---------|----|------|-------------|------|----|----|
| Boiler (U4) | MAX31865 | 430 Ω 0.1 % (REFIN+ ↔ FORCE+) | C7 100 nF across RTDIN+/− ; C10 100 nF VDD | GPIO3 (active LOW) | GPIO13 | 4-wire, 50 Hz filter, SPI mode 1 or 3 ≤ 5 MHz |
| Group (U6)  | MAX31865 | 430 Ω 0.1 %                     | C11 100 nF across RTDIN+/− ; C12 100 nF VDD | not connected (polling) | GPIO18 | 4-wire, 50 Hz filter |

Sensors J3 (boiler PT100) and J6 (group PT100) are both 4-wire off-board connectors.

### 3.4 Boiler SSR drive
- GPIO4 → **R_gate = 100 Ω** → Q1 (2N7002 SOT-23) gate.
- **R9 = 10 kΩ** from Q1 gate to GND — guarantees SSR OFF during ESP32 boot/crash (gate held LOW).
- Q1 drain → SSR-40DA input (−); Q1 source → GND.
- **R7 = 220 Ω** from +5 V to SSR-40DA input (+) → ~17 mA drive (min 7.5 mA; no GPIO current stress).
- SSR-40DA is external (with heatsink). J1 brings in AC mains; J2 carries switched L1 + L2 to boiler.
- F1+F2 T16A slow-blow fuses (one per phase) + RV1 MOV S14K275 across L1_FUSED–L2_FUSED on the AC input side.
- Snubber omitted: SSR-40DA is zero-crossing type; boiler element is purely resistive.

### 3.5 Real-time clock
- **DS3231** on I2C (address 0x68), SDA=GPIO8, SCL=GPIO9.
- Pull-ups R2, R3 = 4.7 kΩ to +3.3 V.
- C8 = 100 nF bypass on VCC.
- CR2032 backup battery holder on VBAT.

### 3.6 Display
- **ILI9341** 2.4" TFT 240×320, 16-bit colour, SPI 4-wire module with pin header.
- Shares the SPI bus with both MAX31865 (SCK=GPIO10, MOSI=GPIO11, MISO=GPIO12).
- ILI9341 does **not** use MISO.
- CS_DISP=GPIO14, DC=GPIO15, RST=GPIO16.
- ILI9341 SPI mode 0, ≤ 40 MHz; MAX31865 uses mode 1/3 @ ≤ 5 MHz — firmware reconfigures per transaction.
- Module connects via J5 (8-pin cable header: VCC, GND, CS, RST, DC, MOSI, SCK, LED).
- Display is mounted in the external UI enclosure (see §3.7); cable length ~40 cm, operate SPI at ≤ 20 MHz over cable.
- Portrait orientation (240 wide × 320 tall). The 52 mm opening in the front panel is not used.

### 3.7 User interface

The display, encoder, and preset buttons are housed in a **dedicated external UI enclosure** mounted on the side of the machine. All elements connect to the main PCB via cables through J5, J8, and J9.

```
┌─────────────────────┐
│   [ ILI9341 2.4" ]  │  portrait, 240×320
│   [   display    ]  │
│                     │
│  [enc]  [●] [●] [●] │  EC11 rotary + 3 preset buttons
└─────────────────────┘
  ~70 mm × ~130 mm (indicative)
```

| Element | Connection | Notes |
|---------|------------|-------|
| ILI9341 2.4" display via J5 (8-pin header) | CS=GPIO14, DC=GPIO15, RST=GPIO16, SCK=GPIO10, MOSI=GPIO11 | External enclosure, ~40 cm cable |
| EC11 encoder (quadrature + push) via J9 | ENC_A=GPIO5, ENC_B=GPIO6, ENC_SW=GPIO7 | 5-pin header; internal pull-ups OK |
| 3 preset buttons via J8 (6-pin: 3 signals + 3.3 V + GND + extra GND) | BTN1=GPIO19, BTN2=GPIO20, BTN3=GPIO21 | R12/R13/R14 = 10 kΩ pull-ups to 3.3 V, active LOW |
| Status LED D1 (green) | GPIO2 → R10 470 Ω → LED → GND | On main PCB — power / Wi-Fi / heating indication |
| Level probe J7 (conductivity, single wire) | GPIO17 → **R11 100 kΩ pull-up to 3.3 V** → probe; return via boiler body to GND | Water present → LOW; dry → HIGH. Firmware pulses read to minimise electrolysis. |

### 3.8 Bypass capacitors
| Cap | Location | Value |
|-----|----------|-------|
| C7  | U4 RTDIN+/− across | 100 nF |
| C8  | DS3231 VCC | 100 nF |
| C9  | ESP32-S3 VDD | 100 nF |
| C10 | U4 VDD | 100 nF |
| C11 | U6 RTDIN+/− across | 100 nF |
| C12 | U6 VDD | 100 nF |

### 3.9 AC protection / isolation
- **F1**: T16A slow blow on L1, 5 × 20 mm fuseholder (THT)
- **F2**: T16A slow blow on L2, 5 × 20 mm fuseholder (THT)
- **RV1**: S14K275 MOV across L1_FUSED–L2_FUSED (THT) — proteção diferencial após fusíveis
- Minimum creepage/clearance AC↔DC: **6 mm** (reinforced isolation)
- Mains wiring to boiler: external 2.5 mm² minimum (off PCB)
- PE rail: dedicated trace from J1-PE to chassis mounting point — **not shared with signal GND**

## 4. GPIO assignment (locked)

| GPIO | Signal | Component |
|------|--------|-----------|
| 2  | LED_STATUS    | D1 + R10 470 Ω |
| 3  | MAX_DRDY      | U4 DRDY (boiler) |
| 4  | SSR_CTRL      | Q1 gate via R_gate + R9 pulldown |
| 5  | ENC_CLK       | Encoder A (via J9) |
| 6  | ENC_DT        | Encoder B (via J9) |
| 7  | ENC_SW        | Encoder push (via J9) |
| 8  | I2C_SDA       | DS3231 |
| 9  | I2C_SCL       | DS3231 |
| 10 | SPI_SCK       | Shared U4 + U6 + GC9A01 |
| 11 | SPI_MOSI      | Shared |
| 12 | SPI_MISO      | Shared (U4 + U6 only) |
| 13 | CS_MAX        | U4 chip select |
| 14 | CS_DISP       | GC9A01 chip select |
| 15 | DC_DISP       | GC9A01 D/C |
| 16 | RST_DISP      | GC9A01 reset |
| 17 | LEVEL_SENSE   | Level probe (R11 pull-up) |
| 18 | CS_MAX2       | U6 chip select |
| 19 | BTN1          | Preset 1 (via J8) |
| 20 | BTN2          | Preset 2 (via J8) |
| 21 | BTN3          | Preset 3 (via J8) |

## 5. Reference designator registry

| Ref | Part | Package | Notes |
|-----|------|---------|-------|
| U1  | ESP32-S3 Mini module | Module | THT/SMD module |
| U2  | HLK-PM05 | Module | AC/DC 5 V, THT |
| U3  | AMS1117-3.3 | SOT-223 | LDO |
| U4  | MAX31865 | SSOP-20 | Boiler sensor |
| U5  | DS3231 | SO-16 | RTC |
| U6  | MAX31865 | SSOP-20 | Group sensor |
| Q1  | 2N7002 | SOT-23 | NMOS low-side switch — drain→SSR(−), source→GND |
| D1  | Green LED | 0603 | Status |
| F1  | T16A fuse | 5×20 mm holder | AC input L1 |
| F2  | T16A fuse | 5×20 mm holder | AC input L2 |
| RV1 | S14K275 MOV | Disc | Across L1_FUSED–L2_FUSED |
| SSR1 | Fotek SSR-40DA | External | Not on PCB (header only) |
| J1  | AC input terminal | THT bornier 3-pin | L1 / L2 / PE |
| J2  | AC boiler output terminal | THT bornier 2-pin | L1_switched (from SSR) / L2 |
| J3  | PT100 boiler | 4-pin header | Off-board, 4-wire |
| J5  | ILI9341 2.4" display cable | 8-pin header 2.54 mm | VCC / GND / CS / RST / DC / MOSI / SCK / LED |
| J6  | PT100 group | 4-pin header | Off-board, 4-wire |
| J7  | Level probe | 2-pin header | Off-board |
| J8  | Preset buttons | 6-pin header | BTN1/BTN2/BTN3 + 3.3V + GND + GND |
| J9  | Encoder | 5-pin header | ENC_A / ENC_B / ENC_SW / 3.3V / GND |
| J10 | SSR-40DA control | 2-pin bornier | SSR input (+) via R7 / SSR input (−) via Q1 drain |
| Rref | 430 Ω 0.1 % | 0603 | U4 reference |
| Rref2 | 430 Ω 0.1 % | 0603 | U6 reference |
| R2, R3 | 4.7 kΩ | 0603 | I2C pull-ups |
| R_gate | 100 Ω | 0603 | GPIO4 → Q1 gate (limita corrente de gate) |
| R7 | 220 Ω | 0603 | +5V → SSR input (+) — ~17 mA drive |
| R9 | 10 kΩ | 0603 | Q1 gate pulldown (SSR OFF durante boot/reset) |
| R10 | 470 Ω | 0603 | LED |
| R11 | 100 kΩ | 0603 | Level probe pull-up |
| R12, R13, R14 | 10 kΩ | 0603 | Button pull-ups |
| C1, C2 | 10 µF | 0805 | Bulk on 5 V / 3.3 V (AMS1117 in/out) |
| C3, C4 | 100 nF | 0603 | AMS1117 in/out ceramic |
| C7 | 100 nF | 0603 | U4 RTDIN filter |
| C8 | 100 nF | 0603 | DS3231 VCC bypass |
| C9 | 100 nF | 0603 | ESP32 VDD bypass |
| C10 | 100 nF | 0603 | U4 VDD bypass |
| C11 | 100 nF | 0603 | U6 RTDIN filter |
| C12 | 100 nF | 0603 | U6 VDD bypass |
| BT1 | CR2032 holder | THT | DS3231 backup |

## 6. Operational requirements

### 6.1 Adaptive PID
- Boiler PT100 → U4 → PID → SSR (~1 s cycle, zero-cross SSR)
- Group PT100 → U6 → feed-forward offset on SV_caldeira
- Hard limits: SV_MIN = 85 °C, SV_MAX = 128 °C

### 6.2 Presets
- Normal: 93 °C (extraction)
- Boost: 108 °C (pre-infusion)
- Steam: 125 °C (milk steam)

### 6.3 Protections
- Level-sense override: any LOW-water reading immediately forces SSR OFF.
- R9 pulldown guarantees SSR OFF while ESP32 is in reset/boot.
- Watchdog + sensor fault handling in firmware.

### 6.4 Scheduling
- DS3231 backup battery maintains time across power-offs.
- Config file defines on/off hours (optional weekday mask).
- **The scheduler controls boiler heating only (via SSR). It does not cut mains power to the machine.**

## 7. Safety

This electronic controller operates alongside — and does not replace — independent mechanical
safety devices already present in the machine (thermal cutout fuse, overpressure valve, pressure
relief valve, boiler safety valve). A failure of this controller must not create an unsafe condition
beyond what those devices would normally catch.

- The boiler element must remain protected by the machine's original thermal fuse.
- This PCB must not bypass or defeat any existing mechanical safety device.
- PE must be connected at J1 and bonded to the chassis at the mounting point.

## 8. Constraints for the design pipeline

- **Source of truth:** `circuits/faema_president.py` (SKiDL) for circuit connections; `kicad/*.kicad_pcb` for layout. SKiDL generates the netlist (`outputs/faema_president.net`) which is imported into KiCad PCB. Do not edit the schematic file directly.
- **Must keep** the locked GPIO assignment in §4 — do not reassign pins.
- **Must reuse** reference designators in §5 for traceability with existing KiCad work.
- **Must prefer** JLCPCB Basic/Preferred LCSC parts; HLK-PM05, SSR, PT100s, display, encoder acceptable as non-LCSC.
- **Must enforce** 6 mm clearance between any AC net (L1, L2, L1_switched, J2) and any DC net.
- **Must include** all bypass capacitors listed in §3.8.
- **J5** is a standard 2.54 mm 8-pin header — no special footprint required.

## 9. Deliverables

1. `circuits/faema_president.py` — SKiDL netlist (primary source of truth)
2. `outputs/faema_president.net` — netlist gerada pelo SKiDL (importar no KiCad PCB)
3. `kicad/faema-president.kicad_pcb` — PCB layout (primary source for layout)
4. `outputs/BOM.csv` — KiCad BOM export (LCSC part numbers in fields)
5. `outputs/erc_report` — KiCad ERC must show 0 errors
6. `outputs/drc_report` — KiCad DRC must show 0 errors (after layout)
7. `sourcing/sourced_bom.md` — LCSC-sourced BOM with stock + pricing (kept in sync)
8. `datasheets/` — PDFs + SUMMARY.md for significant ICs
