# 🌀 FPV Propeller Design Tool

Advanced parametric tool for designing FPV drone propellers with aerodynamic modeling, blade geometry generation, and CAD export compatibility.

Strumento avanzato per la progettazione parametrica di eliche FPV con modellazione aerodinamica, generazione geometrica e compatibilità CAD.

---

# 🇬🇧 ENGLISH VERSION

## 🚀 Overview

This tool allows you to generate a complete **propeller blade geometry** starting from high-level flight behavior goals.

It bridges the gap between:
- empirical FPV prop design
- simplified aerodynamic modeling
- CAD-ready geometry generation (Rhino3D compatible)

---

## 🎯 Main Features

### 1. Parametric Blade Design
- Diameter
- Pitch at 75% radius
- Blade count
- Radial discretization

---

### 2. Flight Behavior Tuning

You can shape the propeller behavior using:

- Aggressiveness
- Grip
- Efficiency
- Smoothness
- Motor load limit

These parameters influence:
- pitch distribution
- chord distribution
- camber
- sweep
- load distribution

---

### 3. Airfoil Progression (Core Feature)

The blade is defined by a **progressive airfoil distribution**:
Root → Mid → Tip

Each section interpolates:
- camber (m)
- camber position (p)
- thickness (t)

Example:
Root: NACA 4410
Mid: NACA 2410
Tip: NACA 0008


This reflects real-world propeller design.

---

### 4. Geometry Generation

For each radial section, the tool computes:

- Radius
- Blade angle (β)
- Local pitch
- Chord
- Sweep offset (geometric)
- Droop angle
- Camber factor
- Local airfoil (interpolated)
- Relative load

---

### 5. Aerodynamic Estimation

The tool estimates:

- Loaded RPM
- Current draw (A)
- Static thrust (kgf)
- Solidity (σ)

⚠️ These are engineering approximations (not CFD-level accurate).

---

### 6. Visualization

Real-time charts:

- Pitch distribution
- Blade angle (β)
- Chord distribution
- Thickness distribution
- Sweep / camber / droop
- Thrust vs current curve

---

### 7. CSV Export (CAD Ready)

Exported parameters:
radius_mm
beta_deg
chord_mm
sweep_offset_mm
droop_deg
camber_factor
naca_code
naca_m
naca_p
thickness_ratio
relative_load


---

### 8. Rhino3D Integration

The included Python script generates:

- blade sections
- interpolated airfoils
- 3D geometry
- lofted blade surface

---

## 🧠 Core Formula

Blade angle:
β(r) = atan( P(r) / (2πr) )


Where:
- P(r) = local pitch
- r = radius

---

## ⚙️ Key Concepts

### Solidity (σ)
Blade area / disk area

- High → more thrust, more current
- Low → more efficiency

---

### Sweep (Scimitar Shape)
Backward curvature of the blade

Effects:
- smoother airflow
- reduced torque spikes
- increased stability

---

### Camber
Lift generation parameter

- Positive → more thrust, more drag
- Negative (reflex) → cleaner and faster

---

### Droop
Vertical blade deformation

- Negative → more stability
- Positive → more aggressive response

---

## ✈️ Design Philosophy

Based on real FPV propeller behavior:

| Style        | Characteristics |
|-------------|----------------|
| HQ-style     | aggressive, high grip, high current |
| Gemfan-style | smooth, efficient, progressive |
| APC-style    | balanced, stable |
| Racing       | high pitch, high load |
| Freestyle    | smooth, predictable |

---

## 📦 Project Structure
/web
propeller_design_mode.html

/rhino
rhino_propeller_section_generator.py

README.md
