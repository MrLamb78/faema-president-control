# HLK-PM05 — 3W Isolated AC/DC Power Module, 5V/600mA Output

| Spec | Value |
|------|-------|
| Package | THT brick module, 33.5 × 20.5 × 15.0 mm |
| Input voltage | 85–265 V AC (universal input) |
| Input frequency | 47–63 Hz |
| Output voltage | 5.0 V DC (±5%) |
| Output current | 600 mA rated, 1000 mA peak |
| Output power | 3 W rated |
| Efficiency | ~70% (typical at full load) |
| Isolation voltage | 3000 V AC (input to output) |
| Ripple & noise | ≤100 mV p-p (typical) |
| Load regulation | ±5% |
| Short circuit protection | Yes (auto-recovery) |
| Operating temp | -40°C to +70°C |
| Connector pitch | 2-pin AC input: ~7.5 mm pitch; 2-pin DC output: ~7.5 mm pitch (4-pin inline, 15.24 mm row pitch) |
| KiCad Footprint | CUSTOM — Hi-Link community footprint `HLK-PM05` or import from Hi-Link website |
| LCSC# | C2834907 — NOTE: This LCSC# resolves to a tactile switch in LCSC database; HLK-PM05 is non-LCSC, hand-soldered by user |
| Manufacturer | Hi-Link (Shenzhen Hilink Electronics) |

## Pin Layout (4-pin THT, viewed from top)

```
  ┌─────────────────────────────┐
  │   HLK-PM05  (top view)      │
  │                             │
  │  [VIN-]  [VIN+]  [VO+] [VO-]│  ← 4 pins in a line
  └─────────────────────────────┘
     Pin1    Pin2    Pin3  Pin4
     (N/L)   (L/N)   5V    GND
```

| Pin | Name | Function |
|-----|------|----------|
| 1 | AC-N (or L) | AC input Live or Neutral (either AC terminal — polarity insensitive for AC) |
| 2 | AC-L (or N) | AC input Neutral or Live |
| 3 | VO+ | DC output +5 V |
| 4 | VO- | DC output GND (0 V reference) |

Note: The exact pin ordering (which of pin 1/2 is L vs N) may vary by production batch — both are AC and are polarity-insensitive for the AC input. Always verify against the silkscreen on the module.

## Connection in This Design

```
J1 (AC screw terminal) ──── HLK-PM05 AC pins (L and N)
HLK-PM05 VO+ (5V) ──[C1 10µF + C3 100nF]──── AMS1117-3.3 VIN (U3)
HLK-PM05 VO- (GND) ─────── Power GND plane

Safety:
  RV1 (MOV S14K275) across L–N at J1 (before HLK-PM05 input)
  F1 (T16A fuse) in series with L line
```

## Notes

- The HLK-PM05 includes internal EMI filtering (inductor + X capacitor). The C6 X2 safety cap was removed from this design since the HLK-PM05 provides internal filtering.
- Minimum 6 mm PCB clearance between AC traces (J1, RV1, F1) and DC output traces.
- The module body sits above the PCB; ensure no components within the module footprint.
- BOM LCSC# C2834907 is incorrect (resolves to a switch) — this part is hand-sourced by the user. Order directly from Hi-Link or via AliExpress/Amazon.
- Maximum continuous output current is 600 mA. Total load: AMS1117 input (~350 mA / 0.7 efficiency = ~500 mA) — within rating. Do not add other 5V loads.
- See Hi-Link product page: https://www.hlktech.com/en/Goods-16.html
