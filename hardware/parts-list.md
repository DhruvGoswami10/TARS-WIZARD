# Parts List

Everything you need to build your own TARS. Links go to Amazon/AliExpress — prices may vary.

## Core Components

| # | Component | Qty | Description | Link |
|---|-----------|-----|-------------|------|
| 1 | **Raspberry Pi 5** | 1 | The brain of TARS — runs all software | [Amazon](https://amzn.to/4j7fhfm) |
| 2 | **Metal Gear Servo LD-3015MG** | 3 | High-torque servos for torso and arms | [Amazon](https://amzn.to/3DVIAkD) |
| 3 | **PCA9685 Servo Driver** | 1 | I2C servo controller — drives all 3 servos | [Amazon](https://amzn.to/40oVYqc) |
| 4 | **12V to 5V DC-DC Converter** | 1 | Stable power regulation for servos | [Amazon](https://amzn.to/40cGq82) |
| 5 | **LiPo Battery 1300mAh 11.1V 76C** | 1 | Power pack for servo motors | [Amazon](https://amzn.to/4j9A3uP) |
| 6 | **LiPo Battery Charger** | 1 | Compatible with 2/3 pin battery packs | [Amazon](https://amzn.to/3DIuD9X) |
| 7 | **Powerbank** | 1 | Portable power for the Raspberry Pi | [AliExpress](https://fr.aliexpress.com/item/1005007622153868.html) |

## Interface & I/O

| # | Component | Qty | Description | Link |
|---|-----------|-----|-------------|------|
| 8 | **5" LCD Display** | 1 | Compact screen for status/media | [Amazon](https://amzn.to/40jiReN) |
| 9 | **Micro HDMI to HDMI Cable** | 1 | Connects Pi 5 to the display | [Amazon](https://amzn.to/3PoFdFu) |
| 10 | **Mini USB Microphone** | 1 | Lets TARS hear your commands | [Amazon](https://amzn.to/4a8WfAZ) |
| 11 | **Mini Bluetooth Speaker** | 1 | Gives TARS a voice | [Amazon](https://amzn.to/4lAmXb1) |
| 12 | **8BitDo Controller** | 1 | Handheld motion control | [Amazon](https://amzn.to/3C7gXVd) |
| 13 | **Mini Keyboard + Touchpad** | 1 | Lightweight input for setup/debugging | [Amazon](https://amzn.to/40k1afc) |

## Hardware & Assembly

| # | Component | Qty | Description | Link |
|---|-----------|-----|-------------|------|
| 14 | **XT60 Connector Cables** | 1 | Male/female pair for battery power connection | [Amazon](https://amzn.to/3ZXSBW0) |
| 15 | **Machine Screws M3** | 1 | Assorted screws for assembly | [Amazon](https://www.amazon.com/Machine-Screws-Countersunk-Phillips-Assortment/dp/B0CCPH974T/) |
| 16 | **Metal Rods (100mm x 4.6mm)** | 1 | Linkage rods for arm mechanism | [AliExpress](https://fr.aliexpress.com/item/1005005995241789.html) |
| 17 | **Soldering Kit** | 1 | Everything needed for clean solder joints | [Amazon](https://amzn.to/4iXKlhk) |

## 3D Printing

| # | Component | Qty | Description | Link |
|---|-----------|-----|-------------|------|
| 18 | **Ender 3D Printer** | 1 | Affordable, builder-friendly printer | [Amazon](https://amzn.to/4a5rg8O) |

> Already have a 3D printer? The STL files are in the [`hardware/STL/`](../hardware/STL/) directory.

## 3D Printed Parts

All printable parts are included in this repo under [`hardware/STL/`](../hardware/STL/). Download the full bundle or print individual pieces.

**Recommended print settings:**
- Material: PLA or PETG
- Layer height: 0.2mm
- Infill: 20-30%
- Supports: Yes (for overhangs)

## Cost Estimate

| Category | Approximate Cost |
|----------|-----------------|
| Raspberry Pi 5 + accessories | ~$80-100 |
| Servos + driver + power | ~$40-60 |
| Display + audio + input | ~$40-60 |
| Hardware (screws, rods, connectors, solder) | ~$30-40 |
| 3D printing (filament) | ~$10-20 |
| **Total (without 3D printer)** | **~$200-280** |

> If you need to buy a 3D printer, add ~$200 for an Ender 3.

## API Services (Ongoing Costs)

| Service | Cost |
|---------|------|
| OpenAI API | ~$0.01-0.05/day with normal use |
| AWS Polly | Free tier: 5M characters/month for 12 months |
| OpenWeatherMap | Free tier: 1,000 calls/day |
