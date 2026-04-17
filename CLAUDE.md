# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projeto

Controlador genérico de máquina de espresso com PID dual, display Nextion 2.4" UART e agendamento por horário. Projetado inicialmente para a Faema President, mas reutilizável em outras máquinas (ex: máquina com bomba MGFR, solenoides, fluxômetro).

**Plataforma:** Raspberry Pi Pico 2 W rodando MicroPython
**Status atual:** Rev.7 — fonte de verdade é `circuits/faema_carrier.py` (SKiDL) → netlist → KiCad PCB

## Convenção: SKiDL vs Schematic manual

- **`circuits/faema_carrier.py` (SKiDL)** = fonte de verdade para netlist e PCB
- **Schematic KiCad manual** = artefato de documentação apenas (*"For reference only — see faema_carrier.py"*)
- Ambos orientados pelo CLAUDE.md/SPEC; divergências entre os dois devem ser resolvidas no SKiDL
- TODO: automatizar comparação de netlists (SKiDL vs Eeschema export) para detectar divergências

## Fluxo de desenvolvimento (hardware)

```bash
# Regenerar netlist (após alterar circuits/faema_carrier.py)
python3 circuits/faema_carrier.py
# → gera outputs/faema_carrier.net (importar no KiCad: File > Import Netlist)

# Placement da carrier board via pcbnew
DYLD_FALLBACK_LIBRARY_PATH=/Applications/KiCad/KiCad.app/Contents/Frameworks \
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
kicad/place_components_carrier.py

# Limpar arquivos temporários SKiDL/Python
bash clean.sh
```

## Fluxo de desenvolvimento (firmware MicroPython)

```bash
pip install mpremote esptool

# Flash do firmware MicroPython para Pico 2W
# (usar firmware RP2350 adequado para Pico 2W)
mpremote cp -r firmware/ :

# REPL interativo
mpremote connect
```

## Arquitetura do hardware

O PCB é uma **carrier board** (backplane) com sockets para módulos plug-in. Não há ICs fine-pitch para soldar na carrier — os chips complexos ficam nos módulos.

**Módulos plug-in (não estão na carrier PCB):**
- `J11/J12` — Raspberry Pi Pico 2 W (2×20 socket fêmea 2.54mm)
- `J13/J14` — MAX31865 RTD breakout ×2 (1×8 socket 2.54mm, pinout Adafruit nativo)
- `J6`       — Nextion NX3224T024 display UART (JST XH 4-pin) — display primário
- `J7`       — SPI display alternativo ILI9341 (JST XH 8-pin) — opcional
- `J8`       — DS3231 RTC I2C (JST XH 4-pin) — opcional; NTP/WiFi preferido
- `U3`       — MCP23017 I2C I/O expander (SOIC-28, montado na carrier)

**Nomes genéricos:** conectores usam nomes funcionais (RTD1/RTD2, SSR1/SSR2, LEVEL1/LEVEL2, OUT1–4, etc.).
O mapeamento para papéis específicos da máquina (caldeira/grupo/tanque) vive apenas no firmware (`config.py`).

**Conectores externos (JST XH 2.5mm keyed):** J3–J10, J15–J20
**Conectores de potência (Phoenix MKDS 5.08mm screw terminal):** J1 (AC in), J2a/J2b (SSR1/SSR2)

**PE (terra proteção):** separado do GND do circuito — J1 pino 3 vai para chassi apenas.

## Mapa de GPIOs (Pico 2 W) — Rev.7

| GPIO | Sinal | Destino |
|------|-------|---------|
| GP0/GP1 | UART0 TX/RX | Nextion display (J6), divisor R6/R7 no RX |
| GP2/GP3/GP4 | SPI0 SCK/MOSI/MISO | MAX31865 ×2 (J13/J14) + SPI display (J7) |
| GP5/GP6 | CS_RTD1/CS_RTD2 | RTD breakouts J13/J14 |
| GP7 | SSR1_CTRL | Driver Q1 → SSR1 (J2a) |
| GP8/GP9 | SPI1 SCK/MOSI | SPI display opcional (J7) — nota: J7 usa SPI0 se SPI1 não disponível |
| GP10 | CS_DISP | SPI display (J7) |
| GP11 | DC_DISP | SPI display (J7) |
| GP12 | RST_DISP | SPI display (J7) |
| GP13 | DISP_LED | Backlight SPI display (J7) |
| GP14/GP15 | I2C SDA/SCL | DS3231 (J8) + MCP23017 (U3) |
| GP16/GP17/GP18 | ENC_CLK/DT/SW | Encoder EC11 (J3) |
| GP19 | SSR2_CTRL | Driver Q2 → SSR2 (J2b) |
| GP20 | PUMP_CTRL | Controle bomba 0–3.3V (J15) |
| GP21 | PULSE_IN | Fluxômetro pulso (J16) |
| GP22 | MCP23017_INT | Interrupção do MCP23017 |
| GP26 | ADC0 — TEMP_AUX | NTC opcional (J17) |
| GP27 | ADC1 — PRESSURE | Sensor pressão 0–4.5V via divisor (J18) |
| GP28 | ADC2 — ANALOG_IN | Potenciômetro (J19) |
| Pin 35 | ADC_VREF | Ligado ao +3V3 carrier (AMS1117) — referência ratiométrica |
| Pin 39 | VSYS | Alimentado pelo +5V do HLK-PM05 |

## MCP23017 — mapa de portas

| Pino | Sinal | Tipo |
|------|-------|------|
| GPA0–GPA4 | BTN1–BTN5 | Input (pull-up interno) |
| GPA5 | LEVEL1 | Input (pull-up externo 100k) |
| GPA6 | LEVEL2 | Input (pull-up externo 100k) |
| GPA7 | LED5 | Output |
| GPB0–GPB3 | OUT1–OUT4 | Output (relé externo) |
| GPB4–GPB7 | LED1–LED4 | Output |

- I2C addr: 0x20 (A0/A1/A2 = GND)
- INTA → Pico GP22; INTB não conectado (ambas as portas usam INTA em mirror mode)
- Expansão futura: segundo MCP23017 addr 0x21 no mesmo barramento, sem mudança de hardware

## Conectores J13/J14 — RTD breakout (pinout Adafruit nativo)

```
1  VIN   ← 3V3 carrier
2  GND
3  3V3   → NC (saída do regulador interno Adafruit, não usada)
4  CLK   ← SPI_SCK
5  SDO   → SPI_MISO
6  SDI   ← SPI_MOSI
7  CS    ← CS_RTD1 / CS_RTD2
8  DRDY  → DRDY_RTD1 / DRDY_RTD2 (conectado)
```

**Adaptador para SEN-30201 (7 vias DuPont):**
Carrier→SEN: VIN(1)→2, GND(2)→1, CLK(4)→6, SDO(5)→4, SDI(6)→7, CS(7)→5, DRDY(8)→3

## Circuito TEMP_AUX (NTC opcional)

`3V3 → R_ref(2k2 0.1%) → GP26 → NTC(10k) → GND`
C_ntc (100nF) filtro em paralelo com NTC. ADC_VREF = AMS1117 3V3 (ratiométrico).
Range: 25°C→2.70V, 85°C→1.08V, 128°C→0.56V. DNF se não usar NTC.

## Circuito PRESSURE (sensor 0–4.5V)

Divisor resistivo 27k + 75k: Vout = Vin × 75/(27+75) = Vin × 0.735
4.5V → 3.31V (≤ ADC_VREF 3.3V com margem mínima — verificar em layout).
Alternativa mais segura: 33k + 82k → Vout = 82/115 × 4.5V = 3.21V.

## Arquitetura de firmware

```
firmware/
├── main.py              # boot e loop principal
├── config.py            # mapeamento máquina → GPIOs/nets, setpoints, Kp/Ki/Kd
├── pid.py               # classe PID genérica
├── sensors/
│   ├── max31865.py      # driver RTD via SPI (×2: RTD1 + RTD2)
│   ├── ntc.py           # driver NTC ADC (TEMP_AUX, opcional)
│   ├── pressure.py      # leitura ADC pressão com calibração
│   ├── flow.py          # contagem de pulsos fluxômetro (GP21 interrupt)
│   └── level.py         # sondas nível LEVEL1/LEVEL2 via MCP23017
├── actuators/
│   ├── ssr.py           # controle SSR1/SSR2 (PWM)
│   └── pump.py          # controle bomba MGFR (PWM 0–3.3V)
├── io/
│   └── mcp23017.py      # driver MCP23017 (botões, LEDs, relés, níveis)
├── display/
│   └── nextion.py       # driver Nextion UART
├── control/
│   └── scheduler.py     # lógica liga/desliga por horário (NTP ou DS3231)
└── web/
    └── server.py        # servidor web (ajuste remoto de setpoint)
```

## Arquitetura de controle

- **PID RTD1:** PT100 → MAX31865 → PID → SSR1. Cycle time ~1s.
- **PID RTD2:** PT100 → MAX31865 → PID → SSR2. Cycle time ~1s.
- **Setpoint adaptativo:** RTD2 pode modular SV do RTD1 (offset grupo frio/quente).
- **Nível água:** LEVEL1/LEVEL2 (condutividade via MCP23017) — bloqueia SSR se seco.
- **Bomba:** PUMP_CTRL PWM 0–3.3V → MGFR. Controlada por potenciômetro (ANALOG_IN) ou encoder.
- **Fluxômetro:** PULSE_IN interrupt (GP21) → volume por dose.
- **Agendamento:** NTP via WiFi (primário) ou DS3231 (fallback).

## Fabricação PCB

- JLCPCB com PCBA (componentes LCSC). BOM/CPL em `outputs/`.
- SMD montados pela fábrica; THT/módulos soldados manualmente.
- SSR-40DA externos à PCB (com dissipador). Fusíveis em porta-fusível de painel externo.
- Clearance AC/DC mínimo 6mm (isolação reforçada). HLK-PM05 tem isolação galvânica 3kV.
- MCP23017 (SOIC-28): montado pela fábrica.

## Referências SKiDL

- `circuits/faema_carrier.py` — circuito atual (carrier board Rev.7)
- `circuits/faema_president.py` — circuito anterior (placa monolítica Rev.5, mantido como referência)
- Partes usam `Part(tool=SKIDL, ...)` — independente de libs KiCad. `generate_schematic()` não funciona com essas partes (falta campo `orientation`); usar `generate_svg()` com netlistsvg para esquema gráfico.
- ERC esperado: aviso "only one pin on PE net" — correto por design (PE vai só ao chassi).
