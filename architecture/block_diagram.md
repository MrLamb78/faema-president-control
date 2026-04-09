# Faema President Control — Block Diagram

**Circuit:** `faema_president_control`
**Revision:** Rev.4 (SKiDL migration from existing KiCad Rev.4)
**Architect pass:** initial
**Source of truth going forward:** SKiDL (replaces `kicad/*.kicad_sch`)

---

## 1. High-level block diagram

```mermaid
flowchart LR
    subgraph AC["AC side (220 VAC, 6 mm creepage)"]
        J1[J1 AC input<br/>L / N / PE]
        F1[F1 T16A<br/>slow-blow]
        RV1[RV1 S14K275<br/>MOV L-N]
        SNUB[R8 100R 1W<br/>+ C6 100nF X1/X2<br/>SSR snubber]
        SSR1[SSR1 Fotek SSR-40DA<br/>external + heatsink]
    end

    subgraph PSU["Isolated power"]
        HLK[U2 HLK-PM05<br/>220VAC to 5V<br/>3 kV isolated]
        BULK5[C1 10uF 0805<br/>C3 100nF 0603<br/>5 V bulk + ceramic]
        LDO[U3 AMS1117-3.3<br/>SOT-223]
        BULK33[C2 10uF 0805<br/>C4 100nF 0603<br/>3V3 bulk + ceramic]
    end

    subgraph MCU["MCU and system"]
        ESP[U1 ESP32-S3 Mini<br/>module, USB-C native]
        C9[C9 100nF<br/>ESP32 VDD]
        LED[D1 green LED<br/>+ R10 470R<br/>GPIO2 STATUS]
    end

    subgraph SENSE["Temperature sensing (SPI)"]
        U4[U4 MAX31865 SSOP-20<br/>BOILER]
        R4[Rref 430R 0.1%]
        C7[C7 100nF RTDIN filter]
        C10[C10 100nF VDD]
        J3[J3 4-wire PT100<br/>boiler]

        U6[U6 MAX31865 SSOP-20<br/>GROUP]
        R5[Rref2 430R 0.1%]
        C11[C11 100nF RTDIN filter]
        C12[C12 100nF VDD]
        J6[J6 4-wire PT100<br/>group]
    end

    subgraph RTC["RTC"]
        U5[U5 DS3231 SO-16<br/>I2C 0x68]
        C8[C8 100nF VCC]
        PU[R2 R3 4.7k<br/>I2C pull-ups]
        BT1[BT1 CR2032<br/>VBAT backup]
    end

    subgraph DISP["Display (SPI, no MISO)"]
        J5[J5 GC9A01 FPC<br/>240x240 1.28in]
    end

    subgraph UI["User I/O"]
        ENC1[ENC1 EC11<br/>quad + push]
        J8[J8 preset buttons<br/>BTN1..3 + 3V3 + 2xGND]
        PU2[R12 R13 R14 10k<br/>button pull-ups]
        J7[J7 level probe<br/>conductivity]
        R11[R11 100k<br/>pull-up to 3V3]
    end

    subgraph DRV["SSR drive"]
        R7[R7 100R series<br/>GPIO4 to SSR+]
        R9[R9 10k pull-down<br/>GPIO4 to GND]
    end

    J1 --> F1 --> HLK
    J1 --> RV1
    HLK --> BULK5 --> LDO --> BULK33
    LDO --> ESP
    BULK33 --> U4 & U6 & U5 & J5 & ENC1 & J8 & J7

    ESP -- SPI SCK/MOSI/MISO --> U4 & U6
    ESP -- SPI SCK/MOSI --> J5
    ESP -- GPIO13 CS --> U4
    ESP -- GPIO18 CS --> U6
    ESP -- GPIO14/15/16 CS DC RST --> J5
    ESP -- GPIO3 DRDY --> U4
    ESP -- I2C GPIO8/9 --> U5
    ESP -- GPIO2 --> LED
    ESP -- GPIO4 --> R7 --> SSR1
    R9 -. keeps OFF .- R7
    ESP -- GPIO5/6/7 --> ENC1
    ESP -- GPIO19/20/21 --> J8
    ESP -- GPIO17 --> J7

    SSR1 --- SNUB
    U4 --- R4 & C7 & C10 & J3
    U6 --- R5 & C11 & C12 & J6
    U5 --- C8 & PU & BT1
```

---

## 2. Functional block list (for modular coding stage)

| # | block_id | description | primary parts | AC/DC domain |
|---|----------|-------------|---------------|--------------|
| 1 | `ac_input_protection` | Mains entry, fuse, MOV, terminal block | J1, F1, RV1 | AC (isolated island) |
| 2 | `power_5v`            | HLK-PM05 AC/DC module + bulk | U2, C1, C3 | AC in / DC out (isolated barrier inside U2) |
| 3 | `power_3v3`           | AMS1117 LDO + bulk | U3, C2, C4 | DC |
| 4 | `mcu_esp32s3`         | ESP32-S3 Mini module + VDD bypass | U1, C9 | DC |
| 5 | `temp_sense_boiler`   | MAX31865 + Rref + caps + PT100 header | U4, Rref, C7, C10, J3 | DC |
| 6 | `temp_sense_group`    | MAX31865 + Rref2 + caps + PT100 header | U6, Rref2, C11, C12, J6 | DC |
| 7 | `rtc_ds3231`          | DS3231 + backup battery + I2C pull-ups + bypass | U5, R2, R3, C8, BT1 | DC |
| 8 | `display_gc9a01`      | FPC header for round IPS display | J5 | DC |
| 9 | `user_io`             | Encoder, preset buttons, level probe, status LED | ENC1, J8, R12, R13, R14, J7, R11, D1, R10 | DC |
| 10 | `ssr_drive_snubber`  | GPIO4 drive, pull-down, series R, RC snubber, external SSR header | R7, R9, R8, C6, SSR1 header | mixed (R7/R9 DC side; R8/C6 AC side with 6 mm clearance) |

**Total blocks = 10.** Per orchestrator rules (§Coding Mode Decision, step 5b): `block_count > 3` → **modular mode** will be used at the coding stage. Block IDs above are the canonical filenames for `circuits/faema_president_control/*.py`.

---

## 3. Bus summary

| Bus | Members | Speed / mode | Notes |
|-----|---------|--------------|-------|
| SPI | U1 master, U4 + U6 + J5 (GC9A01) slaves | MAX31865 mode 1/3 @ <= 5 MHz, GC9A01 mode 0 @ up to 80 MHz | Firmware reconfigures mode per transaction. GC9A01 does not use MISO. |
| I2C | U1 master, U5 slave (0x68) | Standard 100 kHz (fast 400 kHz OK) | 4.7 kOhm pull-ups to 3V3 (R2/R3) |
| Discrete GPIO | LED, SSR gate, encoder, buttons, level probe, DRDY, CS, DC, RST | DC | See net_plan.md |

---

## 4. AC/DC isolation strategy

- **AC island** = J1, F1, RV1, HLK-PM05 primary, R8+C6 snubber, SSR1 header terminals (the SSR output terminals, not the DC-side control pins).
- **DC island** = everything else, referenced to GND.
- Isolation barrier = HLK-PM05 (3 kV reinforced) + SSR-40DA optocoupler (2.5 kV typical).
- **Minimum creepage 6 mm** between any AC net and any DC net, enforced at layout time. All AC copper on bottom layer, slot-routed where it crosses DC.
- The SSR control side (GPIO4 via R7/R9) is DC. The SSR output side (AC hot to boiler) is AC and lives entirely on the AC island.

See `design_risks.md` for layout, EMI, and thermal risks.
