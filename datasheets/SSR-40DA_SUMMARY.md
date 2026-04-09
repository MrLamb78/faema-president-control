# SSR-40DA — 40A DC-to-AC Solid State Relay (Fotek / generic)

| Spec | Value |
|------|-------|
| Type | Single-phase DC control, AC load, zero-crossing |
| Control input voltage | 3–32 V DC |
| Control input current | ~7.5 mA @ 12 V (typical) |
| Load voltage | 24–480 V AC |
| Load current | 40 A rated (continuous, with heatsink) |
| Surge current | 410 A (1 cycle, non-repetitive) |
| On-state voltage drop | ~1.5 V @ 40 A |
| Off-state leakage | <10 mA |
| Isolation voltage | 2500 V AC (control to load) |
| Zero-crossing | Yes (trigger at zero crossing of AC waveform) |
| Status LED | Input-side LED indicator |
| Operating temp | -30°C to +80°C (with heatsink) |
| Package | External DIN-rail or screw-mount module (not on PCB) |
| Dimensions | Approx. 62 × 45 × 28 mm (standard Fotek SSR-25/40 body) |
| Heatsink | Required at loads above ~10 A; use aluminum plate ≥100 cm² |

## Terminal Layout (4 screw terminals)

```
  ┌─────────────────────────────────┐
  │           SSR-40DA              │
  │                                 │
  │  [3] ──── [4]     [1] ─── [2]  │
  │  AC L      AC N   DC+     DC-  │
  │  (Load)  (Load)  (Ctrl+) (Ctrl-)│
  └─────────────────────────────────┘
```

| Terminal | Label | Function |
|----------|-------|----------|
| 1 | DC+ / IN+ | Control positive (+3–32 V DC) |
| 2 | DC- / IN- | Control negative (GND) |
| 3 | AC / LOAD | AC load terminal (Line) |
| 4 | AC / LOAD | AC load terminal (Neutral) |

Note: The exact labeling may differ by manufacturer. Common markings: 3/4 = AC output (load), 1/2 = DC input (control). Always verify silkscreen on the physical unit.

## Connection in This Design

```
ESP32-S3 IO4 ──[R7 100Ω]──── SSR terminal 1 (DC+/IN+)
GND ────────────[R9 10kΩ pulldown on IO4]
GND ──────────────────────── SSR terminal 2 (DC-/IN-)

SSR terminal 3 ──── Boiler heating element (L)
SSR terminal 4 ──── Neutral (N)
                         ↑ AC mains, protected by F1 fuse + RV1 MOV
```

R7 (100 Ω) limits inrush to the LED optocoupler inside the SSR.
R9 (10 kΩ) pull-down ensures SSR stays OFF during ESP32 boot (GPIO4 is low-impedance floating during early boot).

## Control Logic

| ESP32 GPIO4 | SSR State |
|-------------|-----------|
| HIGH (3.3 V) | ON (AC load energized) |
| LOW (0 V) | OFF (AC load de-energized) |
| Floating (boot) | OFF (R9 holds LOW) |

## Notes

- SSR-40DA is external to the PCB — only J9 (2-pin 5.08 mm screw terminal) is on the PCB for control wires.
- Minimum control voltage is 3 V DC — ESP32 3.3 V output (GPIO4) is sufficient without level shifting.
- Heatsink is mandatory for boiler duty cycle > 20%; typical espresso machine duty cycle is 30–60%.
- Zero-crossing switching eliminates EMI spikes at turn-on/turn-off — compatible with SSR operating at 50 Hz mains.
- The SSR-40DA is rated for 40 A; the boiler heating element is typically 1000–1400 W at 230 V = 4.3–6.1 A. Headroom is adequate.
- If substituting with another SSR: control input must accept 3.3 V DC logic HIGH as ON signal.
- Datasheet source: https://handsontec.com/dataspecs/discrete/SSR-40DA.pdf
