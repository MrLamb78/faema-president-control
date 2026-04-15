#!/usr/bin/env python3
"""
faema_carrier.py — Carrier board (backplane) for Faema President controller.

Rev.6: Headers for plug-in modules + power supply + passives.
  - Raspberry Pi Pico 2 W (MCU, 2x20 socket)
  - 3x Playing with Fusion SEN-30201 (MAX31865 RTD breakout, 1x8 socket)
  - Nextion NX3224T024 display (UART, 4-pin)
  Optional: SPI display, DS3231 RTC module, NTC thermistors.

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

# Terminal blocks (5.08mm pitch)
_TB2 = _make_conn(2, 'TerminalBlock_Phoenix:'
                     'TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal')
_TB3 = _make_conn(3, 'TerminalBlock_Phoenix:'
                     'TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal')

# Pin headers (male, 2.54mm)
_PH2 = _make_conn(2, 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical')
_PH4 = _make_conn(4, 'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical')
_PH5 = _make_conn(5, 'Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical')
_PH8 = _make_conn(8, 'Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical')

# Pin sockets (female, 2.54mm — for plug-in modules)
_PS8  = _make_conn(8,  'Connector_PinSocket_2.54mm:PinSocket_1x08_P2.54mm_Vertical')
_PS20 = _make_conn(20, 'Connector_PinSocket_2.54mm:PinSocket_1x20_P2.54mm_Vertical')


# ---------------------------------------------------------------------------
# Global nets
# ---------------------------------------------------------------------------

# Power
GND         = Net('GND')
VCC5V       = Net('+5V')
VCC3V3      = Net('+3V3')
AC_L1_FUSED = Net('AC_L1_FUSED')
AC_L2_FUSED = Net('AC_L2_FUSED')

# SPI bus (shared: RTD breakouts + optional SPI display)
SPI_SCK     = Net('SPI_SCK')
SPI_MOSI    = Net('SPI_MOSI')
SPI_MISO    = Net('SPI_MISO')
CS_RTD1     = Net('CS_RTD1')
CS_RTD2     = Net('CS_RTD2')
CS_RTD3     = Net('CS_RTD3')

# SPI display (option B)
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

# NTC (optional, DNF when using RTD breakouts)
NTC1_ADC    = Net('NTC1_ADC')
NTC2_ADC    = Net('NTC2_ADC')


# ---------------------------------------------------------------------------
# Component templates
# ---------------------------------------------------------------------------
_R = Part('Device', 'R',
          footprint='Resistor_SMD:R_0603_1608Metric', dest=TEMPLATE)

_C_0603 = Part('Device', 'C',
               footprint='Capacitor_SMD:C_0603_1608Metric', dest=TEMPLATE)

_C_0805 = Part('Device', 'C',
               footprint='Capacitor_SMD:C_0805_2012Metric', dest=TEMPLATE)


# ---------------------------------------------------------------------------
# BLOCK 1 — Power Supply
# ---------------------------------------------------------------------------
@subcircuit
def block_power():
    """J1 (AC bornier), RV1 (MOV), U1 (HLK-PM05), U2 (AMS1117), C1-C4.
    220V bifasica (L1+L2, sem neutro). Fusiveis T16A externos a PCB."""

    # J1 — AC input bornier 3-pin: L1_FUSED, L2_FUSED, PE
    j1 = _TB3()
    j1.ref = 'J1'
    j1.value = 'AC_INPUT_220V'
    j1[1] += AC_L1_FUSED   # L1 (fusada externamente, T16A)
    j1[2] += AC_L2_FUSED   # L2 (fusada externamente, T16A)
    j1[3] += GND            # PE / chassis

    # RV1 — MOV S14K275 across AC lines (surge protection)
    rv1 = Part(tool=SKIDL, name='MOV',
               footprint='Varistor:RV_Disc_D15.5mm_W5mm_P7.5mm')
    rv1 += [Pin(num=1, name='1', func=Pin.types.PASSIVE),
            Pin(num=2, name='2', func=Pin.types.PASSIVE)]
    rv1.ref = 'RV1'
    rv1.value = 'S14K275'
    rv1[1] += AC_L1_FUSED
    rv1[2] += AC_L2_FUSED

    # U1 — HLK-PM05 (AC/DC isolated 5V)
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

    # C1 — 10uF 5V bulk
    c1 = _C_0805()
    c1.ref = 'C1'
    c1.value = '10uF_16V'
    c1[1] += VCC5V
    c1[2] += GND

    # C3 — 100nF 5V bypass
    c3 = _C_0603()
    c3.ref = 'C3'
    c3.value = '100nF_50V'
    c3[1] += VCC5V
    c3[2] += GND

    # U2 — AMS1117-3.3 (5V -> 3.3V LDO)
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

    # C2 — 10uF 3V3 bulk
    c2 = _C_0805()
    c2.ref = 'C2'
    c2.value = '10uF_16V'
    c2[1] += VCC3V3
    c2[2] += GND

    # C4 — 100nF 3V3 bypass
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
    GPIO11 -> R2 -> Q1 gate -> drain -> SSR-.  5V -> R1 -> SSR+."""

    # R1 — 220R (+5V -> SSR input +)
    r1 = _R()
    r1.ref = 'R1'
    r1.value = '220R'
    r1[1] += VCC5V
    r1[2] += SSR_CTRL_P

    # R2 — 100R gate series
    r2 = _R()
    r2.ref = 'R2'
    r2.value = '100R'
    r2[1] += SSR_CTRL
    r2[2] += GATE_DRIVE

    # R3 — 10k gate pull-down (boot-safe: SSR OFF at reset)
    r3 = _R()
    r3.ref = 'R3'
    r3.value = '10k'
    r3[1] += GATE_DRIVE
    r3[2] += GND

    # Q1 — 2N7002 N-MOSFET (low-side switch)
    q1 = Part(tool=SKIDL, name='2N7002',
              footprint='Package_TO_SOT_SMD:SOT-23')
    q1 += [Pin(num=1, name='G', func=Pin.types.INPUT),
           Pin(num=2, name='S', func=Pin.types.PASSIVE),
           Pin(num=3, name='D', func=Pin.types.PASSIVE)]
    q1.ref = 'Q1'
    q1.value = '2N7002'
    q1[1] += GATE_DRIVE   # gate
    q1[2] += GND           # source
    q1[3] += SSR_DRIVE     # drain -> SSR input (-)

    # J2 — SSR control bornier 2-pin
    j2 = _TB2()
    j2.ref = 'J2'
    j2.value = 'SSR_CTRL'
    j2[1] += SSR_CTRL_P    # SSR+ (5V via R1)
    j2[2] += SSR_DRIVE     # SSR- (Q1 drain)


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
    """R5 (100k pull-up) + J5 (2-pin). GP22 -> R5 -> 3V3; probe shorts to GND."""

    r5 = _R()
    r5.ref = 'R5'
    r5.value = '100k'
    r5[1] += VCC3V3
    r5[2] += LEVEL_SENSE

    j5 = _PH2()
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
    Junction voltage = 5V * 15k/(10k+15k) = 3.0V -> safe for Pico."""

    r6 = _R()
    r6.ref = 'R6'
    r6.value = '10k'
    r6[1] += UART_RX_5V    # Nextion TX output (5V)
    r6[2] += UART_RX       # junction -> Pico GP1 (3.0V)

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
# BLOCK 7 — NTC Option (DNF when using RTD breakouts)
# ---------------------------------------------------------------------------
@subcircuit
def block_ntc_option():
    """R8/R9 (10k reference) + J9/J10 (NTC connectors).
    VCC3V3 -> R_ref -> ADC_pin -> NTC -> GND. Populate OR use RTD, not both."""

    for r_ref, j_ref, adc_net, label in [
        ('R8', 'J9',  NTC1_ADC, 'NTC_CALDEIRA'),
        ('R9', 'J10', NTC2_ADC, 'NTC_GRUPO'),
    ]:
        r = _R()
        r.ref = r_ref
        r.value = '10k_DNF'
        r[1] += VCC3V3
        r[2] += adc_net

        j = _PH2()
        j.ref = j_ref
        j.value = label
        j[1] += adc_net
        j[2] += GND


# ---------------------------------------------------------------------------
# BLOCK 8 — Connectors
# ---------------------------------------------------------------------------
@subcircuit
def block_connectors():
    """Encoder, buttons, displays, I2C, Pico sockets, RTD breakout sockets."""

    # ── J3 — Encoder (5-pin: CLK, DT, SW, 3V3, GND) ─────────────────
    j3 = _PH5()
    j3.ref = 'J3'
    j3.value = 'ENCODER'
    j3[1] += ENC_CLK
    j3[2] += ENC_DT
    j3[3] += ENC_SW
    j3[4] += VCC3V3
    j3[5] += GND

    # ── J4 — Buttons (4-pin: BTN1, BTN2, BTN3, GND) ─────────────────
    j4 = _PH4()
    j4.ref = 'J4'
    j4.value = 'BUTTONS'
    j4[1] += BTN1
    j4[2] += BTN2
    j4[3] += BTN3
    j4[4] += GND

    # ── J6 — Nextion display (4-pin: 5V, GND, NX_TX, NX_RX) ─────────
    j6 = _PH4()
    j6.ref = 'J6'
    j6.value = 'NEXTION'
    j6[1] += VCC5V          # Nextion power (5V)
    j6[2] += GND
    j6[3] += UART_RX_5V    # Nextion TX -> level shifter -> Pico
    j6[4] += UART_TX       # Pico TX -> Nextion RX (3.3V OK)

    # ── J7 — SPI display (8-pin, optional ILI9341 style) ─────────────
    j7 = _PH8()
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

    # ── J8 — I2C header (4-pin: 3V3, GND, SDA, SCL) ─────────────────
    j8 = _PH4()
    j8.ref = 'J8'
    j8.value = 'I2C_RTC'
    j8[1] += VCC3V3
    j8[2] += GND
    j8[3] += I2C_SDA
    j8[4] += I2C_SCL

    # ── J11/J12 — Pico 2 W sockets (2x 1x20 female) ─────────────────
    # Left side (pin 1 = Pico pin 1 = GP0, top to bottom)
    j11 = _PS20()
    j11.ref = 'J11'
    j11.value = 'PICO_L'
    j11[1]  += UART_TX       # GP0
    j11[2]  += UART_RX       # GP1 (level-shifted 3.0V)
    j11[3]  += GND
    j11[4]  += SPI_SCK       # GP2
    j11[5]  += SPI_MOSI      # GP3
    j11[6]  += SPI_MISO      # GP4
    j11[7]  += CS_RTD1       # GP5
    j11[8]  += GND
    j11[9]  += CS_RTD2       # GP6
    j11[10] += CS_RTD3       # GP7
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

    # Right side (pin 1 = Pico pin 21 = GP16, bottom to top)
    j12 = _PS20()
    j12.ref = 'J12'
    j12.value = 'PICO_R'
    j12[1]  += ENC_CLK       # GP16  (Pico pin 21)
    j12[2]  += ENC_DT        # GP17  (pin 22)
    j12[3]  += GND           #        (pin 23)
    j12[4]  += ENC_SW        # GP18  (pin 24)
    j12[5]  += BTN1          # GP19  (pin 25)
    j12[6]  += BTN2          # GP20  (pin 26)
    j12[7]  += BTN3          # GP21  (pin 27)
    j12[8]  += GND           #        (pin 28)
    j12[9]  += LEVEL_SENSE   # GP22  (pin 29)
    # j12[10] = RUN            (pin 30) — not connected
    j12[11] += NTC1_ADC      # GP26/ADC0 (pin 31)
    j12[12] += NTC2_ADC      # GP27/ADC1 (pin 32)
    j12[13] += GND           # AGND  (pin 33)
    # j12[14] = GP28/ADC2     (pin 34) — spare, not connected
    # j12[15] = ADC_VREF      (pin 35) — not connected
    # j12[16] = 3V3(OUT)      (pin 36) — Pico output, NOT connected to carrier 3V3
    # j12[17] = 3V3_EN        (pin 37) — not connected
    j12[18] += GND           #          (pin 38)
    j12[19] += VCC5V         # VSYS    (pin 39) — 5V power input to Pico
    # j12[20] = VBUS          (pin 40) — USB 5V, not connected

    # ── J13/J14/J15 — SEN-30201 RTD breakout sockets (1x8 female) ────
    # SEN-30201 header pinout (top to bottom on breakout right side):
    #   1: Vin  2: GND  3: SDO(MISO)  4: SDI(MOSI)
    #   5: SCK  6: CS   7: DRDY       8: 3Vo
    for ref, cs_net, label in [
        ('J13', CS_RTD1, 'RTD_CALDEIRA'),
        ('J14', CS_RTD2, 'RTD_GRUPO'),
        ('J15', CS_RTD3, 'RTD_SPARE'),
    ]:
        j = _PS8()
        j.ref = ref
        j.value = label
        j[1] += VCC5V        # Vin — breakout has onboard LDO
        j[2] += GND
        j[3] += SPI_MISO     # SDO
        j[4] += SPI_MOSI     # SDI
        j[5] += SPI_SCK      # SCK
        j[6] += cs_net        # CS (unique per board)
        # j[7] = DRDY — not connected (polling via SPI)
        # j[8] = 3Vo — output from breakout LDO, not used


# ---------------------------------------------------------------------------
# Build circuit
# ---------------------------------------------------------------------------
block_power()
block_ssr_drive()
block_led()
block_level_probe()
block_uart_level_shift()
block_pullups()
block_ntc_option()
block_connectors()


# ---------------------------------------------------------------------------
# Generate netlist
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    ERC()
    generate_netlist(file_='outputs/faema_carrier.net')
    print('\nNetlist gerada: outputs/faema_carrier.net')
    print('Importar no KiCad PCB Editor: File > Import Netlist')
