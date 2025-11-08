#!/usr/bin/env python3
# ADSB Station
#-----------------------------------------------------------------------------------------------------------------------------------
#           :::     :::::::::   ::::::::  :::::::::         :::::::: ::::::::::: ::: ::::::::::: ::::::::::: ::::::::  ::::    :::
#        :+: :+:   :+:    :+: :+:    :+: :+:    :+:       :+:    :+:    :+:   :+: :+:   :+:         :+:    :+:    :+: :+:+:   :+: 
#      +:+   +:+  +:+    +:+ +:+        +:+    +:+       +:+           +:+  +:+   +:+  +:+         +:+    +:+    +:+ :+:+:+  +:+  
#    +#++:++#++: +#+    +:+ +#++:++#++ +#++:++#+        +#++:++#++    +#+ +#++:++#++: +#+         +#+    +#+    +:+ +#+ +:+ +#+   
#   +#+     +#+ +#+    +#+        +#+ +#+    +#+              +#+    +#+ +#+     +#+ +#+         +#+    +#+    +#+ +#+  +#+#+#    
#  #+#     #+# #+#    #+# #+#    #+# #+#    #+#       #+#    #+#    #+# #+#     #+# #+#         #+#    #+#    #+# #+#   #+#+#     
# ###     ### #########   ########  #########         ########     ### ###     ### ###     ########### ########  ###    ####      
#-----------------------------------------------------------------------------------------------------------------------------------
# .- -.. ... -...    ... - .- - .. --- -.
# ---------------------------------------------------------------------------------------------------------------------------------

import math, time, json, urllib.request, collections, pygame, os
# --- Async Polling Thread (prevents render stutter) ---
import threading

_air_lock = threading.Lock()
_stop_evt  = threading.Event()

def _poll_loop():
    """Poll dump1090 in the background and update `aircraft` safely."""
    while not _stop_evt.is_set():
        try:
            data = preprocess(fetch_adsb())
            with _air_lock:
                aircraft[:] = data  
        except Exception:
            pass
        _stop_evt.wait(POLL_SECS)  

# ---------------- Config ----------------
DUMP_URL   = "http://localhost:8080/data.json"
POLL_SECS  = 1.0
FPS        = 60

# Palettes
PALETTES = [
    {"name":"STANDARD","BG":(8,8,10),"NEON":(0,210,120),"NEON_D":(0,180,103),
     "MINT":(132,255,237),"RINGS":(70,75,80),"ALTROW":(14,18,20),"TRAIL":(220,54,54)},
    {"name":"NVG","BG":(2,8,4),"NEON":(24,255,120),"NEON_D":(18,214,100),
     "MINT":(180,255,190),"RINGS":(90,140,100),"ALTROW":(8,20,10),"TRAIL":(250,50,50)},
    {"name":"AMBER","BG":(8,6,2),"NEON":(255,170,30),"NEON_D":(215,140,25),
     "MINT":(255,230,180),"RINGS":(150,120,80),"ALTROW":(25,18,8),"TRAIL":(255,80,60)}
]
pal_ix = 0
def C(k): return PALETTES[pal_ix][k]
WHITE = (235, 238, 240)

# MIL delta colors
MIL_OCEAN   = (0, 180, 255)
MIL_OCEAN_D = (0, 140, 210)

# Badge colors
BADGE_GOLD = (234, 195, 74)
BADGE_RED  = (205, 60, 60)
BADGE_CYAN = (0, 200, 220)

RING_W, OUTLINE_W = 2, 3
RIGHT_FRACTION = 0.41  # RIGHT UI FRAC SPACING
ROW_PAD_Y, HEADER_PAD_Y = 4, 6

COL_FRAC = [0.02, 0.12, 0.34, 0.55, 0.70, 0.85, 0.93]  # RIGHT UI SPACING

TRAIL_MAX_POINTS = 1500
TRAIL_KEEP_SEC   = 86400
TRAIL_WIDTH      = 2  # TRAIL SIZE/WIDTH
MAX_HOP_NM       = 6.0
MAX_SAMPLE_GAP   = 14.0
MAX_SEG_PX       = 1200
MIN_MOVE_NM      = 0.07
FORCE_SAMPLE_EVERY_SEC = 2.5

DECLUTTER_MIN_DIST = 28

ALLOWED_RANGES = [5,8,10,12,16,20,24,30,32,40,50,60,80,100,120,160,200,240,320]
RING_STEPS     = 6
RADAR_INSET    = 24
COMPASS_GUTTER = 18

DELTA_SIZE_PX = 12  # DELTA SIZE (RADAR)
DELTA_LINE_W  = 2
DELTA_DOT_R   = 2

pygame.init()
pygame.display.set_caption("ADSB-Station")
FLAGS = pygame.FULLSCREEN | pygame.SCALED
try:
    screen = pygame.display.set_mode((0, 0), FLAGS)
    if screen.get_width() == 0 or screen.get_height() == 0:
        raise Exception("0-sized mode")
except Exception:
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h), FLAGS)

clock  = pygame.time.Clock()

def load_ttf(path, size):
    try:
        if os.path.exists(path):
            return pygame.font.Font(path, size)
    except Exception:
        pass
    return None

def pick_font(size, bold=False):
    for name in ("TerminusTTF-4.49.3.ttf","TerminusTTF.ttf","Terminus.ttf"):
        f = load_ttf(name, size)
        if f: return f
    for n in ["JetBrains Mono","IBM Plex Mono","DejaVu Sans Mono","Menlo","Consolas","Monaco","Courier New"]:
        try:
            return pygame.font.SysFont(n, size, bold=bold)
        except Exception:
            pass
    return pygame.font.SysFont(None, size, bold=bold)

sh = screen.get_height()

UI_PX     = max(22, int(sh*0.022))
RING_PX   = max(20, int(sh*0.020))
TAG_PX    = max(19, int(sh*0.018))
ui_font   = pick_font(UI_PX)
ring_font = pick_font(RING_PX, bold=True)
tag_font  = pick_font(TAG_PX)

# ---------------- State ----------------
trails_on = True
declutter = False
mil_only  = False
aircraft  = []
trail_hist = {}
last_seen  = {}

radar_rect = pygame.Rect(0,0,0,0)
right_rect = pygame.Rect(0,0,0,0)
topbar_rect= pygame.Rect(0,0,0,0)
bottbar_rect=pygame.Rect(0,0,0,0)
center     = (0,0)
radius_px  = 0

SITE_NAME = "YOUR AIRBASE"  # INPUT YOUR STATION NAME HERE
SITE_LAT, SITE_LON = 00.00000, -000.00000   # REPLACE WITH YOUR CURRENT LAT/LON FOR ACCURATE RANGING
R_NM = 3440.065
_range_idx = ALLOWED_RANGES.index(32)

# ---------------- Helpers ----------------
def current_range_nm(): return ALLOWED_RANGES[_range_idx]

def fetch_adsb():
    try:
        with urllib.request.urlopen(DUMP_URL, timeout=0.9) as r:
            raw = json.loads(r.read().decode("utf-8","ignore"))
            return raw.get("aircraft", []) if isinstance(raw, dict) else raw
    except Exception:
        return []

def pnum(v):
    if v is None: return None
    if isinstance(v,(int,float)): return float(v)
    s=str(v).strip().lower()
    if s in ("","--","none","nan","ground"): return None
    try: return float(s)
    except: return None

def nm_to_px(nm, max_nm, radius_px): return (nm/max_nm)*radius_px

def bearing_to_xy(cx, cy, r, brg):
    a = math.radians(90 - (brg or 0))
    return int(round(cx + r*math.cos(a))), int(round(cy - r*math.sin(a)))

def great_circle_bearing(lat1,lon1,lat2,lon2):
    if None in (lat1,lon1,lat2,lon2): return None
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    dλ = math.radians(lon2-lon1)
    y = math.sin(dλ)*math.cos(φ2)
    x = math.cos(φ1)*math.sin(φ2) - math.sin(φ1)*math.cos(φ2)*math.cos(dλ)
    return (math.degrees(math.atan2(y,x)) + 360) % 360

def gc_distance_nm(lat1,lon1,lat2,lon2):
    if None in (lat1,lon1,lat2,lon2): return None
    φ1,φ2=math.radians(lat1),math.radians(lat2)
    dφ=math.radians(lat2-lat1); dλ=math.radians(lon2-lon1)
    a = math.sin(dφ/2)**2 + math.cos(φ1)*math.cos(φ2)*math.sin(dλ/2)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R_NM*c

def ll_to_range_brg(lat,lon):
    if lat is None or lon is None: return (None,None)
    φ1,φ2=math.radians(SITE_LAT),math.radians(lat)
    dφ=math.radians(lat-SITE_LAT); dλ=math.radians(lon-SITE_LON)
    a = math.sin(dφ/2)**2 + math.cos(φ1)*math.cos(φ2)*math.sin(dλ/2)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    rnm = R_NM*c
    brg = great_circle_bearing(SITE_LAT,SITE_LON,lat,lon)
    return rnm, brg

def mil_heuristic(hexid):
    if not hexid: return False
    h = hexid.upper()
    return h.startswith("AE") or h.startswith("43C")

# ---------------- Layout ----------------
def layout(w,h):
    global radar_rect,right_rect,topbar_rect,bottbar_rect,center,radius_px
    pad=12
    th  = ui_font.get_height()+10
    bh  = ui_font.get_height()+14
    topbar_rect  = pygame.Rect(0,0,w,th)
    bottbar_rect = pygame.Rect(0,h-bh,w,bh)
    usable = pygame.Rect(pad, th + pad, w - 2 * pad, h - (th + bh) - 2 * pad - 4)
    usable = pygame.Rect(pad, th+pad, w-2*pad, h-(th+bh)-2*pad)

    right_w = int(usable.w*RIGHT_FRACTION)
    right_rect = pygame.Rect(usable.right-right_w, usable.y, right_w, usable.h)

    radar_rect = pygame.Rect(usable.x, usable.y, usable.w-right_w, usable.h)
    s = min(radar_rect.w, radar_rect.h)
    radar_rect.size=(s,s)
    center=(radar_rect.left+s//2, radar_rect.top+s//2)
    radius_px = radar_rect.w//2-(RADAR_INSET+COMPASS_GUTTER)

# ---------------- Drawing ----------------
def blit(font, txt, color, pos): screen.blit(font.render(txt, True, color), pos)

#def draw_top():
#    pygame.draw.rect(screen, C("BG"), topbar_rect)
#    msg=f"STN:  {SITE_NAME}   POS:  {SITE_LAT:.5f},  {SITE_LON:.5f}   HDG REF:  N-UP   LCL:  {time.strftime('%H:%M:%S')}"
#    blit(ui_font,msg,C("MINT"),(12,(topbar_rect.h-ui_font.get_height())//2))
def draw_top():
    pygame.draw.rect(screen, C("BG"), topbar_rect)
    left  = f"STN: {SITE_NAME}   POS: {SITE_LAT:.5f}, {SITE_LON:.5f}   HDG REF: N-UP"
    right = f"LCL: {time.strftime('%H:%M:%S')}"
    blit(ui_font, left,  C("MINT"), (12, (topbar_rect.h - ui_font.get_height()) // 2))
    rx = topbar_rect.right - 12 - ui_font.size(right)[0]
    blit(ui_font, right, C("MINT"), (rx, (topbar_rect.h - ui_font.get_height()) // 2))

#def draw_bottom():
#   pygame.draw.rect(screen, C("BG"), bottbar_rect)
#   rng = current_range_nm()
#   left=f"ADSB STATION  |  LINK: {'ACTIVE' if aircraft else 'NO DATA'}  |  TRACKS: {len(aircraft)}  |  RANGE: {rng} NM  |  ALT BAND: ALL  |"
#   mid =f"  TRAILS {'ON' if trails_on else 'OFF'}  |  DECLUTTER {'ON' if declutter else 'OFF'}  |  {'MILITARY' if mil_only else 'ALL'}"
#   blit(ui_font,left+mid,C("MINT"),(12,bottbar_rect.y+(bottbar_rect.h-ui_font.get_height())//2))
    # FPS removed per request
def draw_bottom():
    pygame.draw.rect(screen, C("BG"), bottbar_rect)
    rng = current_range_nm()

    left  = f"ADSB STATION  |  LINK: {'ACTIVE' if aircraft else 'NO DATA'}  |  TRACKS: {len(aircraft)}  |  RANGE: {rng} NM  |  ALT BAND: ALL"
    right = f"TRAILS {'ON' if trails_on else 'OFF'}  |  DECLUTTER {'ON' if declutter else 'OFF'}  |  {'MIL ONLY' if mil_only else 'ALL'}"

    # Left-aligned text
    blit(ui_font, left, C("MINT"), (12, bottbar_rect.y + (bottbar_rect.h - ui_font.get_height()) // 2))

    # Right-aligned text
    rx = bottbar_rect.right - 12 - ui_font.size(right)[0]
    blit(ui_font, right, C("MINT"), (rx, bottbar_rect.y + (bottbar_rect.h - ui_font.get_height()) // 2))


def draw_badges():
    """Draw static radar badges: DECLUTTER / TRAILS OFF / MILITARY."""
    pad = 10
    x, y = radar_rect.x+pad, radar_rect.y+pad
    if declutter:
        tx = ui_font.render("DECLUTTER", True, BADGE_GOLD)
        badge = pygame.Rect(x, y, tx.get_width()+12, tx.get_height()+6)
        pygame.draw.rect(screen, C("BG"), badge)
        pygame.draw.rect(screen, BADGE_GOLD, badge, 1, border_radius=6)
        screen.blit(tx, (badge.x+6, badge.y+3))
        y += badge.height + 6
    if not trails_on:
        tx = ui_font.render("TRAILS OFF", True, BADGE_RED)
        badge = pygame.Rect(x, y, tx.get_width()+12, tx.get_height()+6)
        pygame.draw.rect(screen, C("BG"), badge)
        pygame.draw.rect(screen, BADGE_RED, badge, 1, border_radius=6)
        screen.blit(tx, (badge.x+6, badge.y+3))
        y += badge.height + 6
    if mil_only:
        tx = ui_font.render("MILITARY", True, BADGE_CYAN)
        badge = pygame.Rect(x, y, tx.get_width()+12, tx.get_height()+6)
        pygame.draw.rect(screen, C("BG"), badge)
        pygame.draw.rect(screen, BADGE_CYAN, badge, 1, border_radius=6)
        screen.blit(tx, (badge.x+6, badge.y+3))

def draw_rings():
    cx,cy=center
    outer=radius_px
    pygame.draw.circle(screen,C("RINGS"),(cx,cy),outer,RING_W)
    for i in range(1,RING_STEPS):
        pygame.draw.circle(screen,C("RINGS"),(cx,cy),int(outer*(i/RING_STEPS)),1)

    on=int(outer*((RING_STEPS-1)/RING_STEPS))
    tick=max(8,int(nm_to_px(0.035*current_range_nm(),current_range_nm(),on)))
    for b in range(0,360,15):
        x1,y1=bearing_to_xy(cx,cy,on-2,b); x2,y2=bearing_to_xy(cx,cy,on-2-tick,b)
        pygame.draw.line(screen,C("RINGS"),(x1,y1),(x2,y2),1)

    step = current_range_nm() // RING_STEPS
    for i in range(1,RING_STEPS+1):
        r=int(outer*(i/RING_STEPS))
        t=ring_font.render(f"{i*step} nm",True,C("RINGS"))
        x,y=bearing_to_xy(cx,cy,r-8,90)
        screen.blit(t,(x - t.get_width(), y - t.get_height()//2))

    nesw_r=outer+COMPASS_GUTTER-4
    for b,ch in [(0,'N'),(90,'E'),(180,'S'),(270,'W')]:
        t=ring_font.render(ch,True,C("RINGS")); x,y=bearing_to_xy(cx,cy,nesw_r,b)
        screen.blit(t,(x-t.get_width()//2,y-t.get_height()//2))

    mid=int(outer*(RING_STEPS-1)/RING_STEPS)
    for ang,val in [(315,"315"),(45,"45"),(135,"135"),(225,"225")]:
        t=ring_font.render(val,True,C("RINGS"))
        x,y=bearing_to_xy(cx,cy,mid,ang)
        screen.blit(t,(x-t.get_width()//2,y-t.get_height()//2))

def draw_right():
    x,y,w,h=right_rect
    pad=12
    inner=right_rect.inflate(-pad*2,-pad*2)
    colx=[inner.x+int(fr*inner.w) for fr in COL_FRAC]

    headers=["MIL","CALLSIGN","ICAO","ALT","SPD","TRK","IFF"]
    for i,t in enumerate(headers):
        blit(ui_font,t,C("MINT"),(colx[i], inner.y+HEADER_PAD_Y))
    uy=inner.y+HEADER_PAD_Y+ui_font.get_height()+2
    pygame.draw.line(screen,C("RINGS"),(inner.x,uy),(inner.right,uy),1)

    rows=[a for a in aircraft if (not mil_only or a.get('_mil'))]
    rows.sort(key=lambda a: (a.get('_range_nm') is None, a.get('_range_nm') or 0.0))
    row_y=uy+8; row_h=ui_font.get_height()+ROW_PAD_Y*2

    def clip_txt(txt, maxpx, color):
        if not txt: txt="--"
        surf = ui_font.render(txt, True, color)
        if surf.get_width() <= maxpx: return txt
        s = txt
        lo, hi = 0, len(s)
        while lo < hi:
            mid = (lo+hi)//2
            piece = s[:mid] + "…"
            if ui_font.render(piece, True, color).get_width() <= maxpx:
                lo = mid + 1
            else:
                hi = mid
        return s[:max(1,hi-1)] + "…"

    colw = []
    for i in range(len(COL_FRAC)-1):
        colw.append( max(10, int((COL_FRAC[i+1]-COL_FRAC[i]) * inner.w) - 10) )
    colw.append( max(10, inner.right - colx[-1] - 10) )

    for i,ac in enumerate(rows):
        if i%2: pygame.draw.rect(screen,C("ALTROW"),pygame.Rect(inner.x,row_y,inner.w,row_h))
        fields = [
            ("MIL" if ac.get('_mil') else "--"),
            (ac.get('flight') or "--"),
            (ac.get('hex') or "--").upper(),
            (ac.get('alt_show') if ac.get('alt_show') else "--"),
            (ac.get('spd_show') if ac.get('spd_show') else "--"),
            (str(int((ac.get('track') if ac.get('track') is not None else ac.get('_bearing'))%360)) if (ac.get('track') is not None or ac.get('_bearing') is not None) else "--"),
            (ac.get('squawk') or "--"),
        ]
        for c,txt in enumerate(fields):
            color = WHITE if (c==1) else C("RINGS")
            clipped = clip_txt(str(txt), colw[c], color)
            screen.blit(ui_font.render(clipped,True,color),(colx[c],row_y+ROW_PAD_Y))
        row_y+=row_h
        if row_y>inner.bottom-row_h: break

def draw_delta(x,y,hdg,is_mil,scale=1.0):
    size = int(DELTA_SIZE_PX * scale)
    a = math.radians(90 - (hdg or 0))
    tx = x + size*math.cos(a); ty = y - size*math.sin(a)
    base_depth = size * 0.85
    bx = x - base_depth*math.cos(a); by = y + base_depth*math.sin(a)
    half_w = size * 0.55
    pa = a + math.pi/2
    lx, ly = bx + half_w*math.cos(pa), by - half_w*math.sin(pa)
    rx, ry = bx - half_w*math.cos(pa), by + half_w*math.sin(pa)
    col = (MIL_OCEAN_D if declutter else MIL_OCEAN) if is_mil else (C("NEON_D") if declutter else C("NEON"))
    pygame.draw.polygon(screen, col, [(tx,ty),(lx,ly),(rx,ry)], DELTA_LINE_W)
    if declutter:
        pygame.draw.circle(screen, col, (int(x), int(y)), DELTA_DOT_R, 0)

def parse_alt(it):
    keys=["baro_altitude","alt_baro","altitude","alt_geom","geom_altitude","nav_altitude_mcp","nav_altitude_fms"]
    for k in keys:
        v = pnum(it.get(k))
        if v is not None: return int(round(v))
    return None

def parse_spd(it):
    for k in ["gs","ground_speed","groundspeed","speed","spd"]:
        v = pnum(it.get(k))
        if v is not None: return int(round(v))
    for k in ["tas","ias"]:
        v = pnum(it.get(k))
        if v is not None: return int(round(v))
    m = pnum(it.get("mach"))
    if m is not None: return int(round(m*661.0))
    return None

def preprocess(raw):
    out=[]; now=time.time()
    for it in raw:
        hx=(it.get("hex") or "").lower()
        lat,lon=it.get("lat"),it.get("lon")
        rnm,brg=ll_to_range_brg(lat,lon)
        alt_v = parse_alt(it); spd_v = parse_spd(it)
        trk   = pnum(it.get("track")) or pnum(it.get("trak"))
        ac={
            "hex": hx,
            "flight": (it.get("flight") or "").strip() or None,
            "alt_show": (str(int(alt_v)) if alt_v is not None else None),
            "spd_show": (str(int(spd_v)) if spd_v is not None else None),
            "track": trk,
            "lat": lat, "lon": lon,
            "squawk": it.get("squawk"),
            "_range_nm": rnm,
            "_bearing": brg,
            "_mil": mil_heuristic(hx)
        }
        out.append(ac)
        if hx: last_seen[hx] = now
        if trails_on and hx and lat is not None and lon is not None:
            dq = trail_hist.setdefault(hx, collections.deque(maxlen=TRAIL_MAX_POINTS))
            if dq:
                lt, lla, llo = dq[-1]
                dt = now - lt
                dist_nm = gc_distance_nm(lla, llo, lat, lon) or 0.0
                if (dt <= MAX_SAMPLE_GAP and MIN_MOVE_NM <= dist_nm < MAX_HOP_NM) or dt >= FORCE_SAMPLE_EVERY_SEC:
                    dq.append((now, lat, lon))
            else:
                dq.append((now, lat, lon))
    cutoff=now-TRAIL_KEEP_SEC
    for k in list(trail_hist.keys()):
        if last_seen.get(k,0)<cutoff:
            trail_hist.pop(k,None); last_seen.pop(k,None)
    return out

def draw_scene():
    w,h=screen.get_size()
    screen.fill(C("BG")); layout(w,h)
    pygame.draw.rect(screen,C("NEON"),radar_rect,OUTLINE_W,border_radius=8)
    pygame.draw.rect(screen,C("NEON"),right_rect,OUTLINE_W,border_radius=8)
    draw_top(); draw_rings(); draw_badges()

    cx,cy=center
    trail_layer=pygame.Surface((w,h),pygame.SRCALPHA)
    rng = current_range_nm()
    #acs=[a for a in aircraft if (not mil_only or a.get('_mil'))]
    #acs.sort(key=lambda a:(a.get('_range_nm')is None,a.get('_range_nm')or 0.0))
        # take a snapshot of aircraft under a lock
    with _air_lock:
        acs = list(aircraft)
    acs = [a for a in acs if (not mil_only or a.get('_mil'))]
    acs.sort(key=lambda a:(a.get('_range_nm') is None, a.get('_range_nm') or 0.0))


    for ac in acs:
        rnm=ac.get('_range_nm'); brg_pos=ac.get('_bearing')
        if rnm is None or rnm>rng or brg_pos is None: continue
        rr=int(nm_to_px(rnm,rng,radius_px)); x,y=bearing_to_xy(cx,cy,rr,brg_pos)
        hdg = ac.get('track') if ac.get('track') is not None else brg_pos
        draw_delta(x,y,hdg,ac.get('_mil',False),scale=1.0)
        if not declutter:
            cs=ac.get('flight') or ac.get('hex','').upper()
            screen.blit(tag_font.render(cs,True,WHITE),(x+23,y-12))  # DELTA ICAO SPACING +X (X-AXIS), Y- (Y-AXIS) 
        if trails_on:
            hx=ac.get('hex')
            if hx and hx in trail_hist:
                dq=trail_hist[hx]
                pts=[]
                for (tt,lt,ln) in dq:
                    rnm_h,brg_h=ll_to_range_brg(lt,ln)
                    if rnm_h is None or brg_h is None or rnm_h>rng:
                        pts.append(None);continue
                    rr_h=int(nm_to_px(rnm_h,rng,radius_px))
                    pts.append(bearing_to_xy(cx,cy,rr_h,brg_h))
                lastp=None; n=len(pts); r,g,b=C("TRAIL")
                for i,p in enumerate(pts):
                    if p is None: lastp=None;continue
                    if lastp:
                        dpx=math.hypot(p[0]-lastp[0],p[1]-lastp[1])
                        if dpx<=MAX_SEG_PX:
                            t=(i/max(1,n-1));a=60+int(180*(t*t))
                            pygame.draw.line(trail_layer,(r,g,b,a),lastp,p,TRAIL_WIDTH)
                        else:lastp=None;continue
                    lastp=p
    screen.blit(trail_layer,(0,0))
    draw_right(); draw_bottom()

# ---------------- Controls ----------------
def handle_key(k):
    global trails_on,declutter,mil_only,pal_ix,_range_idx
    if k in(pygame.K_EQUALS,pygame.K_PLUS,pygame.K_KP_PLUS):
        if _range_idx<len(ALLOWED_RANGES)-1:_range_idx+=1
    elif k in(pygame.K_MINUS,pygame.K_UNDERSCORE,pygame.K_KP_MINUS):
        if _range_idx>0:_range_idx-=1
    elif k==pygame.K_t:trails_on=not trails_on
    elif k==pygame.K_d:declutter=not declutter
    elif k==pygame.K_m:mil_only=not mil_only
    elif k==pygame.K_n:
        pal_ix=(pal_ix+1)%len(PALETTES)
        pygame.display.set_caption(f"Lightning — {PALETTES[pal_ix]['name']}")
    elif k==pygame.K_F11:toggle_fullscreen()
    elif k==pygame.K_ESCAPE:pygame.event.post(pygame.event.Event(pygame.QUIT))

def toggle_fullscreen():
    global screen
    pygame.display.quit();pygame.display.init()
    try:
        screen=pygame.display.set_mode((0,0),pygame.FULLSCREEN|pygame.SCALED)
        if screen.get_width()==0:raise Exception()
    except Exception:
        info=pygame.display.Info()
        screen=pygame.display.set_mode((info.current_w,info.current_h),
                                       pygame.FULLSCREEN|pygame.SCALED)

# ---------------- Main ----------------
def main():
    running = True

    t = threading.Thread(target=_poll_loop, daemon=True)
    t.start()

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                handle_key(e.key)

        draw_scene()
        pygame.display.flip()
        clock.tick(FPS)

    _stop_evt.set()
    t.join(timeout=1.0)
    pygame.quit()


if __name__=="__main__":
    main()
