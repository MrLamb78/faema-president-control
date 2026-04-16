#!/usr/bin/env python3
"""
place_components_carrier.py — Posicionamento automático dos componentes
da carrier board Rev.6 no KiCad PCB Editor.

Pré-requisito: criar novo projeto KiCad e importar outputs/faema_carrier.net
(File > Import Netlist) antes de rodar este script.

Uso (linha de comando) — requer Python do KiCad + frameworks no DYLD path:
    DYLD_FALLBACK_LIBRARY_PATH=/Applications/KiCad/KiCad.app/Contents/Frameworks \
    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
    kicad/place_components_carrier.py

Ou no console Python do KiCad PCB Editor (com faema-carrier.kicad_pcb aberto):
    exec(open('kicad/place_components_carrier.py').read())

Layout da placa (120 × 95 mm):

  y =  0..22  ┌─ ZONA AC ────────────────────────────────────────────┐
              │  J1(AC in)   RV1(MOV)   U1(HLK-PM05)               │
  y = 22..28  ├─ ISOLAÇÃO 6 mm (sem trilhas DC) ────────────────────┤
  y = 28..93  │  DC                                                  │
              │  x= 0..32   Alimentação + SSR + passivos             │
              │  x=32..44   Pull-ups (botões + encoder)              │
              │  x=44..70   Sockets Pico 2 W (J11, J12)             │
              │  x=72..100  Sockets RTD breakout (J13, J14, J15)    │
              ├─ BORDA INFERIOR (y≈89) ─────────────────────────────┤
              │  J3 J4 J5 J6 J7 J8  (conectores externos, rot=90)   │
              └─────────────────────────────────────────────────────┘
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
    """Linha decorativa no Dwgs.User (separação AC/DC)."""
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.Dwgs_User)
    seg.SetWidth(mm(0.1))
    seg.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
    seg.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
    board.Add(seg)

# ---------------------------------------------------------------------------
# Dimensões da placa
# ---------------------------------------------------------------------------
OX, OY = 50.0, 50.0   # canto superior esquerdo (coordenadas KiCad absolutas)
W,  H  = 120.0, 95.0  # mm


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

    # Linha indicativa de separação AC/DC (y = 28 mm)
    user_line(board, OX, OY + 28, OX + W, OY + 28)

    print('Posicionando componentes...')

    # ════════════════════════════════════════════════════════════════════
    # ZONA AC  (y = 2..20 mm)
    # Fusíveis T16A externos (porta-fusível de painel).
    # J1 recebe L1_fused / L2_fused / PE.
    # ════════════════════════════════════════════════════════════════════
    place(board, 'J1',    6.0,  12.0)          # bornier 3-pin: L1f / L2f / PE
    place(board, 'RV1',  28.0,  11.0)          # MOV S14K275 disc D15.5mm
    place(board, 'U1',   78.0,  12.0)          # HLK-PM05 (~35×22mm)

    # ════════════════════════════════════════════════════════════════════
    # ALIMENTAÇÃO DC  (x = 2..22, y = 30..54)
    # HLK-PM05 → +5V → AMS1117 → +3V3
    # ════════════════════════════════════════════════════════════════════
    place(board, 'C1',    5.0,  31.0)          # 10 µF 5V  bulk  (0805)
    place(board, 'C3',   12.0,  31.0)          # 100 nF 5V bypass (0603)
    place(board, 'U2',    8.0,  41.0)          # AMS1117-3.3 SOT-223
    place(board, 'C2',    5.0,  50.0)          # 10 µF 3V3 bulk  (0805)
    place(board, 'C4',   12.0,  50.0)          # 100 nF 3V3 bypass (0603)

    # ════════════════════════════════════════════════════════════════════
    # DRIVE SSR  (x = 2..22, y = 55..76)
    # GP11 → R2 → Q1 gate   +5V → R1 → SSR+   Q1 drain → SSR−
    # R3 pull-down: garante SSR OFF durante boot/reset do Pico
    # ════════════════════════════════════════════════════════════════════
    place(board, 'R1',    5.0,  57.0)          # 220 Ω  +5V → SSR+
    place(board, 'R2',    7.0,  64.0)          # 100 Ω  gate série
    place(board, 'Q1',   14.0,  64.0)          # 2N7002 SOT-23
    place(board, 'R3',   20.0,  64.0)          # 10 kΩ  gate pull-down
    place(board, 'J2',    5.0,  73.0)          # bornier 2-pin SSR ctrl (+/−)

    # ════════════════════════════════════════════════════════════════════
    # PASSIVOS AUXILIARES  (x = 2..32, y = 77..89)
    # ════════════════════════════════════════════════════════════════════
    place(board, 'D1',    5.0,  79.0)          # LED verde 0603
    place(board, 'R4',   11.0,  79.0)          # 470 Ω  série LED  (GP12)
    place(board, 'R5',   18.0,  79.0)          # 100 kΩ pull-up sonda nível (GP22)

    # Divisor UART: Nextion TX 5 V → 3.0 V → Pico GP1
    place(board, 'R6',    5.0,  86.0)          # 10 kΩ divisor topo
    place(board, 'R7',   11.0,  86.0)          # 15 kΩ divisor base

    # NTC — funciona simultaneamente com RTD (ADC independente do SPI)
    # Layout: R_ref → C_filter (paralelo NTC) → J_ntc
    place(board, 'R8',   22.0,  79.0)          # 2k2 0.1% ref NTC caldeira (GP26)
    place(board, 'C5',   27.0,  79.0)          # 100 nF filtro ADC caldeira
    place(board, 'J9',   33.0,  79.0)          # NTC caldeira JST XH 2-pin
    place(board, 'R9',   22.0,  86.0)          # 2k2 0.1% ref NTC grupo    (GP27)
    place(board, 'C6',   27.0,  86.0)          # 100 nF filtro ADC grupo
    place(board, 'J10',  33.0,  86.0)          # NTC grupo    JST XH 2-pin
    place(board, 'C7',   65.0,  72.0)          # 100 nF bypass ADC_VREF (J12 pin 15) — ratiométrico NTC

    # ════════════════════════════════════════════════════════════════════
    # PULL-UPS  (x = 33..44, y = 30..42)
    # R10–R12: botões preset (BTN1–BTN3)
    # R13–R15: encoder EC11 (CLK, DT, SW)
    # ════════════════════════════════════════════════════════════════════
    place(board, 'R10',  34.0,  31.0)          # 10 kΩ BTN1  (GP19)
    place(board, 'R11',  38.0,  31.0)          # 10 kΩ BTN2  (GP20)
    place(board, 'R12',  42.0,  31.0)          # 10 kΩ BTN3  (GP21)
    place(board, 'R13',  34.0,  37.0)          # 10 kΩ ENC_CLK (GP16)
    place(board, 'R14',  38.0,  37.0)          # 10 kΩ ENC_DT  (GP17)
    place(board, 'R15',  42.0,  37.0)          # 10 kΩ ENC_SW  (GP18)

    # ════════════════════════════════════════════════════════════════════
    # SOCKETS PICO 2 W  (x = 44..68, y = 33..81)
    #
    # J11 = lado esquerdo do Pico (GP0–GP15, pinos 1–20)
    # J12 = lado direito do Pico  (GP16–VSYS, pinos 21–40)
    #
    # Espaçamento entre eixos: 18 mm (nominal Pico: 17.78 mm)
    # 20 pinos × 2.54 mm = 48.26 mm de comprimento
    # Centro em y = 57 → pin 1 em y ≈ 33, pin 20 em y ≈ 81
    #
    # VERIFICAR no KiCad: pin 1 de J11 deve coincidir com GP0 (canto
    # superior do Pico). Rotacionar 180° se necessário.
    # ════════════════════════════════════════════════════════════════════
    place(board, 'J11',  47.0,  57.0)          # 1×20 socket — Pico esquerdo
    place(board, 'J12',  65.0,  57.0)          # 1×20 socket — Pico direito

    # ════════════════════════════════════════════════════════════════════
    # SOCKETS RTD BREAKOUT  (x = 85..95, y = 38..78)
    #
    # SEN-30201 (MAX31865, 33.66×27.94 mm) — 1×8 socket 2.54mm
    # Breakouts plugados perpendiculares à carrier (em Z).
    # Espaçamento 20 mm entre centros. Ajustar se boards físicos
    # precisarem de mais folga lateral.
    # ════════════════════════════════════════════════════════════════════
    place(board, 'J13',  90.0,  38.0)          # RTD caldeira (CS_RTD1 = GP5)
    place(board, 'J14',  90.0,  58.0)          # RTD grupo    (CS_RTD2 = GP6)
    place(board, 'J15',  90.0,  78.0)          # RTD spare    (CS_RTD3 = GP7)

    # ════════════════════════════════════════════════════════════════════
    # CONECTORES EXTERNOS — borda inferior  (y ≈ 89, rot=90)
    # Cabos saem para periféricos fora da caixa.
    # rot=90: conector deitado ao longo do eixo X, acessível pela borda.
    # ════════════════════════════════════════════════════════════════════
    place(board, 'J3',   40.0,  89.0, rot=90)  # encoder EC11 5-pin (CLK/DT/SW/3V3/GND)
    place(board, 'J4',   54.0,  89.0, rot=90)  # botões preset 4-pin (BTN1/2/3/GND)
    place(board, 'J5',   65.0,  89.0, rot=90)  # sonda nível 2-pin
    place(board, 'J6',   73.0,  89.0, rot=90)  # Nextion UART 4-pin (5V/GND/TX/RX)
    place(board, 'J7',   86.0,  89.0, rot=90)  # display SPI alternativo 8-pin
    place(board, 'J8',  101.0,  89.0, rot=90)  # DS3231 I2C breakout 4-pin

    # ── Salvar ────────────────────────────────────────────────────────
    board.Save(PCB_FILE)
    print(f'\nPCB salvo: {PCB_FILE}')
    print('Abrir no KiCad PCB Editor para verificar e rotear.')
    print()
    print('ATENÇÃO: zona AC (y < 28 mm) → clearance mínimo 6 mm para trilhas DC')
    print()
    print('VERIFICAR NO KICAD:')
    print('  • J11 pin 1 = GP0 (topo do Pico) — rotacionar 180° se invertido')
    print('  • J12 pin 1 = GP16 (topo do Pico) — idem')
    print('  • J13–J15: ajustar espaçamento se SEN-30201 precisar de mais folga')
    print('  • J9/J10 (NTC): DNF quando usando breakouts RTD')


if __name__ == '__main__':
    main()
