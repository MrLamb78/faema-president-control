"""
Faema President - Controle de Temperatura Rev.4
Circuito SKiDL — gera netlist para KiCad PCB

Uso:
    pip install skidl
    python -m circuits.faema_president

Saída: faema_president.net (importar no KiCad PCB Editor)
"""

from skidl import *

# ---------------------------------------------------------------------------
# Configuração de bibliotecas KiCad
# ---------------------------------------------------------------------------
KICAD_SYM_DIR = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols'
lib_search_paths[KICAD] = [KICAD_SYM_DIR, '.']

import os
os.environ.setdefault('KICAD8_SYMBOL_DIR', KICAD_SYM_DIR)

# ---------------------------------------------------------------------------
# Templates de partes definidos via SKIDL (independente de libs externas)
# Garante portabilidade sem depender de instalação KiCad no path
# ---------------------------------------------------------------------------

def _make_passive_2pin(name, footprint):
    p = Part(tool=SKIDL, name=name, footprint=footprint, dest=TEMPLATE)
    p += [Pin(num=1, name='~', func=Pin.types.PASSIVE),
          Pin(num=2, name='~', func=Pin.types.PASSIVE)]
    return p

_R     = _make_passive_2pin('R',     'Resistor_SMD:R_0603_1608Metric')
_C_0603 = _make_passive_2pin('C',   'Capacitor_SMD:C_0603_1608Metric')
_C_0805 = _make_passive_2pin('C',   'Capacitor_SMD:C_0805_2012Metric')

_LED = Part(tool=SKIDL, name='LED', footprint='LED_SMD:LED_0603_1608Metric', dest=TEMPLATE)
_LED += [Pin(num=1, name='A', func=Pin.types.PASSIVE),
         Pin(num=2, name='K', func=Pin.types.PASSIVE)]

def _make_conn(n_pins, footprint):
    c = Part(tool=SKIDL, name=f'Conn_{n_pins}', footprint=footprint, dest=TEMPLATE)
    c += [Pin(num=i, name=str(i), func=Pin.types.PASSIVE) for i in range(1, n_pins + 1)]
    return c

_Conn2 = _make_conn(2, 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical')
_Conn3 = _make_conn(3, 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal')
_Conn4 = _make_conn(4, 'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical')
_Conn5 = _make_conn(5, 'Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical')
_Conn6 = _make_conn(6, 'Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical')

_Conn8 = _make_conn(8, 'Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical')

# ---------------------------------------------------------------------------
# Partes customizadas (não disponíveis nas libs KiCad padrão)
# ---------------------------------------------------------------------------

def make_esp32s3_mini():
    """ESP32-S3-MINI-1-N8 — LCSC C2913206"""
    u = Part(tool=SKIDL, name='ESP32_S3_Mini',
             footprint='PCM_Espressif:ESP32-S3-MINI-1',
             dest=TEMPLATE)
    u += [
        Pin(num=1,  name='3V3',           func=Pin.types.PWRIN),
        Pin(num=2,  name='GND',           func=Pin.types.PWRIN),
        Pin(num=3,  name='GPIO3_DRDY',    func=Pin.types.BIDIR),
        Pin(num=4,  name='GPIO4_SSR',     func=Pin.types.OUTPUT),
        Pin(num=5,  name='GPIO5_ENCCLK',  func=Pin.types.BIDIR),
        Pin(num=6,  name='GPIO6_ENCDT',   func=Pin.types.BIDIR),
        Pin(num=7,  name='GPIO7_ENCSW',   func=Pin.types.BIDIR),
        Pin(num=8,  name='GPIO8_SDA',     func=Pin.types.BIDIR),
        Pin(num=9,  name='GPIO9_SCL',     func=Pin.types.BIDIR),
        Pin(num=10, name='GPIO10_SCK',    func=Pin.types.OUTPUT),
        Pin(num=11, name='GPIO11_MOSI',   func=Pin.types.OUTPUT),
        Pin(num=12, name='GPIO12_MISO',   func=Pin.types.INPUT),
        Pin(num=13, name='GPIO13_CSMAX',  func=Pin.types.OUTPUT),
        Pin(num=14, name='GPIO14_CSDISP', func=Pin.types.OUTPUT),
        Pin(num=15, name='GPIO15_DCDISP', func=Pin.types.OUTPUT),
        Pin(num=16, name='GPIO16_RSTDSP', func=Pin.types.OUTPUT),
        Pin(num=17, name='GPIO17_LEVEL',  func=Pin.types.INPUT),
        Pin(num=18, name='GPIO18_CSMAX2', func=Pin.types.OUTPUT),
        Pin(num=19, name='GPIO19_BTN1',   func=Pin.types.INPUT),
        Pin(num=20, name='GPIO20_BTN2',   func=Pin.types.INPUT),
        Pin(num=21, name='GPIO21_BTN3',   func=Pin.types.INPUT),
        Pin(num=22, name='GPIO2_LED',     func=Pin.types.OUTPUT),
        Pin(num=23, name='USB_DP',        func=Pin.types.BIDIR),
        Pin(num=24, name='USB_DN',        func=Pin.types.BIDIR),
        Pin(num=25, name='EN',            func=Pin.types.INPUT),
    ]
    return u()


def make_max31865(ref, value):
    """MAX31865AAP+T — LCSC C779509 — SSOP-20-208mil"""
    u = Part(tool=SKIDL, name='MAX31865',
             footprint='Package_SO:SSOP-20_5.3x7.2mm_P0.65mm',
             dest=TEMPLATE)
    u += [
        Pin(num=1,  name='VDD',     func=Pin.types.PWRIN),
        Pin(num=2,  name='CS',      func=Pin.types.INPUT),
        Pin(num=3,  name='SDI',     func=Pin.types.INPUT),   # MOSI
        Pin(num=4,  name='SDO',     func=Pin.types.TRISTATE),  # MISO — tristate via CS
        Pin(num=5,  name='SCLK',    func=Pin.types.INPUT),
        Pin(num=6,  name='DRDY',    func=Pin.types.OUTPUT),
        Pin(num=7,  name='FORCE_P', func=Pin.types.PASSIVE),
        Pin(num=8,  name='FORCE_N', func=Pin.types.PASSIVE),
        Pin(num=9,  name='GND',     func=Pin.types.PWRIN),
        Pin(num=10, name='RTDIN_P', func=Pin.types.INPUT),
        Pin(num=11, name='RTDIN_N', func=Pin.types.INPUT),
        Pin(num=12, name='REFIN_P', func=Pin.types.INPUT),
        Pin(num=13, name='REFIN_N', func=Pin.types.INPUT),
    ]
    inst = u()
    inst.ref   = ref
    inst.value = value
    return inst


def make_ds3231():
    """DS3231SN# — LCSC C131027 — SOIC-16W"""
    u = Part(tool=SKIDL, name='DS3231',
             footprint='Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm',
             dest=TEMPLATE)
    u += [
        Pin(num=1,  name='32K',   func=Pin.types.OUTPUT),
        Pin(num=2,  name='VCC',   func=Pin.types.PWRIN),
        Pin(num=3,  name='INT_SQW', func=Pin.types.OUTPUT),
        Pin(num=4,  name='GND',   func=Pin.types.PWRIN),
        Pin(num=5,  name='RST',   func=Pin.types.INPUT),
        Pin(num=14, name='VBAT',  func=Pin.types.PWRIN),
        Pin(num=15, name='SDA',   func=Pin.types.BIDIR),
        Pin(num=16, name='SCL',   func=Pin.types.INPUT),
    ]
    return u()


def make_hlk_pm05():
    """HLK-PM05 — 220VAC→5VDC 3W — THT, hand-soldered"""
    u = Part(tool=SKIDL, name='HLK_PM05',
             footprint='Converter_ACDC:Converter_ACDC_Hi-Link_HLK-PMxx',
             dest=TEMPLATE)
    u += [
        Pin(num=1, name='AC_N', func=Pin.types.PASSIVE),
        Pin(num=2, name='AC_L', func=Pin.types.PASSIVE),
        Pin(num=3, name='VO_P', func=Pin.types.PWROUT),
        Pin(num=4, name='VO_N', func=Pin.types.PWRIN),
    ]
    return u()


def make_ams1117():
    """AMS1117-3.3 — LCSC C6186 — SOT-223"""
    u = Part(tool=SKIDL, name='AMS1117_3V3',
             footprint='Package_TO_SOT_SMD:SOT-223-3_TabPin2',
             dest=TEMPLATE)
    u += [
        Pin(num=1, name='GND',  func=Pin.types.PWRIN),
        Pin(num=2, name='VOUT', func=Pin.types.PWROUT),
        Pin(num=3, name='VIN',  func=Pin.types.PWRIN),
    ]
    return u()


# ---------------------------------------------------------------------------
# Nets globais
# ---------------------------------------------------------------------------
VCC3V3    = Net('+3V3')
VCC5V     = Net('+5V')
GND       = Net('GND')
AC_L1     = Net('AC_L1')     # 220V bifásica — fase 1
AC_L2     = Net('AC_L2')     # 220V bifásica — fase 2

SPI_SCK   = Net('SPI_SCK')
SPI_MOSI  = Net('SPI_MOSI')
SPI_MISO  = Net('SPI_MISO')
CS_MAX_CALD  = Net('CS_MAX_CALD')
CS_MAX_GRUPO = Net('CS_MAX_GRUPO')
CS_DISP   = Net('CS_DISP')
DC_DISP   = Net('DC_DISP')
RST_DISP  = Net('RST_DISP')

I2C_SCL   = Net('I2C_SCL')
I2C_SDA   = Net('I2C_SDA')

SSR_CTRL  = Net('SSR_CTRL')
MAX_DRDY  = Net('MAX_DRDY')
LEVEL_SENSE = Net('LEVEL_SENSE')
LED_STATUS  = Net('LED_STATUS')

ENC_CLK   = Net('ENC_CLK')
ENC_DT    = Net('ENC_DT')
ENC_SW    = Net('ENC_SW')
BTN1      = Net('BTN1')
BTN2      = Net('BTN2')
BTN3      = Net('BTN3')

# Nets internas entre blocos
PT100_CALD_FP  = Net('PT100_CALD_FP')   # FORCE+  caldeira
PT100_CALD_FN  = Net('PT100_CALD_FN')   # FORCE-
PT100_CALD_RP  = Net('PT100_CALD_RP')   # RTDIN+
PT100_CALD_RN  = Net('PT100_CALD_RN')   # RTDIN-
PT100_GRUP_FP  = Net('PT100_GRUP_FP')
PT100_GRUP_FN  = Net('PT100_GRUP_FN')
PT100_GRUP_RP  = Net('PT100_GRUP_RP')
PT100_GRUP_RN  = Net('PT100_GRUP_RN')
RREF_CALD_P    = Net('RREF_CALD_P')
RREF_GRUP_P    = Net('RREF_GRUP_P')
AC_L1_FUSED    = Net('AC_L1_FUSED')      # L1 após fusível F1
AC_L2_FUSED    = Net('AC_L2_FUSED')      # L2 após fusível F2
# L1_SWITCHED removido: fiação AC de potência (SSR→caldeira) é totalmente externa à PCB
SSR_CTRL_P     = Net('SSR_CTRL_P')       # R7 output → SSR input (+)
SSR_DRIVE      = Net('SSR_DRIVE')        # Q1 drain → SSR input (−)
Q1_GATE        = Net('Q1_GATE')          # R_gate → Q1 gate
VBAT           = Net('VBAT')             # CR2032 backup


# ---------------------------------------------------------------------------
# BLOCO 1 — AC Power
# ---------------------------------------------------------------------------
@subcircuit
def block_ac_power():
    """J1 (AC screw terminal), F1/F2 (fuses), RV1 (MOV), U2 (HLK-PM05)
    220V bifásica (L1+L2, sem neutro) — fusível em cada fase."""

    # J1 — entrada AC bifásica (L1/L2/PE)
    j1 = _Conn3()
    j1.ref   = 'J1'
    j1.value = 'AC_INPUT_220V'
    j1[1] += AC_L1   # Fase 1
    j1[2] += AC_L2   # Fase 2
    j1[3] += GND     # PE / chassis

    # Template de fusível (reusado por F1 e F2)
    _Fuse = Part(tool=SKIDL, name='Fuse',
                 footprint='Fuse:Fuseholder_Cylinder-5x20mm_Schurter_FAB_0031-355x_Horizontal_Closed',
                 dest=TEMPLATE)
    _Fuse += [Pin(num=1, name='A', func=Pin.types.PASSIVE),
              Pin(num=2, name='K', func=Pin.types.PASSIVE)]

    # F1 — fusível T16A na fase L1
    f1 = _Fuse()
    f1.ref   = 'F1'
    f1.value = 'T16A_SLOW'
    f1[1] += AC_L1
    f1[2] += AC_L1_FUSED

    # F2 — fusível T16A na fase L2
    f2 = _Fuse()
    f2.ref   = 'F2'
    f2.value = 'T16A_SLOW'
    f2[1] += AC_L2
    f2[2] += AC_L2_FUSED

    # RV1 — MOV S14K275 entre as linhas fusíveis (proteção diferencial)
    rv1 = Part(tool=SKIDL, name='Varistor',
               footprint='Varistor:RV_Disc_D15.5mm_W5mm_P7.5mm',
               dest=TEMPLATE)
    rv1 += [Pin(num=1, name='1', func=Pin.types.PASSIVE),
            Pin(num=2, name='2', func=Pin.types.PASSIVE)]
    rv1 = rv1()
    rv1.ref   = 'RV1'
    rv1.value = 'S14K275'
    rv1[1] += AC_L1_FUSED
    rv1[2] += AC_L2_FUSED

    # U2 — HLK-PM05
    u2 = make_hlk_pm05()
    u2.ref   = 'U2'
    u2.value = 'HLK-PM05'
    u2['AC_L'] += AC_L1_FUSED
    u2['AC_N'] += AC_L2_FUSED
    u2['VO_P'] += VCC5V
    u2['VO_N'] += GND

    # J2 removido: toda a fiação AC de potência (SSR→caldeira) fica
    # externa à PCB em cabo 2.5mm². Não rotear 11A pela placa.


# ---------------------------------------------------------------------------
# BLOCO 2 — Regulação DC (5V → 3.3V)
# ---------------------------------------------------------------------------
@subcircuit
def block_dc_regulation():
    """U3 (AMS1117-3.3), C1-C4 (bulk e bypass)"""

    u3 = make_ams1117()
    u3.ref   = 'U3'
    u3.value = 'AMS1117-3.3'
    u3['VIN']  += VCC5V
    u3['VOUT'] += VCC3V3
    u3['GND']  += GND

    # C1 — bulk 10µF 16V 0805 na entrada 5V
    c1 = _C_0805()
    c1.ref   = 'C1'
    c1.value = '10uF_16V_X5R'
    c1[1] += VCC5V
    c1[2] += GND

    # C2 — bulk 10µF 10V 0805 na saída 3V3
    c2 = _C_0805()
    c2.ref   = 'C2'
    c2.value = '10uF_10V_X5R'
    c2[1] += VCC3V3
    c2[2] += GND

    # C3 — 100nF 0603 X7R na entrada U3 (5V)
    c3 = _C_0603()
    c3.ref   = 'C3'
    c3.value = '100nF_50V_X7R'
    c3[1] += VCC5V
    c3[2] += GND

    # C4 — 100nF 0603 X7R na saída U3 (3V3)
    c4 = _C_0603()
    c4.ref   = 'C4'
    c4.value = '100nF_50V_X7R'
    c4[1] += VCC3V3
    c4[2] += GND


# ---------------------------------------------------------------------------
# BLOCO 3 — MCU (ESP32-S3-MINI-1-N8)
# ---------------------------------------------------------------------------
@subcircuit
def block_mcu():
    """U1 (ESP32-S3-MINI-1-N8), C9 (bypass VDD)"""

    u1 = make_esp32s3_mini()
    u1.ref   = 'U1'
    u1.value = 'ESP32-S3-MINI-1-N8'

    u1['3V3']           += VCC3V3
    u1['GND']           += GND
    u1['GPIO10_SCK']    += SPI_SCK
    u1['GPIO11_MOSI']   += SPI_MOSI
    u1['GPIO12_MISO']   += SPI_MISO
    u1['GPIO13_CSMAX']  += CS_MAX_CALD
    u1['GPIO18_CSMAX2'] += CS_MAX_GRUPO
    u1['GPIO14_CSDISP'] += CS_DISP
    u1['GPIO15_DCDISP'] += DC_DISP
    u1['GPIO16_RSTDSP'] += RST_DISP
    u1['GPIO8_SDA']     += I2C_SDA
    u1['GPIO9_SCL']     += I2C_SCL
    u1['GPIO4_SSR']     += SSR_CTRL
    u1['GPIO3_DRDY']    += MAX_DRDY
    u1['GPIO17_LEVEL']  += LEVEL_SENSE
    u1['GPIO2_LED']     += LED_STATUS
    u1['GPIO5_ENCCLK']  += ENC_CLK
    u1['GPIO6_ENCDT']   += ENC_DT
    u1['GPIO7_ENCSW']   += ENC_SW
    u1['GPIO19_BTN1']   += BTN1
    u1['GPIO20_BTN2']   += BTN2
    u1['GPIO21_BTN3']   += BTN3
    u1['EN']            += VCC3V3   # EN puxado para VCC via pull-up interno
    u1['USB_DP']        += NC(drive=True)
    u1['USB_DN']        += NC(drive=True)

    # C9 — bypass 100nF no VDD do ESP32
    c9 = _C_0603()
    c9.ref   = 'C9'
    c9.value = '100nF_50V_X7R'
    c9[1] += VCC3V3
    c9[2] += GND


# ---------------------------------------------------------------------------
# BLOCO 4 — RTD Caldeira (MAX31865 U4)
# ---------------------------------------------------------------------------
@subcircuit
def block_rtd_boiler():
    """U4 (MAX31865), Rref (430R 0.1%), J3 (PT100 4-wire), C7/C10 (bypass)"""

    u4 = make_max31865('U4', 'MAX31865_CALDEIRA')

    u4['VDD']     += VCC3V3
    u4['GND']     += GND
    u4['CS']      += CS_MAX_CALD
    u4['SDI']     += SPI_MOSI
    u4['SDO']     += SPI_MISO
    u4['SCLK']    += SPI_SCK
    u4['DRDY']    += MAX_DRDY
    u4['FORCE_P'] += PT100_CALD_FP
    u4['FORCE_N'] += PT100_CALD_FN
    u4['RTDIN_P'] += PT100_CALD_RP
    u4['RTDIN_N'] += PT100_CALD_RN
    u4['REFIN_P'] += RREF_CALD_P
    u4['REFIN_N'] += PT100_CALD_FN   # REFIN- = FORCE- para 4 fios

    # Rref — 430Ω 0.1% 25ppm 0603 (LCSC C666878)
    rref = _R()
    rref.ref   = 'Rref'
    rref.value = '430R_0.1pct'
    rref[1] += RREF_CALD_P
    rref[2] += PT100_CALD_FN

    # J3 — conector PT100 caldeira (4 pinos: F+, R+, R-, F-)
    j3 = _Conn4()
    j3.ref   = 'J3'
    j3.value = 'PT100_CALDEIRA'
    j3[1] += PT100_CALD_FP
    j3[2] += PT100_CALD_RP
    j3[3] += PT100_CALD_RN
    j3[4] += PT100_CALD_FN

    # C7 — 100nF bypass RTDIN filter
    c7 = _C_0603()
    c7.ref   = 'C7'
    c7.value = '100nF_50V_X7R'
    c7[1] += PT100_CALD_RP
    c7[2] += PT100_CALD_RN

    # C10 — 100nF VDD bypass U4
    c10 = _C_0603()
    c10.ref   = 'C10'
    c10.value = '100nF_50V_X7R'
    c10[1] += VCC3V3
    c10[2] += GND


# ---------------------------------------------------------------------------
# BLOCO 5 — RTD Grupo (MAX31865 U6)
# ---------------------------------------------------------------------------
@subcircuit
def block_rtd_group():
    """U6 (MAX31865), Rref2 (430R 0.1%), J6 (PT100 4-wire), C11/C12 (bypass)"""

    u6 = make_max31865('U6', 'MAX31865_GRUPO')

    u6['VDD']     += VCC3V3
    u6['GND']     += GND
    u6['CS']      += CS_MAX_GRUPO
    u6['SDI']     += SPI_MOSI
    u6['SDO']     += SPI_MISO
    u6['SCLK']    += SPI_SCK
    u6['DRDY']    += NC(drive=True)   # DRDY grupo: não conectado (polling por CS)
    u6['FORCE_P'] += PT100_GRUP_FP
    u6['FORCE_N'] += PT100_GRUP_FN
    u6['RTDIN_P'] += PT100_GRUP_RP
    u6['RTDIN_N'] += PT100_GRUP_RN
    u6['REFIN_P'] += RREF_GRUP_P
    u6['REFIN_N'] += PT100_GRUP_FN

    # Rref2
    rref2 = _R()
    rref2.ref   = 'Rref2'
    rref2.value = '430R_0.1pct'
    rref2[1] += RREF_GRUP_P
    rref2[2] += PT100_GRUP_FN

    # J6 — conector PT100 grupo
    j6 = _Conn4()
    j6.ref   = 'J6'
    j6.value = 'PT100_GRUPO'
    j6[1] += PT100_GRUP_FP
    j6[2] += PT100_GRUP_RP
    j6[3] += PT100_GRUP_RN
    j6[4] += PT100_GRUP_FN

    # C11 — bypass RTDIN filter
    c11 = _C_0603()
    c11.ref   = 'C11'
    c11.value = '100nF_50V_X7R'
    c11[1] += PT100_GRUP_RP
    c11[2] += PT100_GRUP_RN

    # C12 — VDD bypass U6
    c12 = _C_0603()
    c12.ref   = 'C12'
    c12.value = '100nF_50V_X7R'
    c12[1] += VCC3V3
    c12[2] += GND


# ---------------------------------------------------------------------------
# BLOCO 6 — Acionamento SSR (low-side NMOS drive)
# ---------------------------------------------------------------------------
@subcircuit
def block_ssr_drive():
    """Topologia: GPIO4→R_gate(100Ω)→Q1 gate ; R9(10kΩ) gate→GND ;
    +5V→R7(220Ω)→SSR_CTRL_P=SSR+(J10p1) ; Q1 drain=SSR_DRIVE=SSR-(J10p2) ; Q1 source→GND
    GPIO4 HIGH → Q1 ON → corrente via R7 → SSR ON (lógica direta)"""

    # R_gate — 100 Ω série entre GPIO4 e gate do Q1 (limita corrente de gate)
    r_gate = _R()
    r_gate.ref   = 'R_gate'
    r_gate.value = '100R_1pct'
    r_gate[1] += SSR_CTRL      # GPIO4
    r_gate[2] += Q1_GATE

    # R9 — pull-down 10 kΩ: mantém Q1 desligado durante boot/reset do ESP32
    r9 = _R()
    r9.ref   = 'R9'
    r9.value = '10k_1pct'
    r9[1] += Q1_GATE
    r9[2] += GND

    # Q1 — 2N7002 NMOS SOT-23: low-side switch do SSR-40DA
    q1 = Part(tool=SKIDL, name='2N7002',
              footprint='Package_TO_SOT_SMD:SOT-23',
              dest=TEMPLATE)
    q1 += [Pin(num=1, name='S',  func=Pin.types.PASSIVE),   # source
           Pin(num=2, name='G',  func=Pin.types.INPUT),     # gate
           Pin(num=3, name='D',  func=Pin.types.PASSIVE)]   # drain
    q1 = q1()
    q1.ref   = 'Q1'
    q1.value = '2N7002'
    q1['G'] += Q1_GATE
    q1['S'] += GND
    q1['D'] += SSR_DRIVE       # drain → SSR input (−)

    # R7 — 220 Ω de +5V para SSR input (+); ~17 mA drive (min 7.5 mA)
    r7 = _R()
    r7.ref   = 'R7'
    r7.value = '220R_1pct'
    r7[1] += VCC5V
    r7[2] += SSR_CTRL_P        # SSR input (+)

    # J10 — bornier 2 pinos para SSR-40DA externo (CTRL+ e CTRL-)
    j10 = Part(tool=SKIDL, name='Conn_SSR',
               footprint='TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal',
               dest=TEMPLATE)
    j10 += [Pin(num=1, name='CTRL_P', func=Pin.types.PASSIVE),
            Pin(num=2, name='CTRL_N', func=Pin.types.PASSIVE)]
    j10 = j10()
    j10.ref   = 'J10'
    j10.value = 'SSR_CTRL_HEADER'
    j10[1] += SSR_CTRL_P       # SSR input (+): +5V via R7
    j10[2] += SSR_DRIVE        # SSR input (−): Q1 drain


# ---------------------------------------------------------------------------
# BLOCO 7 — Sonda de Nível
# ---------------------------------------------------------------------------
@subcircuit
def block_level_sense():
    """J7 (sonda condutividade), R11 (100kΩ pull-up)"""

    # R11 — pull-up 100kΩ para VCC3V3 (limita corrente eletrólise)
    r11 = _R()
    r11.ref   = 'R11'
    r11.value = '100k_1pct'
    r11[1] += VCC3V3
    r11[2] += LEVEL_SENSE

    # J7 — conector 2 pinos (sonda e GND)
    j7 = _Conn2()
    j7.ref   = 'J7'
    j7.value = 'SONDA_NIVEL'
    j7[1] += LEVEL_SENSE
    j7[2] += GND


# ---------------------------------------------------------------------------
# BLOCO 8 — RTC (DS3231)
# ---------------------------------------------------------------------------
@subcircuit
def block_rtc():
    """U5 (DS3231), BT1 (CR2032), R2/R3 (I2C pull-ups), C8 (bypass VCC)"""

    u5 = make_ds3231()
    u5.ref   = 'U5'
    u5.value = 'DS3231SN'

    u5['VCC']     += VCC3V3
    u5['GND']     += GND
    u5['SDA']     += I2C_SDA
    u5['SCL']     += I2C_SCL
    u5['VBAT']    += VBAT
    u5['RST']     += VCC3V3   # RST puxado alto (sem uso)
    u5['INT_SQW'] += NC(drive=True)
    u5['32K']     += NC(drive=True)

    # BT1 — CR2032 holder
    bt1 = Part(tool=SKIDL, name='BatteryHolder',
               footprint='Battery:BatteryHolder_Keystone_3002_1x2032',
               dest=TEMPLATE)
    bt1 += [Pin(num=1, name='BAT_P', func=Pin.types.PWROUT),
            Pin(num=2, name='BAT_N', func=Pin.types.PWRIN)]
    bt1 = bt1()
    bt1.ref   = 'BT1'
    bt1.value = 'CR2032'
    bt1[1] += VBAT
    bt1[2] += GND

    # R2 — pull-up I2C SDA (4.7kΩ)
    r2 = _R()
    r2.ref   = 'R2'
    r2.value = '4k7_1pct'
    r2[1] += VCC3V3
    r2[2] += I2C_SDA

    # R3 — pull-up I2C SCL (4.7kΩ)
    r3 = _R()
    r3.ref   = 'R3'
    r3.value = '4k7_1pct'
    r3[1] += VCC3V3
    r3[2] += I2C_SCL

    # C8 — bypass 100nF VCC do DS3231
    c8 = _C_0603()
    c8.ref   = 'C8'
    c8.value = '100nF_50V_X7R'
    c8[1] += VCC3V3
    c8[2] += GND


# ---------------------------------------------------------------------------
# BLOCO 9 — Display ILI9341 2.4"
# ---------------------------------------------------------------------------
@subcircuit
def block_display():
    """J5 (8-pin 2.54mm header — cabo do módulo ILI9341 2.4")
    Pinout: VCC / GND / CS / RST / DC / MOSI / SCK / LED"""

    j5 = _Conn8()
    j5.ref   = 'J5'
    j5.value = 'ILI9341_2.4_HEADER'

    j5[1] += VCC3V3     # VCC
    j5[2] += GND        # GND
    j5[3] += CS_DISP    # CS   — GPIO14
    j5[4] += RST_DISP   # RST  — GPIO16
    j5[5] += DC_DISP    # DC   — GPIO15
    j5[6] += SPI_MOSI   # MOSI — GPIO11
    j5[7] += SPI_SCK    # SCK  — GPIO10
    j5[8] += VCC3V3     # LED (backlight sempre ligado via 3V3)


# ---------------------------------------------------------------------------
# BLOCO 10 — Interface de Usuário (Encoder + Botões + LED)
# ---------------------------------------------------------------------------
@subcircuit
def block_ui():
    """J9 (encoder off-board), J8 (botões preset), D1 (LED), R10/R12/R13/R14"""

    # J9 — encoder EC11 off-board (5-pin header: ENC_CLK/ENC_DT/ENC_SW/3V3/GND)
    j9 = _Conn5()
    j9.ref   = 'J9'
    j9.value = 'ENCODER_EC11'
    j9[1] += ENC_CLK
    j9[2] += ENC_DT
    j9[3] += ENC_SW
    j9[4] += VCC3V3
    j9[5] += GND

    # J8 — painel de botões (6 pinos: BTN1/BTN2/BTN3 + 3V3 + GND + GND)
    j8 = _Conn6()
    j8.ref   = 'J8'
    j8.value = 'BOTOES_PRESET'
    j8[1] += BTN1
    j8[2] += BTN2
    j8[3] += BTN3
    j8[4] += VCC3V3
    j8[5] += GND
    j8[6] += GND

    # R12/R13/R14 — pull-ups 10kΩ para os botões (active LOW)
    for ref, net in [('R12', BTN1), ('R13', BTN2), ('R14', BTN3)]:
        r = _R()
        r.ref   = ref
        r.value = '10k_1pct'
        r[1] += VCC3V3
        r[2] += net

    # D1 — LED status verde 0603
    d1 = _LED()
    d1.ref   = 'D1'
    d1.value = 'LED_GREEN'
    D1_A = Net('D1_A')
    d1['A'] += D1_A
    d1['K'] += GND

    # R10 — 470Ω série para D1 (≈6mA com 3V3)
    r10 = _R()
    r10.ref   = 'R10'
    r10.value = '470R_1pct'
    r10[1] += LED_STATUS
    r10[2] += D1_A


# ---------------------------------------------------------------------------
# Instancia todos os blocos
# ---------------------------------------------------------------------------
block_ac_power()
block_dc_regulation()
block_mcu()
block_rtd_boiler()
block_rtd_group()
block_ssr_drive()
block_level_sense()
block_rtc()
block_display()
block_ui()

# ---------------------------------------------------------------------------
# ERC + geração de netlist
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    ERC()
    generate_netlist(file_='outputs/faema_president.net')
    print("Netlist gerada em outputs/faema_president.net")
    print("Importar no KiCad PCB Editor: File > Import Netlist")
