# MAX31865AAP+T — RTD-to-Digital Converter (PT100/PT1000)

| Spec | Value |
|------|-------|
| Package | SSOP-20-208mil (5.3×7.2mm, 0.65mm pitch) |
| Vcc / Vin range | 3.0 V – 3.6 V (DVDD and VDD) |
| Resolution | 15-bit (0.03125 Ω LSB) |
| ADC Architecture | Sigma-Delta |
| Interface | SPI (Mode 1 or Mode 3, CS active-low) |
| Max SPI clock | 5 MHz |
| Quiescent current | 2 mA (conversion active) |
| Shutdown current | ~100 µA |
| Operating temp | -40°C to +125°C |
| RTD types | 2-, 3-, or 4-wire PT100/PT1000 |
| Reference resistor | 430 Ω ±0.1% for PT100 (Rref = 4.30× RTD nominal) |
| Filter options | 50 Hz or 60 Hz (set via configuration register bit 0) |
| Fault detection | Open RTD, RTD short, over/under range |
| LCSC# | C779509 |
| Datasheet URL | https://www.lcsc.com/datasheet/lcsc_datasheet_2101201911_Analog-Devices-Inc--Maxim-Integrated-MAX31865AAP-T_C779509.pdf |

## Pinout (SSOP-20, pin 1 at top-left, counting down left side then up right side)

| Pin | Name | Function |
|-----|------|----------|
| 1 | DRDY# | Data Ready, active-LOW output; signals conversion complete |
| 2 | DVDD | Digital supply (3.0–3.6 V); bypass with 100 nF to DGND |
| 3 | VDD | Analog supply (3.0–3.6 V); bypass with 100 nF to GND |
| 4 | BIAS | Bias voltage output (connect to RTD excitation path) |
| 5 | REFIN+ | Reference input positive (connect to Rref top, i.e., +side) |
| 6 | REFIN- | Reference input negative (connect to Rref bottom / FORCE-) |
| 7 | ISENSOR | Unused in 2/3/4-wire mode; leave floating or connect per app note |
| 8 | FORCE+ | RTD high side force (connect to RTD terminal) |
| 9 | FORCE2 | Second force pin (3-wire only; tie to FORCE+ for 2/4-wire) |
| 10 | RTDIN+ | RTD sense positive input |
| 11 | RTDIN- | RTD sense negative input |
| 12 | FORCE- | RTD low side force (connect to Rref bottom) |
| 13 | GND2 | Analog ground (tie to GND) |
| 14 | SDI | SPI data input (MOSI) |
| 15 | SCLK | SPI clock input |
| 16 | CS# | SPI chip select, active-LOW |
| 17 | SDO | SPI data output (MISO) |
| 18 | DGND | Digital ground |
| 19 | GND | Analog ground |
| 20 | N.C. | No connect |

## SPI Register Map (key registers)

| Address | Name | Function |
|---------|------|----------|
| 0x00 | Configuration | Bit7=VBIAS, Bit6=1-shot, Bit4=3-wire, Bit1=50Hz filter |
| 0x01/0x02 | RTD MSB/LSB | 15-bit RTD resistance ratio result + fault bit (bit0) |
| 0x03/0x04 | High Fault MSB/LSB | Over-range threshold |
| 0x05/0x06 | Low Fault MSB/LSB | Under-range threshold |
| 0x07 | Fault Status | Fault flags (read-only) |

Write address = register address | 0x80.

## Typical Application (2-wire PT100, this design)

```
VDD (3.3V) ──┬── REFIN+
             │
           430Ω Rref (0.1%)
             │
             ├── REFIN-  ── FORCE-
             │
            GND

FORCE+ ── PT100 ── RTDIN+   (2-wire: bridge RTDIN- to FORCE-)
RTDIN-  ── (bridge to FORCE- for 2-wire)
```

Config register for 50 Hz filter, VBIAS on, auto-convert: 0xC3 (2-wire) or 0xD3 (3-wire).

## Notes

- This design uses 2-wire PT100 (U4 = boiler, U6 = group head).
- DRDY# is connected to ESP32 GPIO3 (boiler) and GPIO18 is CS_MAX2; DRDY2 can be polled via timeout since only one DRDY line is connected per BOM.
- 50 Hz filter selected (bit 0 = 1 in config) to reject mains interference.
- VDD and DVDD must both be 3.0–3.6 V — do NOT exceed 3.6 V; ESP32-S3 I/O is 3.3 V native.
- Rref must be 0.1% tolerance — see Rref/Rref2 = C666878 (TD03G4300BT 430 Ω 0.1%).
- CS# is active during full SPI transaction; raise CS# between bytes will abort.
- See datasheet Fig. 5 for 2-wire connection, Fig. 6 for 3-wire, Fig. 8 for fault detection.
