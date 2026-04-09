# Faema President — Placa de controle de temperatura
**Status:** Rev.4 em definição — próximo passo: atualizar esquemático + layout PCB + firmware

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
| U6 | MAX31865 | ADC PT100 grupo — IC direto (SSOP-20) (Rev.4) |
| SSR1 | SSR-40DA | Controle resistência caldeira 2400W/220V/10.9A |
| J5 | GC9A01 1.28" | Display IPS redondo 240×240, SPI compartilhado, conector FPC |
| ENC1 | EC11 / KY-040 | Encoder rotativo com botão, menu/setpoint |
| J3 | PT100 4-wire | Sensor temperatura caldeira |
| J6 | PT100 4-wire | Sensor temperatura grupo (Rev.4, substitui NTC) |
| J7 | Sonda nível | Haste condutividade, nível água caldeira (Rev.4) |
| J8 | Header 6-pin | 3 botões de preset + 3.3V + GND (Rev.4) |
| D1 | LED verde | Indicação de status (power/wifi/heating) |

### Circuito de aplicação MAX31865 — U4 caldeira (Rev.3)
- Rref: 430Ω 0.1% entre REFIN+ e FORCE+
- C7: 100nF filtro across RTDIN+/RTDIN−
- C10: 100nF bypass no VDD
- DRDY → GPIO3 (interrupção, active LOW)
- Configuração: 4-wire, filtro 50Hz
- SPI Mode 1 ou 3, max 5 MHz

### Circuito de aplicação MAX31865 — U6 grupo (Rev.4)
- Rref2: 430Ω 0.1% entre REFIN+ e FORCE+
- C11: 100nF filtro across RTDIN+/RTDIN−
- C12: 100nF bypass no VDD
- DRDY2 não conectado (leitura por polling, não é time-critical)
- CS → GPIO18
- Compartilha SPI bus (SCK/MOSI/MISO) com U4 e J5
- Configuração: 4-wire, filtro 50Hz

### Sensor de nível — sonda condutividade (Rev.4)
- Haste metálica isolada submersa na caldeira
- Circuito: GPIO17 (pull-up interno) → R11 100kΩ → sonda → água → corpo caldeira (GND)
- Água presente → GPIO lê LOW; ausente → GPIO lê HIGH
- Firmware: pulsar leitura (ms) para minimizar eletrólise
- Ação: bloquear SSR + alerta no display + LED piscando
- **Proteção crítica:** impede aquecimento com caldeira seca

### Botões de preset (Rev.4)
- Header J8 com 3 entradas + 3.3V + GND (6 pinos)
- R12/R13/R14: 10kΩ pull-up → 3.3V por entrada
- Botão fecha para GND; LOW = pressionado
- GPIOs: 19 (BTN1), 20 (BTN2), 21 (BTN3)
- Uso não definido — exemplos: boost pré-infusão, vapor, flush
- Presets configuráveis em config.py

### Proteções AC
- F1: Fusível T16A tempo lento (porta-fusível 5×20mm)
- RV1: MOV S14K275 (varistor surto, across L-N)
- R8+C6: Snubber 100Ω + 100nF/400V across SSR
- Fio mínimo 2.5mm² para trecho caldeira

### Proteções de segurança (Rev.3)
- R9: 10kΩ pull-down no GPIO4/SSR_CTRL — garante SSR OFF durante boot/crash do ESP32
- R7: 100Ω série no SSR_CTRL (I ≈ 21mA, margem sobre os 7.5mA mínimos do SSR)

### Bypass capacitors
- C7: 100nF across RTDIN+/RTDIN− (U4 MAX31865 caldeira)
- C8: 100nF no VCC do DS3231
- C9: 100nF no VDD do ESP32-S3
- C10: 100nF no VDD do U4 MAX31865 caldeira
- C11: 100nF across RTDIN+/RTDIN− (U6 MAX31865 grupo) (Rev.4)
- C12: 100nF no VDD do U6 MAX31865 grupo (Rev.4)

---

## Mapa de GPIOs

| GPIO | Sinal | Descrição |
|------|-------|-----------|
| 2 | LED_STATUS | LED status via R10 470Ω |
| 3 | MAX_DRDY | MAX31865 caldeira data ready, active LOW |
| 4 | SSR_CTRL | SSR via R7 100Ω + R9 10kΩ pull-down — HIGH=resistência ligada |
| 5 | ENC_CLK | Encoder canal A |
| 6 | ENC_DT | Encoder canal B |
| 7 | ENC_SW | Encoder botão (push) |
| 8 | I2C_SDA | DS3231 (0x68) |
| 9 | I2C_SCL | DS3231 (0x68) |
| 10 | SPI_SCK | U4 + U6 + GC9A01 (compartilhado) |
| 11 | SPI_MOSI | U4 + U6 + GC9A01 (compartilhado) |
| 12 | SPI_MISO | U4 + U6 (MAX31865s apenas) |
| 13 | CS_MAX | Chip select MAX31865 caldeira (U4) |
| 14 | CS_DISP | Chip select GC9A01 |
| 15 | DC_DISP | Data/Command GC9A01 |
| 16 | RST_DISP | Reset GC9A01 |
| 17 | LEVEL_SENSE | Sonda nível água caldeira (Rev.4) |
| 18 | CS_MAX2 | Chip select MAX31865 grupo (U6) (Rev.4) |
| 19 | BTN1 | Botão preset 1 — pull-up 10kΩ (Rev.4) |
| 20 | BTN2 | Botão preset 2 — pull-up 10kΩ (Rev.4) |
| 21 | BTN3 | Botão preset 3 — pull-up 10kΩ (Rev.4) |

---

## Baramentos

### SPI (compartilhado U4 + U6 + GC9A01)
- SCK=10, MOSI=11, MISO=12
- CS separados: U4 MAX31865 caldeira=13, GC9A01=14, U6 MAX31865 grupo=18
- GC9A01 não usa MISO
- **Atenção:** modos SPI diferentes — MAX31865 usa Mode 1/3 (max 5 MHz), GC9A01 usa Mode 0 (até 80 MHz). Firmware deve reconfigurar o barramento ao alternar dispositivo.

### I2C (DS3231 apenas)
- SDA=8, SCL=9
- Pull-ups R2/R3 4.7kΩ → 3.3V
- DS3231 endereço: 0x68

---

## Lógica de controle

### PID caldeira com setpoint adaptativo (Rev.4)
- Sensor caldeira: PT100 via U4 MAX31865 (SPI)
- Sensor grupo: PT100 via U6 MAX31865 (SPI)
- Atuador: SSR-40DA (GPIO4, zero-cross)
- Cycle time PID: ~1s (adequado para zero-cross SSR)
- Parâmetros Kp/Ki/Kd: a ajustar experimentalmente

#### Setpoint adaptativo baseado na temperatura do grupo
```
SV_caldeira = SV_base + offset(T_grupo)

T_grupo frio  (< 60°C)  → offset positivo (+4 a +8°C)
T_grupo ideal (70-80°C)  → offset zero
T_grupo quente (> 85°C)  → offset negativo (-2 a -4°C)

Limites hard (segurança):
  SV_HARD_MAX = 128°C  (margem segura; válvula abre ~131°C a 1.8 bar gauge)
  SV_HARD_MIN = 85°C
```

#### Presets de temperatura (via botões físicos)
```python
PRESETS = {
    'normal':  {'sv': 93,  'desc': 'Extração'},
    'boost':   {'sv': 108, 'desc': 'Pré-infusão ~1.2 bar'},
    'steam':   {'sv': 125, 'desc': 'Vapor leite ~1.3 bar'},
}
```

#### Referência pressão × temperatura (vapor saturado)
| Bar (gauge) | °C aprox | Uso |
|-------------|----------|-----|
| 0 | 100 | Ebulição |
| 0.2 | 105 | Boost leve |
| 0.5 | 111 | Pré-infusão forte |
| 1.0 | 120 | Vapor fraco |
| 1.3 | 125 | Vapor leite |
| 1.8 | 131 | **Válvula de segurança** |

#### Proteção nível de água (Rev.4)
- Sensor: sonda condutividade (GPIO17)
- Nível baixo → bloquear SSR imediatamente + alerta no display + LED piscando
- Prioridade máxima: override sobre qualquer preset ou PID

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
│   ├── max31865.py      # driver PT100 (2 instâncias: caldeira + grupo)
│   └── level.py         # sonda nível água (condutividade pulsada)
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

- [ ] Atualizar esquemático SVG para Rev.4
- [ ] Layout PCB no KiCad ou EasyEDA Pro (dimensões alvo: ~90×80mm)
- [ ] Web UI para ajuste de setpoint e horários via Wi-Fi
- [ ] Watchdog e recovery em caso de falha do sensor
- [ ] Teste de isolação AC/DC antes de ligar na máquina
- [ ] Definir uso dos 3 botões de preset
- [ ] Calibrar curva offset(T_grupo) para setpoint adaptativo

---

## Notas de montagem (PCBA)

- **Fabricante recomendado:** JLCPCB com PCBA (componentes LCSC)
- **SMD montados pela fábrica:** U1, U3, U4, U5, U6, R1-R14, Rref, Rref2, C1-C12, D1, conectores FPC
- **THT/manual:** U2 (HLK-PM05), J1 (bornier AC), F1 (porta-fusível), RV1 (MOV), R8 (snubber 1W), J8 (header botões)
- **Externos (fora da PCB):** SSR1 (SSR-40DA com dissipador), J3 (PT100 caldeira), J6 (PT100 grupo), J7 (sonda nível), ENC1 (encoder), botões
- **Nota térmica:** AMS1117-3.3 dissipa ~1W. Garantir copper pour generoso no pad GND (SOT-223).
- **Nota SSR:** verificar autenticidade do Fotek SSR-40DA. Alternativas genuínas: Omron G3NA, Crydom, Carlo Gavazzi.

---

## Changelog

### Rev.4 (atual — documentação, esquemático SVG pendente)
- Segundo MAX31865 (U6) para PT100 no grupo — substitui NTC/divisor (removidos R1, C5, J4)
- Setpoint adaptativo: T_grupo modula SV da caldeira (feedforward)
- Sensor de nível por condutividade (GPIO17, R11 100kΩ) — bloqueia SSR se caldeira seca
- Header J8 com 3 botões de preset (GPIO19/20/21, R12-R14 pull-up 10kΩ)
- Presets configuráveis: boost pré-infusão, vapor, livre
- Tabela pressão × temperatura para limites de segurança
- Dimensão PCB alvo revisada: ~90×80mm (mais componentes)

### Rev.3
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
