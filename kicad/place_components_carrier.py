#!/usr/bin/env python3
"""
place_components_carrier.py — Posicionamento automático Rev.7
carrier board genérica para controlador de espresso.

Pré-requisito: criar projeto KiCad e importar outputs/faema_carrier.net
(File > Import Netlist) antes de rodar este script.

Uso (linha de comando):
    DYLD_FALLBACK_LIBRARY_PATH=/Applications/KiCad/KiCad.app/Contents/Frameworks \
    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
    kicad/place_components_carrier.py

Ou no console Python do KiCad PCB Editor (com faema-carrier.kicad_pcb aberto):
    exec(open('kicad/place_components_carrier.py').read())

Layout da placa (150 × 110 mm):

  y =  0..25  ┌─ ZONA AC ──────────────────────────────────────────────────────┐
              │  J1(AC)   RV1(MOV)                        U1(HLK-PM05)        │
  y = 25..31  ├─ ISOLAÇÃO 6 mm ──────────────────────────────────────────────── ┤
  y = 31..106 │  DC                                                             │
              │  x= 2..24  Alimentação (U2, C1-C4) + SSR1/SSR2 (Q1/Q2) + UART  │
              │  x=25..47  MCP23017 (U3) + I2C pull-ups + LEDs D1-D5            │
              │  x=47..74  Sockets Pico 2W (J11, J12) + passivos adjacentes     │
              │  x=74..100 RTD sockets (J13, J14) + NTC + pressão + fluxômetro  │
              │  x=100..148 Nível (J15a/b) + relés J21-J24 + pot/bomba          │
              ├─ BORDA INFERIOR (y≈107, rot=90) ─────────────────────────────── ┤
              │  J3 J4 J6 J7 J8 J16 J17 J18 J19 J20                            │
              └────────────────────────────────────────────────────────────────┘
  Borda direita (rot=0): J21 J22 J23 J24 (relay outputs)
"""

import sys, os

KICAD_PY = (
    '/Applications/KiCad/KiCad.app/Contents/Frameworks/'
    'Python.framework/Versions/3.9/lib/python3.9/site-packages'
)
if KICAD_PY not in sys.path:
    sys.path.insert(0, KICAD_PY)

import pcbnew

try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    SCRIPT_DIR = os.path.dirname(pcbnew.GetBoard().GetFileName())
PCB_FILE = os.path.join(SCRIPT_DIR, 'faema-carrier', 'faema-carrier.kicad_pcb')

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
OX, OY = 50.0, 50.0   # canto superior esquerdo (coordenadas KiCad absolutas)
W,  H  = 150.0, 110.0  # mm

def mm(v):
    return pcbnew.FromMM(float(v))

def place(board, ref, x, y, rot=0):
    fp = board.FindFootprintByReference(ref)
    if fp is None:
        print(f'  AVISO: {ref} não encontrado — ignorando')
        return
    fp.SetPosition(pcbnew.VECTOR2I(mm(OX + x), mm(OY + y)))
    fp.SetOrientationDegrees(rot)
    print(f'  {ref:<10} ({x:6.1f}, {y:6.1f})  rot={rot}°')

def edge_line(board, x1, y1, x2, y2):
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetWidth(mm(0.05))
    seg.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
    seg.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
    board.Add(seg)

def user_line(board, x1, y1, x2, y2):
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.Dwgs_User)
    seg.SetWidth(mm(0.1))
    seg.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
    seg.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
    board.Add(seg)


def main():
    if os.path.exists(PCB_FILE):
        print(f'Carregando: {PCB_FILE}')
        board = pcbnew.LoadBoard(PCB_FILE)
    else:
        print(f'Criando nova board: {PCB_FILE}')
        board = pcbnew.BOARD()
        board.SetFileName(PCB_FILE)

    # ── Borda da placa ────────────────────────────────────────────────────
    print(f'Desenhando borda ({W}×{H} mm)...')
    corners = [(OX,     OY    ),
               (OX + W, OY    ),
               (OX + W, OY + H),
               (OX,     OY + H)]
    for i in range(4):
        x1, y1 = corners[i]
        x2, y2 = corners[(i + 1) % 4]
        edge_line(board, x1, y1, x2, y2)

    # Linha indicativa separação AC/DC (y = 28 mm)
    user_line(board, OX, OY + 28, OX + W, OY + 28)

    print('Posicionando componentes...')

    # ════════════════════════════════════════════════════════════════════
    # ZONA AC  (y = 2..22)
    # ════════════════════════════════════════════════════════════════════
    place(board, 'J1',   8.0,  12.0)           # bornier 3-pin AC in (L1/L2/PE)
    place(board, 'RV1', 28.0,  12.0)           # MOV S14K275 disc
    place(board, 'U1',  95.0,  12.0)           # HLK-PM05 (~35×22 mm)

    # ════════════════════════════════════════════════════════════════════
    # ALIMENTAÇÃO DC  (x = 2..22, y = 32..55)
    # ════════════════════════════════════════════════════════════════════
    place(board, 'C1',   5.0,  33.0)           # 10 µF 5V  (0805)
    place(board, 'C3',  12.0,  33.0)           # 100 nF 5V (0603)
    place(board, 'U2',   8.0,  42.0)           # AMS1117-3.3 SOT-223
    place(board, 'C2',   5.0,  51.0)           # 10 µF 3V3 (0805)
    place(board, 'C4',  12.0,  51.0)           # 100 nF 3V3 (0603)

    # ════════════════════════════════════════════════════════════════════
    # DRIVE SSR1  (x = 2..24, y = 57..73)
    # ════════════════════════════════════════════════════════════════════
    place(board, 'R1',   5.0,  58.0)           # 220 Ω  +5V → SSR1+
    place(board, 'R3',  11.0,  65.0)           # 100 Ω  gate série Q1
    place(board, 'R5',  20.0,  65.0)           # 10 kΩ  gate pull-down Q1
    place(board, 'Q1',  16.0,  65.0)           # 2N7002 SOT-23
    place(board, 'J2a',  5.0,  71.0)           # bornier 2-pin SSR1

    # ════════════════════════════════════════════════════════════════════
    # DRIVE SSR2  (x = 2..24, y = 75..91)
    # ════════════════════════════════════════════════════════════════════
    place(board, 'R2',   5.0,  76.0)           # 220 Ω  +5V → SSR2+
    place(board, 'R4',  11.0,  83.0)           # 100 Ω  gate série Q2
    place(board, 'R6',  20.0,  83.0)           # 10 kΩ  gate pull-down Q2
    place(board, 'Q2',  16.0,  83.0)           # 2N7002 SOT-23
    place(board, 'J2b',  5.0,  89.0)           # bornier 2-pin SSR2

    # ════════════════════════════════════════════════════════════════════
    # DIVISOR UART  (x = 2..18, y = 95..101)
    # Nextion TX 5V → R16 → R17 → GND  → Pico GP1 (3.0V)
    # ════════════════════════════════════════════════════════════════════
    place(board, 'R16',  5.0,  96.0)           # 10 kΩ divisor topo
    place(board, 'R17', 12.0,  96.0)           # 15 kΩ divisor base

    # ════════════════════════════════════════════════════════════════════
    # MCP23017  (x = 26..44, y = 33..72)
    # ════════════════════════════════════════════════════════════════════
    place(board, 'R7',  27.0,  35.0)           # 4k7 pull-up I2C SDA
    place(board, 'R8',  33.0,  35.0)           # 4k7 pull-up I2C SCL
    place(board, 'C5',  27.0,  42.0)           # 100 nF bypass VDD MCP23017
    place(board, 'U3',  35.0,  55.0)           # MCP23017 SOIC-28 (~7.5×17.9 mm)

    # ════════════════════════════════════════════════════════════════════
    # LEDs D1–D5  (x = 26..46, y = 66..76)
    # Driven by MCP23017 GPA7/GPB4-7 via series resistors
    # ════════════════════════════════════════════════════════════════════
    for i, (rx, dx) in enumerate([(26, 26), (31, 31), (36, 36), (41, 41), (46, 46)], start=1):
        place(board, f'R{8 + i}',  rx,  66.0)  # R9–R13  470 Ω
        place(board, f'D{i}',      dx,  73.0)  # D1–D5   LED 0603

    # ════════════════════════════════════════════════════════════════════
    # ENCODER PULL-UPS  (x = 26..38, y = 80..86)
    # ════════════════════════════════════════════════════════════════════
    place(board, 'R18', 27.0,  83.0)           # 10 kΩ ENC_CLK (GP16)
    place(board, 'R19', 33.0,  83.0)           # 10 kΩ ENC_DT  (GP17)
    place(board, 'R20', 39.0,  83.0)           # 10 kΩ ENC_SW  (GP18)

    # ════════════════════════════════════════════════════════════════════
    # SOCKETS PICO 2W  (x = 47..74, y = 35..83)
    # J11 (left, GP0-GP15, pinos 1-20): centro em x=50
    # J12 (right, GP16-VSYS, pinos 21-40): centro em x=68
    # 20 pinos × 2.54 mm = 48.26 mm → pin 1 em y≈35, pin 20 em y≈83
    # VERIFICAR no KiCad: pin 1 = GP0/GP16 (topo do Pico)
    # ════════════════════════════════════════════════════════════════════
    place(board, 'J11', 50.0,  59.0)           # 1×20 socket Pico esquerdo
    place(board, 'J12', 68.0,  59.0)           # 1×20 socket Pico direito

    # ADC_VREF bypass — perto de J12 pin 15 (pino físico 35 do Pico)
    place(board, 'C7',  69.0,  71.0)           # 100 nF ADC_VREF (ratiométrico)

    # ════════════════════════════════════════════════════════════════════
    # SOCKETS RTD  (x = 76..84, y = 37..67)
    # 1×8 socket 2.54mm — pinout Adafruit
    # 8 pinos × 2.54 mm = 17.78 mm → pin 1 em y≈37, pin 8 em y≈55
    # VERIFICAR: pin 1 (VIN) deve corresponder ao pino 1 do breakout Adafruit
    # ════════════════════════════════════════════════════════════════════
    place(board, 'J13', 80.0,  46.0)           # RTD1 socket (CS_RTD1 = GP5)
    place(board, 'J14', 80.0,  64.0)           # RTD2 socket (CS_RTD2 = GP6)

    # ════════════════════════════════════════════════════════════════════
    # NTC TEMP_AUX  (x = 74..92, y = 70..80)
    # DNF se não usar sensor NTC
    # ════════════════════════════════════════════════════════════════════
    place(board, 'R21', 76.0,  74.0)           # 2k2 0.1% ref NTC (GP26/ADC0)
    place(board, 'C6',  82.0,  74.0)           # 100 nF filtro ADC

    # ════════════════════════════════════════════════════════════════════
    # SENSOR DE PRESSÃO  (x = 86..106, y = 55..72)
    # Divisor R22/R23: 4.5V → 3.21V para ADC GP27
    # ════════════════════════════════════════════════════════════════════
    place(board, 'R22',  88.0,  59.0)          # 33 kΩ divisor topo
    place(board, 'R23',  94.0,  59.0)          # 82 kΩ divisor base
    place(board, 'C8',  100.0,  59.0)          # 100 nF filtro ADC

    # ════════════════════════════════════════════════════════════════════
    # FLUXÔMETRO  (x = 86..106, y = 76..88)
    # ════════════════════════════════════════════════════════════════════
    place(board, 'R25',  88.0,  80.0)          # 10 kΩ pull-up PULSE_IN (GP21)
    place(board, 'C9',   94.0,  80.0)          # 10 nF debounce

    # ════════════════════════════════════════════════════════════════════
    # CONTROLE BOMBA  (x = 88..108, y = 90..100)
    # ════════════════════════════════════════════════════════════════════
    place(board, 'R24',  90.0,  94.0)          # 100 Ω proteção saída PUMP_CTRL

    # ════════════════════════════════════════════════════════════════════
    # SONDAS DE NÍVEL  (x = 108..128, y = 33..52)
    # ════════════════════════════════════════════════════════════════════
    place(board, 'R14', 110.0,  37.0)          # 100 kΩ pull-up LEVEL1
    place(board, 'R15', 110.0,  47.0)          # 100 kΩ pull-up LEVEL2

    # ════════════════════════════════════════════════════════════════════
    # SAÍDAS RELÉ J21–J24  (borda direita, rot=0)
    # VCC/SIGNAL/GND para placas de relé externas
    # ════════════════════════════════════════════════════════════════════
    place(board, 'J21', 144.0,  40.0, rot=0)   # OUT1
    place(board, 'J22', 144.0,  52.0, rot=0)   # OUT2
    place(board, 'J23', 144.0,  64.0, rot=0)   # OUT3
    place(board, 'J24', 144.0,  76.0, rot=0)   # OUT4

    # ════════════════════════════════════════════════════════════════════
    # CONECTORES EXTERNOS — borda inferior  (y ≈ 107, rot=90)
    # Cabos de conexão aos periféricos externos
    # ════════════════════════════════════════════════════════════════════
    place(board, 'J3',   16.0, 107.0, rot=90)  # encoder EC11 5-pin
    place(board, 'J4',   31.0, 107.0, rot=90)  # botões 5-pin (→ MCP23017)
    place(board, 'J6',   46.0, 107.0, rot=90)  # Nextion UART 4-pin
    place(board, 'J7',   61.0, 107.0, rot=90)  # SPI display 8-pin (opcional)
    place(board, 'J8',   78.0, 107.0, rot=90)  # I2C RTC DS3231 4-pin
    place(board, 'J15a', 91.0, 107.0, rot=90)  # LEVEL1 sonda nível 2-pin
    place(board, 'J15b', 99.0, 107.0, rot=90)  # LEVEL2 sonda nível 2-pin
    place(board, 'J16', 108.0, 107.0, rot=90)  # fluxômetro 3-pin
    place(board, 'J17', 118.0, 107.0, rot=90)  # NTC TEMP_AUX 2-pin
    place(board, 'J18', 127.0, 107.0, rot=90)  # pressão 3-pin
    place(board, 'J19', 137.0, 107.0, rot=90)  # potenciômetro 3-pin
    place(board, 'J20', 146.0, 107.0, rot=90)  # bomba PUMP_CTRL 2-pin

    # ── Salvar ────────────────────────────────────────────────────────
    board.Save(PCB_FILE)
    print(f'\nPCB salvo: {PCB_FILE}')
    print('Abrir no KiCad PCB Editor para verificar e rotear.')
    print()
    print('ATENÇÃO:')
    print('  • Zona AC (y < 28 mm) → clearance mínimo 6 mm para trilhas DC')
    print()
    print('VERIFICAR NO KICAD:')
    print('  • J11 pin 1 = GP0, J12 pin 1 = GP16 — rotacionar 180° se invertido')
    print('  • J13/J14 pin 1 = VIN — conferir orientação do breakout Adafruit')
    print('  • D1-D5: conferir polaridade (cátodo K para GND)')
    print('  • J21-J24 (borda direita): ajustar rotação se necessário')
    print('  • R21/C6/J17 (NTC): DNF se não usar sensor NTC')


if __name__ == '__main__':
    main()
