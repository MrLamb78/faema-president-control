#!/usr/bin/env python3
"""
faema_carrier.py — Carrier board (backplane) for Faema President controller.

Rev.6b: Headers for plug-in modules + power supply + passives.
  - Raspberry Pi Pico 2 W (MCU, 2x20 socket)
  - 2x Playing with Fusion SEN-30201 (MAX31865 RTD breakout, 1x8 socket)
  - 2x NTC 10k on GP26/GP27 — works simultaneously with RTD
  - Nextion NX3224T024 display (UART, JST XH 4-pin)
  Optional: SPI display (JST XH 8-pin), DS3231 RTC (JST XH 4-pin).

Connector types:
  Power/SSR:    Phoenix MKDS 5.08mm screw terminal (J1, J2)
  Plug-in PCBs: 2.54mm pin socket (J11, J12 Pico; J13, J14 RTD breakouts)
  External cable: JST XH 2.5mm keyed (J3–J10)

NTC circuit (J9/J10 + R8/R9 + C5/C6) — funciona simultaneamente com RTD:
  3V3 → R_ref(2k2 0.1%) → GP26/GP27 → NTC(10k) → GND
  C5/C6 (100nF) filtro passa-baixo em paralelo com NTC (ADC → GND).
  Range útil: 25°C→2.70V, 85°C→1.08V, 128°C→0.56V (ref 2k2, NTC 10k).

Usage:
    python3 circuits/faema_carrier.py

Generates: outputs/faema_carrier.net
"""

import os
from skidl import *

# ---------------------------------------------------------------------------
# KiCad symbol library path (macOS)
# ---------------------------------------------------------------------------
KICAD_SYM_DIR = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols'
lib_search_paths[KICAD] = [KICAD_SYM_DIR, '.']
os.environ.setdefault('KICAD8_SYMBOL_DIR', KICAD_SYM_DIR)


# ---------------------------------------------------------------------------
# Component templates (SKIDL tool — independent of KiCad libs)
# ---------------------------------------------------------------------------
def _make_passive_2pin(name, footprint):
    p = Part(tool=SKIDL, name=name, footprint=footprint, dest=TEMPLATE)
    p += [Pin(num=1, name='~', func=Pin.types.PASSIVE),
          Pin(num=2, name='~', func=Pin.types.PASSIVE)]
    return p

_R      = _make_passive_2pin('R', 'Resistor_SMD:R_0603_1608Metric')
_C_0603 = _make_passive_2pin('C', 'Capacitor_SMD:C_0603_1608Metric')
_C_0805 = _make_passive_2pin('C', 'Capacitor_SMD:C_0805_2012Metric')

_LED = Part(tool=SKIDL, name='LED', footprint='LED_SMD:LED_0603_1608Metric',
            dest=TEMPLATE)
_LED += [Pin(num=1, name='A', func=Pin.types.PASSIVE),
         Pin(num=2, name='K', func=Pin.types.PASSIVE)]

def _make_conn(n_pins, footprint):
    c = Part(tool=SKIDL, name=f'Conn_{n_pins}', footprint=footprint, dest=TEMPLATE)
    c += [Pin(num=i, name=str(i), func=Pin.types.PASSIVE)
          for i in range(1, n_pins + 1)]
    return c

# Power connectors — Phoenix MKDS 5.08mm screw terminal
_TB2 = _make_conn(2, 'TerminalBlock_Phoenix:'
                     'TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal')
_TB3 = _make_conn(3, 'TerminalBlock_Phoenix:'
                     'TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal')

# Cable connectors — JST XH 2.5mm keyed (external cables)
_JXH2 = _make_conn(2, 'Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical')
_JXH4 = _make_conn(4, 'Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical')
_JXH5 = _make_conn(5, 'Connector_JST:JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical')
_JXH8 = _make_conn(8, 'Connector_JST:JST_XH_B8B-XH-A_1x08_P2.50mm_Vertical')

# Module sockets — 2.54mm female (plug-in PCBs)
_PS8  = _make_conn(8,  'Connector_PinSocket_2.54mm:PinSocket_1x08_P2.54mm_Vertical')
_PS20 = _make_conn(20, 'Connector_PinSocket_2.54mm:PinSocket_1x20_P2.54mm_Vertical')


# ---------------------------------------------------------------------------
# Global nets
# ---------------------------------------------------------------------------

# Power
GND         = Net('GND')     # DC signal ground — isolated from PE
PE          = Net('PE')       # Protective earth — chassis only, NOT connected to GND
VCC5V       = Net('+5V')
VCC3V3      = Net('+3V3')
AC_L1_FUSED = Net('AC_L1_FUSED')
AC_L2_FUSED = Net('AC_L2_FUSED')

# SPI bus (shared: 2x RTD breakouts + optional SPI display)
SPI_SCK     = Net('SPI_SCK')
SPI_MOSI    = Net('SPI_MOSI')
SPI_MISO    = Net('SPI_MISO')
CS_RTD1     = Net('CS_RTD1')   # GP5 — caldeira
CS_RTD2     = Net('CS_RTD2')   # GP6 — grupo

# SPI display (option B — alternative to Nextion)
CS_DISP     = Net('CS_DISP')
DC_DISP     = Net('DC_DISP')
RST_DISP    = Net('RST_DISP')
DISP_LED    = Net('DISP_LED')

# UART (Nextion, option A)
UART_TX     = Net('UART_TX')
UART_RX     = Net('UART_RX')
UART_RX_5V  = Net('UART_RX_5V')

# I2C (optional DS3231)
I2C_SDA     = Net('I2C_SDA')
I2C_SCL     = Net('I2C_SCL')

# SSR drive
SSR_CTRL    = Net('SSR_CTRL')
SSR_DRIVE   = Net('SSR_DRIVE')
SSR_CTRL_P  = Net('SSR_CTRL_P')
GATE_DRIVE  = Net('GATE_DRIVE')

# Status LED
LED_STATUS  = Net('LED_STATUS')
LED_ANODE   = Net('LED_ANODE')

# Level probe
LEVEL_SENSE = Net('LEVEL_SENSE')

# Encoder
ENC_CLK     = Net('ENC_CLK')
ENC_DT      = Net('ENC_DT')
ENC_SW      = Net('ENC_SW')

# Buttons
BTN1        = Net('BTN1')
BTN2        = Net('BTN2')
BTN3        = Net('BTN3')

# NTC (optional — DNF when using RTD breakouts on J13/J14)
NTC1_ADC    = Net('NTC1_ADC')  # GP26/ADC0
NTC2_ADC    = Net('NTC2_ADC')  # GP27/ADC1


# ---------------------------------------------------------------------------
# BLOCK 1 — Power Supply
# ---------------------------------------------------------------------------
@subcircuit
def block_power():
    """J1 (AC bornier), RV1 (MOV), U1 (HLK-PM05), U2 (AMS1117), C1-C4.
    220V bifasica (L1+L2, sem neutro). Fusiveis T16A externos a PCB."""

    j1 = _TB3()
    j1.ref = 'J1'
    j1.value = 'AC_INPUT_220V'
    j1[1] += AC_L1_FUSED
    j1[2] += AC_L2_FUSED
    j1[3] += PE             # chassis earth — separate from DC GND

    rv1 = Part(tool=SKIDL, name='MOV',
               footprint='Varistor:RV_Disc_D15.5mm_W5mm_P7.5mm')
    rv1 += [Pin(num=1, name='1', func=Pin.types.PASSIVE),
            Pin(num=2, name='2', func=Pin.types.PASSIVE)]
    rv1.ref = 'RV1'
    rv1.value = 'S14K275'
    rv1[1] += AC_L1_FUSED
    rv1[2] += AC_L2_FUSED

    u1 = Part(tool=SKIDL, name='HLK_PM05',
              footprint='Converter_ACDC:Converter_ACDC_Hi-Link_HLK-PMxx')
    u1 += [Pin(num=1, name='AC_L',  func=Pin.types.PWRIN),
           Pin(num=2, name='AC_N',  func=Pin.types.PWRIN),
           Pin(num=3, name='VO_P',  func=Pin.types.PWROUT),
           Pin(num=4, name='VO_N',  func=Pin.types.PWROUT)]
    u1.ref = 'U1'
    u1.value = 'HLK-PM05'
    u1[1] += AC_L1_FUSED
    u1[2] += AC_L2_FUSED
    u1[3] += VCC5V
    u1[4] += GND

    c1 = _C_0805()
    c1.ref = 'C1'
    c1.value = '10uF_16V'
    c1[1] += VCC5V
    c1[2] += GND

    c3 = _C_0603()
    c3.ref = 'C3'
    c3.value = '100nF_50V'
    c3[1] += VCC5V
    c3[2] += GND

    u2 = Part(tool=SKIDL, name='AMS1117_3V3',
              footprint='Package_TO_SOT_SMD:SOT-223-3_TabPin2')
    u2 += [Pin(num=1, name='GND', func=Pin.types.PWRIN),
           Pin(num=2, name='VO',  func=Pin.types.PWROUT),
           Pin(num=3, name='VI',  func=Pin.types.PWRIN)]
    u2.ref = 'U2'
    u2.value = 'AMS1117-3.3'
    u2[1] += GND
    u2[2] += VCC3V3
    u2[3] += VCC5V

    c2 = _C_0805()
    c2.ref = 'C2'
    c2.value = '10uF_16V'
    c2[1] += VCC3V3
    c2[2] += GND

    c4 = _C_0603()
    c4.ref = 'C4'
    c4.value = '100nF_50V'
    c4[1] += VCC3V3
    c4[2] += GND


# ---------------------------------------------------------------------------
# BLOCK 2 — SSR Drive
# ---------------------------------------------------------------------------
@subcircuit
def block_ssr_drive():
    """Q1 (2N7002), R1 (220R), R2 (100R gate), R3 (10k pull-down), J2 (bornier).
    GP11 -> R2 -> Q1 gate -> drain -> SSR-.  5V -> R1 -> SSR+."""

    r1 = _R()
    r1.ref = 'R1'
    r1.value = '220R'
    r1[1] += VCC5V
    r1[2] += SSR_CTRL_P

    r2 = _R()
    r2.ref = 'R2'
    r2.value = '100R'
    r2[1] += SSR_CTRL
    r2[2] += GATE_DRIVE

    r3 = _R()
    r3.ref = 'R3'
    r3.value = '10k'
    r3[1] += GATE_DRIVE
    r3[2] += GND

    q1 = Part(tool=SKIDL, name='2N7002',
              footprint='Package_TO_SOT_SMD:SOT-23')
    q1 += [Pin(num=1, name='G', func=Pin.types.INPUT),
           Pin(num=2, name='S', func=Pin.types.PASSIVE),
           Pin(num=3, name='D', func=Pin.types.PASSIVE)]
    q1.ref = 'Q1'
    q1.value = '2N7002'
    q1[1] += GATE_DRIVE
    q1[2] += GND
    q1[3] += SSR_DRIVE

    j2 = _TB2()
    j2.ref = 'J2'
    j2.value = 'SSR_CTRL'
    j2[1] += SSR_CTRL_P
    j2[2] += SSR_DRIVE


# ---------------------------------------------------------------------------
# BLOCK 3 — Status LED
# ---------------------------------------------------------------------------
@subcircuit
def block_led():
    """D1 (green LED 0603) + R4 (470R). GP12 -> R4 -> D1 -> GND."""

    r4 = _R()
    r4.ref = 'R4'
    r4.value = '470R'
    r4[1] += LED_STATUS
    r4[2] += LED_ANODE

    d1 = _LED()
    d1.ref = 'D1'
    d1.value = 'GREEN'
    d1[1] += LED_ANODE
    d1[2] += GND


# ---------------------------------------------------------------------------
# BLOCK 4 — Level Probe
# ---------------------------------------------------------------------------
@subcircuit
def block_level_probe():
    """R5 (100k pull-up) + J5 (JST XH 2-pin). GP22 -> R5 -> 3V3; probe shorts to GND."""

    r5 = _R()
    r5.ref = 'R5'
    r5.value = '100k'
    r5[1] += VCC3V3
    r5[2] += LEVEL_SENSE

    j5 = _JXH2()
    j5.ref = 'J5'
    j5.value = 'LEVEL_PROBE'
    j5[1] += LEVEL_SENSE
    j5[2] += GND


# ---------------------------------------------------------------------------
# BLOCK 5 — UART Level Shifter (Nextion 5V -> Pico 3.3V)
# ---------------------------------------------------------------------------
@subcircuit
def block_uart_level_shift():
    """R6 (10k top) + R7 (15k bottom) voltage divider.
    Nextion TX (5V) -> R6 -> junction -> R7 -> GND.
    Junction = 5V * 15k/25k = 3.0V — safe for Pico (VIH = 2.31V)."""

    r6 = _R()
    r6.ref = 'R6'
    r6.value = '10k'
    r6[1] += UART_RX_5V
    r6[2] += UART_RX

    r7 = _R()
    r7.ref = 'R7'
    r7.value = '15k'
    r7[1] += UART_RX
    r7[2] += GND


# ---------------------------------------------------------------------------
# BLOCK 6 — Pull-ups (Buttons + Encoder)
# ---------------------------------------------------------------------------
@subcircuit
def block_pullups():
    """R10-R12 (10k) button pull-ups. R13-R15 (10k) encoder pull-ups."""

    for ref, net in [('R10', BTN1), ('R11', BTN2), ('R12', BTN3),
                     ('R13', ENC_CLK), ('R14', ENC_DT), ('R15', ENC_SW)]:
        r = _R()
        r.ref = ref
        r.value = '10k'
        r[1] += VCC3V3
        r[2] += net


# ---------------------------------------------------------------------------
# BLOCK 7 — NTC (works simultaneously with RTD breakouts on J13/J14)
# ---------------------------------------------------------------------------
@subcircuit
def block_ntc():
    """R8/R9 (2k2 0.1%) + C5/C6 (100nF) + C7 (100nF) + J9/J10 (JST XH 2-pin).
    3V3 -> R_ref(2k2) -> GP26/GP27 -> NTC(10k) -> GND.
    C5/C6 low-pass filter (100nF in parallel with NTC) reduces ADC noise.
    C7 (100nF): bypass on ADC_VREF (Pico pin 35), placed next to J12 pin 15.
    V_adc = 3.3V * R_NTC / (2200 + R_NTC):
      25°C (10k): 2.70V   85°C (1k07): 1.08V   128°C (~450R): 0.56V
    Use 0.1% resistor for R8/R9 to keep temperature error < 0.5°C.
    ADC_VREF tied to AMS1117 3V3 (ratiometric: supply variations cancel in NTC ratio)."""

    for r_ref, c_ref, j_ref, adc_net, label in [
        ('R8', 'C5', 'J9',  NTC1_ADC, 'NTC_CALDEIRA'),
        ('R9', 'C6', 'J10', NTC2_ADC, 'NTC_GRUPO'),
    ]:
        r = _R()
        r.ref = r_ref
        r.value = '2k2_0.1%'
        r[1] += VCC3V3
        r[2] += adc_net

        c = _C_0603()
        c.ref = c_ref
        c.value = '100nF_50V'
        c[1] += adc_net
        c[2] += GND

        j = _JXH2()
        j.ref = j_ref
        j.value = label
        j[1] += adc_net
        j[2] += GND

    # C7: local bypass on ADC_VREF (Pico pin 35) — place near J12 pin 15
    c7 = _C_0603()
    c7.ref = 'C7'
    c7.value = '100nF_50V'
    c7[1] += VCC3V3
    c7[2] += GND


# ---------------------------------------------------------------------------
# BLOCK 8 — Connectors
# ---------------------------------------------------------------------------
@subcircuit
def block_connectors():
    """Encoder, buttons, displays, I2C, Pico sockets, RTD breakout sockets."""

    # ── J3 — Encoder EC11 (JST XH 5-pin: CLK, DT, SW, 3V3, GND) ─────
    j3 = _JXH5()
    j3.ref = 'J3'
    j3.value = 'ENCODER'
    j3[1] += ENC_CLK
    j3[2] += ENC_DT
    j3[3] += ENC_SW
    j3[4] += VCC3V3
    j3[5] += GND

    # ── J4 — Buttons preset (JST XH 4-pin: BTN1, BTN2, BTN3, GND) ────
    j4 = _JXH4()
    j4.ref = 'J4'
    j4.value = 'BUTTONS'
    j4[1] += BTN1
    j4[2] += BTN2
    j4[3] += BTN3
    j4[4] += GND

    # ── J6 — Nextion display (JST XH 4-pin: 5V, GND, NX_TX, NX_RX) ──
    j6 = _JXH4()
    j6.ref = 'J6'
    j6.value = 'NEXTION'
    j6[1] += VCC5V
    j6[2] += GND
    j6[3] += UART_RX_5V    # Nextion TX -> divisor -> Pico GP1
    j6[4] += UART_TX        # Pico GP0 TX -> Nextion RX (3.3V OK)

    # ── J7 — SPI display alternativo (JST XH 8-pin, ILI9341 style) ───
    j7 = _JXH8()
    j7.ref = 'J7'
    j7.value = 'SPI_DISPLAY'
    j7[1] += VCC3V3
    j7[2] += GND
    j7[3] += CS_DISP
    j7[4] += RST_DISP
    j7[5] += DC_DISP
    j7[6] += SPI_MOSI
    j7[7] += SPI_SCK
    j7[8] += DISP_LED

    # ── J8 — I2C DS3231 breakout (JST XH 4-pin: 3V3, GND, SDA, SCL) ─
    j8 = _JXH4()
    j8.ref = 'J8'
    j8.value = 'I2C_RTC'
    j8[1] += VCC3V3
    j8[2] += GND
    j8[3] += I2C_SDA
    j8[4] += I2C_SCL

    # ── J11/J12 — Pico 2 W sockets (2x 1x20 female, 2.54mm) ──────────
    # Left side: Pico pins 1–20 (GP0–GP15)
    j11 = _PS20()
    j11.ref = 'J11'
    j11.value = 'PICO_L'
    j11[1]  += UART_TX       # GP0
    j11[2]  += UART_RX       # GP1 (3.0V from divider)
    j11[3]  += GND
    j11[4]  += SPI_SCK       # GP2
    j11[5]  += SPI_MOSI      # GP3
    j11[6]  += SPI_MISO      # GP4
    j11[7]  += CS_RTD1       # GP5 — caldeira
    j11[8]  += GND
    j11[9]  += CS_RTD2       # GP6 — grupo
    # j11[10] = GP7           (pin 10) — spare, not connected
    j11[11] += CS_DISP       # GP8
    j11[12] += DC_DISP       # GP9
    j11[13] += GND
    j11[14] += RST_DISP      # GP10
    j11[15] += SSR_CTRL      # GP11
    j11[16] += LED_STATUS    # GP12
    j11[17] += DISP_LED      # GP13
    j11[18] += GND
    j11[19] += I2C_SDA       # GP14
    j11[20] += I2C_SCL       # GP15

    # Right side: Pico pins 21–40 (GP16–VBUS)
    j12 = _PS20()
    j12.ref = 'J12'
    j12.value = 'PICO_R'
    j12[1]  += ENC_CLK       # GP16  (pin 21)
    j12[2]  += ENC_DT        # GP17  (pin 22)
    j12[3]  += GND           #        (pin 23)
    j12[4]  += ENC_SW        # GP18  (pin 24)
    j12[5]  += BTN1          # GP19  (pin 25)
    j12[6]  += BTN2          # GP20  (pin 26)
    j12[7]  += BTN3          # GP21  (pin 27)
    j12[8]  += GND           #        (pin 28)
    j12[9]  += LEVEL_SENSE   # GP22  (pin 29)
    # j12[10] = RUN           (pin 30) — not connected
    j12[11] += NTC1_ADC      # GP26/ADC0 (pin 31)
    j12[12] += NTC2_ADC      # GP27/ADC1 (pin 32)
    j12[13] += GND           # AGND  (pin 33)
    # j12[14] = GP28          (pin 34) — spare
    j12[15] += VCC3V3        # ADC_VREF (pin 35) — tied to AMS1117 3V3 for ratiometric NTC + WiFi noise isolation
    # j12[16] = 3V3(OUT)      (pin 36) — Pico output, NOT tied to carrier 3V3
    # j12[17] = 3V3_EN        (pin 37) — not connected
    j12[18] += GND           #          (pin 38)
    j12[19] += VCC5V         # VSYS    (pin 39) — 5V in
    # j12[20] = VBUS          (pin 40) — USB 5V, not connected

    # ── J13/J14 — SEN-30201 RTD breakout sockets (1x8 female, 2.54mm) ─
    # Pinout SEN-30201: 1=Vin 2=GND 3=SDO 4=SDI 5=SCK 6=CS 7=DRDY 8=3Vo
    for ref, cs_net, label in [
        ('J13', CS_RTD1, 'RTD_CALDEIRA'),
        ('J14', CS_RTD2, 'RTD_GRUPO'),
    ]:
        j = _PS8()
        j.ref = ref
        j.value = label
        j[1] += VCC5V
        j[2] += GND
        j[3] += SPI_MISO
        j[4] += SPI_MOSI
        j[5] += SPI_SCK
        j[6] += cs_net
        # j[7] = DRDY — not connected (polling via SPI register read)
        # j[8] = 3Vo  — breakout LDO output, not used on carrier


# ---------------------------------------------------------------------------
# Build circuit
# ---------------------------------------------------------------------------
block_power()
block_ssr_drive()
block_led()
block_level_probe()
block_uart_level_shift()
block_pullups()
block_ntc()
block_connectors()


# ---------------------------------------------------------------------------
# Generate netlist
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    ERC()
    generate_netlist(file_='outputs/faema_carrier.net')
    print('\nNetlist gerada: outputs/faema_carrier.net')
    print('Importar no KiCad PCB Editor: File > Import Netlist')
    # generate_schematic() não funciona com Part(tool=SKIDL,...) — falta campo orientation
    # Para esquema gráfico use: generate_svg() + netlistsvg

