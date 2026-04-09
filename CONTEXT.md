# Faema President — Placa de controle de temperatura
**Status:** Esquemático Rev.3 concluído — próximo passo: layout PCB (KiCad) + firmware MicroPython

---

## Objetivo

Substituir o pressostato original da Faema President (grupo manual) por controle
eletrônico de temperatura com PID, display redondo e agendamento por horário.

---

## Hardware definido (Rev.3)

| Ref | Componente | Função |
|-----|-----------|--------|
| U1 (MCU) | ESP32-S3 Mini | MicroPython, Wi-Fi+BT, USB nativo |
| U2 | HLK-PM05 | SMPS 220VAC→5VDC/5W isolado 3kV |
| U3 | AMS1117-3.3 | LDO 5V→3.3V/800mA (SOT-223, copper pour no GND pad) |
| U4 | MAX31865 | ADC PT100 caldeira — IC direto na PCB (SSOP-20) |
| U5 | DS3231 | RTC I2C, agendamento liga/desliga, backup CR2032 |
| SSR1 | SSR-40DA | Controle resistência caldeira 2400W/220V/10.9A |
| J5 | GC9A01 1.28" | Display IPS redondo 240×240, SPI compartilhado, conector FPC |
| ENC1 | EC11 / KY-040 | Encoder rotativo com botão, menu/setpoint |
| J3 | PT100 4-wire | Sensor temperatura caldeira |
| J4 | NTC 10k | Sensor temperatura grupo (display apenas) |
| D1 | LED verde | Indicação de status (power/wifi/heating) |

### Circuito de aplicação MAX31865 (Rev.3 — IC direto)
- Rref: 430Ω 0.1% entre REFIN+ e FORCE+
- C7: 100nF filtro across RTDIN+/RTDIN−
- C10: 100nF bypass no VDD
- DRDY → GPIO3 (interrupção, active LOW)
- Configuração: 4-wire, filtro 50Hz
- SPI Mode 1 ou 3, max 5 MHz

### Proteções AC
- F1: Fusível T16A tempo lento (porta-fusível 5×20mm)
- RV1: MOV S14K275 (varistor surto, across L-N)
- R8+C6: Snubber 100Ω + 100nF/400V across SSR
- Fio mínimo 2.5mm² para trecho caldeira

### Proteções de segurança (Rev.3)
- R9: 10kΩ pull-down no GPIO4/SSR_CTRL — garante SSR OFF durante boot/crash do ESP32
- R7: 100Ω série no SSR_CTRL (I ≈ 21mA, margem sobre os 7.5mA mínimos do SSR)

### Bypass capacitors (Rev.3)
- C7: 100nF across RTDIN+/RTDIN− (MAX31865)
- C8: 100nF no VCC do DS3231
- C9: 100nF no VDD do ESP32-S3
- C10: 100nF no VDD do MAX31865

---

## Mapa de GPIOs

| GPIO | Sinal | Descrição |
|------|-------|-----------|
| 1 | ADC_NTC | NTC grupo — divisor R1(4.7kΩ)+NTC+C5(100nF) |
| 2 | LED_STATUS | LED status via R10 470Ω (Rev.3) |
| 3 | MAX_DRDY | MAX31865 data ready, active LOW (Rev.3) |
| 4 | SSR_CTRL | SSR via R7 100Ω + R9 10kΩ pull-down — HIGH=resistência ligada |
| 5 | ENC_CLK | Encoder canal A |
| 6 | ENC_DT | Encoder canal B |
| 7 | ENC_SW | Encoder botão (push) |
| 8 | I2C_SDA | DS3231 (0x68) |
| 9 | I2C_SCL | DS3231 (0x68) |
| 10 | SPI_SCK | MAX31865 + GC9A01 (compartilhado) |
| 11 | SPI_MOSI | MAX31865 + GC9A01 (compartilhado) |
| 12 | SPI_MISO | MAX31865 apenas |
| 13 | CS_MAX | Chip select MAX31865 |
| 14 | CS_DISP | Chip select GC9A01 |
| 15 | DC_DISP | Data/Command GC9A01 |
| 16 | RST_DISP | Reset GC9A01 |

---

## Baramentos

### SPI (compartilhado MAX31865 + GC9A01)
- SCK=10, MOSI=11, MISO=12
- CS separados: MAX31865=13, GC9A01=14
- GC9A01 não usa MISO
- **Atenção:** modos SPI diferentes — MAX31865 usa Mode 1/3 (max 5 MHz), GC9A01 usa Mode 0 (até 80 MHz). Firmware deve reconfigurar o barramento ao alternar dispositivo.

### I2C (DS3231 apenas)
- SDA=8, SCL=9
- Pull-ups R2/R3 4.7kΩ → 3.3V
- DS3231 endereço: 0x68

---

## Lógica de controle

### PID caldeira
- Sensor: PT100 via MAX31865 (SPI)
- Atuador: SSR-40DA (GPIO4, zero-cross)
- Setpoint típico: 90–96°C
- Cycle time PID: ~1s (adequado para zero-cross SSR)
- Parâmetros Kp/Ki/Kd: a ajustar experimentalmente

### Temperatura do grupo
- Sensor: NTC 10k com divisor resistivo (R1=4.7kΩ)
- Uso: exibição apenas (sem controle PID)
- Fórmula NTC: equação de Steinhart-Hart ou beta simples

### Agendamento
- DS3231 fornece hora real com precisão ±2ppm
- Backup CR2032: mantém hora sem alimentação
- Configurações: hora liga, hora desliga (dia da semana opcional)

---

## Display GC9A01
- Resolução: 240×240px, IPS, 65k cores
- Conexão: conector FPC
- Biblioteca MicroPython: `gc9a01` de Russ Hughes
  - Instalação: `mip.install('gc9a01')` no REPL
- Layout sugerido:
  - Gauge analógico central: temperatura caldeira (arco colorido)
  - Temperatura do grupo (canto superior)
  - Setpoint atual (canto inferior)
  - Hora atual do RTC (canto superior oposto)
  - Status: aquecendo / estável / agendado

---

## Estrutura de firmware sugerida

```
firmware/
├── main.py              # boot e loop principal
├── config.py            # setpoints, horários, Kp/Ki/Kd
├── pid.py               # classe PID genérica
├── sensors/
│   ├── max31865.py      # driver PT100
│   └── ntc.py           # leitura NTC + Steinhart-Hart
├── display/
│   ├── ui.py            # layout gauge + telas
│   └── gauge.py         # desenho arco analógico
├── rtc/
│   └── ds3231.py        # driver RTC + alarmes
├── control/
│   └── scheduler.py     # lógica liga/desliga por horário
└── web/
    └── server.py        # servidor web simples (ajuste remoto)
```

---

## Decisões em aberto

- [ ] Layout PCB no KiCad (dimensões alvo: ~80×70mm)
- [ ] Web UI para ajuste de setpoint e horários via Wi-Fi
- [ ] Watchdog e recovery em caso de falha do sensor
- [ ] Teste de isolação AC/DC antes de ligar na máquina

---

## Notas de montagem (PCBA)

- **Fabricante recomendado:** JLCPCB com PCBA (componentes LCSC)
- **SMD montados pela fábrica:** U1, U3, U4, U5, R1-R10, Rref, C1-C10, D1, conector FPC
- **THT/manual:** U2 (HLK-PM05), J1 (bornier AC), F1 (porta-fusível), RV1 (MOV), R8 (snubber 1W)
- **Externos (fora da PCB):** SSR1 (SSR-40DA com dissipador), J3 (PT100), J4 (NTC), ENC1 (encoder)
- **Nota térmica:** AMS1117-3.3 dissipa ~1W. Garantir copper pour generoso no pad GND (SOT-223).
- **Nota SSR:** verificar autenticidade do Fotek SSR-40DA. Alternativas genuínas: Omron G3NA, Crydom, Carlo Gavazzi.

---

## Changelog

### Rev.3 (atual)
- R9 10kΩ pull-down no GPIO4 (segurança: SSR OFF durante boot)
- R7 220Ω → 100Ω (corrente SSR: 9.5mA → 21mA, margem sobre mínimo 7.5mA)
- R1 10kΩ → 4.7kΩ (melhor resolução ADC do NTC na faixa 60-100°C)
- MAX31865 como IC direto na PCB (era implicitamente breakout): Rref 430Ω, filtros, DRDY
- DRDY do MAX31865 conectado a GPIO3 (interrupção)
- Bypass caps C7-C10 (100nF locais em MAX31865, DS3231, ESP32)
- LED de status D1 em GPIO2 via R10 470Ω
- Referências harmonizadas: U2=HLK-PM05, U3=AMS1117, U4=MAX31865, U5=DS3231
- Display GC9A01 via conector FPC (decisão confirmada)
- Nota térmica no AMS1117 (copper pour)
- Alerta de autenticidade do SSR Fotek

### Rev.2
- Esquemático inicial com todos os componentes
- SPI compartilhado MAX31865 + GC9A01
- I2C dedicado para DS3231

---

## Arquivos do projeto

- `president_schematic_v3.html` — esquemático interativo Rev.3 (pan/zoom)
- `president_schematic_v2.html` — esquemático Rev.2 (arquivo anterior)
- `CONTEXT.md` — este arquivo
