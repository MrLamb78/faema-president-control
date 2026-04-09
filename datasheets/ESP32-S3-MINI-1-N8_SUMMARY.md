# ESP32-S3-MINI-1-N8 — WiFi + BT5 MCU Module (Espressif)

| Spec | Value |
|------|-------|
| Package | SMD castellated module, 27.0 × 15.0 × 3.2 mm |
| Vcc / Vin range | 3.0 V – 3.6 V (3V3 pin) |
| SoC | ESP32-S3FN8 (Xtensa LX7 dual-core, 240 MHz) |
| Flash | 8 MB integrated (N8 variant) |
| PSRAM | None (N8; use N8R2 or N8R8 for PSRAM) |
| Wireless | 2.4 GHz 802.11 b/g/n WiFi + Bluetooth 5.0 LE |
| Antenna | On-board PCB antenna (no external antenna connector) |
| TX current | 330 mA peak |
| RX current | 97 mA |
| Sensitivity | -104.5 dBm |
| TX power | 20.5 dBm |
| Operating temp | -40°C to +85°C |
| GPIOs available | 36 (IO0–IO48, not all exposed on module pads) |
| ADC | 2× SAR 12-bit, up to 20 channels |
| Peripherals | SPI×4, I2C×2, UART×3, I2S×2, USB-OTG, USB-Serial/JTAG |
| LCSC# | C2913206 |
| Footprint | CUSTOM — use Espressif KiCad library: `Espressif_ESP32-S3-MINI-1_27x15mm` |
| Datasheet URL | https://www.lcsc.com/datasheet/lcsc_datasheet_2411121055_Espressif-Systems-ESP32-S3-MINI-1-N8_C2913206.pdf |

## Pinout (61 pads — castellated, left side top-to-bottom then right side)

### Left-side pads (pin 1 = top-left)

| Pin | Name | Function in this design |
|-----|------|------------------------|
| 1 | GND | Ground |
| 2 | GND | Ground |
| 3 | 3V3 | 3.3 V power supply input |
| 4 | IO0 | (Boot mode strap — pull high for normal boot) |
| 5 | IO1 | General GPIO |
| 6 | IO2 | LED_STATUS → R10 (470 Ω) → D1 green LED |
| 7 | IO3 | MAX_DRDY — DRDY# from MAX31865 U4 (boiler), active LOW |
| 8 | IO4 | SSR_CTRL — SSR-40DA control via R7 (100 Ω series), R9 pull-down |
| 9 | IO5 | ENC_CLK — EC11 encoder CLK |
| 10 | IO6 | ENC_DT — EC11 encoder DT |
| 11 | IO7 | ENC_SW — EC11 encoder push switch |
| 12 | IO8 | I2C_SDA — DS3231 SDA (R2 4.7 kΩ pull-up to 3.3 V) |
| 13 | IO9 | I2C_SCL — DS3231 SCL (R3 4.7 kΩ pull-up to 3.3 V) |
| 14 | IO10 | SPI_SCK — shared SPI clock (MAX31865 × 2 + GC9A01 display) |
| 15 | IO11 | SPI_MOSI — shared SPI data out |
| 16 | IO12 | SPI_MISO — shared SPI data in (MAX31865 only; GC9A01 has no MISO) |
| 17 | IO13 | CS_MAX — chip select MAX31865 U4 (boiler), active LOW |
| 18 | IO14 | CS_DISP — chip select GC9A01 display |
| 19 | IO15 | DC_DISP — GC9A01 data/command select |
| 20 | IO16 | RST_DISP — GC9A01 reset |
| 21 | IO17 | LEVEL_SENSE — water level probe (R11 100 kΩ pull-up) |
| 22 | IO18 | CS_MAX2 — chip select MAX31865 U6 (group), active LOW |
| 23 | IO19 | BTN1 — preset button 1 (R12 10 kΩ pull-up, active LOW) |
| 24 | IO20 | BTN2 — preset button 2 (R13 10 kΩ pull-up, active LOW) |
| 25 | IO21 | BTN3 — preset button 3 (R14 10 kΩ pull-up, active LOW) |

### Right-side / bottom pads

| Pin | Name | Function |
|-----|------|----------|
| 26 | IO26 | Not used |
| 27 | IO47 | Not used |
| 28 | IO33 | Not used |
| 29 | IO34 | Not used |
| 30 | IO48 | Not used |
| 31 | IO35 | Not used |
| 32 | IO36 | Not used |
| 33 | IO37 | Not used |
| 34 | IO38 | Not used |
| 35 | IO39 | Not used |
| 36 | IO40 | Not used |
| 37 | IO41 | Not used |
| 38 | IO42 | Not used |
| 39 | TXD0 | UART0 TX (USB-Serial debug) |
| 40 | RXD0 | UART0 RX (USB-Serial debug) |
| 41 | IO45 | Not used (strap: leave floating) |
| 42–60 | GND | Exposed ground pads (bottom paddle and edge) |
| 44 | IO46 | Not used |
| 45 | EN | Enable / reset (active HIGH; add RC to ensure clean power-on) |

## Strap pins (boot configuration)

| GPIO | State at boot | Effect |
|------|---------------|--------|
| IO0 | HIGH (pull-up) | Normal boot from flash |
| IO0 | LOW (pull-down) | ROM download mode (programming) |
| IO45 | Leave floating | Default flash voltage 3.3 V |
| IO46 | Leave floating | Normal operation |

## Notes

- Supply current: 330 mA peak during WiFi TX; design 5 V rail for ≥500 mA, AMS1117-3.3 rated 1 A — adequate.
- Decoupling: 100 nF (C9) at 3V3 pin; add 10 µF bulk if not already nearby.
- IO0 boot strap: connect 10 kΩ pull-up to 3.3 V; may need button to GND for programming.
- SPI note: MAX31865 uses Mode 1 or 3 (CPOL=0/1, CPHA=1) at 5 MHz; GC9A01 uses Mode 0 at up to 80 MHz — reconfigure SPI bus between accesses.
- EN pin: add 10 kΩ pull-up + 100 nF RC filter for reliable reset; omitting causes unreliable boot.
- Custom footprint required: import `Espressif_ESP32-S3-MINI-1_27x15mm` from https://github.com/espressif/kicad-libraries
- See ESP32-S3-MINI-1 datasheet Hardware Design Guidelines Section 4 for recommended decoupling and antenna keep-out.
