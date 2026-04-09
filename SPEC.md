# Faema President Temperature Controller — SPEC

**Circuit name:** `faema_president_control`
**Revision:** Rev.4
**Source:** Extracted from CONTEXT.md and CLAUDE.md (interview bypassed — spec pre-defined by user)
**Target manufacturer:** JLCPCB with PCBA (LCSC parts, prefer Basic/Preferred tier)
**Target board size:** ~90 x 80 mm

---

## 1. Purpose

Replace the mechanical pressostat in a Faema President espresso machine (manual group)
with an electronic PID temperature controller featuring:
- PID control of the boiler heating resistor
- Round IPS display with analog gauge UI
- Real-time clock scheduling (on/off by time of day)
- Adaptive setpoint based on group head temperature
- Dry-boiler protection via conductivity level sensor
- 3 physical preset buttons (extraction / boost / steam)

## 2. System overview

```
220 VAC  ──► HLK-PM05 (isolated SMPS) ──► 5 V rail
                                          │
                                          ├──► AMS1117-3.3 ──► 3.3 V rail
                                          │                     │
                                          │                     ├──► ESP32-S3 Mini (MCU)
                                          │                     ├──► 2 x MAX31865 (SPI)
                                          │                     ├──► DS3231 RTC (I2C)
                                          │                     ├──► GC9A01 display (SPI + FPC)
                                          │                     └──► 3 preset buttons, encoder, level probe, LED
                                          │
                                          └──► SSR-40DA gate drive (via GPIO4, R7 100R series, R9 10k pulldown)
                                                     │
                                                     └─ switches 220 VAC to boiler resistor (external, with snubber)
```

## 3. Electrical requirements

### 3.1 Power
| Rail | Source | Current budget | Notes |
|------|--------|----------------|-------|
| 220 VAC | Mains | ~11 A peak (boiler) | F1 T16A slow-blow, MOV S14K275, 6 mm creepage min |
| +5 V    | HLK-PM05 (AC/DC isolated, 3 kV) | ~1 A | powers AMS1117 + status LED |
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
- GPIO4 → **R7 = 100 Ω series** → SSR-40DA input (21 mA @ 3.3 V, margin over 7.5 mA min).
- **R9 = 10 kΩ pulldown** on GPIO4 to guarantee SSR OFF during boot/crash of ESP32.
- SSR-40DA is external (with heatsink). J1 bornier brings in AC; RC snubber (R8 100 Ω 1 W + C6 100 nF / 400 V) across SSR terminals, on-board.
- F1 T16A fuse + RV1 MOV S14K275 across L–N on the AC input side.

### 3.5 Real-time clock
- **DS3231** on I2C (address 0x68), SDA=GPIO8, SCL=GPIO9.
- Pull-ups R2, R3 = 4.7 kΩ to +3.3 V.
- C8 = 100 nF bypass on VCC.
- CR2032 backup battery holder on VBAT.

### 3.6 Display
- **GC9A01** 1.28" round IPS 240×240, IPS, 65 k colours, FPC connector.
- Shares the SPI bus with both MAX31865 (SCK=GPIO10, MOSI=GPIO11, MISO=GPIO12).
- GC9A01 does **not** use MISO.
- CS_DISP=GPIO14, DC=GPIO15, RST=GPIO16.
- Note: GC9A01 prefers SPI mode 0 @ up to 80 MHz; MAX31865 uses mode 1/3 @ ≤ 5 MHz. Firmware reconfigures the bus per transaction.

### 3.7 User interface
| Element | Connection | Notes |
|---------|------------|-------|
| EC11 encoder (quadrature + push) | ENC_A=GPIO5, ENC_B=GPIO6, ENC_SW=GPIO7 | Internal pull-ups OK; optional external pull-ups if noisy |
| 3 preset buttons via header J8 (6-pin: 3 signals + 3.3 V + GND + extra GND) | BTN1=GPIO19, BTN2=GPIO20, BTN3=GPIO21 | R12/R13/R14 = 10 kΩ pull-ups to 3.3 V, buttons short to GND (active LOW) |
| Status LED D1 (green) | GPIO2 → R10 470 Ω → LED → GND | Power / Wi-Fi / heating indication |
| Level probe J7 (conductivity, single wire) | GPIO17 → **R11 100 kΩ pull-up to 3.3 V** → probe; return path via boiler body to GND | Water present → GPIO reads LOW; dry → HIGH. Firmware pulses read to minimise electrolysis. |

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
- **F1**: T16A slow blow, 5 × 20 mm fuseholder (THT)
- **RV1**: S14K275 MOV across L–N (THT)
- **R8 + C6**: snubber 100 Ω 1 W + 100 nF / 400 V X1/X2 across SSR output (on PCB)
- Minimum creepage/clearance AC↔DC: **6 mm** (reinforced isolation)
- Mains wiring to boiler: external 2.5 mm² minimum (off PCB)

## 4. GPIO assignment (locked)

| GPIO | Signal | Component |
|------|--------|-----------|
| 2  | LED_STATUS    | D1 + R10 470 Ω |
| 3  | MAX_DRDY      | U4 DRDY (boiler) |
| 4  | SSR_CTRL      | SSR input via R7 + R9 |
| 5  | ENC_CLK       | Encoder A |
| 6  | ENC_DT        | Encoder B |
| 7  | ENC_SW        | Encoder push |
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
| 19 | BTN1          | Preset 1 |
| 20 | BTN2          | Preset 2 |
| 21 | BTN3          | Preset 3 |

## 5. Reference designator registry (seed list)

| Ref | Part | Package | Notes |
|-----|------|---------|-------|
| U1  | ESP32-S3 Mini module | Module | THT/SMD module |
| U2  | HLK-PM05 | Module | AC/DC 5 V, THT |
| U3  | AMS1117-3.3 | SOT-223 | LDO |
| U4  | MAX31865 | SSOP-20 | Boiler sensor |
| U5  | DS3231 | SO-16 | RTC |
| U6  | MAX31865 | SSOP-20 | Group sensor |
| D1  | Green LED | 0603 | Status |
| F1  | T16A fuse | 5×20 mm holder | AC input |
| RV1 | S14K275 MOV | Disc | AC input |
| SSR1 | Fotek SSR-40DA | External | Not on PCB (header only) |
| J1  | AC input terminal | THT bornier | L / N / PE |
| J3  | PT100 boiler | 4-pin header | Off-board |
| J5  | GC9A01 FPC | FPC connector | Off-board display |
| J6  | PT100 group | 4-pin header | Off-board |
| J7  | Level probe | 2-pin header | Off-board |
| J8  | Preset buttons | 6-pin header | Off-board |
| ENC1 | EC11 encoder | 5-pin encoder | Off-board |
| Rref | 430 Ω 0.1 % | 0603 | U4 reference |
| Rref2 | 430 Ω 0.1 % | 0603 | U6 reference |
| R2, R3 | 4.7 kΩ | 0603 | I2C pull-ups |
| R7 | 100 Ω | 0603 | SSR series |
| R8 | 100 Ω 1 W | 2512 or axial | Snubber |
| R9 | 10 kΩ | 0603 | SSR pull-down |
| R10 | 470 Ω | 0603 | LED |
| R11 | 100 kΩ | 0603 | Level probe pull-up |
| R12, R13, R14 | 10 kΩ | 0603 | Button pull-ups |
| C1, C2 | 10 µF | 0805 | Bulk on 5 V / 3.3 V (AMS1117 in/out) |
| C3, C4 | 100 nF | 0603 | AMS1117 in/out ceramic |
| C6 | 100 nF 400 V X1/X2 | radial | SSR snubber |
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

## 7. Constraints for the design pipeline

- **Must keep** the locked GPIO assignment above — do not reassign pins.
- **Must reuse** the reference designators in §5 for traceability with existing KiCad work.
- **Must prefer** JLCPCB Basic/Preferred LCSC parts; HLK-PM05, SSR, PT100s, display, encoder are acceptable non-LCSC items.
- **Must enforce** 6 mm clearance between any AC net (L, N, SSR output, snubber) and any DC net.
- **Must include** all bypass capacitors listed in §3.8.
- **Must produce** a SKiDL Python module whose ERC passes with zero errors.

## 8. Deliverables

1. `architecture/` — block diagram, net plan, IC selection justification, skeleton BOM
2. `sourcing/sourced_bom.md` — LCSC-sourced parts with stock + pricing
3. `datasheets/` — PDFs + SUMMARY.md
4. `circuits/faema_president_control.py` (monolithic) **or** `circuits/faema_president_control/` package (modular) depending on block count
5. `outputs/erc_report.md` — must show 0 errors
6. (Later, after ERC PASS) KiCad netlist + BOM CSV exports
