# Faema President Control — Skeleton BOM

**Circuit:** `faema_president_control`
**Revision:** Rev.4 (SKiDL migration)
**Status:** skeleton — part-sourcer will validate stock, pricing, and exact LCSC PNs in the next stage.

Columns:
- **Refdes** — from SPEC §5 (locked)
- **Function** — block / role
- **Value / MPN** — architect's intent
- **Package** — footprint target
- **Qty** — in this design
- **Sourcing tier** — desired JLC tier (Basic / Preferred / Extended / non-LCSC)
- **Notes**

---

## Integrated circuits and modules

| Refdes | Function | Value / MPN | Package | Qty | Tier | Notes |
|--------|----------|-------------|---------|-----|------|-------|
| U1 | MCU module | ESP32-S3-MINI-1-N8 | Module 27x15 mm | 1 | Extended | Espressif; native USB; MicroPython |
| U2 | AC/DC 5 V isolated | HLK-PM05 | THT brick | 1 | Non-LCSC | User-soldered; 3 kV isolation |
| U3 | LDO 3.3 V | AMS1117-3.3 | SOT-223 | 1 | Basic | 1 W dissipation; needs thermal pour |
| U4 | RTD-to-digital (boiler) | MAX31865AAP+ | SSOP-20 | 1 | Extended | 4-wire, 50 Hz filter |
| U5 | RTC | DS3231SN# | SOIC-16W | 1 | Extended | ±2 ppm, I2C 0x68 |
| U6 | RTD-to-digital (group) | MAX31865AAP+ | SSOP-20 | 1 | Extended | same as U4 |

## Resistors

| Refdes | Value | Tolerance | Package | Qty | Tier | Role |
|--------|-------|-----------|---------|-----|------|------|
| Rref   | 430 Ω | 0.1 % 25 ppm | 0603 | 1 | Preferred | MAX31865 U4 reference |
| Rref2  | 430 Ω | 0.1 % 25 ppm | 0603 | 1 | Preferred | MAX31865 U6 reference |
| R2     | 4.7 kΩ | 1 % | 0603 | 1 | Basic | I2C SDA pull-up |
| R3     | 4.7 kΩ | 1 % | 0603 | 1 | Basic | I2C SCL pull-up |
| R7     | 100 Ω | 1 % | 0603 | 1 | Basic | SSR series current-limit |
| R9     | 10 kΩ | 1 % | 0603 | 1 | Basic | SSR pull-down (boot-safe) |
| R10    | 470 Ω | 1 % | 0603 | 1 | Basic | LED_STATUS current-limit |
| R11    | 100 kΩ | 1 % | 0603 | 1 | Basic | Level-probe pull-up |
| R12    | 10 kΩ | 1 % | 0603 | 1 | Basic | BTN1 pull-up |
| R13    | 10 kΩ | 1 % | 0603 | 1 | Basic | BTN2 pull-up |
| R14    | 10 kΩ | 1 % | 0603 | 1 | Basic | BTN3 pull-up |

Subtotal resistors: **11 pcs** across 7 distinct values.

## Capacitors

| Refdes | Value | Voltage | Dielectric | Package | Qty | Tier | Role |
|--------|-------|---------|------------|---------|-----|------|------|
| C1 | 10 µF | 16 V | X5R/X7R | 0805 | 1 | Basic | +5 V bulk at HLK-PM05 output |
| C2 | 10 µF | 10 V | X5R/X7R | 0805 | 1 | Basic | +3V3 bulk at AMS1117 output |
| C3 | 100 nF | 50 V | X7R | 0603 | 1 | Basic | +5 V ceramic at U3 input |
| C4 | 100 nF | 50 V | X7R | 0603 | 1 | Basic | +3V3 ceramic at U3 output |
| C7 | 100 nF | 50 V | X7R | 0603 | 1 | Basic | U4 RTDIN filter |
| C8 | 100 nF | 50 V | X7R | 0603 | 1 | Basic | DS3231 VCC bypass |
| C9 | 100 nF | 50 V | X7R | 0603 | 1 | Basic | ESP32 VDD bypass |
| C10 | 100 nF | 50 V | X7R | 0603 | 1 | Basic | U4 VDD bypass |
| C11 | 100 nF | 50 V | X7R | 0603 | 1 | Basic | U6 RTDIN filter |
| C12 | 100 nF | 50 V | X7R | 0603 | 1 | Basic | U6 VDD bypass |

Subtotal capacitors: **10 pcs** — collapse identical SKUs:
- 10 µF 0805: 2 pcs (C1, C2)
- 100 nF 0603 X7R: 8 pcs (C3, C4, C7–C12)

## Diodes / LEDs

| Refdes | Part | Package | Qty | Tier | Role |
|--------|------|---------|-----|------|------|
| D1 | Green LED 2 V | 0603 | 1 | Basic | Status indicator |

## Protection / safety

| Refdes | Part | Package | Qty | Tier | Role |
|--------|------|---------|-----|------|------|
| F1 | T16A slow-blow fuse | 5x20 mm glass + holder | 1 | Non-LCSC | AC input fuse |
| RV1 | S14K275 MOV | Disc radial THT | 1 | Non-LCSC | AC surge protection |

## Connectors / mechanical

| Refdes | Part | Package | Qty | Tier | Role |
|--------|------|---------|-----|------|------|
| J1 | 3-way screw terminal, 5.08 mm pitch | THT | 1 | Non-LCSC | L / N / PE in |
| J3 | 4-pin header, 2.54 mm | THT | 1 | Basic | Boiler PT100 (off-board) |
| J5 | 24-pin FPC 0.5 mm | SMD | 1 | Preferred | GC9A01 display ribbon |
| J6 | 4-pin header, 2.54 mm | THT | 1 | Basic | Group PT100 (off-board) |
| J7 | 2-pin header, 2.54 mm | THT | 1 | Basic | Level probe |
| J8 | 6-pin header, 2.54 mm | THT | 1 | Basic | Preset buttons panel |
| J9 | 2-pin screw terminal, 5.08 mm | THT | 1 | Non-LCSC | SSR output to boiler (optional on-board header) |
| ENC1 | EC11 rotary encoder + push | 5-pin THT | 1 | Non-LCSC | User input |
| BT1 | CR2032 battery holder | THT | 1 | Preferred | DS3231 backup |
| SSR1 | Fotek SSR-40DA | External | 1 | Non-LCSC | Not on PCB — header only |

## Totals

| Category | Distinct SKUs | Total pcs |
|----------|----------------|-----------|
| ICs / modules | 6 | 6 |
| Resistors | 7 distinct values | 11 |
| Capacitors | 2 distinct SKUs | 10 |
| LEDs / diodes | 1 | 1 |
| Protection | 2 | 2 |
| Connectors + mechanical | 9 | 10 (plus off-PCB SSR1) |
| **Grand total** | **~29 SKUs** | **~42 parts on PCB** |

---

## Open questions for the part-sourcer

1. **MAX31865 stock** — confirm at least 2 pcs available at LCSC with reasonable price (< $8 each). If out of stock, escalate to the architect (MAX31865 has no drop-in substitute in this architecture).
2. **430 Ω 0.1 % 25 ppm 0603** — verify LCSC has Preferred-tier stock for 2 pcs. A 0.1 % part is a hard requirement; do NOT substitute with 1 %.
3. **100 nF 400 V AC X1/X2 radial safety cap** — LCSC stocks a handful; pick the cheapest in-stock one with X1/Y2 or X2 rating. If nothing suitable, leave the footprint and flag for user hand-sourcing.
4. **S14K275 MOV** and **T16A fuse holder** — typically non-LCSC; sourcer may simply stub these to "user-source" in the final BOM, as they are hand-soldered.
5. **CR2032 holder** — pick the lowest-cost THT holder in LCSC Preferred (Keystone 1066, BAT-HLD-001 equivalent, etc.).
6. **ESP32-S3-MINI-1-N8** — verify current LCSC stock; if low, flag but do not substitute (architecture depends on this exact module pinout).
