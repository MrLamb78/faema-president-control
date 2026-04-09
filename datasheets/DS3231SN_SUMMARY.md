# DS3231SN# — Extremely Accurate I2C RTC with Integrated TCXO

| Spec | Value |
|------|-------|
| Package | SOIC-16-300mil (wide body, 7.5×10.3mm, 1.27mm pitch) |
| Vcc range | 2.3 V – 5.5 V (VCC pin) |
| VBAT range | 2.3 V – 5.5 V (CR2032 backup battery) |
| Supply current (active) | 200 µA |
| Supply current (standby) | 0.84 µA (C9866 variant) / 100 nA (C722469 variant) |
| Accuracy | ±2 ppm (0–40°C), integrated TCXO — no external crystal needed |
| Interface | I2C, up to 400 kHz (Fast mode); address 0x68 (fixed) |
| Alarms | 2 programmable alarms (Alarm 1: seconds resolution; Alarm 2: minutes resolution) |
| Clock output | Programmable SQW/INT pin: 1 Hz, 1.024 kHz, 4.096 kHz, 8.192 kHz |
| Temperature sensor | On-chip, ±3°C accuracy, 0.25°C resolution |
| Time registers | Seconds, Minutes, Hours (12/24h), Day, Date, Month, Year (with century) |
| Features | Temperature compensation, backup power management, alarm output |
| Operating temp | -40°C to +85°C |
| LCSC# (BOM) | C131027 (verified as DS3231SN# from BOM; use C9866 DS3231SN#T&R as functional equivalent) |
| KiCad Footprint | `Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm` |
| Datasheet URL | https://www.lcsc.com/datasheet/lcsc_datasheet_2401031635_Analog-Devices-Inc--Maxim-Integrated-DS3231SN-T-R_C9866.pdf |

## Pinout (SOIC-16, 16 pads — 8 per side)

Note: The DS3231 only uses 8 of the 16 SOIC-16 pads. The remaining pads (5–12 on some pinning conventions, or per EasyEDA data pins 5–12) are NC.

| Pin | Name | Function |
|-----|------|----------|
| 1 | 32kHz | 32.768 kHz output (open-drain); connect 10 kΩ pull-up if used, otherwise leave floating |
| 2 | VCC | Main supply 2.3–5.5 V; bypass with 100 nF (C8) |
| 3 | INT/SQW | Interrupt / square wave output (open-drain, active LOW); connect to ESP32 GPIO if alarm used |
| 4 | RST | Active-LOW reset output (open-drain); can be left floating or pull up to VCC |
| 5–12 | NC | No connect |
| 13 | GND | Ground |
| 14 | VBAT | Battery input (CR2032 via BT1); 2.3–5.5 V; must NOT be left floating |
| 15 | SDA | I2C data (open-drain); requires external pull-up (R2 = 4.7 kΩ) |
| 16 | SCL | I2C clock (open-drain); requires external pull-up (R3 = 4.7 kΩ) |

## I2C Address

| A2 | A1 | A0 | 7-bit Address |
|----|----|----|---------------|
| — | — | — | 0x68 (fixed, not configurable) |

## Key Registers (I2C)

| Register | Address | Content |
|----------|---------|---------|
| Seconds | 0x00 | BCD seconds 00–59 |
| Minutes | 0x01 | BCD minutes 00–59 |
| Hours | 0x02 | BCD hours (12/24h mode) |
| Control | 0x0E | SQW freq, alarm enables, BBSQW |
| Status | 0x0F | OSF, alarm flags, 32kHz enable |
| Temp MSB | 0x11 | Temperature integer part (signed) |
| Temp LSB | 0x12 | Temperature fractional part (bits 7:6 = 0.25°C LSB) |

## Typical Application

```
VCC (3.3V) ──[C8 100nF]── pin2 VCC
                           │
                        DS3231SN
                           │
              pin13 GND ── GND plane
              pin14 VBAT ── CR2032 (+) via BT1
              pin15 SDA ──[R2 4.7kΩ]── 3.3V
              pin16 SCL ──[R3 4.7kΩ]── 3.3V
              pin3 INT/SQW: connect to ESP32 if alarm needed (open-drain, pull HIGH)
              pin1 32kHz: leave floating (not used in this design)
              pin4 RST: leave floating
```

## Notes

- VBAT pin must always have a connection — either to CR2032 (via BT1) or to VCC through a diode. Leaving it floating is not permitted per datasheet.
- The 32kHz output is open-drain; if unused leave floating (no pull-up needed when disabled — default state is disabled after power-on).
- INT/SQW is open-drain — pull-up to VCC required if used. This design can use it to wake ESP32 from light sleep for scheduled control.
- Power switch-over: DS3231 automatically switches to VBAT when VCC drops below VBAT. No external circuitry needed.
- Crystal is internal (TCXO) — no external crystal, load capacitors, or oscillator components needed.
- C8 (100 nF at VCC) is the only required bypass capacitor.
- See datasheet Table 2 for alarm register configuration.
