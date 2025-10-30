# ADSB Station ⚓︎
---
## Project Background
---

**ADSB-Station** is a modern reinterpretation of [nicespoon’s _retro-adsb-radar_](https://github.com/nicespoon/retro-adsb-radar).  _retro-adsb-radar_ was built for **Raspberry Pi** and **tar1090** with a classic CRT-style display, ADSB-Station extends the concept for **desktops, laptops, and small Pi displays** using dump1090 by default.

It maintains the **military aviation aesthetic** while adding modern functionality.  

The program reads from **dump1090**, **tar1090**, or any **1090 MHz decoder**
that outputs a `data.json` feed, rendering a live tactical display using **Python/Pygame**.

---
## How It Works
---

ADSB-Station connects to a local ADSB receiver (such as `dump1090`) to collect live aircraft broadcast data.  

Each aircraft periodically transmits its position, altitude, velocity, and unique ICAO address.

The software uses the configured station coordinates to calculate each aircraft’s position relative to the receiver.

- `SITE_LAT` and `SITE_LON` define the fixed geographic location of the station.

The result is a live, polar-style radar centered on your station, displaying all detected aircraft in real time.

---
## Design
---

- Modern tactical interface with subdued tones and vector graphics
    
- Multi-layer layout modeled after Military/ATC displays

----
## Key Features
---

- **Directional deltas** showing heading and movement
    
- **Motion trails** for track history
	
- **Expanded aircraft table** (MIL, ICAO, IFF, ALT, SPD, TRK)
    
- **Live status bar** with link, range, and track info
    
- **Refined geometry and contrast** for situational awareness
    
- **Full user customization** (open source)
	

---
## Controls
---

`+` Increase range  
	
`-` Decrease range  
	
`D` Toggle declutter  
	
`T` Toggle trails  
	
`M` Military-only filter  
	
`N` Change color palette  
	
`ESC` Exit

---
## Configuration
---

## How to configure ⛯

- **The python script contains configuration parameters for full user customization, you can use any text editor to modify these values (advice varies based on text editor used)**


			sudo nano ADSB-Station.py

**or**

			sudo vim ADSB-Station.py

**or**

			sudo vi ADSB-Station.py
## Station Name ✈︎

		   SITE_NAME="YOUR STATION NAME"

## Coordinates (Longitude/Latitude) ⏲

- **Input your Latitude**

		 SITE_LAT="CURRENT LATITUDE"

- **Input your Longitude**

		 SITE_LON="CURRENT LONGITUDE

## Station UI font size ⌞ ⌝

		UI_PX 

## Radar Compass font size ⏱

		RING_PX = Font Size for [RADAR COMPASS]

## Delta ICAO font positioning ➤

- **(x+) Change X-AXIS POS, (y)- Y-AXIS-POS**

		(tag_font.render(cs,True,WHITE),(x+23,y-12)

## Adjusting (Trail Width) ╰┈➤

		TRAIL_WIDTH
