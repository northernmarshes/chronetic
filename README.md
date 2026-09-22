# Chronetic

## Hardware components

- E-paper E-Ink 4,2'' 400x300px SPI - Waveshare 13353
- ESP32 WiFi + BT 4.2 Development Board with ESP-WROOM-32 module

## Pinout

```
                        ┌───────────────────────┐
                        │    ╔═════════════╗    │
                 EN   ──┤    ║             ║    ├──   D23               
                 VP   ──┤    ║ ┌────────┐  ║    ├──   D22                
                 VN   ──┤    ║ │ ESP-32 │  ║    ├──   TXO
                D34   ──┤    ║ │        │  ║    ├──   RXO
                D35   ──┤    ║ └────────┘  ║    ├──   D21
                D32   ──┤    ║             ║    ├──   D19
                D33   ──┤    ║             ║    ├──   D18               
                D25   ──┤    ║             ║    ├──   D5
                D26   ──┤    ║             ║    ├──   TX2              
                D27   ──┤    ║             ║    ├──   RX2               
                D14   ──┤    ║             ║    ├──   D4
                D12   ──┤    ║             ║    ├──   D2
                D13   ──┤    ║    ┌───┐    ║    ├──   D15
                GND   ──┤    ║    │   │    ║    ├──   GND               
                 VN   ──┤    ║    └───┘    ║    ├──   3V3               
                        │    ╚═════USB═════╝    │
                        └───────────────────────┘
```
