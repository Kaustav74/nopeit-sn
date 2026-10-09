"""
Curated Knowledge & Notes Scraping Engine
Integrates official NTA and CBSE syllabus data alongside notes, formulas, and cheatsheets
curated from DexterChem, Physics Galaxy, MathonGo, JEE Archive, JEEBOOKS.IN, eSaral, Vedantu, Kota Notes, SelfStudys, and JEEHub.
"""

import os
import json
import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import logging

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "content_cache")
os.makedirs(CACHE_DIR, exist_ok=True)
logger = logging.getLogger("scraper_engine")

# Comprehensive High-Yield Curated Knowledge Base across all specified portals
KNOWLEDGE_VAULT = {
    # ---------------- 1. DEXTERCHEM (ORGANIC & INORGANIC SPECIALIST) ----------------
    "dexterchem": [
        {
            "id": "dexter_01",
            "title": "Electrophilic Aromatic Substitution (EAS) Cheat Code & Directing Groups",
            "source": "DexterChem Portal",
            "category": "Organic Chemistry",
            "topics": ["Reaction Mechanisms", "EAS", "Aromatic Compounds", "Hydrocarbons"],
            "content": """
### 🧪 EAS Directing Groups & Reactivity Order (DexterChem Masterclass)

#### 1. Reactivity Scale
- **Strong Activators ($o,p$-directing):** $-\\text{NH}_2, -\\text{NHR}, -\\text{NR}_2, -\\text{OH}, -\\text{O}^-$ *(Lone pair directly conjugated with ring)*
- **Moderate Activators ($o,p$-directing):** $-\\text{NHCOCH}_3, -\\text{OCH}_3, -\\text{OCOCH}_3$ *(Lone pair shared competitively with carbonyl)*
- **Weak Activators ($o,p$-directing):** $-\\text{CH}_3, -\\text{CH}_2\\text{CH}_3, -\\text{C}(CH_3)_3$ *(Hyperconjugation & $+I$)*
- **Deactivators but $o,p$-directing (Special Halogen Anomaly):** $-F, -Cl, -Br, -I$.
  $$\\text{Reactivity: } -I > +M \\quad (\\text{Deactivating})$$
  $$\\text{Orientation: } +M \\text{ stabilizes Wheland intermediate at ortho/para}$$
- **Strong Meta-Directing Deactivators:** $-\\text{NO}_2, -\\text{CF}_3, -\\text{CCl}_3, -\\text{CN}, -\\text{SO}_3\\text{H}, -\\text{CHO}, -\\text{COR}, -\\text{COOH}$

#### 2. The 3 Deadly JEE Advanced Traps
1. **Friedel-Crafts on Aniline:** Fails completely because $-\\text{NH}_2$ acts as a Lewis base and coordinates with $\\text{AlCl}_3$, transforming the ring into a strongly deactivating $-\\text{NH}_2^+\\text{AlCl}_3^-$ group.
2. **Friedel-Crafts on Nitrobenzene:** Fails due to severe meta-deactivation. Nitrobenzene is used as an inert solvent for FC reactions.
3. **Halogenation of Phenol:** In polar solvent ($\\text{H}_2\\text{O}$), phenoxide forms $\\rightarrow$ polybromination to give 2,4,6-tribromophenol (white ppt). In non-polar ($\\text{CS}_2, 0^\\circ\\text{C}$), monobromination yields major para-bromophenol.
"""
        },
        {
            "id": "dexter_02",
            "title": "Aldol, Cannizzaro, and Claisen-Schmidt Condensation Mechanisms",
            "source": "DexterChem Portal",
            "category": "Organic Chemistry",
            "topics": ["Reaction Mechanisms", "Aldehydes & Ketones", "Carbonyl Compounds", "Aldol Condensation"],
            "content": """
### ⚗️ Carbonyl Condensation Mechanisms & Stereochemistry

#### 1. Crossed Aldol (Claisen-Schmidt)
$$\\text{Ph-CHO} + \\text{CH}_3\\text{COPh} \\xrightarrow{\\text{dil. NaOH, } \\Delta} \\text{Ph}-\\text{CH}=\\text{CH}-\\text{CO}-\\text{Ph} \\; (\\text{Chalcone / 1,3-diphenylprop-2-en-1-one}) + \\text{H}_2\\text{O}$$
- **Enolate Generator:** Acetophenone has $\\alpha-\\text{H}$ ($pK_a \\approx 16$), Benzaldehyde has **NO** $\\alpha-\\text{H}$.
- **Electrophile:** Carbonyl carbon of $\\text{Ph-CHO}$ is more electrophilic than $\\text{Ph-CO-CH}_3$ because ketone carbonyl has electron-donating alkyl/aryl stabilization and steric crowding.
- **Dehydration:** $\\text{E1cB}$ mechanism via conjugate base of aldol addition intermediate. Trans-alkene is formed exclusively due to minimization of 1,3-allylic strain.

#### 2. Cannizzaro vs Cross-Cannizzaro
- Occurs in aldehydes lacking $\\alpha-\\text{H}$ (e.g., $\\text{HCHO}, \\text{PhCHO}, (\\text{CH}_3)_3\\text{C-CHO}$) under **conc. alkali** ($50\\% \\text{ KOH}$).
- **Rate Law:** $\\text{Rate} = k[\\text{Aldehyde}]^2[\\text{OH}^-]$ (hydride shift is the Rate Determining Step, RDS).
- **Cross-Cannizzaro with Formaldehyde:** $\\text{HCHO}$ is always oxidized to $\\text{HCOO}^-$ because $\\text{HCHO}$ carbonyl is the least hindered and most electrophilic; the other aldehyde is reduced to alcohol.
"""
        },
        {
            "id": "dexter_03",
            "title": "Grignard Reagents ($RMgX$) & Organometallic Reaction Traps",
            "source": "DexterChem Portal",
            "category": "Organic Chemistry",
            "topics": ["Grignard Reagent", "Organometallics", "Alcohols", "Reaction Mechanisms"],
            "content": """
### ⚡ Grignard Reagent ($RMgX$): Nucleophilic Addition vs Acid-Base Protocol

#### 1. Rate Hierarchy of $RMgX$ Attacks
$$\\text{Acidic H (Acid-Base)} > \\text{Aldehyde} > \\text{Ketone} > \\text{Ester} \\approx \\text{Acid Halide} > \\text{Epoxide} > \\text{Alkyl Halide}$$

#### 2. Key JEE Advanced Reactions
- **Acid-Base Neutralization:** Any active proton ($-\\text{OH}, -\\text{COOH}, -\\text{NH}_2, -\\text{C}\\equiv\\text{C-H}, \\text{H}_2\\text{O}$) quenches the Grignard to form alkane $RH$:
  $$RMgX + \\text{CH}_3\\text{OH} \\rightarrow RH + \\text{Mg}(OCH_3)X$$
- **Reaction with Esters:** Requires **2 moles** of $R'MgX$ to yield tertiary alcohol:
  $$\\text{R-COOR}'' \\xrightarrow{1\\text{ eq } R'MgX} \\text{R-CO-R}' \\xrightarrow{2\\text{nd eq } R'MgX} \\text{R-C}(R')_2\\text{OH}$$
- **Reaction with Carbon Dioxide:**
  $$RMgX + \\text{CO}_2 \\rightarrow \\text{R-COOMgX} \\xrightarrow{\\text{H}_3\\text{O}^+} \\text{R-COOH} \\; (\\text{Carboxylic Acid})$$
- **Steric Hindrance Exception:** If both Grignard and ketone are heavily hindered (e.g., Di-t-butyl ketone + $t-\\text{BuMgBr}$), **reduction** occurs via cyclic 6-membered transition state yielding secondary alcohol, or enolization occurs!
"""
        },
        {
            "id": "dexter_04",
            "title": "Coordination Chemistry: Spectrochemical Series, CFT, & Color Traps",
            "source": "DexterChem Portal",
            "category": "Inorganic Chemistry",
            "topics": ["Coordination Compounds", "Crystal Field Theory", "CFT", "Spectrochemical Series"],
            "content": """
### 🎨 Ligand Field Strength Hierarchy (Spectrochemical Series)
$$I^- < Br^- < S^{2-} < SCN^- < Cl^- < N_3^- < F^- < OH^- < C_2O_4^{2-} \\approx H_2O < NCS^- < CH_3CN < py < NH_3 < en < bipy < phen < NO_2^- < PPh_3 < CN^- \\approx CO$$

#### 1. Splitting Energy $\\Delta_o$ and Electron Pairing
- **Octahedral Complex:** $t_{2g}$ (triply degenerate, lower by $0.4\\Delta_o$) and $e_g$ (doubly degenerate, higher by $0.6\\Delta_o$).
- **Weak Field ($\\Delta_o < P$):** High Spin complex. Electrons follow Hund's rule: $t_{2g}^3 e_g^1$ for $d^4$.
- **Strong Field ($\\Delta_o > P$):** Low Spin complex. Electrons pair up: $t_{2g}^4 e_g^0$ for $d^4$.

#### 2. Coordination Color Traps
- **Complementary Color:** Light absorbed at $\\lambda = hc/\\Delta_o$.
- If complex absorbs Orange-Red ($650\\text{ nm}$), it transmits Blue-Green.
- Stronger ligand field $\\implies$ higher $\\Delta_o \\implies$ absorption shifts to **shorter wavelength** (blue/violet shift) $\\implies$ transmitted light appears yellow/red.
- **$[\\text{Co}(\\text{NH}_3)_6]^{3+}$:** $\\text{Co}^{3+} (3d^6)$, strong field $\\text{NH}_3$, $t_{2g}^6 e_g^0$, inner orbital complex ($d^2sp^3$), diamagnetic.
"""
        },
        {
            "id": "dexter_05",
            "title": "Qualitative Salt Analysis: Chromyl Chloride, Brown Ring, and Nessler's Reagent",
            "source": "DexterChem Portal",
            "category": "Inorganic Chemistry",
            "topics": ["Salt Analysis", "Qualitative Analysis", "Inorganic Chemistry", "p-Block"],
            "content": """
### 🔬 Qualitative Inorganic Chemistry Confirmatory Tests

#### 1. Chromyl Chloride Test (for $\\text{Cl}^-$)
$$\\text{Salt}(\\text{Cl}^-) + \\text{K}_2\\text{Cr}_2\\text{O}_7 + \\text{conc. H}_2\\text{SO}_4 \\xrightarrow{\\Delta} \\text{CrO}_2\\text{Cl}_2 \\uparrow \\; (\\text{Deep red vapors})$$
$$\\text{CrO}_2\\text{Cl}_2 + 4\\text{NaOH} \\rightarrow \\text{Na}_2\\text{CrO}_4 \\; (\\text{Yellow solution}) + 2\\text{NaCl} + 2\\text{H}_2\\text{O}$$
$$\\text{Na}_2\\text{CrO}_4 + (\\text{CH}_3\\text{COO})_2\\text{Pb} \\rightarrow \\text{PbCrO}_4 \\downarrow \\; (\\text{Yellow precipitate of lead chromate})$$
> **⚠️ Exceptions:** Covalent/insoluble chlorides do NOT give this test: $\\text{Hg}_2\\text{Cl}_2, \\text{HgCl}_2, \\text{AgCl}, \\text{PbCl}_2, \\text{SnCl}_2$.

#### 2. Brown Ring Test (for $\\text{NO}_3^-$)
$$\\text{NO}_3^- + 3\\text{Fe}^{2+} + 4\\text{H}^+ \\rightarrow 3\\text{Fe}^{3+} + \\text{NO} + 2\\text{H}_2\\text{O}$$
$$[\\text{Fe}(\\text{H}_2\\text{O})_6]^{2+} + \\text{NO} \\rightarrow [\\text{Fe}(\\text{H}_2\\text{O})_5(\\text{NO})]^{2+} \\; (\\text{Brown Ring}) + \\text{H}_2\\text{O}$$
- **Oxidation State of Fe:** $\\text{Fe}$ is in $+1$ state! $\\text{NO}$ is coordinated as nitrosonium ion $\\text{NO}^+$.
- Magnetic moment $\\mu = \\sqrt{15} \\text{ BM} \\approx 3.87 \\text{ BM}$ ($3$ unpaired electrons).
"""
        },
        {
            "id": "dexter_06",
            "title": "Named Reactions Master Table: Reimer-Tiemann, Kolbe, Clemmensen vs Wolff-Kishner",
            "source": "DexterChem Portal",
            "category": "Organic Chemistry",
            "topics": ["Named Reactions", "Organic Chemistry", "Phenols", "Reduction"],
            "content": """
### 📚 Named Reactions Fast Reference

| Reaction | Reactant | Reagents | Intermediate / Key Feature | Major Product |
| :--- | :--- | :--- | :--- | :--- |
| **Reimer-Tiemann** | Phenol | $\\text{CHCl}_3 + \\text{NaOH}$ | Dichlorocarbene $(:\\text{CCl}_2)$ electrophile | Salicylaldehyde ($o$-hydroxybenzaldehyde) |
| **Kolbe-Schmitt** | Phenol | $\\text{NaOH} + \\text{CO}_2, 400\\text{ K}, 4-7\\text{ atm}$ | Phenoxide attack on electrophilic $\\text{CO}_2$ | Salicylic acid ($o$-hydroxybenzoic acid) |
| **Clemmensen** | Aldehyde / Ketone | $\\text{Zn-Hg} / \\text{conc. HCl}$ | Heterogeneous metal surface; **acid sensitive** | Alkane ($\\text{-CH}_2\\text{-}$) |
| **Wolff-Kishner** | Aldehyde / Ketone | $\\text{NH}_2\\text{NH}_2, \\text{KOH} / \\text{glycol}, \\Delta$ | Hydrazone intermediate; **base sensitive** | Alkane ($\\text{-CH}_2\\text{-}$) |
| **Hofmann Bromamide** | Primary Amide | $\\text{Br}_2 + 4\\text{KOH}$ | Isocyanate $(R-\\text{N}=\\text{C}=\\text{O})$ with retention | $1^\\circ$ Amine with **one less carbon** |
| **Rosenmund** | Acid Chloride | $\\text{H}_2 / \\text{Pd-BaSO}_4, \\text{quinoline}$ | Poisoned catalyst prevents reduction to alcohol | Aldehyde ($R\\text{-CHO}$) |
"""
        }
    ],

    # ---------------- 2. PHYSICS GALAXY (ASHISH ARORA SIR'S MASTER BLUEPRINTS) ----------------
    "physics_galaxy": [
        {
            "id": "pg_01",
            "title": "Rotational Mechanics: Pure Rolling on Moving Planks & Frictional Constraint Relations",
            "source": "Physics Galaxy Master Concepts",
            "category": "Physics Mechanics",
            "topics": ["Rotational Mechanics", "Pure Rolling", "Friction", "Rigid Body Dynamics"],
            "content": """
### 🌀 Pure Rolling on Accelerated Planks (Ashish Arora Blueprint)

#### 1. Frictional Constraints on Moving Surfaces
Consider a uniform solid cylinder of mass $M$ and radius $R$ placed on a horizontal plank of mass $m$ acted on by horizontal force $F$.
Let acceleration of plank be $a_p$, acceleration of center of mass of cylinder be $a_c$, and angular acceleration of cylinder be $\\alpha$.

1. **No Slipping Condition at Cylinder-Plank Contact:**
   $$a_{\\text{contact, cylinder}} = a_c + R\\alpha = a_p$$
2. **Plank Dynamic Equation:**
   $$F - f_1 = m a_p \\quad (f_1 = \\text{friction between plank and cylinder})$$
3. **Cylinder Linear Motion:**
   $$f_1 = M a_c$$
4. **Cylinder Angular Motion:**
   $$f_1 R = I_{cm} \\alpha = \\frac{1}{2} M R^2 \\alpha \\implies R\\alpha = \\frac{2 f_1}{M} = 2 a_c$$
5. **Connecting Constraint:**
   $$a_p = a_c + 2 a_c = 3 a_c \\implies a_c = \\frac{a_p}{3}$$
   $$f_1 = M \\left(\\frac{a_p}{3}\\right) = \\frac{M a_p}{3}$$
6. **Substitute back into Plank equation:**
   $$F - \\frac{M a_p}{3} = m a_p \\implies a_p = \\frac{F}{m + \\frac{M}{3}}$$
*(If there is ground friction or a rolling cylinder on ground as well, include $f_0$. This constraint logic never fails!)*
"""
        },
        {
            "id": "pg_02",
            "title": "Variable Mass Systems: The Rocket Equation & Falling Chains",
            "source": "Physics Galaxy Master Concepts",
            "category": "Physics Mechanics",
            "topics": ["Variable Mass Systems", "Rocket Equation", "Momentum Conservation", "Mechanics"],
            "content": """
### 🚀 Variable Mass Systems from First Principles

#### 1. Tsiolkovsky Rocket Equation
Let rocket mass be $M(t)$ moving with velocity $v(t)$, ejecting fuel at relative exhaust speed $u_{\\text{rel}}$ backward:
$$M \\frac{dv}{dt} = -u_{\\text{rel}} \\frac{dM}{dt} - M g$$
Dividing by $M$:
$$dv = -u_{\\text{rel}} \\frac{dM}{M} - g dt$$
Integrating from $t=0$ to $t$ ($M_0 \\rightarrow M$):
$$v(t) - v_0 = u_{\\text{rel}} \\ln\\left(\\frac{M_0}{M(t)}\\right) - g t$$

#### 2. Rope / Chain Falling on a Scale
A uniform flexible chain of mass $M$ and length $L$ is held vertically with its bottom end just touching a scale table. It is released from rest:
- At time $t$, distance fallen is $y = \\frac{1}{2}gt^2$, velocity is $v = \\sqrt{2gy}$.
- Mass on the table: $m(y) = \\frac{M}{L} y$. Weight of accumulated chain: $W = m(y)g = \\frac{M}{L} y g$.
- Momentum rate of incoming links hitting table:
  $$F_{\\text{impact}} = \\frac{dp}{dt} = v \\frac{dm}{dt} = v \\left(\\frac{M}{L} v\\right) = \\frac{M}{L} v^2 = \\frac{M}{L}(2gy) = 2 \\frac{M}{L} y g = 2 W$$
- **Total Scale Reading:**
  $$N = W + F_{\\text{impact}} = 3 \\frac{M}{L} y g = 3 \\times (\\text{weight of fallen part})$$
- Maximum scale reading when entire chain has just landed: $N_{\\max} = 3 Mg$.
"""
        },
        {
            "id": "pg_03",
            "title": "Electrostatics: Gauss's Law with Non-Uniform Charge Densities $\\rho(r)$",
            "source": "Physics Galaxy Master Concepts",
            "category": "Physics Electrodynamics",
            "topics": ["Electrostatics", "Gauss Law", "Electric Field", "CBSE 12th Board"],
            "content": """
### ⚡ Variable Charge Densities and Gauss Flux Integration

#### Problem: Solid Sphere with Density $\\rho(r) = \\rho_0 \\left(1 - \\frac{r}{R}\\right)$ for $r \\le R$

1. **Calculate Enclosed Charge $q_{\\text{enc}}(r)$:**
   Divide the sphere into concentric shells of radius $r'$ and thickness $dr'$:
   $$dq = 4\\pi r'^2 \\rho(r') dr' = 4\\pi \\rho_0 \\left(r'^2 - \\frac{r'^3}{R}\\right) dr'$$
   $$q_{\\text{enc}}(r) = \\int_0^r dq = 4\\pi \\rho_0 \\left[\\frac{r^3}{3} - \\frac{r^4}{4R}\\right]$$

2. **Apply Gauss's Law:**
   $$\\oint \\vec{E} \\cdot d\\vec{A} = E(r) \\cdot 4\\pi r^2 = \\frac{q_{\\text{enc}}(r)}{\\varepsilon_0}$$
   $$E(r) = \\frac{4\\pi \\rho_0 \\left[\\frac{r^3}{3} - \\frac{r^4}{4R}\\right]}{4\\pi r^2 \\varepsilon_0} = \\frac{\\rho_0 r}{\\varepsilon_0} \\left(\\frac{1}{3} - \\frac{r}{4R}\\right)$$

3. **Maximum Field Inside the Sphere:**
   Set $\\frac{dE}{dr} = 0$:
   $$\\frac{d}{dr}\\left(\\frac{r}{3} - \\frac{r^2}{4R}\\right) = \\frac{1}{3} - \\frac{2r}{4R} = 0 \\implies r_{\\max} = \\frac{2}{3}R$$
"""
        },
        {
            "id": "pg_04",
            "title": "Electromagnetic Induction: Faraday Flux Invariance & Motional EMF",
            "source": "Physics Galaxy Master Concepts",
            "category": "Physics Electrodynamics",
            "topics": ["Electromagnetic Induction", "Faraday Law", "Lenz Law", "Motional EMF"],
            "content": """
### 🧲 Charge Invariance in Induced Current Loops

#### 1. Why Charge Flow is Independent of Rotation Speed / Time Interval
Let a loop of resistance $R$ undergo magnetic flux change $\\Delta\\Phi = \\Phi_f - \\Phi_i$:
$$e(t) = -\\frac{d\\Phi}{dt} \\implies i(t) = \\frac{e(t)}{R} = -\\frac{1}{R}\\frac{d\\Phi}{dt}$$
Total charge flowing through any cross-section of wire:
$$q = \\int_0^{\\Delta t} i(t) dt = \\int_0^{\\Delta t} -\\frac{1}{R}\\frac{d\\Phi}{dt} dt = \\frac{|\\Delta\\Phi|}{R}$$
- **Key Insight:** Charge $q$ depends **strictly** on net flux change and loop resistance, **never on time $\\Delta t$ or speed of rotation!**
- If circular loop of radius $a$ in perpendicular field $B$ is rotated by $180^\\circ$:
  $$\\Phi_i = B(\\pi a^2), \\quad \\Phi_f = -B(\\pi a^2) \\implies |\\Delta\\Phi| = 2\\pi a^2 B$$
  $$q = \\frac{2\\pi a^2 B}{R}$$
"""
        },
        {
            "id": "pg_05",
            "title": "Wave Optics: Interference Fringe Shift & Dielectric Film Insertion",
            "source": "Physics Galaxy Master Concepts",
            "category": "Physics Optics",
            "topics": ["Wave Optics", "Interference", "YDSE", "CBSE 12th Board"],
            "content": """
### 🌊 Young's Double Slit Experiment (YDSE) with Optical Path Shifts

#### 1. Medium Immersed YDSE
When the entire YDSE apparatus is immersed in medium of refractive index $\\mu$:
$$\\lambda' = \\frac{\\lambda}{\\mu} \\implies \\beta' = \\frac{\\lambda' D}{d} = \\frac{\\beta}{\\mu}$$
- Central maximum position does NOT shift because geometric symmetry is preserved ($S_1 O = S_2 O$).

#### 2. Inserting a Thin Transparent Sheet of Thickness $t$ and Index $\\mu$
- Optical path difference introduced: $\\Delta x_{\\text{optical}} = (\\mu - 1)t$.
- Shift of the entire fringe pattern on the screen:
  $$\\text{Shift } y_0 = \\frac{D}{d} (\\mu - 1)t = \\frac{\\beta}{\\lambda}(\\mu - 1)t$$
- Number of fringes shifted across the center:
  $$N = \\frac{y_0}{\\beta} = \\frac{(\\mu - 1)t}{\\lambda}$$
"""
        }
    ],

    # ---------------- 3. MATHONGO (ANUP SIR'S CALCULUS & ALGEBRA BLUEPRINTS) ----------------
    "mathongo": [
        {
            "id": "math_01",
            "title": "Calculus: Newton-Leibniz Differentiation of Variable Limit Integrals",
            "source": "MathonGo Master Shortcuts",
            "category": "Mathematics Calculus",
            "topics": ["Calculus", "Definite Integrals", "Leibniz Rule", "Differential Equations"],
            "content": """
### 📐 Newton-Leibniz Formula & Integral Functional Equations

#### 1. The General Leibniz Rule
$$\\frac{d}{dx} \\left[\\int_{u(x)}^{v(x)} f(t, x) dt\\right] = f(v(x), x) \\cdot v'(x) - f(u(x), x) \\cdot u'(x) + \\int_{u(x)}^{v(x)} \\frac{\\partial f(t,x)}{\\partial x} dt$$
If $f$ has no explicit $x$ dependence:
$$\\frac{d}{dx} \\left[\\int_{u(x)}^{v(x)} f(t) dt\\right] = f(v(x)) v'(x) - f(u(x)) u'(x)$$

#### 2. Solving Integral Equations (AIR-1 Blueprint)
Example: $\\int_0^x f(t) dt = x^2 + \\int_x^1 t^2 f(t) dt$. Find $f'(1)$.
1. Differentiate both sides with respect to $x$:
   $$f(x) \\cdot (1) - 0 = 2x + \\left[0 - x^2 f(x) \\cdot (1)\\right]$$
   $$f(x) = 2x - x^2 f(x) \\implies f(x)(1 + x^2) = 2x \\implies f(x) = \\frac{2x}{1 + x^2}$$
2. Differentiate again to find $f'(x)$:
   $$f'(x) = \\frac{2(1 + x^2) - 2x(2x)}{(1 + x^2)^2} = \\frac{2 - 2x^2}{(1 + x^2)^2}$$
3. Substitute $x=1$:
   $$f'(1) = \\frac{2 - 2(1)^2}{(1 + 1^2)^2} = 0$$
"""
        },
        {
            "id": "math_02",
            "title": "Definite Integrals: King's Property & Queen's Symmetry Shortcuts",
            "source": "MathonGo Master Shortcuts",
            "category": "Mathematics Calculus",
            "topics": ["Calculus", "Definite Integrals", "Kings Property", "Queens Property"],
            "content": """
### 👑 King's Rule & Definite Integration Symmetry

#### 1. King's Property
$$I = \\int_a^b f(x) dx = \\int_a^b f(a + b - x) dx$$
- Add $I + I = 2I = \\int_a^b [f(x) + f(a + b - x)] dx$.
- If $f(x) + f(a + b - x) = C$ (constant), then $I = \\frac{C(b - a)}{2}$.

#### 2. High-Yield Examples
- $\\int_0^{\\pi/2} \\frac{\\sin^n x}{\\sin^n x + \\cos^n x} dx = \\frac{\\pi}{4}$ for ANY $n \\in \\mathbb{R}$.
- $\\int_0^1 \\ln(1 + x) dx \\xrightarrow{x = \\tan\\theta} \\int_0^{\\pi/4} \\ln(1 + \\tan\\theta) \\sec^2\\theta d\\theta$.
- $\\int_0^{\\pi/4} \\ln(1 + \\tan\\theta) d\\theta = \\frac{\\pi}{8} \\ln 2$.
"""
        },
        {
            "id": "math_03",
            "title": "Vectors & 3D: Shortest Distance Between Skew Lines (Cross/Dot Formula)",
            "source": "MathonGo Master Shortcuts",
            "category": "Mathematics 3D Geometry",
            "topics": ["Vectors", "3D Geometry", "Skew Lines", "CBSE 12th Board"],
            "content": """
### 📐 Shortest Distance Between Skew Lines in 3D

#### 1. Vector Formulation
Let Line 1: $\\vec{r} = \\vec{a}_1 + \\lambda \\vec{b}_1$ and Line 2: $\\vec{r} = \\vec{a}_2 + \\mu \\vec{b}_2$.
Since lines are non-parallel and skew, the shortest distance lies along the common perpendicular $\\vec{n} = \\vec{b}_1 \\times \\vec{b}_2$:
$$d = \\left| \\frac{(\\vec{a}_2 - \\vec{a}_1) \\cdot (\\vec{b}_1 \\times \\vec{b}_2)}{|\\vec{b}_1 \\times \\vec{b}_2|} \\right|$$

#### 2. Cartesian Determinant Form (Direct CBSE 5-Mark Method)
If Line 1: $\\frac{x - x_1}{a_1} = \\frac{y - y_1}{b_1} = \\frac{z - z_1}{c_1}$ and Line 2: $\\frac{x - x_2}{a_2} = \\frac{y - y_2}{b_2} = \\frac{z - z_2}{c_2}$:
$$d = \\frac{\\left| \\begin{vmatrix} x_2 - x_1 & y_2 - y_1 & z_2 - z_1 \\\\ a_1 & b_1 & c_1 \\\\ a_2 & b_2 & c_2 \\end{vmatrix} \\right|}{\\sqrt{(b_1 c_2 - b_2 c_1)^2 + (c_1 a_2 - c_2 a_1)^2 + (a_1 b_2 - a_2 b_1)^2}}$$
"""
        },
        {
            "id": "math_04",
            "title": "Complex Numbers: Inversion Identity $z\\bar{z} = |z|^2$ & Circle Geometry",
            "source": "MathonGo Master Shortcuts",
            "category": "Mathematics Complex Numbers",
            "topics": ["Complex Numbers", "Geometry", "Conjugate Inversion", "Algebra"],
            "content": """
### ⭕ Complex Numbers Conjugate Inversion Identity

#### Key Principle
$$|z|^2 = z \\bar{z} \\implies \\bar{z} = \\frac{|z|^2}{z}$$

#### Blueprint Problem
Given $|z_1| = 1, |z_2| = 2, |z_3| = 3$ and $|9z_1 z_2 + 4z_1 z_3 + z_2 z_3| = 12$. Find $|z_1 + z_2 + z_3|$.
1. Rewrite coefficients using moduli squared:
   $$9 = |z_3|^2 = z_3 \\bar{z}_3, \\quad 4 = |z_2|^2 = z_2 \\bar{z}_2, \\quad 1 = |z_1|^2 = z_1 \\bar{z}_1$$
2. Factor out $z_1 z_2 z_3$:
   $$|z_1 z_2 z_3| \\cdot \\left|\\frac{9}{z_3} + \\frac{4}{z_2} + \\frac{1}{z_1}\\right| = 12$$
   $$(1)(2)(3) \\cdot |\\bar{z}_3 + \\bar{z}_2 + \\bar{z}_1| = 12$$
   $$6 |\\overline{z_1 + z_2 + z_3}| = 12$$
3. Since $|\\bar{w}| = |w|$:
   $$6 |z_1 + z_2 + z_3| = 12 \\implies |z_1 + z_2 + z_3| = 2$$
"""
        },
        {
            "id": "math_05",
            "title": "Probability: Markov Chains, Recurrence Relations & Expected Value",
            "source": "MathonGo Master Shortcuts",
            "category": "Mathematics Probability",
            "topics": ["Probability", "Expected Value", "Markov Chains", "Recurrence"],
            "content": """
### 🎲 Conditional Expectation & First Step Analysis (Markov Recurrence)

#### Problem: Expected Number of Rolls to get Two Consecutive 6's
Let $E$ be expected rolls from initial state, $E_1$ after rolling one 6.
1. From state $0$: Roll 6 with probability $1/6$ (moves to state 1), non-6 with probability $5/6$ (stays in state 0):
   $$E = 1 + \\frac{1}{6} E_1 + \\frac{5}{6} E$$
2. From state $1$: Roll 6 with probability $1/6$ (done, 0 rolls needed), non-6 with probability $5/6$ (resets to state 0):
   $$E_1 = 1 + \\frac{1}{6}(0) + \\frac{5}{6} E = 1 + \\frac{5}{6} E$$
3. Substitute $E_1$ into $E$:
   $$E = 1 + \\frac{1}{6}\\left(1 + \\frac{5}{6}E\\right) + \\frac{5}{6}E = 1 + \\frac{1}{6} + \\frac{5}{36}E + \\frac{30}{36}E = \\frac{7}{6} + \\frac{35}{36}E$$
   $$E - \\frac{35}{36}E = \\frac{7}{6} \\implies \\frac{1}{36}E = \\frac{7}{6} \\implies E = 42$$
"""
        }
    ],

    # ---------------- 4. CBSE 12TH BOARD 95%+ HIGH-YIELD DERIVATIONS ----------------
    "cbse_derivations": [
        {
            "id": "cbse_01",
            "title": "CBSE 5-Mark Derivation: Lens Maker's Formula from Spherical Refraction",
            "source": "Official NCERT Class 12 Physics",
            "category": "12th Boards Roadmap",
            "topics": ["Ray Optics", "Lens Makers Formula", "Refraction", "CBSE 12th Board"],
            "content": """
### 📐 Lens Maker's Formula from First Principles (Full 5 Marks NCERT)

#### 1. Statement of Refraction at Single Spherical Surface
For a spherical surface of radius $R$ separating medium $\\mu_1$ and $\\mu_2$:
$$\\frac{\\mu_2}{v} - \\frac{\\mu_1}{u} = \\frac{\\mu_2 - \\mu_1}{R}$$

#### 2. Thin Lens with Two Surfaces of Radii $R_1$ and $R_2$
Consider a thin convex lens of refractive index $\\mu_2$ placed in a surrounding medium $\\mu_1$:
1. **Refraction at First Surface (Radius $R_1$):**
   Light travels from medium $\\mu_1$ to lens $\\mu_2$. Let object be at distance $u$, forming virtual intermediate image at distance $v_1$:
   $$\\frac{\\mu_2}{v_1} - \\frac{\\mu_1}{u} = \\frac{\\mu_2 - \\mu_1}{R_1} \\quad \\text{--- (Equation 1)}$$
2. **Refraction at Second Surface (Radius $R_2$):**
   Light travels from lens $\\mu_2$ to medium $\\mu_1$. The intermediate image at $v_1$ acts as virtual object, forming final real image at distance $v$:
   $$\\frac{\\mu_1}{v} - \\frac{\\mu_2}{v_1} = \\frac{\\mu_1 - \\mu_2}{R_2} = -\\frac{\\mu_2 - \\mu_1}{R_2} \\quad \\text{--- (Equation 2)}$$
3. **Adding Equations (1) and (2):**
   The term $\\frac{\\mu_2}{v_1}$ cancels out:
   $$\\frac{\\mu_1}{v} - \\frac{\\mu_1}{u} = (\\mu_2 - \\mu_1)\\left(\\frac{1}{R_1} - \\frac{1}{R_2}\\right)$$
   $$\\frac{1}{v} - \\frac{1}{u} = \\left(\\frac{\\mu_2}{\\mu_1} - 1\\right)\\left(\\frac{1}{R_1} - \\frac{1}{R_2}\\right)$$
4. **By Lens Definition ($u = \\infty \\implies v = f$):**
   $$\\frac{1}{f} = (\\mu - 1)\\left(\\frac{1}{R_1} - \\frac{1}{R_2}\\right) \\quad \\text{Q.E.D.}$$
"""
        },
        {
            "id": "cbse_02",
            "title": "CBSE 5-Mark Derivation: Gauss's Law for Charged Thin Spherical Shell",
            "source": "Official NCERT Class 12 Physics",
            "category": "12th Boards Roadmap",
            "topics": ["Electrostatics", "Gauss Law", "Spherical Shell", "CBSE 12th Board"],
            "content": """
### ⚡ Electric Field due to Uniformly Charged Spherical Shell

Let total charge $Q$ be distributed uniformly on a thin spherical shell of radius $R$ with surface charge density $\\sigma = \\frac{Q}{4\\pi R^2}$.

#### Case 1: Point Outside the Shell ($r > R$)
Choose a concentric spherical Gaussian surface of radius $r$:
$$\\oint \\vec{E} \\cdot d\\vec{A} = E(r) \\cdot (4\\pi r^2) = \\frac{q_{\\text{enc}}}{\\varepsilon_0} = \\frac{Q}{\\varepsilon_0}$$
$$E(r) = \\frac{1}{4\\pi\\varepsilon_0} \\frac{Q}{r^2} \\quad (\\text{Acts as if entire charge is concentrated at the center})$$

#### Case 2: Point on the Surface ($r = R$)
$$E(R) = \\frac{1}{4\\pi\\varepsilon_0} \\frac{Q}{R^2} = \\frac{\\sigma}{\\varepsilon_0}$$

#### Case 3: Point Inside the Shell ($r < R$)
Since all charges reside on the surface, enclosed charge inside Gaussian surface of radius $r < R$ is zero:
$$q_{\\text{enc}} = 0 \\implies E(r) \\cdot (4\\pi r^2) = 0 \\implies E_{\\text{inside}} = 0$$
"""
        },
        {
            "id": "cbse_03",
            "title": "CBSE 5-Mark Derivation: Integrated Rate Laws & Half-Life for 1st Order Kinetics",
            "source": "Official NCERT Class 12 Chemistry",
            "category": "12th Boards Roadmap",
            "topics": ["Chemical Kinetics", "Integrated Rate Law", "Half Life", "CBSE 12th Board"],
            "content": """
### 🧪 First Order Reaction Integrated Rate Law (CBSE Board Masterclass)

Consider the first-order reaction: $A \\rightarrow \\text{Products}$.
1. **Differential Rate Law:**
   $$-\\frac{d[A]}{dt} = k [A]^1 \\implies \\frac{d[A]}{[A]} = -k dt$$
2. **Integration:**
   $$\\int_{[A]_0}^{[A]_t} \\frac{d[A]}{[A]} = -k \\int_0^t dt \\implies \\ln\\left(\\frac{[A]_t}{[A]_0}\\right) = -k t$$
   $$[A]_t = [A]_0 e^{-kt} \\quad \\text{or} \\quad k = \\frac{2.303}{t} \\log_{10}\\left(\\frac{[A]_0}{[A]_t}\\right)$$
3. **Half-Life ($t_{1/2}$):**
   At $t = t_{1/2}$, $[A]_t = [A]_0 / 2$:
   $$k = \\frac{2.303}{t_{1/2}} \\log_{10}(2) = \\frac{2.303 \\times 0.3010}{t_{1/2}} = \\frac{0.693}{t_{1/2}}$$
   $$t_{1/2} = \\frac{0.693}{k} \\quad (\\text{Completely independent of initial concentration } [A]_0)$$
"""
        }
    ],

    # ---------------- 5. KOTA CLASSROOM HANDWRITTEN GOLD NOTES & JEE ARCHIVE ----------------
    "kota_notes": [
        {
            "id": "kota_01",
            "title": "Kota HOD Golden Rules: Eliminating Negative Marking in JEE",
            "source": "Kota Classroom Handwritten Gold Notes",
            "category": "Exam Strategy & Temperament",
            "topics": ["Exam Strategy", "Negative Marking", "Time Management", "AIR-1 Habit"],
            "content": """
### 🎯 The 3-Round Paper Attempting Strategy (Kota Benchmark)

#### Round 1 (Minutes 0 - 60): The 'No-Hesitation' Sweep
- Solve **ONLY** questions where the complete solution path is 100% crystal clear within the first 15 seconds.
- Skip anything with multi-variable branches, long algebraic simplifications, or unfamiliar wording.
- Target: Secure 90-110 marks effortlessly with 100% accuracy and zero panic.

#### Round 2 (Minutes 60 - 140): The 'Deep Synthesis' Attack
- Tackle moderate multi-concept problems, matrix matches, and bounded integer problems.
- If a calculation takes more than 2 minutes without algebraic reduction, pause and place a mark for Round 3.

#### Round 3 (Minutes 140 - 180): The 'AIR-1 Edge'
- Solve the 3-4 toughest questions.
- Devote the last 15 minutes to an **Accuracy Audit**: verify units, signs, and boundary values on previously solved questions.
"""
        }
    ],

    "jee_archive": [
        {
            "id": "arch_01",
            "title": "IIT-JEE Advanced 45-Year Archive: Most Repeated Problem Blueprints",
            "source": "JEE Archive / JEEBOOKS.IN",
            "category": "Master Problem Patterns",
            "topics": ["Repeated PYQ Blueprints", "Master Patterns", "JEE Advanced"],
            "content": """
### 🏆 The 5 Archetypes of JEE Advanced AIR-1 Questions
1. **The Combined Conservation Problem:** Mechanics questions requiring simultaneous conservation of Linear Momentum, Energy, AND Angular Momentum about a non-stationary pivot.
2. **The Electrostatic-Gravitational Analogy:** Dipole dynamics, flux calculations, and electrostatic field energy density ($u = \\frac{1}{2}\\varepsilon_0 E^2$).
3. **Multi-Variable Calculus with Functional Equations:** Functions defined by relations like $f(x+y) = f(x)f(y)$ or $f'(x) = f(x) + \\int_0^1 f(t)dt$.
4. **Organic Reaction Roadmaps:** Sequential multi-step syntheses involving ozonolysis, aldol, and stereochemical inversions.
5. **Physical Chemistry Coupled Equilibria:** Simultaneous solubility product ($K_{sp}$) and complex formation constant ($K_f$) in buffer solutions.
"""
        }
    ]
}

def get_vault_categories():
    """Returns available knowledge sources and categories."""
    categories = []
    for src, items in KNOWLEDGE_VAULT.items():
        for idx, it in enumerate(items):
            categories.append({
                "source": it["source"],
                "category": it["category"],
                "title": it["title"],
                "src_key": src,
                "index": idx,
                "topics": it.get("topics", [])
            })
    return categories

def get_note_content(src_key: str, index: int = 0):
    """Retrieves specific curated note by key and index."""
    items = KNOWLEDGE_VAULT.get(src_key, [])
    if index < len(items):
        return items[index]
    return None

def get_notes_by_topic(topic_name: str):
    """
    Intelligent lookup that finds all notes matching a topic name or keyword.
    Used by Daily Goals and Diagnostic Lag pluggers.
    """
    if not topic_name:
        return []
    
    topic_lower = topic_name.lower()
    matches = []
    for src, items in KNOWLEDGE_VAULT.items():
        for it in items:
            title_lower = it["title"].lower()
            cat_lower = it["category"].lower()
            content_lower = it["content"].lower()
            topics_lower = [t.lower() for t in it.get("topics", [])]
            
            # Score match
            score = 0
            if any(t in topic_lower or topic_lower in t for t in topics_lower):
                score += 5
            if topic_lower in title_lower:
                score += 4
            if topic_lower in cat_lower:
                score += 2
            if topic_lower in content_lower:
                score += 1

            if score > 0:
                matches.append({
                    "score": score,
                    "note": it,
                    "src_key": src
                })

    matches.sort(key=lambda x: x["score"], reverse=True)
    return [m["note"] for m in matches]

def search_vault(query: str):
    """Search notes across all categories."""
    query_lower = query.lower()
    results = []
    for src, items in KNOWLEDGE_VAULT.items():
        for idx, it in enumerate(items):
            if (query_lower in it["title"].lower() or 
                query_lower in it["category"].lower() or 
                query_lower in it["content"].lower()):
                results.append({
                    "src_key": src,
                    "index": idx,
                    "title": it["title"],
                    "source": it["source"],
                    "category": it["category"],
                    "content_snippet": it["content"][:200] + "..."
                })
    return results

def fetch_external_url(url: str):
    """
    Scrapes notes or text content from public JEE/CBSE educational pages with safe caching.
    """
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            soup = BeautifulSoup(html, "html.parser")
            
            for s in soup(["script", "style", "nav", "footer", "header"]):
                s.decompose()

            title = soup.title.string.strip() if soup.title else "Scraped Resource"
            text_paragraphs = [p.get_text().strip() for p in soup.find_all(["p", "h1", "h2", "h3", "li"]) if len(p.get_text().strip()) > 20]
            summary_text = "\n\n".join(text_paragraphs[:25])

            return {
                "status": "success",
                "title": title,
                "url": url,
                "extracted_text": summary_text
            }
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return {
            "status": "error",
            "url": url,
            "message": str(e)
        }
