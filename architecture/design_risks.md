# Faema President Control — Design Risks

**Circuit:** `faema_president_control`
**Revision:** Rev.4 (SKiDL migration)

This document captures foreseeable risks for the pipeline, layout, firmware, and field operation. Ordered by severity.

---

## 1. HIGH: AC mains isolation and clearance

**Risk:** Insufficient creepage between 220 VAC nets and DC logic would fail any safety inspection and can arc over humid conditions in a commercial kitchen.

**Mitigations:**
- **6 mm minimum** clearance between any AC net (`AC_L`, `AC_N`, `AC_SSR_L_IN`, `AC_SSR_L_OUT`) and any DC net. Enforced at layout time.
- Slot-milled isolation gap between AC and DC islands under HLK-PM05 and under the SSR header.
- HLK-PM05 and SSR-40DA provide the formal reinforced isolation barrier (3 kV and 2.5 kV respectively).
- C6 (snubber) must be X1/X2 safety rated — no substitution with generic X7R.
- AC copper only on bottom layer; all DC signal routing on top.
- Silkscreen legend "HIGH VOLTAGE" on the AC island.

**Verification at layout stage:** use KiCad DRC with a custom rule `(rule "ac_clearance" (constraint clearance (min 6mm)) (condition "A.NetClass == 'AC' && B.NetClass != 'AC'"))`. SKiDL does not enforce this — it is a layout rule.

---

## 2. HIGH: SSR gate drive stuck-on during ESP32 boot

**Risk:** If GPIO4 floats during ESP32 boot, SSR could briefly energise the boiler. With no water this damages the heating element.

**Mitigations:**
- **R9 = 10 kΩ pull-down** on GPIO4 — net `SSR_CTRL` — guarantees 0 V at SSR+ until firmware explicitly drives HIGH.
- R7 = 100 Ω series limits fault current even if GPIO and pull-down fight each other.
- ESP32-S3 strapping pins: GPIO4 is not a strap pin on S3, safe to use.
- Firmware watchdog (SPEC §6.3) disables SSR on fault.
- Level-probe override (SPEC §6.3) forces SSR OFF on any low-water reading.

**Verification:** ERC must show `SSR_CTRL` reaches both R7 and R9. Bench test at bring-up: measure GPIO4 with boot loop 10x — no spike > 100 mV.

---

## 3. HIGH: MAX31865 — no drop-in substitute

**Risk:** Supply disruption of MAX31865 halts the whole design. The architecture depends on two of these; there is no alternative RTD-to-digital IC with the same interface and pinout in LCSC Basic/Preferred tier.

**Mitigations:**
- Sourcer must escalate on stock < 4 pcs (2× design qty for safety stock).
- On escalation, architect revision would move to ADS1220 + external bridge network, which is a block-diagram rewrite. Budget: ~4 h of rework.
- Optionally stock a few MAX31865 as spares outside the JLC PCBA order (user-soldered).

---

## 4. MEDIUM: AMS1117 thermal dissipation

**Risk:** 5 V → 3.3 V @ 500 mA = 850 mW dissipation in SOT-223. Without copper pour, junction could exceed 125 °C in a hot espresso machine enclosure (ambient ~50 °C).

**Mitigations:**
- Minimum 150 mm² 1 oz copper pour on GND tab of U3 (per datasheet θ_JA ≈ 50 °C/W with that copper).
- Typical current is ~200 mA average (ESP32 idle + peripherals idle), peaks to ~350 mA during Wi-Fi TX; 500 mA is worst-case.
- Consider a 5 V → 3.3 V buck in a future revision if thermal margin is tight.
- Do **not** place AMS1117 directly next to HLK-PM05 — HLK dissipates 1 W + its own heat.

---

## 5. MEDIUM: SPI bus sharing (MAX31865 modes 1/3 vs GC9A01 mode 0)

**Risk:** The SPI bus is shared between two MAX31865 (SPI mode 1 or 3, 5 MHz max) and GC9A01 (SPI mode 0, up to 80 MHz). Transactions must reconfigure the peripheral each switch. Race conditions or a missed mode change can corrupt RTD readings or glitch the display.

**Mitigations:**
- Firmware uses a mutex around the SPI peripheral and always sets mode + clock before asserting CS.
- CS lines are independent (CS_MAX, CS_MAX2, CS_DISP) so there is no multiplex hardware risk.
- PCB layout: keep SCK trace short and matched; series termination (0 Ω footprint) near ESP32 if ringing is seen.
- Display SPI clock runs at 40 MHz in practice (not 80) to keep ringing low on shared bus.

**Verification:** Firmware test routine cycles all three devices at max rate for 10 minutes and verifies CRC on display and RTD readings.

---

## 6. MEDIUM: DS3231 backup battery reverse / leakage

**Risk:** CR2032 miswired (reversed) or unprotected can cause back-feed into DS3231 VCC or slow leakage across VBAT.

**Mitigations:**
- Use DS3231's internal battery-switching (VBAT pin) — external diode is unnecessary and in fact discouraged by datasheet.
- Battery holder polarity silkscreen marking.
- Series 1 kΩ current limit on VBAT rail (optional, datasheet does not require it).

---

## 7. MEDIUM: Level probe electrolysis

**Risk:** DC current on the boiler conductivity probe electrolyses the water and corrodes the probe tip over months.

**Mitigations:**
- R11 = 100 kΩ pull-up → probe current is ~33 µA max.
- Firmware pulses the read (drives GPIO17 as output LOW briefly, releases to input with pull-up, samples, then floats) → duty cycle < 1 %.
- Effective DC current on probe < 1 µA average.

---

## 8. LOW: Encoder debounce

**Risk:** EC11 encoder mechanical contact bounce at high-speed rotation can produce phantom counts.

**Mitigations:**
- Firmware uses a state-machine debounce (Gray-code filtering).
- Optionally add 100 nF parallel caps on ENC1.A and ENC1.B — not on current skeleton BOM, but the SKiDL coder may add them if ERC/user requests.

---

## 9. LOW: Display FPC mechanical stress

**Risk:** The 24-pin 0.5 mm FPC tail on the GC9A01 module is fragile; repeated flexing can fracture the ribbon.

**Mitigations:**
- Mount the display to the front panel with the ribbon looped once and strain-relieved.
- Use a locking FPC connector (flip-lock type). Non-locking connectors are also acceptable.
- Document in the assembly guide.

---

## 10. LOW: HLK-PM05 EMI radiation

**Risk:** HLK-PM05 is a switching AC/DC converter. Its 65 kHz primary switching radiates conducted noise that can show up on the 5 V rail and on the MAX31865 readings.

**Mitigations:**
- C1 (10 µF bulk) + C3 (100 nF) on the HLK-PM05 output is a mandatory RC filter.
- Optional: add a common-mode choke on the HLK-PM05 output if bench tests show > 50 mV ripple.
- MAX31865 has an internal 50 Hz filter and high input impedance — relatively immune.
- Physical separation: keep HLK-PM05 at least 15 mm from U4/U6 on the layout.

---

## 11. Layout / manufacturing notes (not risks per se, but captured)

- JLCPCB PCBA limitations: HLK-PM05, SSR header, fuse holder, MOV, encoder, screw terminals, PT100 headers, CR2032 holder, and C6 safety cap are all THT or non-LCSC → user-soldered post-assembly.
- SMD side (bottom or top, user's choice) holds U1, U3, U4, U5, U6, all 0603/0805 passives, J5 FPC, D1.
- Recommend front-panel orientation: display J5 on top-left, encoder in center-top, preset buttons panel below, AC input at back.

---

## 12. Pipeline-stage risks (for the orchestrator)

- **Sourcing stage:** MAX31865 and 430 Ω 0.1 % are the two most likely escalation triggers.
- **Coding stage:** 10 blocks → modular mode (per orchestrator rule §5b). Block-level error attribution for ERC failures will keep retry budget bounded.
- **ERC stage:** Expected clean bill of health. Floating-pin warnings on U6.DRDY and ESP32 unused IOs must be explicitly NC'd by the coder.
- **Netlist export:** Only after ERC PASS. Rev.4 .kicad_sch is preserved in git history for reference but SKiDL becomes the source of truth going forward.
