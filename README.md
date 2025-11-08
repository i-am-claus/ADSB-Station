# ADSB Station ⚓︎
---
## Project Background
---

**ADSB-Station** is a modern reinterpretation of [nicespoon’s _retro-adsb-radar_](https://github.com/nicespoon/retro-adsb-radar).
Built from the ground up, It maintains the **military aviation aesthetic** while adding modern functionality using the same fundamentals.  

The program reads from **dump1090**, **tar1090**, or any **1090 MHz decoder**
that outputs a `data.json` feed, rendering a live tactical display using **Python/Pygame**.

---
## How It Works
---

ADSB-Station connects to a local ADSB receiver (such as `dump1090`) to collect live aircraft broadcast data.  

Each aircraft periodically transmits its position, altitude, velocity, and unique ICAO address.

The software uses the configured station coordinates to calculate each aircraft’s position relative to the receiver.

- `SITE_LAT` and `SITE_LON` define the fixed geographic location of the station.

The result is a live, polar-style radar centered on your station, displaying all detected aircraft in real time through **pygame**.

---
## Design
---

- Modern tactical interface with subdued tones and vector graphics
    
- Multi-layer layout modeled after Military/ATC displays

---
## Color Schemes
---

**LIGHTNING**

---

<img width="1920" height="1200" alt="image" src="https://github.com/user-attachments/assets/0b76dd52-f0c6-49ef-9298-045365bfc3d6" />

---

**HUNTER**

---

<img width="1920" height="1200" alt="image" src="https://github.com/user-attachments/assets/71823e1f-5403-4226-ab00-edc5bd06caa8" />

---

**AMBER**

---

<img width="1920" height="1200" alt="image" src="https://github.com/user-attachments/assets/15c5e05c-177e-4d24-842a-c156675332b7" />


---
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
## Requirements
---

- Laptop, (Android) Tablet running Linux, Single Board Computer, or Desktop.
	
- RTL-SDR Dongle (Software Defined Radio)
	
- dump1090 or tar1090 for live data.json outputs
	
- 1090 mhz antenna, or 1GHZ-2.4GHZ antenna. 

---
## How to Install Pygame
---

- **Debian or Ubuntu (Dependencies)**

		 sudo apt install pip && python3

- **Fedora or RHEL (Dependencies)**

		 sudo dnf install pip && python3

- **Install Pygame** 

		python3 -m pip install -U pygame --user
---
## How to use the script?
---

		python3 ADSB-Station.py

- **Note:** You must have **dump1090** or **tar1090** running to display live aircraft data while the script is active.

---
## How to configure ⛯
---

**The python script contains configuration parameters for full user customization, you can use any text editor to modify the values (advice varies based on text editor used)**

---
## Station Name ✈︎
---

		   SITE_NAME="YOUR STATION NAME"

---
## Coordinates (Longitude/Latitude) ⏲
---

**Input your Latitude**

		 SITE_LAT="CURRENT LATITUDE"

**Input your Longitude**

		 SITE_LON="CURRENT LONGITUDE

---
## Station UI font size ⌞ ⌝
---

		UI_PX=

---
## Radar Compass font size ⏱
---

		RING_PX=

---
## Delta ICAO font positioning ➤
---

**(x+) Change X-AXIS POS, (y)- Y-AXIS-POS**

		(tag_font.render(cs,True,WHITE),(x+23,y-12)

---
## Adjusting (Trail Width) ╰┈➤
---

		TRAIL_WIDTH=
