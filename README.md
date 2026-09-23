# Chronetic

An e-ink public transport timetable. The software is composed of a micropython frontend and a rust microservice.<br>
The service is written to parse the Warsaw's Public Transport API. If you want to add parsing logic for other cities feel free to open a pull request.

## Assembly and installation

### 1. Assembling hardware

#### 1.1 Connect the components according to the pinout

##### Components

- E-paper E-Ink 4,2'' 400x300px SPI - Waveshare 13353
- ESP32 WiFi + BT 4.2 Development Board with ESP-WROOM-32 module

##### Pinout

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

### 2. Setting up the service (for Warsaw's Public Transport API)

#### 2.1 Get the credentials

- API key

```
To obtain API key you need to register for free at <https://api.um.warszawa.pl/>
```

- List ID

```
???
```

- Timetable ID

```
???
```

- IP

```
Your subnet IP with a chosen port (eg. 192.168.1.0:7878)
```

- Your WIFI SSID & password

```
Your network name and password
```

- Bus stop ID & number

```
 Stops' IDs and numbers can be found at <https://www.wtp.waw.pl>
```

#### 2.2 Fill the credentials

Fill the variables in the following files:

```
chronetic/chronetic_service/.cargo/config.toml
chronetic/src/secrets.py
```

#### 2.3 Run the service

- Install Rust if needed
- Test the service

```
cargo test
```

- Run the service

```
cargo run --release
```

### 3. Flashing the esp32

#### 3.1 Connecting microcontroller

Make sure esp32 is visible and connected and flashed with micropython.

#### 3.2 Flash it

Run the bash script to flash and run the app:

```
cd chronetic
./deploy_esp32
```
