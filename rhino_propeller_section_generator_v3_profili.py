# Rhino Python - Propeller Section Generator
# Compatible with Rhino 7/8 Python editor.
#
# Workflow:
# 1. Export "progetto_elica_geometria.csv" from the Propeller Design Mode tool.
# 2. Open Rhino.
# 3. Run this script in Rhino Python.
# 4. Select the CSV file.
# 5. The script generates simplified blade sections using:
#    radius_mm, beta_deg, chord_mm, sweep_offset_mm, droop_deg, camber_factor.
#
# CSV expected columns:
# pct_radius,radius_mm,beta_deg,pitch_in,pitch_mm,chord_mm,sweep_factor,droop_deg,camber_factor,relative_load
#
# Units are assumed to be millimetres.

import rhinoscriptsyntax as rs
import csv
import math

AIRFOIL_POINTS = 17
DEFAULT_THICKNESS_RATIO = 0.075
CAMBER_SCALE = 0.08
SWEEP_SCALE = 0.35  # fallback only if sweep_offset_mm is missing
CREATE_LOFT = True
CREATE_REFERENCE_LINES = True
CREATE_AXIS = True

def deg_to_rad(a):
    return a * math.pi / 180.0

def rotate_x(point, angle_deg):
    x, y, z = point
    a = deg_to_rad(angle_deg)
    c = math.cos(a)
    s = math.sin(a)
    return (x, y * c - z * s, y * s + z * c)

def rotate_y(point, angle_deg):
    x, y, z = point
    a = deg_to_rad(angle_deg)
    c = math.cos(a)
    s = math.sin(a)
    return (x * c + z * s, y, -x * s + z * c)

def naca_thickness(x, t):
    # NACA 00xx thickness distribution
    return 5 * t * (
        0.2969 * math.sqrt(max(x, 0.000001))
        - 0.1260 * x
        - 0.3516 * x**2
        + 0.2843 * x**3
        - 0.1015 * x**4
    )

def naca4_params(code):
    try:
        code = str(code).strip()
        if len(code) != 4:
            return 0.0, 0.4, DEFAULT_THICKNESS_RATIO
        m = int(code[0]) / 100.0
        p = int(code[1]) / 10.0
        t = int(code[2:]) / 100.0
        if p <= 0:
            p = 0.4
        return m, p, t
    except Exception:
        return 0.0, 0.4, DEFAULT_THICKNESS_RATIO

def naca4_camber(x, m, p):
    if m == 0:
        return 0.0
    if x < p:
        return m / (p * p) * (2 * p * x - x * x)
    return m / ((1 - p) * (1 - p)) * ((1 - 2 * p) + 2 * p * x - x * x)

def family_modifiers(family):
    f = (family or "").lower()
    if "thin racing" in f:
        return 0.80, 0.75, 0.12
    if "long range" in f:
        return 1.05, 1.25, -0.03
    if "apc" in f:
        return 1.12, 1.30, -0.02
    if "hq" in f:
        return 0.86, 0.85, 0.08
    if "gemfan" in f:
        return 0.95, 1.05, 0.04
    if "scimitar" in f:
        return 0.90, 0.75, 0.14
    if "custom" in f:
        return 1.0, 1.0, 0.0
    return 1.0, 1.0, 0.02

def camber_line(x, camber_factor, family, naca_code):
    family = family or "Balanced FPV"
    if "custom" in family.lower():
        m, p, t = naca4_params(naca_code)
        base = naca4_camber(x, m, p)
    else:
        base = math.sin(math.pi * x) * CAMBER_SCALE * camber_factor

    thickness_mult, camber_mult, reflex = family_modifiers(family)
    rear = (x - 0.55) * max(0, x - 0.45) * 2.0
    return camber_mult * base + reflex * rear * CAMBER_SCALE

def make_section_points(radius, beta_deg, chord, sweep_factor, sweep_offset_mm, droop_deg, camber_factor, thickness_ratio, airfoil_family, naca_code):
    upper = []
    lower = []

    for i in range(AIRFOIL_POINTS):
        x = i / float(AIRFOIL_POINTS - 1)
        xc = (x - 0.5) * chord
        thickness_mult, camber_mult, reflex = family_modifiers(airfoil_family)
        yt = naca_thickness(x, thickness_ratio * thickness_mult) * chord
        yc = camber_line(x, camber_factor, airfoil_family, naca_code) * chord
        upper.append((xc, 0, yc + yt))
        lower.append((xc, 0, yc - yt))

    pts = upper + list(reversed(lower))
    sweep_offset = sweep_offset_mm if sweep_offset_mm is not None else -sweep_factor * chord * SWEEP_SCALE

    transformed = []
    for p in pts:
        x, y, z = p

        # Pitch rotation around radial axis.
        x, y, z = rotate_y((x, y, z), beta_deg)

        # Droop rotation around chord axis.
        x, y, z = rotate_x((x, y, z), droop_deg)

        # Position section along blade radius.
        x += sweep_offset
        y += radius

        transformed.append((x, y, z))

    transformed.append(transformed[0])
    return transformed

def read_csv(path):
    rows = []
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rows.append({
                    "pct": float(row["pct_radius"]),
                    "radius": float(row["radius_mm"]),
                    "beta": float(row["beta_deg"]),
                    "pitch_in": float(row["pitch_in"]),
                    "pitch_mm": float(row["pitch_mm"]),
                    "chord": float(row["chord_mm"]),
                    "sweep": float(row["sweep_factor"]),
                    "sweep_offset": float(row["sweep_offset_mm"]) if "sweep_offset_mm" in row and row["sweep_offset_mm"] not in [None, ""] else None,
                    "droop": float(row["droop_deg"]),
                    "camber": float(row["camber_factor"]),
                    "thickness": float(row["thickness_ratio"]) if "thickness_ratio" in row and row["thickness_ratio"] not in [None, ""] else DEFAULT_THICKNESS_RATIO,
                    "family": row["airfoil_family"] if "airfoil_family" in row else "Balanced FPV",
                    "naca": row["naca_code"] if "naca_code" in row else "2410",
                    "load": float(row["relative_load"])
                })
            except Exception:
                pass
    return sorted(rows, key=lambda r: r["radius"])

def main():
    csv_path = rs.OpenFileName("Select propeller geometry CSV", "CSV files (*.csv)|*.csv||")
    if not csv_path:
        print("No file selected.")
        return

    rows = read_csv(csv_path)
    if not rows:
        print("No valid rows found. Check CSV format.")
        return

    rs.EnableRedraw(False)

    layer_sections = "Propeller_Sections"
    layer_refs = "Propeller_References"
    layer_loft = "Propeller_Loft"

    for layer in [layer_sections, layer_refs, layer_loft]:
        if not rs.IsLayer(layer):
            rs.AddLayer(layer)

    section_curves = []

    if CREATE_AXIS:
        rs.CurrentLayer(layer_refs)
        max_r = max(r["radius"] for r in rows)
        rs.AddLine((0, 0, 0), (0, max_r * 1.08, 0))
        rs.AddText("Rotation axis / blade radius reference", (3, max_r * 1.02, 0), height=3)

    for idx, r in enumerate(rows):
        pts = make_section_points(
            r["radius"],
            r["beta"],
            r["chord"],
            r["sweep"],
            r["sweep_offset"],
            r["droop"],
            r["camber"],
            r["thickness"],
            r["family"],
            r["naca"]
        )

        rs.CurrentLayer(layer_sections)
        crv = rs.AddInterpCurve(pts, degree=3)
        if crv:
            section_curves.append(crv)
            rs.ObjectName(crv, "section_%02d_R%.1f_beta%.1f" % (idx+1, r["radius"], r["beta"]))

        if CREATE_REFERENCE_LINES:
            rs.CurrentLayer(layer_refs)

            chord = r["chord"]
            sweep_offset = r["sweep_offset"] if r["sweep_offset"] is not None else -r["sweep"] * chord * SWEEP_SCALE

            local1 = rotate_y((-chord/2, 0, 0), r["beta"])
            local2 = rotate_y(( chord/2, 0, 0), r["beta"])
            local1 = rotate_x(local1, r["droop"])
            local2 = rotate_x(local2, r["droop"])

            p1 = (local1[0] + sweep_offset, local1[1] + r["radius"], local1[2])
            p2 = (local2[0] + sweep_offset, local2[1] + r["radius"], local2[2])

            line = rs.AddLine(p1, p2)
            if line:
                rs.ObjectName(line, "chord_ref_R%.1f" % r["radius"])

            rs.AddText(
                "R %.1f | beta %.1f | chord %.1f | %s" % (r["radius"], r["beta"], r["chord"], r["family"]),
                (p2[0] + 2, p2[1], p2[2]),
                height=2.2
            )

    if CREATE_LOFT and len(section_curves) >= 2:
        rs.CurrentLayer(layer_loft)
        loft = rs.AddLoftSrf(section_curves, loft_type=0)
        if loft:
            if isinstance(loft, list):
                for obj in loft:
                    rs.ObjectName(obj, "Preliminary_Propeller_Blade_Loft")
            else:
                rs.ObjectName(loft, "Preliminary_Propeller_Blade_Loft")

    rs.EnableRedraw(True)

    print("Generated %d blade sections." % len(section_curves))
    print("Use the lofted surface as a preliminary reference.")
    print("Refine leading edge, trailing edge, hub transition and structural thickness before manufacturing.")

if __name__ == "__main__":
    main()
