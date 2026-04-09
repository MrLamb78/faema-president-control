# Faema President Control — Net Plan

**Circuit:** `faema_president_control`
**Revision:** Rev.4 (SKiDL migration)

This is the authoritative list of named nets, their electrical type, and every pin they reach. Downstream (SKiDL coder and assembler) must use these exact net names.

---

## 1. Power and ground nets

| Net name | Type | Voltage | Source | Sinks | Notes |
|----------|------|---------|--------|-------|-------|
| `AC_L`   | AC power | 220 VAC | J1.1 | F1.1 (then F1.2 -> U2.L), RV1.1 | AC island, 6 mm clearance |
| `AC_N`   | AC power | 220 VAC | J1.2 | U2.N, RV1.2 | AC island |
| `PE`     | Protective earth | 0 V (safety) | J1.3 | chassis / mounting hole | Not tied to GND on PCB |
| `AC_SSR_L_IN`  | AC power | 220 VAC | F1.2 via J9 (external wiring from live through SSR) | SSR1 output terminal 1 header | AC island |
| `AC_SSR_L_OUT` | AC power | 220 VAC (switched) | SSR1 output terminal 2 header | J9.x (to boiler) | AC island; R8+C6 snubber across IN/OUT |
| `+5V`    | Power (rail) | +5 V DC | U2.V+ (HLK-PM05 out) | U3.IN (AMS1117 Vin), C1.+, C3.1 | DC island |
| `+3V3`   | Power (rail) | +3.3 V DC | U3.OUT | C2.+, C4.1, U1.VDD, C9.1, U4.VDD, C10.1, U6.VDD, C12.1, U5.VCC, C8.1, R2 (pull-up), R3 (pull-up), R11, R12, R13, R14, J5 (VCC), J7 (if needed), J8 (3V3 pin), ENC1 common | Bulk sink on the whole DC side |
| `GND`    | Ground | 0 V DC | U2.V- | Common return: all ICs, all bypass caps negative, U1.GND, J5 GND, J6/J3 GND, J7 GND, J8 GND x2, ENC1 GND, BT1-, R9 (to GND), D1 cathode return via LED, snubber DC-side reference n/a | Single continuous pour |
| `VBAT_RTC` | Power (battery) | ~3 V DC | BT1+ | U5.VBAT, BT1 via pad | Backup coin cell |

---

## 2. MCU I/O nets (GPIO-bound — locked by SPEC §4, do NOT reassign)

| Net name | Type | ESP32 pin (GPIO) | Other pins on this net | Purpose |
|----------|------|------------------|------------------------|---------|
| `LED_STATUS` | Digital out | GPIO2 | R10.1 (R10.2 -> D1.anode, D1.cathode -> GND) | Status LED |
| `MAX_DRDY`   | Digital in  | GPIO3 | U4.DRDY_N | Boiler MAX31865 data ready, active LOW |
| `SSR_CTRL`   | Digital out | GPIO4 | R7.1, R9.1 (R9.2 -> GND) (R7.2 -> SSR1+ header) | SSR gate drive with pull-down guarantee-OFF |
| `ENC_CLK`    | Digital in  | GPIO5 | ENC1.A (internal pull-up OK) | Encoder A |
| `ENC_DT`     | Digital in  | GPIO6 | ENC1.B | Encoder B |
| `ENC_SW`     | Digital in  | GPIO7 | ENC1.SW | Encoder push |
| `I2C_SDA`    | I2C data    | GPIO8 | U5.SDA, R2.1 (R2.2 -> +3V3) | DS3231 SDA |
| `I2C_SCL`    | I2C clock   | GPIO9 | U5.SCL, R3.1 (R3.2 -> +3V3) | DS3231 SCL |
| `SPI_SCK`    | SPI clock   | GPIO10 | U4.SCLK, U6.SCLK, J5.SCK (GC9A01) | Shared bus |
| `SPI_MOSI`   | SPI data    | GPIO11 | U4.SDI, U6.SDI, J5.MOSI | Shared bus |
| `SPI_MISO`   | SPI data    | GPIO12 | U4.SDO, U6.SDO | NOT connected to J5 (GC9A01 has no MISO) |
| `CS_MAX`     | Digital out | GPIO13 | U4.CS_N | Boiler chip select |
| `CS_DISP`    | Digital out | GPIO14 | J5.CS | Display chip select |
| `DC_DISP`    | Digital out | GPIO15 | J5.DC | Display data/command |
| `RST_DISP`   | Digital out | GPIO16 | J5.RST | Display reset |
| `LEVEL_SENSE`| Digital in  | GPIO17 | R11.1 (R11.2 -> +3V3), J7.1 | Conductivity probe; pulse-driven |
| `CS_MAX2`    | Digital out | GPIO18 | U6.CS_N | Group chip select |
| `BTN1`       | Digital in  | GPIO19 | R12.1 (R12.2 -> +3V3), J8 BTN1 pin | Preset 1 (active LOW) |
| `BTN2`       | Digital in  | GPIO20 | R13.1 (R13.2 -> +3V3), J8 BTN2 pin | Preset 2 (active LOW) |
| `BTN3`       | Digital in  | GPIO21 | R14.1 (R14.2 -> +3V3), J8 BTN3 pin | Preset 3 (active LOW) |

---

## 3. Analog / sensor nets (off-board to PT100 probes)

### Boiler PT100 (J3, 4-wire) → U4 MAX31865

| Net name | Type | U4 pin | J3 pin | Through |
|----------|------|--------|--------|---------|
| `RTD_B_FORCE_P` | Analog | FORCE+ | J3.1 | Rref (430R) between REFIN+ and FORCE+ (one pad) |
| `RTD_B_FORCE_N` | Analog | FORCE- | J3.4 | — |
| `RTD_B_SENSE_P` | Analog | RTDIN+ | J3.2 | C7.1 (C7.2 -> RTDIN-) |
| `RTD_B_SENSE_N` | Analog | RTDIN- | J3.3 | C7.2 |
| `RTD_B_REFIN_P` | Analog | REFIN+ | — | Rref.1 to FORCE+ side, Rref.2 to REFIN+; internal filter per MAX31865 datasheet |
| `RTD_B_REFIN_N` | Analog | REFIN- | — | tie to FORCE- per 4-wire config |

Note: exact Rref topology follows the MAX31865 "4-wire" reference wiring from the Maxim datasheet (REFIN+ and FORCE+ are bridged by the 430 R, REFIN- and FORCE- are bridged on-board). The SKiDL coder must copy that topology exactly.

### Group PT100 (J6, 4-wire) → U6 MAX31865

| Net name | Type | U6 pin | J6 pin | Through |
|----------|------|--------|--------|---------|
| `RTD_G_FORCE_P` | Analog | FORCE+ | J6.1 | Rref2 to REFIN+ |
| `RTD_G_FORCE_N` | Analog | FORCE- | J6.4 | — |
| `RTD_G_SENSE_P` | Analog | RTDIN+ | J6.2 | C11.1 |
| `RTD_G_SENSE_N` | Analog | RTDIN- | J6.3 | C11.2 |
| `RTD_G_REFIN_P` | Analog | REFIN+ | — | Rref2 |
| `RTD_G_REFIN_N` | Analog | REFIN- | — | tied to FORCE- |

U6 DRDY is **not connected** (polling mode) — see SPEC §3.3.

---

## 4. Bypass / decoupling nets (implicit, listed for completeness)

| Cap | Between | Note |
|-----|---------|------|
| C1  | +5V / GND | 10 uF 0805 bulk at HLK-PM05 output |
| C3  | +5V / GND | 100 nF 0603 ceramic, at U3.IN |
| C2  | +3V3 / GND | 10 uF 0805 bulk at U3.OUT |
| C4  | +3V3 / GND | 100 nF 0603 ceramic, at U3.OUT |
| C9  | +3V3 / GND | 100 nF 0603 at U1.VDD |
| C10 | +3V3 / GND | 100 nF 0603 at U4.VDD |
| C12 | +3V3 / GND | 100 nF 0603 at U6.VDD |
| C8  | +3V3 / GND | 100 nF 0603 at U5.VCC |
| C7  | RTD_B_SENSE_P / RTD_B_SENSE_N | 100 nF 0603 RTDIN filter |
| C11 | RTD_G_SENSE_P / RTD_G_SENSE_N | 100 nF 0603 RTDIN filter |
| C6  | AC_SSR_L_IN / AC_SSR_L_OUT | 100 nF 400 V X1/X2 (snubber cap, AC island) |

---

## 5. No-connect declarations (for ERC silence)

The SKiDL coder must mark the following as `NC` explicitly to suppress ERC floating-pin warnings:

- **U6.DRDY_N** — polled, firmware-only
- **J5.MISO pad** (if FPC layout exposes one) — GC9A01 has no MISO
- **ESP32-S3 Mini** — any unused module IO pins (IO0..IO46 that are not in §2 above). The coder should iterate and NC everything not listed.
- **U4 unused pins** per MAX31865 4-wire config (DIN/SEL/etc. if package exposes them)
- **U5.32KHZ, U5.INT_N, U5.RST_N** — DS3231 alarm/32kHz outputs unused in this design; explicitly NC

---

## 6. Net-level constraints

- `AC_L`, `AC_N`, `AC_SSR_L_IN`, `AC_SSR_L_OUT` must maintain **6 mm minimum** clearance to any DC net on the PCB. SKiDL can't enforce this — it's a layout rule — but `design_risks.md` captures it and the net names are prefixed so it is visually obvious in ratsnests.
- `+5V` and `+3V3` bulk caps (C1, C2) must sit as close as possible to U2 output and U3 output respectively (layout constraint, not ERC).
- SPI star vs chain: the coder should route `SPI_SCK`/`SPI_MOSI` as a shared bus; `SPI_MISO` reaches only U4 and U6. All three CS lines (`CS_MAX`, `CS_MAX2`, `CS_DISP`) are independent GPIOs.
