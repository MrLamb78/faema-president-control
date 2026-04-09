# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projeto

Controle eletrônico de temperatura para a Faema President (grupo manual). Substitui o pressostato original por PID com display redondo e agendamento por horário.

**Plataforma:** ESP32-S3 Mini rodando MicroPython
**Status atual:** Rev.4 — esquemático KiCad (`kicad/`) com componentes posicionados, próximo passo: completar wiring + layout PCB + firmware

## Comandos de desenvolvimento (firmware MicroPython)

```bash
# Instalar ferramentas
pip install mpremote esptool

# Flash do firmware MicroPython
esptool.py --chip esp32s3 erase_flash
esptool.py --chip esp32s3 write_flash 0x0 firmware.bin

# Upload de arquivos para o dispositivo
mpremote cp firmware/main.py :main.py
mpremote cp -r firmware/ :

# REPL interativo
mpremote connect

# Instalar bibliotecas no dispositivo (via REPL)
# import mip; mip.install('gc9a01')
```

## Estrutura de firmware

```
firmware/
├── main.py              # boot e loop principal
├── config.py            # setpoints, horários, Kp/Ki/Kd
├── pid.py               # classe PID genérica
├── sensors/
│   ├── max31865.py      # driver PT100 via SPI (2 instâncias: caldeira U4 + grupo U6)
│   └── level.py         # sonda nível água (condutividade pulsada, GPIO17)
├── display/
│   ├── ui.py            # layout gauge + telas
│   └── gauge.py         # desenho arco analógico (gauge central 240×240)
├── rtc/
│   └── ds3231.py        # driver RTC + alarmes I2C
├── control/
│   └── scheduler.py     # lógica liga/desliga por horário
└── web/
    └── server.py        # servidor web simples (ajuste remoto de setpoint)
```

## Mapa de GPIOs

| GPIO | Sinal | Componente |
|------|-------|------------|
| 2 | LED_STATUS | LED status via R10 470Ω |
| 3 | MAX_DRDY | MAX31865 caldeira data ready (active LOW) |
| 4 | SSR_CTRL | SSR-40DA caldeira — HIGH=ligado, R9 pull-down |
| 5/6/7 | ENC_CLK/DT/SW | Encoder EC11 |
| 8/9 | I2C_SDA/SCL | DS3231 RTC (0x68) |
| 10/11/12 | SPI_SCK/MOSI/MISO | Barramento SPI compartilhado (U4+U6+GC9A01) |
| 13 | CS_MAX | Chip select MAX31865 caldeira (U4) |
| 14/15/16 | CS/DC/RST_DISP | GC9A01 display via FPC (não usa MISO) |
| 17 | LEVEL_SENSE | Sonda nível água caldeira (R11 100kΩ) |
| 18 | CS_MAX2 | Chip select MAX31865 grupo (U6) |
| 19/20/21 | BTN1/BTN2/BTN3 | Botões preset (pull-up 10kΩ, active LOW) |

## Arquitetura de controle

- **PID caldeira:** PT100 → MAX31865 U4 (SPI, IC direto, Rref 430Ω) → PID → SSR-40DA (GPIO4). Cycle time ~1s.
- **Setpoint adaptativo:** T_grupo (PT100 via U6) modula SV caldeira — offset positivo com grupo frio, negativo com grupo quente. Limites: 85–128°C.
- **Nível água:** sonda condutividade (GPIO17) — bloqueia SSR se caldeira seca. Override sobre PID.
- **Presets:** 3 botões físicos (GPIO19-21) para modos pré-configurados (extração, boost, vapor).
- **Agendamento:** DS3231 fornece hora real (±2ppm); config hora liga/desliga em `config.py`.
- **Display:** biblioteca `gc9a01` de Russ Hughes (FPC). Gauge analógico central + widgets.
- **SPI compartilhado:** MAX31865 x2 (Mode 1/3, 5MHz) e GC9A01 (Mode 0, 80MHz) — reconfigurar modo ao alternar.

## Referências de componentes

U1=ESP32-S3, U2=HLK-PM05, U3=AMS1117-3.3, U4=MAX31865 caldeira (SSOP-20), U5=DS3231, U6=MAX31865 grupo (SSOP-20)

## Fabricação PCB

- JLCPCB com PCBA (componentes LCSC)
- SMD montados pela fábrica; THT/módulos soldados manualmente
- SSR-40DA é externo à PCB (com dissipador)
- Clearance AC/DC mínimo 6mm (isolação reforçada)
