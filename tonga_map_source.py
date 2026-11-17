# created with Claude
import glob, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, Ellipse, Circle, FancyArrowPatch

for f in glob.glob("/usr/share/fonts/opentype/inter/Inter-*.otf"):
    if "Italic" not in f:
        fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Inter"

W, H = 2560, 1440
fig = plt.figure(figsize=(W/100, H/100), dpi=100, facecolor="#0A1120")
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")

pt = lambda px: px * 0.72
BG, PANEL, BORDER = "#0A1120", "#101A2C", "#1E2D46"
TXT, MUTED, DIM = "#E8EEF8", "#8DA2C0", "#5B7090"
SAAB, Y12, DHC = "#38BDF8", "#FBBF24", "#A78BFA"
TEAL = "#2DD4BF"

def T(x, y, s, size=22, color=TXT, weight="regular", ha="left", va="center", z=10, **k):
    return ax.text(x, y, s, fontsize=pt(size), color=color, fontweight=weight, ha=ha, va=va, zorder=z, **k)

def rbox(x, y, w, h, r, fc, ec=None, lw=1.5, z=1, alpha=1):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                       fc=fc, ec=ec or "none", lw=lw, zorder=z, alpha=alpha)
    ax.add_patch(p); return p

# ---------- data ----------
AP = {
 "TBU": dict(icao="NFTF", name="Fua'amotu International", grp="Tongatapu", lat=-21.2412, lon=-175.1497),
 "EUA": dict(icao="NFTE", name="'Eua (Kaufana)",           grp="'Eua",      lat=-21.3772, lon=-174.9578),
 "HPA": dict(icao="NFTL", name="Lifuka (Salote Pilolevu)", grp="Ha'apai Group", lat=-19.7767, lon=-174.3411),
 "VAV": dict(icao="NFTV", name="Vava'u (Lupepau'u)",       grp="Vava'u Group", lat=-18.5853, lon=-173.9620),
 "NTT": dict(icao="NFTP", name="Niuatoputapu",             grp="Niuas",     lat=-15.9770, lon=-173.7550),
 "NFO": dict(icao="NFTO", name="Niuafo'ou (Kuini Lavinia)",grp="Niuas",     lat=-15.5711, lon=-175.6308),
}
ROUTES = [  # a, b, label, minutes-note, primary colour, aircraft list
 ("TBU","VAV","Tongatapu → Vava'u","60","reported 50–85 min", SAAB, [("Saab 340B",SAAB)]),
 ("TBU","HPA","Tongatapu → Ha'apai","30–50","sources vary", SAAB, [("Saab 340B",SAAB),("DHC-6",DHC)]),
 ("TBU","EUA","Tongatapu → 'Eua","8–10","one of the world's shortest", Y12, [("Harbin Y-12",Y12),("DHC-6",DHC)]),
 ("VAV","HPA","Vava'u → Ha'apai","20–30","", SAAB, [("Saab 340B",SAAB)]),
 ("VAV","NTT","Vava'u → Niuatoputapu","~70","weekly / fortnightly", DHC, [("DHC-6",DHC),("Harbin Y-12",Y12)]),
 ("VAV","NFO","Vava'u → Niuafo'ou","~90","weekly / fortnightly", DHC, [("DHC-6",DHC),("Harbin Y-12",Y12)]),
]
def hav(a, b):
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"])
    dl = math.radians(b["lon"]-a["lon"]); dp = p2-p1
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*6371*math.asin(math.sqrt(h))

# ---------- map projection (equirectangular, cos-lat corrected) ----------
MX0, MY0, MX1, MY1 = 72, 190, 752, 1330
LAT_TOP, LON_MIN = -15.0, -176.9
S = (MY1-MY0)/7.0                     # px per degree latitude
COS = math.cos(math.radians(18.5))
def P(lat, lon): return (MX0 + (lon-LON_MIN)*COS*S, MY0 + (LAT_TOP-lat)*S)
KM = S/111.2                           # px per km

# ---------- header ----------
T(72, 78, "Airports of Tonga", 62, TXT, "bold")
T(74, 132, "Scheduled domestic network  ·  flight times in minutes  ·  aircraft types", 26, MUTED)
rbox(2230, 62, 258, 52, 26, "#13203A", BORDER)
T(2359, 88, "Updated 15 Nov 2026", 22, MUTED, "medium", ha="center")

# ---------- map panel ----------
mp = rbox(MX0, MY0, MX1-MX0, MY1-MY0, 28, "none", BORDER, z=1)
grad = np.linspace(0, 1, 256).reshape(-1, 1)
from matplotlib.colors import LinearSegmentedColormap
cm = LinearSegmentedColormap.from_list("sea", ["#0F2540", "#0B1A30", "#0A1527"])
im = ax.imshow(grad, extent=(MX0, MX1, MY1, MY0), cmap=cm, aspect="auto", zorder=0.5)
clip = FancyBboxPatch((MX0, MY0), MX1-MX0, MY1-MY0, boxstyle="round,pad=0,rounding_size=28", transform=ax.transData)
im.set_clip_path(clip)
ax.set_xlim(0, W); ax.set_ylim(H, 0)

# graticule
for la in range(-21, -15):
    x, y = P(la, LON_MIN)
    ax.plot([MX0+14, MX1-14], [y, y], color="#1B2B45", lw=1.2, zorder=2)
    T(MX0+22, y-13, f"{abs(la)}°S", 17, DIM, "medium")
for lo in (-176, -175, -174, -173):
    x, y = P(-15, lo)
    ax.plot([x, x], [MY0+14, MY1-14], color="#1B2B45", lw=1.2, zorder=2)
    T(x+8, MY0+30, f"{abs(lo)}°W", 17, DIM, "medium")

# island footprints (schematic, approximate sizes)
def island(lat, lon, wkm, hkm, ang=0, col="#2B4766"):
    x, y = P(lat, lon)
    for k, a in ((2.6, .10), (1.9, .16)):
        ax.add_patch(Ellipse((x, y), wkm*KM*k, hkm*KM*k, angle=ang, fc=TEAL, ec="none", alpha=a*0.45, zorder=3))
    ax.add_patch(Ellipse((x, y), max(wkm*KM, 6), max(hkm*KM, 5), angle=ang, fc=col, ec="#4B6E96", lw=1.2, zorder=4))
island(-21.20, -175.15, 38, 15, -22)          # Tongatapu
island(-21.38, -174.93, 7, 20, 0)             # 'Eua
island(-19.78, -174.32, 4, 22, 8)             # Lifuka–Foa
island(-20.27, -174.80, 6, 6)                 # Nomuka
island(-18.66, -173.98, 20, 11, -10)          # Vava'u
island(-18.60, -174.10, 6, 6); island(-18.72, -174.10, 6, 5)
island(-15.96, -173.78, 11, 4.5, 0)           # Niuatoputapu
island(-15.86, -173.72, 3.5, 3.5)             # Tafahi
island(-15.60, -175.63, 8, 8)                 # Niuafo'ou

# routes
rt_pts = {}
for a, b, lab, mins, note, col, ac in ROUTES:
    xa, ya = P(AP[a]["lat"], AP[a]["lon"]); xb, yb = P(AP[b]["lat"], AP[b]["lon"])
    ax.plot([xa, xb], [ya, yb], color=col, lw=10, alpha=.13, solid_capstyle="round", zorder=5)
    ax.plot([xa, xb], [ya, yb], color=col, lw=3.2, alpha=.95, solid_capstyle="round", zorder=6)
    rt_pts[(a, b)] = ((xa, ya), (xb, yb))

# international arrow
xt, yt = P(AP["TBU"]["lat"], AP["TBU"]["lon"])
ax.add_patch(FancyArrowPatch((xt-14, yt+8), (xt-120, yt+44), arrowstyle="-|>", mutation_scale=20,
             color=TEAL, lw=2.2, linestyle=(0, (4, 4)), zorder=6, alpha=.9))
T(MX0+22, MY1-46, "To Auckland  ·  ~2,150 km", 19, TEAL, "semibold")
T(MX0+22, MY1-22, "Air New Zealand · Fiji Airways", 17, MUTED)

# duration pills on the map
def pill(cx, cy, s, col):
    w = 15.5*len(s) + 58
    rbox(cx-w/2, cy-19, w, 38, 19, "#0A1527", col, 2, z=8)
    T(cx-w/2+16+ (0), cy+1, "", 1)
    T(cx, cy+1, f"{s} min", 20, TXT, "bold", ha="center", z=9)
mid = lambda a, b: tuple((np.array(rt_pts[(a,b)][0])+np.array(rt_pts[(a,b)][1]))/2)
for a, b, lab, mins, note, col, ac in ROUTES:
    cx, cy = mid(a, b)
    if (a, b) == ("TBU", "EUA"):
        ax.plot([cx, cx+64], [cy, cy+58], color=col, lw=1.4, alpha=.8, zorder=7)
        cx, cy = cx+64, cy+58
    if (a, b) == ("VAV", "NFO"): cx, cy = cx-4, cy+4
    off = {("TBU","VAV"): (136, 44), ("TBU","HPA"): (-78, 8), ("VAV","HPA"): (84, 0)}
    if (a, b) in off:
        ox, oy = off[(a, b)]
        ax.plot([cx, cx+ox], [cy, cy+oy], color=col, lw=1.4, alpha=.8, zorder=7)
        cx, cy = cx+ox, cy+oy
    pill(cx, cy, mins, col)

# airport markers + labels
LBL = {  # (dx, dy, ha)
 "TBU": (-24, -22, "right"), "EUA": (22, 0, "left"), "HPA": (22, 0, "left"),
 "VAV": (22, 0, "left"), "NTT": (22, 0, "left"), "NFO": (-22, 0, "right")}
for k, d in AP.items():
    x, y = P(d["lat"], d["lon"])
    hub = k == "TBU"
    if hub:
        for r, a in ((30, .10), (22, .18)):
            ax.add_patch(Circle((x, y), r, fc=TEAL, ec="none", alpha=a, zorder=9))
    ax.add_patch(Circle((x, y), 12 if hub else 9, fc="#F8FAFF", ec=TEAL if hub else "#0A1527", lw=3, zorder=11))
    dx, dy, ha = LBL[k]
    T(x+dx, y+dy-11, f"{k} · {d['icao']}", 23, TXT, "bold", ha=ha, z=12)
    T(x+dx, y+dy+13, d["grp"], 18, MUTED, "regular", ha=ha, z=12)

# north arrow + scale bar
nx, ny = MX1-44, MY0+330
ax.add_patch(FancyArrowPatch((nx, ny+34), (nx, ny-18), arrowstyle="-|>", mutation_scale=22, color=MUTED, lw=2.4, zorder=8))
T(nx, ny-36, "N", 20, MUTED, "bold", ha="center")
sbx, sby = MX1-30-100*KM, MY1-34
ax.plot([sbx, sbx+100*KM], [sby, sby], color=MUTED, lw=3, zorder=8)
for xx in (sbx, sbx+100*KM): ax.plot([xx, xx], [sby-7, sby+7], color=MUTED, lw=3, zorder=8)
T(sbx+50*KM, sby-20, "100 km", 17, MUTED, "medium", ha="center")

# ---------- route cards ----------
CX0, CY0, CW, CH, GAP = 800, 190, 832, 250, 24
for i, (a, b, lab, mins, note, col, ac) in enumerate(ROUTES):
    c, r = i % 2, i // 2
    x, y = CX0 + c*(CW+GAP), CY0 + r*(CH+GAP)
    rbox(x, y, CW, CH, 26, PANEL, BORDER, 1.6, z=2)
    rbox(x+0, y+28, 7, CH-56, 3.5, col, z=3)
    T(x+36, y+42, lab.upper(), 21, MUTED, "semibold")
    T(x+36, y+104, a, 58, TXT, "bold")
    T(x+36+ 58*0.72*len(a)*1.07 + 22, y+104, "→", 44, DIM, "medium")
    T(x+36+ 58*0.72*len(a)*1.07 + 22 + 78, y+104, b, 58, TXT, "bold")
    T(x+36, y+186, mins, 92 if len(mins) < 4 else 78, col, "bold")
    nx_ = x+36 + (len(mins)*(92 if len(mins)<4 else 78)*0.62) + 22
    T(nx_, y+200, "min", 32, MUTED, "medium")
    if note: T(x+36, y+238, note, 17, DIM)
    # right column
    rx = x+470
    T(rx, y+62, "DISTANCE", 17, DIM, "semibold")
    T(rx, y+98, f"{hav(AP[a], AP[b]):.0f} km", 38, TXT, "bold")
    T(rx, y+150, "AIRCRAFT", 17, DIM, "semibold")
    cxp = rx
    for nm, cc in ac:
        w = 13.2*len(nm) + 54
        rbox(cxp, y+170, w, 44, 22, "#0A1527", cc, 2, z=4)
        ax.add_patch(Circle((cxp+22, y+192), 7, fc=cc, ec="none", zorder=5))
        T(cxp+38, y+193, nm, 20, TXT, "medium", z=5)
        cxp += w + 10

# ---------- airports table ----------
TY, TH = 1020, 310
rbox(800, TY, 1160, TH, 26, PANEL, BORDER, 1.6, z=2)
T(836, TY+40, "AIRPORTS", 21, MUTED, "semibold")
cols = (836, 1010, 1380, 1620)
for cx_, s in zip(cols, ("CODE", "AIRPORT", "GROUP", "NOTES")):
    T(cx_, TY+80, s, 16, DIM, "semibold")
ax.plot([836, 1924], [TY+98, TY+98], color=BORDER, lw=1.5, zorder=3)
notes = {"TBU": "International · hub", "VAV": "Intl status · domestic flights", "HPA": "3 km N of Pangai",
         "EUA": "Unsealed coral strip", "NTT": "1,659 m asphalt runway", "NFO": "Opened 1983"}
for i, (k, d) in enumerate(AP.items()):
    yy = TY + 128 + i*34
    ax.add_patch(Circle((cols[0]-1, yy), 0, zorder=3))
    T(cols[0], yy, f"{k}", 21, TXT, "bold"); T(cols[0]+62, yy, d["icao"], 19, MUTED, "medium")
    T(cols[1], yy, d["name"], 21, TXT, "medium")
    T(cols[2], yy, d["grp"], 20, MUTED)
    T(cols[3], yy, notes[k], 19, MUTED)

# ---------- aircraft legend ----------
rbox(1984, TY, 504, TH, 26, PANEL, BORDER, 1.6, z=2)
T(2020, TY+40, "AIRCRAFT", 21, MUTED, "semibold")
fleet = [(SAAB, "Saab 340B(Plus)", "Twin turboprop · up to 34 pax"),
         (Y12,  "Harbin Y-12",     "Twin turboprop · up to 17 pax"),
         (DHC,  "DHC-6 Twin Otter","Series 400 · short-field utility")]
for i, (cc, nm, ds) in enumerate(fleet):
    yy = TY + 112 + i*66
    ax.plot([2020, 2062], [yy, yy], color=cc, lw=4, solid_capstyle="round", zorder=4)
    ax.add_patch(Circle((2041, yy), 8, fc="#F8FAFF", ec=cc, lw=3, zorder=5))
    T(2086, yy-12, nm, 23, TXT, "bold"); T(2086, yy+15, ds, 18, MUTED)

# ---------- footer ----------
T(72, 1366, "Flight times are approximate and vary by schedule, aircraft and weather (Tonga Airports Ltd / Logistics Cluster, Tonga Pocket Guide, schedule sites).", 17, DIM)
T(72, 1390, "Aircraft per route are indicative: Lulutai's operations were suspended by Tonga CAD on 18 Jul 2025 and an Air Chathams Saab 340B covered domestic service.", 17, DIM)
T(72, 1414, "Positions to scale (equirectangular, cos-latitude corrected); island footprints are schematic. Check current schedules before travel.", 17, DIM)

fig.savefig("/mnt/user-data/outputs/tonga_airports_map_2560x1440.png", dpi=100, facecolor=fig.get_facecolor())
print("saved")
