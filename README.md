# ADSB Station
---
## Project Background

**ADSB-Station** is a modern reinterpretation of [nicespoon’s _retro-adsb-radar_](https://github.com/nicespoon/retro-adsb-radar). While _retro-adsb-radar_ was built for **Raspberry Pi** and **tar1090** with a classic CRT-style display, ADSB-Station extends the concept for **desktops, laptops, and small Pi displays**.

It maintains the **military aviation aesthetic** while adding modern functionality.  

The program reads from **dump1090**, **tar1090**, or any **1090 MHz decoder**
that outputs a `data.json` feed, rendering a live tactical display using **Python/Pygame**.

---

## Key Features

- **Directional deltas** showing heading and movement
    
- **Motion trails** for track history
    
- **Declutter mode** (`D`)
    
- **Adjustable range** (`+` / `–`)
    
- **MIL target filter** (`M`)
    
- **Palette cycling** (`N`)
    
- **Expanded aircraft table** (MIL, ICAO, IFF, ALT, SPD, TRK)
    
- **Live status bar** with link, range, and track info
    
- **Refined geometry and contrast** for situational awareness
    

---

## Design

- Modern tactical interface with subdued tones and vector graphics
    
- Multi-layer layout modeled after military/ATC displays
    


---

## How It Works

- A receiver (e.g., RTL-SDR) captures **1090 MHz ADS-B** signals.
    
- Decoders like **dump1090** or **tar1090** output aircraft data as `data.json`.
    
- ADSB-Station reads the JSON and renders it in real time using **Pygame**.

---

## Controls

`+` Increase range  
`-` Decrease range  
`D` Toggle declutter  
`T` Toggle trails  
`M` Military-only filter  
`N` Change color palette  
`ESC` Exit

---


