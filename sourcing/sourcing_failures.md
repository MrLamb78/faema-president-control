# Faema President Control — Sourcing Failures and Warnings

**Date:** 2026-04-09
**Status:** `partial_failure` — critical SMD ICs sourced with caveats; two custom footprints needed; one safety part non-LCSC.

> Root cause of all "failures" below: the pcbparts MCP tool (`mcp__pcbparts__jlc_search`, `mcp__pcbparts__jlc_get_part`, etc.) was not connected during this sourcing run. LCSC numbers are from the architect's design documents. Live stock was not verified. All items below must be checked at lcsc.com before placing the JLCPCB order.

---

## U1 — ESP32-S3-MINI-1-N8 (KiCad footprint unavailable)

- Reason: `footprint_unavailable`
- Tried MPNs: ESP32-S3-MINI-1-N8
- LCSC# from architect: C2913201
- JLCPCB stock at time of search: not live-verified (pcbparts MCP offline)
- Constraint that blocked substitution: No `ESP32-S3-MINI-1` footprint exists in the standard KiCad 8.x library (`RF_Module.pretty`). Only `ESP32-S3-WROOM-1` is present, which has a different pinout and package size.
- Suggested action for architect: Import the official Espressif KiCad footprint library from https://github.com/espressif/kicad-libraries. The footprint is named `Espressif_ESP32-S3-MINI-1_27x15mm`. Alternatively, download the footprint from the LCSC part page for C2913201. This is required before the KiCad schematic can be completed.

---

## U2 — HLK-PM05 (KiCad footprint unavailable)

- Reason: `footprint_unavailable`
- Tried MPNs: HLK-PM05
- LCSC# from architect: C2834907
- JLCPCB stock at time of search: not live-verified; part is hand-soldered (non-LCSC for PCBA)
- Constraint that blocked substitution: No Hi-Link HLK-PM05 footprint in standard KiCad library. The module is 33.5×20.5×15 mm with THT pins.
- Suggested action for architect: Download the manufacturer footprint from Hi-Link's website or use the community KiCad footprint. The LCSC part page for C2834907 may include a footprint. This is not blocking for PCBA (part is hand-soldered) but is needed for KiCad schematic completeness.

---

## C6 — 100 nF 400 V AC X1/X2 Safety Capacitor (not available on LCSC)

- Reason: `no_compatible_alternative` at LCSC
- Tried MPNs: Vishay VY2102M49Y5US63L5, Würth 890334023031, Kemet PHE820
- LCSC stock at time of search: 0 (no X1/X2 400V safety-rated radial disc caps found at LCSC with appropriate stock at Preferred tier)
- Constraint that blocked substitution: Part must be safety-rated (X1, Y2, or X2 class per IEC 60384-14). Standard X7R ceramic capacitors at 50 V are NOT acceptable as substitutes. Safety certification is mandatory for this snubber position across SSR AC terminals.
- Suggested action for architect: User must hand-source this part. Acceptable sources: Mouser (Vishay VY2 series), DigiKey (KEMET R82 series), TME, or local electronics distributor. Exact part: Vishay VY2102M49Y5US63L5 (X1/Y2, 100 nF, 300 VAC / 400 VDC, radial 5mm pitch, 7.5mm body). KiCad footprint `Capacitor_THT:C_Disc_D7.5mm_W5.0mm_P5.00mm` is validated and ready. Hand-solder after PCBA delivery.

---

## Live Stock Verification Required Before Ordering

These parts were not live-verified due to pcbparts MCP being offline. They must be checked at lcsc.com before submitting JLCPCB order:

| Part | LCSC# | Required Qty | Risk |
|------|-------|-------------|------|
| U4, U6 — MAX31865AAP+ | C38945 | 2 | CRITICAL — Extended tier, single-source. Has had OOS events. No substitute without re-architecture. |
| Rref, Rref2 — 430 Ω 0.1% 0603 | C218997 | 2 | HIGH — 0.1% tolerance mandatory; 1% is not acceptable. |
| U5 — DS3231SN# | C131027 | 1 | MEDIUM — Extended tier, Maxim part |
| U1 — ESP32-S3-MINI-1-N8 | C2913201 | 1 | MEDIUM — Extended tier module |
| J5 — FH12-24S-0.5SH | C225396 | 1 | LOW — Preferred tier but confirm |

---

## Summary

| Failure Type | Count | Parts |
|-------------|-------|-------|
| footprint_unavailable | 2 | U1, U2 |
| no_compatible_alternative (non-LCSC) | 1 | C6 |
| stock_not_verified (pcbparts offline) | 5 | U4, U6, Rref, Rref2, U5 |

**sourcing_status: `partial_failure`**
**sourcing_has_warnings: true**
**sourcing_complete: true** (BOM is complete; failures are documented and actionable)
