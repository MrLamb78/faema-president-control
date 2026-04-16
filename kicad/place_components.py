#!/usr/bin/env python3
"""
place_components.py — Posicionamento automático dos componentes no PCB.

Usa a API pcbnew do KiCad para posicionar todos os componentes e criar
a borda da placa. Roda APÓS importar a netlist no KiCad PCB Editor.

Uso (linha de comando) — requer Python do KiCad + frameworks no DYLD path:
    DYLD_FALLBACK_LIBRARY_PATH=/Applications/KiCad/KiCad.app/Contents/Frameworks \
    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
    kicad/place_components.py

Ou no console Python do KiCad PCB Editor:
    exec(open('kicad/place_components.py').read())
"""

import sys, os

# Localizar pcbnew no KiCad macOS
KICAD_PY = (
    '/Applications/KiCad/KiCad.app/Contents/Frameworks/'
    'Python.framework/Versions/3.9/lib/python3.9/site-packages'
)
if KICAD_PY not in sys.path:
    sys.path.insert(0, KICAD_PY)

import pcbnew

# Funciona tanto na linha de comando quanto no console Python do KiCad
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # No console do KiCad __file__ não existe — usa o diretório do .kicad_pcb aberto
    SCRIPT_DIR = os.path.dirname(pcbnew.GetBoard().GetFileName())
PCB_FILE = os.path.join(SCRIPT_DIR, 'faema-president.kicad_pcb')

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
    print(f'  {ref:<10} ({x:5.1f}, {y:5.1f})  rot={rot}°')

def edge_line(board, x1, y1, x2, y2):
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetWidth(mm(0.05))
    seg.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
    seg.SetEnd(pcbnew.VECTOR2I(mm(x2),   mm(y2)))
    board.Add(seg)

def courtyard_line(board, x1, y1, x2, y2):
    """Linha de separação AC/DC no layer Dwgs.User."""
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.Dwgs_User)
    seg.SetWidth(mm(0.1))
    seg.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
    seg.SetEnd(pcbnew.VECTOR2I(mm(x2),   mm(y2)))
    board.Add(seg)

# ---------------------------------------------------------------------------
# Origem da placa (canto superior esquerdo em coordenadas KiCad absolutas)
# ---------------------------------------------------------------------------
OX, OY = 50.0, 50.0   # mm
W,  H  = 90.0, 80.0   # mm — tamanho da placa

# ---------------------------------------------------------------------------
# Coordenadas relativas (0,0 = canto sup-esq da placa)
#
# Divisão vertical:
#   y =  0–22  →  ZONA AC (J1, F1, RV1, U2, J2)
#   y = 22–28  →  FAIXA DE ISOLAÇÃO 6mm (proibido trilhas DC)
#   y = 28–80  →  ZONA DC
#
# Divisão horizontal (zona DC):
#   x =  0–35  →  Regulação + drive SSR + sensores PT100
#   x = 35–72  →  MCU ESP32
#   x = 72–90  →  RTC + periféricos
# ---------------------------------------------------------------------------

def main():
    print(f'Carregando: {PCB_FILE}')
    board = pcbnew.LoadBoard(PCB_FILE)

    # ── Borda da placa ────────────────────────────────────────────────────
    print('Desenhando borda da placa (90×80 mm)...')
    corners = [(OX,   OY),
               (OX+W, OY),
               (OX+W, OY+H),
               (OX,   OY+H)]
    for i in range(4):
        x1, y1 = corners[i]
        x2, y2 = corners[(i+1) % 4]
        edge_line(board, x1, y1, x2, y2)

    # Linha indicativa de separação AC/DC (Dwgs.User) em y=28
    courtyard_line(board, OX, OY+28, OX+W, OY+28)

    print('Posicionando componentes...')

    # ════════════════════════════════════════════════════════════════════
    # ZONA AC  (y = 2–20 mm)
    # Fusíveis T16A são EXTERNOS à PCB (porta-fusível de painel).
    # J1 recebe L1_fused / L2_fused / PE — toda fiação de potência externa.
    # ════════════════════════════════════════════════════════════════════
    place(board, 'J1',   8.0,  11.0)          # bornier 3-pin: L1f / L2f / PE
    place(board, 'RV1', 28.0,  11.0)          # MOV S14K275 disc D15.5mm
    place(board, 'U2',  62.0,  12.0)          # HLK-PM05 34×20mm

    # ════════════════════════════════════════════════════════════════════
    # REGULAÇÃO DE TENSÃO  (x = 2–32, y = 29–46)
    # ════════════════════════════════════════════════════════════════════
    place(board, 'C1',   5.0,  31.0)          # 10 µF/16V  5V bulk
    place(board, 'C2',  10.0,  31.0)          # 10 µF/16V  3V3 bulk
    place(board, 'C3',  15.0,  31.0)          # 100 nF     5V bypass
    place(board, 'C4',  20.0,  31.0)          # 100 nF     3V3 bypass
    place(board, 'U3',  12.0,  40.0)          # AMS1117-3.3 SOT-223

    # ════════════════════════════════════════════════════════════════════
    # DRIVE SSR  (x = 2–28, y = 47–62)
    # GPIO4 → R_gate → Q1 → SSR−  /  +5V → R7 → SSR+
    # ════════════════════════════════════════════════════════════════════
    place(board, 'R7',      5.0,  49.0)           # 220 Ω  +5V→SSR+
    place(board, 'J10',    14.0,  49.0)           # bornier 2-pin SSR externo (CTRL+/CTRL-)
    place(board, 'R_gate',  5.0,  57.0, rot=90)   # 100 Ω  gate série (horizontal)
    place(board, 'Q1',     12.0,  57.0)           # 2N7002 SOT-23
    place(board, 'R9',     20.0,  57.0)           # 10 kΩ  gate pull-down

    # ════════════════════════════════════════════════════════════════════
    # MCU ESP32-S3-MINI-1  (x = 37–73, y = 29–70)
    # Módulo ~18×20 mm, centrado no bloco
    # ════════════════════════════════════════════════════════════════════
    place(board, 'C9',  38.0,  31.0)          # 100 nF bypass VDD
    place(board, 'U1',  55.0,  50.0)          # ESP32-S3-MINI-1-N8

    # LED status (perto do ESP32, visível pela caixa)
    place(board, 'D1',  38.0,  62.0)          # LED verde 0603
    place(board, 'R10', 43.0,  62.0)          # 470 Ω série LED

    # ════════════════════════════════════════════════════════════════════
    # RTC  (x = 73–88, y = 29–62)
    # ════════════════════════════════════════════════════════════════════
    place(board, 'R2',  73.0,  31.0)          # 4k7 pull-up SDA
    place(board, 'R3',  78.0,  31.0)          # 4k7 pull-up SCL
    place(board, 'C8',  73.0,  37.0)          # 100 nF VCC DS3231
    place(board, 'BT1', 82.0,  36.0)          # CR2032 holder
    place(board, 'U5',  80.0,  52.0)          # DS3231 SOIC-16W

    # ════════════════════════════════════════════════════════════════════
    # SENSOR CALDEIRA  (x = 2–34, y = 55–68)
    # U4 MAX31865, Rref, filtros, conector PT100 4-wire
    # ════════════════════════════════════════════════════════════════════
    place(board, 'Rref',  5.0,  59.0, rot=90) # 430 Ω 0.1 %  (horizontal)
    place(board, 'C7',   11.0,  59.0)         # 100 nF RTDIN filter
    place(board, 'C10',  16.0,  59.0)         # 100 nF VDD bypass
    place(board, 'U4',   20.0,  63.0)         # MAX31865 SSOP-20
    place(board, 'J3',    5.0,  66.0)         # conector PT100 caldeira 4-pin

    # ════════════════════════════════════════════════════════════════════
    # SENSOR GRUPO  (x = 2–34, y = 68–79)
    # ════════════════════════════════════════════════════════════════════
    place(board, 'Rref2',  5.0,  70.0, rot=90)
    place(board, 'C11',   11.0,  70.0)
    place(board, 'C12',   16.0,  70.0)
    place(board, 'U6',    20.0,  74.0)        # MAX31865 SSOP-20
    place(board, 'J6',     5.0,  77.0)        # conector PT100 grupo 4-pin

    # ════════════════════════════════════════════════════════════════════
    # SONDA DE NÍVEL  (x = 34–42, y = 62–75)
    # ════════════════════════════════════════════════════════════════════
    place(board, 'R11', 35.0,  65.0)          # 100 kΩ pull-up
    place(board, 'J7',  35.0,  72.0)          # conector sonda 2-pin

    # ════════════════════════════════════════════════════════════════════
    # CONECTORES UI — borda inferior  (y = 74–79)
    # Cabos saem para caixinha externa com display + encoder + botões
    # ════════════════════════════════════════════════════════════════════
    place(board, 'R12', 50.0,  68.0)          # 10 kΩ pull-up BTN1
    place(board, 'R13', 55.0,  68.0)          # 10 kΩ pull-up BTN2
    place(board, 'R14', 60.0,  68.0)          # 10 kΩ pull-up BTN3
    place(board, 'J5',  49.0,  76.0)          # display ILI9341 8-pin
    place(board, 'J8',  64.0,  76.0)          # botões preset 6-pin
    place(board, 'J9',  76.0,  76.0)          # encoder EC11 5-pin

    # ── Salvar ────────────────────────────────────────────────────────
    board.Save(PCB_FILE)
    print(f'\nPCB salvo: {PCB_FILE}')
    print('Abrir no KiCad PCB Editor para verificar e rotear.')
    print()
    print('ATENÇÃO: zona AC (y < 28 mm da borda) → manter clearance mínimo 6 mm')
    print('         em relação a qualquer trilha DC.')


if __name__ == '__main__':
    main()
