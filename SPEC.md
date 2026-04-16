# Faema President Temperature Controller — SPEC

**Circuit name:** `faema_carrier`
**Revision:** Rev.6b — Carrier Board
**Date:** 2026-04-16
**Target:** PCB bare (JLCPCB), hand-soldered. Single unit.

---

## 1. Purpose

Replace the mechanical pressostat in a Faema President espresso machine (manual group)
with an electronic PID temperature controller featuring:
- PID control of the boiler heating element via SSR-40DA (external)
- Display (Nextion NX3224T024 2.4" UART primary, SPI ILI9341 optional)
- Time-based scheduling via NTP (WiFi) or optional DS3231 RTC module
- Adaptive setpoint based on group head temperature
- Dry-boiler protection via conductivity level sensor
- 3 physical preset buttons + rotary encoder

## 2. Architecture — Carrier Board

The PCB is a **carrier board** (backplane) with connectors for plug-in modules.
No fine-pitch SMD ICs to solder — the complex chips live on ready-made modules.

```
┌──────────────────────────────────────────────────────────────┐
│  ZONA AC (6mm clearance)         │    ZONA DC                │
│                                  │                            │
│  J1 (bornier AC 3-pin)           │    [Pico 2 W]              │
│  RV1 (MOV S14K275)               │     2×20 socket            │
│  U1 (HLK-PM05)                   │                            │
│                                  │    [SEN-30201] ×2          │
│ ─────── isolação 6mm ────────────│     1×8 socket (vertical)  │
│                                  │                            │
│  U2 (AMS1117-3.3)  C1-C4        │    J6 Nextion (UART 4-pin) │
│  SSR drive (Q1 + R1-R3)         │    J7 SPI display (8-pin)  │
│  J2 (bornier SSR 2-pin)         │    J8 I2C/RTC (4-pin)      │
│                                  │    J9/J10 NTC (JST XH 2-pin)│
│  D1+R4 (LED status)             │                            │
│  R5+J5 (level probe)            │    J3 encoder (5-pin)      │
│                                  │    J4 buttons (4-pin)      │
└──────────────────────────────────────────────────────────────┘
```

### Plug-in modules (not on carrier PCB)

| Module | Interface | Connector on carrier |
|--------|-----------|---------------------|
| Raspberry Pi Pico 2 W | 2×20 headers | J11 + J12 (female sockets) |
| Playing with Fusion SEN-30201 ×2 | 1×8 header each | J13, J14 (female sockets) |
| Nextion NX3224T024 (primary display) | UART 4-wire | J6 (male header) |
| DS3231 module (optional RTC) | I2C 4-wire | J8 (male header) |
| SSR-40DA (external, with heatsink) | 2-wire control | J2 (bornier) |

### Components ON the carrier PCB

| Category | Components |
|----------|-----------|
| Power | U1 HLK-PM05, U2 AMS1117-3.3, C1-C4 |
| Protection | RV1 MOV S14K275 |
| SSR drive | Q1 2N7002, R1 220Ω, R2 100Ω, R3 10kΩ |
| LED | D1 green 0603, R4 470Ω |
| Level probe | R5 100kΩ pull-up |
| UART level shift | R6 10kΩ, R7 15kΩ (Nextion 5V→3.3V) |
| NTC (simultâneo com RTD) | R8, R9 2k2 0.1% ref; C5, C6 100nF filtro |
| Button pull-ups | R10, R11, R12 10kΩ |
| Encoder pull-ups | R13, R14, R15 10kΩ |
| Connectors | J1–J15 (headers + borniers) |

## 3. Electrical requirements

### 3.1 Power

| Rail | Source | Current budget | Notes |
|------|--------|----------------|-------|
| 220 VAC | Mains (bifásica L1+L2, sem neutro) | ~11 A peak (boiler, external) | External T16A slow-blow fuses (panel-mount), MOV on PCB |
| +5 V | HLK-PM05 (AC/DC isolated, 3 kV) | ~600 mA | Pico (via VSYS), Nextion, SSR drive, SEN-30201 breakouts |
| +3.3 V | AMS1117-3.3 (SOT-223 LDO) | ~50 mA | Pull-ups, NTC dividers, LED. Pico has own 3.3V via internal regulator |

- HLK-PM05: THT module, hand-soldered.
- Pico powered via VSYS (pin 39) with +5V. Pico's internal regulator provides 3.3V to RP2350.
- AMS1117 provides independent 3.3V for carrier board passives.
- SEN-30201 breakouts: fed 5V on Vin, use their own onboard LDO.

### 3.2 Microcontroller — Raspberry Pi Pico 2 W

- RP2350 dual-core ARM Cortex-M33, 150 MHz
- 520KB SRAM, 4MB flash
- WiFi (CYW43439) + Bluetooth
- MicroPython
- 26 GPIO pins, 3 ADC channels
- Plugs into 2×20 female sockets on carrier

### 3.3 Temperature sensing

**Primary: RTD via SEN-30201 breakout boards (2×)**

Each SEN-30201 contains a MAX31865 with onboard Rref, LDO, and level shifter.
Connects via 1×8 header: Vin, GND, SDO, SDI, SCK, CS, DRDY, 3Vo.
SPI bus shared (SCK/MOSI/MISO common), CS unique per board.

| Slot | Connector | CS | Sensor | Notes |
|------|-----------|-----|--------|-------|
| Caldeira | J13 | GP5 | PT100 or PT1000 | Boiler temperature |
| Grupo | J14 | GP6 | PT100 or PT1000 | Group head temperature |

- DRDY pins not connected on carrier (polling via SPI register read).
- SEN-30201 supports PT100, PT500, PT1000 via jumper/config on breakout.
- 4-wire RTD connection via screw terminal on each breakout board.

**Simultaneous: NTC thermistors on GP26/GP27**

NTC circuit operates simultaneously with RTD (independent ADC vs SPI interfaces).
Voltage divider: VCC3V3 → R_ref(2k2 0.1%) → ADC_pin → NTC(10k) → GND.
C5/C6 (100nF) low-pass filter in parallel with NTC reduces ADC noise.
Connected to GP26 (ADC0, caldeira) and GP27 (ADC1, grupo).
V_adc range: 25°C→2.70V, 85°C→1.08V, 128°C→0.56V.
Use 0.1% precision for R8/R9 to keep temperature error < 0.5°C.

### 3.4 Display

**Option A — Nextion NX3224T024 (primary)**
- 2.4" TFT with resistive touch, built-in processor
- UART interface: 4 pins (5V, GND, TX, RX)
- J6 on carrier board
- Level shifter required: Nextion TX (5V) → voltage divider (R6 10kΩ + R7 15kΩ) → Pico RX (3.0V)
- Pico TX (3.3V) → Nextion RX directly (3.3V accepted as HIGH)
- UI designed in Nextion Editor, uploaded to display via SD card

**Option B — SPI display 2.4" ILI9341 (alternative)**
- Standard SPI 4-wire, 8-pin header J7
- Shares SPI bus with RTD breakouts
- CS=GP8, DC=GP9, RST=GP10, LED=GP13
- J7 pinout: VCC, GND, CS, RST, DC, MOSI, SCK, LED

### 3.5 SSR drive

- GP11 → R2 (100Ω gate series) → Q1 gate (2N7002 SOT-23)
- R3 (10kΩ) Q1 gate → GND: guarantees SSR OFF during boot/reset
- Q1 drain → J2 pin 2 (SSR input −)
- Q1 source → GND
- R1 (220Ω) from +5V → J2 pin 1 (SSR input +): ~17 mA drive current
- SSR-40DA is external with heatsink. Zero-crossing type, no snubber needed.
- AC power wiring (SSR → boiler) is entirely external, NOT on PCB.

### 3.6 Level probe

- GP22 → R5 (100kΩ pull-up to 3.3V) → J5 pin 1 → probe
- J5 pin 2 → GND (return via boiler chassis)
- Water present → LOW (conductivity shorts to GND via boiler body)
- Dry → HIGH (probe floating, pull-up holds high)
- R5 = 100kΩ limits current to ~33µA (minimizes electrolysis)
- Firmware uses pulsed reading to further reduce electrolysis

### 3.7 User interface

| Element | Connector | Notes |
|---------|-----------|-------|
| Encoder EC11 (quadrature + push) | J3 (5-pin: CLK, DT, SW, 3V3, GND) | R13-R15 10kΩ pull-ups on carrier |
| 3 preset buttons (active LOW) | J4 (4-pin: BTN1, BTN2, BTN3, GND) | R10-R12 10kΩ pull-ups on carrier |
| Status LED D1 (green 0603) | On carrier board | GP12 → R4 470Ω → D1 → GND |

### 3.8 RTC (optional)

- J8: 4-pin I2C header (3V3, GND, SDA=GP14, SCL=GP15)
- Accepts any DS3231 module (ZS-042 or similar)
- Pull-ups on DS3231 module (not on carrier)
- Alternative: use NTP via Pico's WiFi (no RTC needed)

### 3.9 AC protection / isolation

- **RV1**: S14K275 MOV across L1_FUSED–L2_FUSED on PCB (surge/transient protection)
- **External fuses**: T16A slow-blow (one per phase), panel-mount fuse holders (NOT on PCB)
- J1 receives pre-fused phases: L1_FUSED, L2_FUSED, PE
- **6 mm minimum clearance** between AC nets and DC nets on PCB layout
- PE rail from J1 pin 3 to chassis mounting point — separate from signal GND
- HLK-PM05 provides 3kV isolation between AC and DC sides
- AMS1117 has thermal shutdown
- Boiler element protected by machine's original thermal fuse (independent of this controller)

## 4. GPIO assignment — Pico 2 W

| GPIO | Signal | Direction | Component |
|------|--------|-----------|-----------|
| GP0 | UART_TX | OUT | → Nextion RX |
| GP1 | UART_RX | IN | ← Nextion TX (via R6/R7 level shift) |
| GP2 | SPI_SCK | OUT | Shared: RTDs + SPI display |
| GP3 | SPI_MOSI | OUT | Shared |
| GP4 | SPI_MISO | IN | Shared |
| GP5 | CS_RTD1 | OUT | SEN-30201 caldeira |
| GP6 | CS_RTD2 | OUT | SEN-30201 grupo |
| GP7 | — | — | Spare (not connected on carrier) |
| GP8 | CS_DISP | OUT | SPI display option (J7) |
| GP9 | DC_DISP | OUT | SPI display option (J7) |
| GP10 | RST_DISP | OUT | SPI display option (J7) |
| GP11 | SSR_CTRL | OUT | Q1 gate via R2 |
| GP12 | LED_STATUS | OUT | D1 via R4 |
| GP13 | DISP_LED | OUT | SPI display backlight (J7) |
| GP14 | I2C_SDA | I/O | DS3231 module (J8) |
| GP15 | I2C_SCL | OUT | DS3231 module (J8) |
| GP16 | ENC_CLK | IN | Encoder A (J3) |
| GP17 | ENC_DT | IN | Encoder B (J3) |
| GP18 | ENC_SW | IN | Encoder push (J3) |
| GP19 | BTN1 | IN | Preset 1 (J4) |
| GP20 | BTN2 | IN | Preset 2 (J4) |
| GP21 | BTN3 | IN | Preset 3 (J4) |
| GP22 | LEVEL_SENSE | IN | Level probe (J5) |
| GP26 | NTC1_ADC | ADC IN | NTC caldeira (J9) — simultâneo com RTD |
| GP27 | NTC2_ADC | ADC IN | NTC grupo (J10) — simultâneo com RTD |

## 5. Reference designator registry

| Ref | Part | Package | Notes |
|-----|------|---------|-------|
| U1 | HLK-PM05 | THT module | AC/DC 5V isolated |
| U2 | AMS1117-3.3 | SOT-223 | LDO 3.3V |
| Q1 | 2N7002 | SOT-23 | NMOS SSR low-side switch |
| D1 | Green LED | 0603 | Status |
| RV1 | S14K275 MOV | Disc THT | Surge protection |
| R1 | 220Ω 1% | 0603 | +5V → SSR+ current limit |
| R2 | 100Ω 1% | 0603 | Gate series resistor |
| R3 | 10kΩ 1% | 0603 | Gate pull-down (boot-safe) |
| R4 | 470Ω 1% | 0603 | LED current limit |
| R5 | 100kΩ 1% | 0603 | Level probe pull-up |
| R6 | 10kΩ 1% | 0603 | UART level shift top |
| R7 | 15kΩ 1% | 0603 | UART level shift bottom |
| R8 | 2k2Ω 0.1% | 0603 | NTC1 reference (caldeira) |
| R9 | 2k2Ω 0.1% | 0603 | NTC2 reference (grupo) |
| R10 | 10kΩ 1% | 0603 | BTN1 pull-up |
| R11 | 10kΩ 1% | 0603 | BTN2 pull-up |
| R12 | 10kΩ 1% | 0603 | BTN3 pull-up |
| R13 | 10kΩ 1% | 0603 | ENC_CLK pull-up |
| R14 | 10kΩ 1% | 0603 | ENC_DT pull-up |
| R15 | 10kΩ 1% | 0603 | ENC_SW pull-up |
| C1 | 10µF 16V X5R | 0805 | +5V bulk |
| C2 | 10µF 16V X5R | 0805 | +3.3V bulk |
| C3 | 100nF 50V X7R | 0603 | +5V bypass |
| C4 | 100nF 50V X7R | 0603 | +3.3V bypass |
| C5 | 100nF 50V X7R | 0603 | NTC1 ADC filter (GP26) |
| C6 | 100nF 50V X7R | 0603 | NTC2 ADC filter (GP27) |
| J1 | AC input bornier | 3-pin 5.08mm | L1_FUSED, L2_FUSED, PE |
| J2 | SSR control bornier | 2-pin 5.08mm | SSR+, SSR− |
| J3 | Encoder | JST XH 5-pin 2.5mm | CLK, DT, SW, 3V3, GND |
| J4 | Buttons | JST XH 4-pin 2.5mm | BTN1, BTN2, BTN3, GND |
| J5 | Level probe | JST XH 2-pin 2.5mm | SENSE, GND |
| J6 | Nextion display | JST XH 4-pin 2.5mm | 5V, GND, NX_TX, NX_RX |
| J7 | SPI display (optional) | JST XH 8-pin 2.5mm | VCC, GND, CS, RST, DC, MOSI, SCK, LED |
| J8 | I2C / RTC (optional) | JST XH 4-pin 2.5mm | 3V3, GND, SDA, SCL |
| J9 | NTC caldeira | JST XH 2-pin 2.5mm | NTC1, GND |
| J10 | NTC grupo | JST XH 2-pin 2.5mm | NTC2, GND |
| J11 | Pico left socket | 1×20 female 2.54mm | GP0–GP15 side |
| J12 | Pico right socket | 1×20 female 2.54mm | GP16–GP28 + power side |
| J13 | RTD caldeira socket | 1×8 female 2.54mm | SEN-30201 slot 1 |
| J14 | RTD grupo socket | 1×8 female 2.54mm | SEN-30201 slot 2 |

## 6. Operational requirements

### 6.1 Adaptive PID
- RTD caldeira (J13) → MAX31865 SPI → PID → SSR (~1s cycle, zero-cross)
- RTD grupo (J14) → feed-forward offset on SV_caldeira
- Hard limits: SV_MIN = 85°C, SV_MAX = 128°C

### 6.2 Presets
- Normal: 93°C (extraction)
- Boost: 108°C (pre-infusion)
- Steam: 125°C (milk steam)

### 6.3 Protections
- Level-sense override: LOW-water forces SSR OFF immediately
- R3 pull-down guarantees SSR OFF while Pico is in reset/boot
- Watchdog + sensor fault handling in firmware
- Machine's original thermal fuse provides independent backup protection

### 6.4 Scheduling
- NTP via WiFi (primary): Pico syncs time at boot
- DS3231 RTC via I2C (optional fallback): maintains time across power-offs
- Config defines on/off hours

## 7. Safety

This controller operates alongside — and does not replace — independent mechanical
safety devices already present in the machine (thermal cutout fuse, overpressure valve,
safety valve). A failure of this controller must not create an unsafe condition.

- RV1 MOV: surge/transient protection on AC lines
- External T16A fuses: overcurrent protection (one per phase)
- 6mm AC/DC clearance: reinforced isolation on PCB layout
- R3 gate pull-down: SSR OFF guaranteed during boot/reset/crash
- R5 100kΩ: limits probe current to prevent electrolysis
- PE bonded to chassis at J1 — not shared with signal GND
- HLK-PM05: 3kV galvanic isolation, internal overcurrent protection
- AMS1117: thermal shutdown
- All AC power wiring external to PCB (2.5mm² minimum)

## 8. Constraints

- **Source of truth:** `circuits/faema_carrier.py` (SKiDL) → `outputs/faema_carrier.net`
- **GPIO assignment** in §4 is locked — do not reassign pins
- **6mm clearance** between AC and DC nets (layout rule)
- **SEN-30201 pinout** (1×8): Vin, GND, SDO, SDI, SCK, CS, DRDY, 3Vo — verify against actual board before fabrication
- **Pico 2 W socket — pins deliberadamente NC:**
  - Pin 40 VBUS: não conectar ao +5V (back-feed USB → dano ao computador em debug)
  - Pin 35 ADC_VREF: conectado ao +3V3 do carrier (AMS1117) — referência ratiométrica para NTC; cancela variações da fonte e isola ruído SMPS/WiFi do regulador interno do Pico. C7 (100nF) de bypass entre ADC_VREF e AGND, posicionado próximo ao J12 pino 15.
  - Pin 36 3V3(OUT): NC — saída do regulador interno do Pico, não conectar ao +3V3 do carrier
  - Pin 37 3V3_EN: NC — pull-up interno mantém o regulador ligado
  - Pin 30 RUN: NC — pull-up interno; conectar apenas se precisar de reset externo por hardware
  - Pin 33 AGND e todos os pinos GND: conectados ao GND do carrier
- PCB bare from JLCPCB, all components hand-soldered

## 9. Deliverables

1. `circuits/faema_carrier.py` — SKiDL circuit (source of truth)
2. `outputs/faema_carrier.net` — netlist for KiCad PCB import
3. `kicad/faema-carrier.kicad_pcb` — PCB layout
4. `outputs/bom_carrier.csv` — BOM for ordering
