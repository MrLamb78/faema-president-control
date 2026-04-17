#!/usr/bin/env python3
"""
faema_carrier.py — Generic espresso machine controller carrier board.

Rev.7: Dual PID (RTD1+RTD2), MGFR pump, flow meter, pressure sensor,
       MCP23017 I/O expander, 2x SSR, 5 buttons, 5 LEDs, 4 relay outputs,
       2 level probes, Nextion UART display, optional SPI display, optional RTC.

Connector naming is generic (RTD1/RTD2, SSR1/SSR2, LEVEL1/LEVEL2, OUT1–4…).
Machine-specific mapping (caldeira/grupo/tanque) lives in firmware config.py.

Plug-in modules (not on carrier PCB):
  J11/J12 — Raspberry Pi Pico 2 W (2×20 socket 2.54mm)
  J13/J14 — MAX31865 RTD breakout ×2 (1×8 socket 2.54mm, Adafruit pinout)
  J6      — Nextion UART display (JST XH 4-pin)
  J7      — SPI display optional (JST XH 8-pin)
  J8      — DS3231 RTC I2C (JST XH 4-pin)
  U3      — MCP23017 I/O expander (SOIC-28, mounted on carrier)

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
# Component templates
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

# Cable connectors — JST XH 2.5mm keyed
_JXH2 = _make_conn(2, 'Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical')
_JXH3 = _make_conn(3, 'Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical')
_JXH4 = _make_conn(4, 'Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical')
_JXH5 = _make_conn(5, 'Connector_JST:JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical')
_JXH8 = _make_conn(8, 'Connector_JST:JST_XH_B8B-XH-A_1x08_P2.50mm_Vertical')

# Module sockets — 2.54mm female
_PS8  = _make_conn(8,  'Connector_PinSocket_2.54mm:PinSocket_1x08_P2.54mm_Vertical')
_PS20 = _make_conn(20, 'Connector_PinSocket_2.54mm:PinSocket_1x20_P2.54mm_Vertical')


# ---------------------------------------------------------------------------
# Global nets
# ---------------------------------------------------------------------------

# Power
GND         = Net('GND')
PE          = Net('PE')           # Chassis earth — NOT connected to GND
VCC5V       = Net('+5V')
VCC3V3      = Net('+3V3')
AC_L1_FUSED = Net('AC_L1_FUSED')
AC_L2_FUSED = Net('AC_L2_FUSED')

# SPI0 bus — RTD breakouts (J13/J14) + SPI display (J7)
SPI_SCK     = Net('SPI_SCK')      # GP2
SPI_MOSI    = Net('SPI_MOSI')     # GP3
SPI_MISO    = Net('SPI_MISO')     # GP4
CS_RTD1     = Net('CS_RTD1')      # GP5
CS_RTD2     = Net('CS_RTD2')      # GP6
# DRDY pins (J13/J14 pin 8) left NC — no free GPIO; firmware uses SPI polling

# SPI display (J7) — uses SPI0 bus
CS_DISP     = Net('CS_DISP')      # GP10
DC_DISP     = Net('DC_DISP')      # GP11
RST_DISP    = Net('RST_DISP')     # GP12
DISP_LED    = Net('DISP_LED')     # GP13

# UART — Nextion (J6)
UART_TX     = Net('UART_TX')      # GP0
UART_RX     = Net('UART_RX')      # GP1 (3.3V after divider)
UART_RX_5V  = Net('UART_RX_5V')  # Nextion TX before divider

# I2C — DS3231 (J8) + MCP23017 (U3)
I2C_SDA     = Net('I2C_SDA')      # GP14
I2C_SCL     = Net('I2C_SCL')      # GP15

# SSR drive — dual
SSR1_CTRL   = Net('SSR1_CTRL')    # GP7
SSR1_DRIVE  = Net('SSR1_DRIVE')
SSR1_CTRL_P = Net('SSR1_CTRL_P')
GATE1_DRIVE = Net('GATE1_DRIVE')

SSR2_CTRL   = Net('SSR2_CTRL')    # GP19
SSR2_DRIVE  = Net('SSR2_DRIVE')
SSR2_CTRL_P = Net('SSR2_CTRL_P')
GATE2_DRIVE = Net('GATE2_DRIVE')

# Pump control
PUMP_CTRL   = Net('PUMP_CTRL')    # GP20 — 0–3.3V to MGFR

# Encoder (J3)
ENC_CLK     = Net('ENC_CLK')      # GP16
ENC_DT      = Net('ENC_DT')       # GP17
ENC_SW      = Net('ENC_SW')       # GP18

# Pulse input — flow meter (J16)
PULSE_IN    = Net('PULSE_IN')     # GP21

# MCP23017 interrupt
MCP_INT     = Net('MCP_INT')      # GP22 ← MCP23017 INTA

# ADC inputs
TEMP_AUX    = Net('TEMP_AUX')     # GP26/ADC0 — NTC optional
PRESSURE    = Net('PRESSURE')     # GP27/ADC1 — 0–4.5V sensor (via divider)
ANALOG_IN   = Net('ANALOG_IN')    # GP28/ADC2 — potentiometer

# MCP23017 — buttons (GPA0–4, pulled up internally)
BTN1        = Net('BTN1')
BTN2        = Net('BTN2')
BTN3        = Net('BTN3')
BTN4        = Net('BTN4')
BTN5        = Net('BTN5')

# MCP23017 — level probes (GPA5–6)
LEVEL1      = Net('LEVEL1')
LEVEL2      = Net('LEVEL2')

# MCP23017 — LEDs (GPA7, GPB4–7) — driven via current-limiting resistors
LED1        = Net('LED1')
LED2        = Net('LED2')
LED3        = Net('LED3')
LED4        = Net('LED4')
LED5        = Net('LED5')

# MCP23017 — relay outputs (GPB0–3)
OUT1        = Net('OUT1')
OUT2        = Net('OUT2')
OUT3        = Net('OUT3')
OUT4        = Net('OUT4')


# ---------------------------------------------------------------------------
# BLOCK 1 — Power Supply
# ---------------------------------------------------------------------------
@subcircuit
def block_power():
    """J1 (AC bornier), RV1 (MOV), U1 (HLK-PM05), U2 (AMS1117), C1-C4."""

    j1 = _TB3()
    j1.ref = 'J1'
    j1.value = 'AC_INPUT_220V'
    j1[1] += AC_L1_FUSED
    j1[2] += AC_L2_FUSED
    j1[3] += PE

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
# BLOCK 2 — SSR Drive (dual: SSR1 + SSR2)
# ---------------------------------------------------------------------------
@subcircuit
def block_ssr_drive():
    """Q1/Q2 (2N7002), R-series gate resistors + pull-downs, J2a/J2b (borniers).
    GPx -> Rx_gate -> Qx gate -> drain -> SSR-.  5V -> Rx_led -> SSR+."""

    for idx, (ctrl, ctrl_p, gate, drive, j_ref) in enumerate([
        (SSR1_CTRL, SSR1_CTRL_P, GATE1_DRIVE, SSR1_DRIVE, 'J2a'),
        (SSR2_CTRL, SSR2_CTRL_P, GATE2_DRIVE, SSR2_DRIVE, 'J2b'),
    ], start=1):
        r_led = _R()
        r_led.ref = f'R{idx}'          # R1, R2
        r_led.value = '220R'
        r_led[1] += VCC5V
        r_led[2] += ctrl_p

        r_gate = _R()
        r_gate.ref = f'R{idx + 2}'     # R3, R4
        r_gate.value = '100R'
        r_gate[1] += ctrl
        r_gate[2] += gate

        r_pd = _R()
        r_pd.ref = f'R{idx + 4}'       # R5, R6
        r_pd.value = '10k'
        r_pd[1] += gate
        r_pd[2] += GND

        q = Part(tool=SKIDL, name='2N7002',
                 footprint='Package_TO_SOT_SMD:SOT-23')
        q += [Pin(num=1, name='G', func=Pin.types.INPUT),
              Pin(num=2, name='S', func=Pin.types.PASSIVE),
              Pin(num=3, name='D', func=Pin.types.PASSIVE)]
        q.ref = f'Q{idx}'
        q.value = '2N7002'
        q[1] += gate
        q[2] += GND
        q[3] += drive

        j = _TB2()
        j.ref = j_ref
        j.value = f'SSR{idx}_OUT'
        j[1] += ctrl_p
        j[2] += drive


# ---------------------------------------------------------------------------
# BLOCK 3 — MCP23017 I/O Expander
# ---------------------------------------------------------------------------
@subcircuit
def block_mcp23017():
    """U3 (MCP23017 SOIC-28): 16 GPIO via I2C.
    Port A: BTN1-5 (inputs, internal pull-up), LEVEL1/2 (inputs).
    Port B: OUT1-4 (relay outputs), LED1-4 (outputs).
    GPA7: LED5. INTA -> MCP_INT (GP22). Addr 0x20 (A0/A1/A2 = GND).
    Decoupling: C_mcp (100nF) close to VDD pin."""

    u3 = Part(tool=SKIDL, name='MCP23017', dest=TEMPLATE,
              footprint='Package_SO:SOIC-28W_7.5x17.9mm_P1.27mm')
    u3 += [
        Pin(num=1,  name='GPB0',  func=Pin.types.BIDIR),
        Pin(num=2,  name='GPB1',  func=Pin.types.BIDIR),
        Pin(num=3,  name='GPB2',  func=Pin.types.BIDIR),
        Pin(num=4,  name='GPB3',  func=Pin.types.BIDIR),
        Pin(num=5,  name='GPB4',  func=Pin.types.BIDIR),
        Pin(num=6,  name='GPB5',  func=Pin.types.BIDIR),
        Pin(num=7,  name='GPB6',  func=Pin.types.BIDIR),
        Pin(num=8,  name='GPB7',  func=Pin.types.BIDIR),
        Pin(num=9,  name='VDD',   func=Pin.types.PWRIN),
        Pin(num=10, name='VSS',   func=Pin.types.PWRIN),
        Pin(num=11, name='CS',    func=Pin.types.INPUT),   # NC (I2C mode)
        Pin(num=12, name='SCK',   func=Pin.types.INPUT),
        Pin(num=13, name='SDA',   func=Pin.types.BIDIR),
        Pin(num=14, name='A2',    func=Pin.types.INPUT),
        Pin(num=15, name='A1',    func=Pin.types.INPUT),
        Pin(num=16, name='A0',    func=Pin.types.INPUT),
        Pin(num=17, name='INTA',  func=Pin.types.OUTPUT),
        Pin(num=18, name='INTB',  func=Pin.types.OUTPUT),
        Pin(num=19, name='RESET', func=Pin.types.INPUT),
        Pin(num=20, name='GPA7',  func=Pin.types.BIDIR),
        Pin(num=21, name='GPA6',  func=Pin.types.BIDIR),
        Pin(num=22, name='GPA5',  func=Pin.types.BIDIR),
        Pin(num=23, name='GPA4',  func=Pin.types.BIDIR),
        Pin(num=24, name='GPA3',  func=Pin.types.BIDIR),
        Pin(num=25, name='GPA2',  func=Pin.types.BIDIR),
        Pin(num=26, name='GPA1',  func=Pin.types.BIDIR),
        Pin(num=27, name='GPA0',  func=Pin.types.BIDIR),
        Pin(num=28, name='NC',    func=Pin.types.NOCONNECT),
    ]
    ic = u3()
    ic.ref = 'U3'
    ic.value = 'MCP23017'

    ic['VDD']   += VCC3V3
    ic['VSS']   += GND
    ic['SCK']   += I2C_SCL
    ic['SDA']   += I2C_SDA
    ic['A0']    += GND        # addr 0x20
    ic['A1']    += GND
    ic['A2']    += GND
    ic['RESET'] += VCC3V3     # tie high (active-low reset)
    ic['CS']    += VCC3V3     # NC in I2C mode — tie high per datasheet
    ic['INTA']  += MCP_INT
    # INTB not connected (mirror mode: INTA reflects both ports)

    # Port A — inputs
    ic['GPA0'] += BTN1
    ic['GPA1'] += BTN2
    ic['GPA2'] += BTN3
    ic['GPA3'] += BTN4
    ic['GPA4'] += BTN5
    ic['GPA5'] += LEVEL1
    ic['GPA6'] += LEVEL2
    ic['GPA7'] += LED5        # output

    # Port B — outputs
    ic['GPB0'] += OUT1
    ic['GPB1'] += OUT2
    ic['GPB2'] += OUT3
    ic['GPB3'] += OUT4
    ic['GPB4'] += LED1
    ic['GPB5'] += LED2
    ic['GPB6'] += LED3
    ic['GPB7'] += LED4

    # Decoupling
    c_mcp = _C_0603()
    c_mcp.ref = 'C5'
    c_mcp.value = '100nF_50V'
    c_mcp[1] += VCC3V3
    c_mcp[2] += GND

    # I2C pull-ups (shared with DS3231 on same bus)
    r_sda = _R()
    r_sda.ref = 'R7'
    r_sda.value = '4k7'
    r_sda[1] += VCC3V3
    r_sda[2] += I2C_SDA

    r_scl = _R()
    r_scl.ref = 'R8'
    r_scl.value = '4k7'
    r_scl[1] += VCC3V3
    r_scl[2] += I2C_SCL


# ---------------------------------------------------------------------------
# BLOCK 4 — LED drivers (MCP23017 outputs → LED 0603)
# ---------------------------------------------------------------------------
@subcircuit
def block_leds():
    """LED1–LED5: 0603 LEDs with 470R series resistors driven by MCP23017."""

    for i, net in enumerate([LED1, LED2, LED3, LED4, LED5], start=1):
        r = _R()
        r.ref = f'R{8 + i}'    # R9–R13
        r.value = '470R'
        anode = Net(f'LED{i}_A')
        r[1] += net
        r[2] += anode

        d = _LED()
        d.ref = f'D{i}'
        d.value = 'GREEN'
        d[1] += anode
        d[2] += GND


# ---------------------------------------------------------------------------
# BLOCK 5 — Level probes (LEVEL1/LEVEL2 — pull-ups, JST XH 2-pin)
# ---------------------------------------------------------------------------
@subcircuit
def block_level_probes():
    """R14/R15 (100k pull-up to 3V3) + J15a/J15b (JST XH 2-pin).
    MCP23017 GPA5/GPA6 read HIGH when probe open, LOW when submerged."""

    for idx, (net, j_ref, label) in enumerate([
        (LEVEL1, 'J15a', 'LEVEL1'),
        (LEVEL2, 'J15b', 'LEVEL2'),
    ], start=14):
        r = _R()
        r.ref = f'R{idx}'      # R14, R15
        r.value = '100k'
        r[1] += VCC3V3
        r[2] += net

        j = _JXH2()
        j.ref = j_ref
        j.value = label
        j[1] += net
        j[2] += GND


# ---------------------------------------------------------------------------
# BLOCK 6 — UART Level Shifter (Nextion 5V TX → Pico 3.3V RX)
# ---------------------------------------------------------------------------
@subcircuit
def block_uart_level_shift():
    """R16 (10k) + R17 (15k) voltage divider.
    Nextion TX 5V → R16 → junction → R17 → GND.
    Vout = 5V × 15k/25k = 3.0V — within Pico VIH spec."""

    r16 = _R()
    r16.ref = 'R16'
    r16.value = '10k'
    r16[1] += UART_RX_5V
    r16[2] += UART_RX

    r17 = _R()
    r17.ref = 'R17'
    r17.value = '15k'
    r17[1] += UART_RX
    r17[2] += GND


# ---------------------------------------------------------------------------
# BLOCK 7 — Encoder pull-ups
# ---------------------------------------------------------------------------
@subcircuit
def block_encoder_pullups():
    """R18–R20 (10k) pull-ups for EC11 encoder CLK/DT/SW."""

    for ref, net in [('R18', ENC_CLK), ('R19', ENC_DT), ('R20', ENC_SW)]:
        r = _R()
        r.ref = ref
        r.value = '10k'
        r[1] += VCC3V3
        r[2] += net


# ---------------------------------------------------------------------------
# BLOCK 8 — TEMP_AUX NTC (optional — DNF if not used)
# ---------------------------------------------------------------------------
@subcircuit
def block_ntc():
    """R21 (2k2 0.1%) + C6 (100nF) + C7 (ADC_VREF bypass) + J17 (JST XH 2-pin).
    3V3 → R21 → TEMP_AUX(GP26) → NTC(10k) → GND.
    C6: low-pass filter in parallel with NTC.
    C7: 100nF bypass on ADC_VREF (Pico pin 35), place near J12 pin 15."""

    r21 = _R()
    r21.ref = 'R21'
    r21.value = '2k2_0.1%'
    r21[1] += VCC3V3
    r21[2] += TEMP_AUX

    c6 = _C_0603()
    c6.ref = 'C6'
    c6.value = '100nF_50V'
    c6[1] += TEMP_AUX
    c6[2] += GND

    j17 = _JXH2()
    j17.ref = 'J17'
    j17.value = 'TEMP_AUX'
    j17[1] += TEMP_AUX
    j17[2] += GND

    c7 = _C_0603()
    c7.ref = 'C7'
    c7.value = '100nF_50V'
    c7[1] += VCC3V3
    c7[2] += GND


# ---------------------------------------------------------------------------
# BLOCK 9 — Pressure sensor input (0–4.5V → ADC 0–3.3V)
# ---------------------------------------------------------------------------
@subcircuit
def block_pressure():
    """R22 (33k) + R23 (82k) voltage divider + C8 (100nF) filter + J18 (JST XH 3-pin).
    Vin_max=4.5V → Vout = 4.5 × 82/115 = 3.21V ≤ ADC_VREF 3.3V.
    J18: pin1=VCC (sensor supply, 5V), pin2=SIGNAL, pin3=GND."""

    r22 = _R()
    r22.ref = 'R22'
    r22.value = '33k'
    PRESSURE_RAW = Net('PRESSURE_RAW')
    r22[1] += PRESSURE_RAW
    r22[2] += PRESSURE

    r23 = _R()
    r23.ref = 'R23'
    r23.value = '82k'
    r23[1] += PRESSURE
    r23[2] += GND

    c8 = _C_0603()
    c8.ref = 'C8'
    c8.value = '100nF_50V'
    c8[1] += PRESSURE
    c8[2] += GND

    j18 = _JXH3()
    j18.ref = 'J18'
    j18.value = 'PRESSURE'
    j18[1] += VCC5V          # sensor Vcc (most 0-4.5V sensors run on 5V)
    j18[2] += PRESSURE_RAW   # raw signal in (before divider)
    j18[3] += GND


# ---------------------------------------------------------------------------
# BLOCK 10 — Analog inputs: potentiometer + pump control
# ---------------------------------------------------------------------------
@subcircuit
def block_analog():
    """J19 (JST XH 3-pin): potentiometer wiper → ANALOG_IN (GP28/ADC2).
    J20 (JST XH 2-pin): PUMP_CTRL 0–3.3V → MGFR pump control input.
    R24 (100R): output series resistor on PUMP_CTRL for protection."""

    j19 = _JXH3()
    j19.ref = 'J19'
    j19.value = 'ANALOG_IN'
    j19[1] += VCC3V3         # pot high end
    j19[2] += ANALOG_IN      # wiper
    j19[3] += GND            # pot low end

    r24 = _R()
    r24.ref = 'R24'
    r24.value = '100R'
    PUMP_OUT = Net('PUMP_OUT')
    r24[1] += PUMP_CTRL
    r24[2] += PUMP_OUT

    j20 = _JXH2()
    j20.ref = 'J20'
    j20.value = 'PUMP_CTRL'
    j20[1] += PUMP_OUT
    j20[2] += GND


# ---------------------------------------------------------------------------
# BLOCK 11 — Flow meter pulse input
# ---------------------------------------------------------------------------
@subcircuit
def block_flow():
    """R25 (10k pull-up) + C9 (10nF debounce) + J16 (JST XH 3-pin).
    J16: pin1=VCC(5V), pin2=PULSE, pin3=GND. Open-collector flow meter.
    PULSE_IN → GP21 (interrupt-capable)."""

    r25 = _R()
    r25.ref = 'R25'
    r25.value = '10k'
    r25[1] += VCC3V3
    r25[2] += PULSE_IN

    c9 = _C_0603()
    c9.ref = 'C9'
    c9.value = '10nF'
    c9[1] += PULSE_IN
    c9[2] += GND

    j16 = _JXH3()
    j16.ref = 'J16'
    j16.value = 'FLOW'
    j16[1] += VCC5V
    j16[2] += PULSE_IN
    j16[3] += GND


# ---------------------------------------------------------------------------
# BLOCK 12 — Relay outputs (MCP23017 GPB0–3 → JST XH)
# ---------------------------------------------------------------------------
@subcircuit
def block_relay_outputs():
    """J21–J24 (JST XH 3-pin): MCP23017 OUT1–4 for external relay boards.
    Each connector: pin1=VCC(3V3 logic), pin2=SIGNAL, pin3=GND."""

    for i, net in enumerate([OUT1, OUT2, OUT3, OUT4], start=1):
        j = _JXH3()
        j.ref = f'J{20 + i}'   # J21–J24
        j.value = f'OUT{i}'
        j[1] += VCC3V3
        j[2] += net
        j[3] += GND


# ---------------------------------------------------------------------------
# BLOCK 13 — Connectors (Pico sockets, RTD sockets, displays, I2C, encoder)
# ---------------------------------------------------------------------------
@subcircuit
def block_connectors():
    """J3 (encoder), J4 (buttons via MCP — header only), J6 (Nextion),
    J7 (SPI display), J8 (I2C RTC), J11/J12 (Pico sockets), J13/J14 (RTD sockets)."""

    # ── J3 — Encoder EC11 (JST XH 5-pin: CLK, DT, SW, 3V3, GND) ──────
    j3 = _JXH5()
    j3.ref = 'J3'
    j3.value = 'ENCODER'
    j3[1] += ENC_CLK
    j3[2] += ENC_DT
    j3[3] += ENC_SW
    j3[4] += VCC3V3
    j3[5] += GND

    # ── J4 — Button panel (JST XH 4-pin to MCP23017 via I2C — header) ─
    # Buttons are read by MCP23017; this connector provides 3V3+GND+I2C
    # for a button sub-panel if desired, or direct wires to BTN nets.
    j4 = _JXH5()
    j4.ref = 'J4'
    j4.value = 'BUTTONS'
    j4[1] += BTN1
    j4[2] += BTN2
    j4[3] += BTN3
    j4[4] += BTN4
    j4[5] += BTN5

    # ── J6 — Nextion display (JST XH 4-pin: 5V, GND, NX_TX, NX_RX) ───
    j6 = _JXH4()
    j6.ref = 'J6'
    j6.value = 'NEXTION'
    j6[1] += VCC5V
    j6[2] += GND
    j6[3] += UART_RX_5V      # Nextion TX → divider → Pico GP1
    j6[4] += UART_TX          # Pico GP0 TX → Nextion RX (3.3V ok)

    # ── J7 — SPI display optional (JST XH 8-pin, ILI9341 style) ────────
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

    # ── J8 — I2C RTC DS3231 (JST XH 4-pin: 3V3, GND, SDA, SCL) ────────
    j8 = _JXH4()
    j8.ref = 'J8'
    j8.value = 'I2C_RTC'
    j8[1] += VCC3V3
    j8[2] += GND
    j8[3] += I2C_SDA
    j8[4] += I2C_SCL

    # ── J11/J12 — Pico 2W sockets (2× 1×20 female 2.54mm) ─────────────
    # J11: left side, Pico physical pins 1–20

    j11 = _PS20()
    j11.ref = 'J11'
    j11.value = 'PICO_L'
    j11[1]  += UART_TX        # GP0  (pin 1)
    j11[2]  += UART_RX        # GP1  (pin 2) — 3.0V from divider
    j11[3]  += GND            #       (pin 3)
    j11[4]  += SPI_SCK        # GP2  (pin 4)
    j11[5]  += SPI_MOSI       # GP3  (pin 5)
    j11[6]  += SPI_MISO       # GP4  (pin 6)
    j11[7]  += CS_RTD1        # GP5  (pin 7)
    j11[8]  += GND            #       (pin 8)
    j11[9]  += CS_RTD2        # GP6  (pin 9)
    j11[10] += SSR1_CTRL      # GP7  (pin 10)
    j11[11] += SPI_SCK        # GP8  (pin 11) — SPI1 SCK, tied to SPI0 SCK for shared bus
    j11[12] += SPI_MOSI       # GP9  (pin 12) — SPI1 MOSI, tied to SPI0 MOSI
    j11[13] += GND            #       (pin 13)
    j11[14] += CS_DISP        # GP10 (pin 14)
    j11[15] += DC_DISP        # GP11 (pin 15)
    j11[16] += RST_DISP       # GP12 (pin 16)
    j11[17] += DISP_LED       # GP13 (pin 17)
    j11[18] += GND            #       (pin 18)
    j11[19] += I2C_SDA        # GP14 (pin 19)
    j11[20] += I2C_SCL        # GP15 (pin 20)

    # J12: right side, Pico physical pins 21–40
    j12 = _PS20()
    j12.ref = 'J12'
    j12.value = 'PICO_R'
    j12[1]  += ENC_CLK        # GP16 (pin 21)
    j12[2]  += ENC_DT         # GP17 (pin 22)
    j12[3]  += GND            #       (pin 23)
    j12[4]  += ENC_SW         # GP18 (pin 24)
    j12[5]  += SSR2_CTRL      # GP19 (pin 25)
    j12[6]  += PUMP_CTRL      # GP20 (pin 26)
    j12[7]  += PULSE_IN       # GP21 (pin 27)
    j12[8]  += GND            #       (pin 28)
    j12[9]  += MCP_INT        # GP22 (pin 29)
    # j12[10] = RUN            (pin 30) — not connected
    j12[11] += TEMP_AUX       # GP26/ADC0 (pin 31)
    j12[12] += PRESSURE       # GP27/ADC1 (pin 32)
    j12[13] += GND            # AGND      (pin 33)
    j12[14] += ANALOG_IN      # GP28/ADC2 (pin 34)
    j12[15] += VCC3V3         # ADC_VREF  (pin 35) — AMS1117 3V3, ratiometric ref
    # j12[16] = 3V3_OUT        (pin 36) — Pico output, not tied to carrier 3V3
    # j12[17] = 3V3_EN         (pin 37) — not connected
    j12[18] += GND            #           (pin 38)
    j12[19] += VCC5V          # VSYS      (pin 39)
    # j12[20] = VBUS           (pin 40) — USB 5V, not connected

    # ── J13/J14 — RTD breakout sockets (1×8 female 2.54mm, Adafruit pinout) ─
    # Pin 3 (3V3 out from Adafruit regulator) → NC on carrier
    for ref, cs_net, label in [
        ('J13', CS_RTD1, 'RTD1'),
        ('J14', CS_RTD2, 'RTD2'),
    ]:
        j = _PS8()
        j.ref = ref
        j.value = label
        j[1] += VCC3V3        # VIN  — 3V3 to Adafruit VIN
        j[2] += GND           # GND
        # j[3] = 3V3 out      — NC (Adafruit regulator output, not used)
        j[4] += SPI_SCK       # CLK
        j[5] += SPI_MISO      # SDO
        j[6] += SPI_MOSI      # SDI
        j[7] += cs_net        # CS
        # j[8] = DRDY         — NC (no free GPIO; firmware uses SPI polling)


# ---------------------------------------------------------------------------
# Build circuit
# ---------------------------------------------------------------------------
block_power()
block_ssr_drive()
block_mcp23017()
block_leds()
block_level_probes()
block_uart_level_shift()
block_encoder_pullups()
block_ntc()
block_pressure()
block_analog()
block_flow()
block_relay_outputs()
block_connectors()


# ---------------------------------------------------------------------------
# Generate netlist
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    ERC()
    generate_netlist(file_='outputs/faema_carrier.net')
    print('\nNetlist gerada: outputs/faema_carrier.net')
    print('Importar no KiCad PCB Editor: File > Import Netlist')
