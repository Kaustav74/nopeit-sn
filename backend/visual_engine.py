"""
Visual Engine for Organic Reactions, Symbolic Math Derivations, and Physics Visualizations
Uses SymPy for step-by-step derivations and Matplotlib for dynamic SVG diagrams.
"""

import io
import base64
import sympy as sp
from sympy import symbols, Eq, solve, diff, integrate, latex, sin, cos, exp, pi, oo, limit, Matrix
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ----------------- 1. SYMBOLIC DERIVATIONS ENGINE (SYMPY) -----------------

def derive_lens_maker():
    """Step-by-step derivation of Lens Maker Formula for CBSE Board 5-Mark question."""
    return {
        "title": "Lens Maker's Formula Derivation",
        "subject": "Physics (Optics)",
        "board_marks": 5,
        "steps": [
            {
                "step": 1,
                "label": "Refraction at First Spherical Surface (Radius $R_1$)",
                "formula": "\\frac{\\mu_2}{v_1} - \\frac{\\mu_1}{u} = \\frac{\\mu_2 - \\mu_1}{R_1}",
                "note": "Light travels from medium of refractive index $\\mu_1$ to lens of index $\\mu_2$. Image formed at $v_1$ acts as virtual object for second surface."
            },
            {
                "step": 2,
                "label": "Refraction at Second Spherical Surface (Radius $R_2$)",
                "formula": "\\frac{\\mu_1}{v} - \\frac{\\mu_2}{v_1} = \\frac{\\mu_1 - \\mu_2}{R_2} = -\\frac{\\mu_2 - \\mu_1}{R_2}",
                "note": "Light emerges back into medium $\\mu_1$ from lens medium $\\mu_2$."
            },
            {
                "step": 3,
                "label": "Summing Equations for Thin Lens Approximation",
                "formula": "\\frac{\\mu_1}{v} - \\frac{\\mu_1}{u} = (\\mu_2 - \\mu_1)\\left(\\frac{1}{R_1} - \\frac{1}{R_2}\\right)",
                "note": "Intermediate image distance term $\\frac{\\mu_2}{v_1}$ cancels out algebraically."
            },
            {
                "step": 4,
                "label": "Applying Focus Boundary Condition ($u = \\infty \\implies v = f$)",
                "formula": "\\frac{1}{f} = \\left(\\frac{\\mu_2}{\\mu_1} - 1\\right)\\left(\\frac{1}{R_1} - \\frac{1}{R_2}\\right)",
                "note": "When surrounding medium is air ($\\mu_1 = 1$, $\\mu_2 = \\mu$): $\\frac{1}{f} = (\\mu - 1)\\left(\\frac{1}{R_1} - \\frac{1}{R_2}\\right)$."
            }
        ]
    }

def derive_variable_mass_rocket():
    """Derivation of Tsiolkovsky Rocket Equation for JEE Advanced."""
    m, v, u_rel, dm, dv, t, g = symbols('m v u_rel dm dv t g')
    # m dv = - u_rel dm - m g dt
    return {
        "title": "Variable Mass Dynamics: Rocket Propulsion Equation",
        "subject": "Physics (Mechanics)",
        "jee_level": "JEE Advanced",
        "steps": [
            {
                "step": 1,
                "label": "Momentum Conservation in Inactive Frame",
                "formula": "P(t) = m v, \\quad P(t+dt) = (m - |dm|)(v + dv) + |dm|(v - u_{rel})",
                "note": "Ejected gas has velocity $(v - u_{rel})$ relative to ground where $u_{rel}$ is exhaust speed."
            },
            {
                "step": 2,
                "label": "Thrust Force Equation",
                "formula": "m \\frac{dv}{dt} = u_{rel}\\left(-\\frac{dm}{dt}\\right) - m g",
                "note": "Thrust force $F_{thrust} = u_{rel} \\left(-\\frac{dm}{dt}\\right)$. Fuel burn rate is negative of mass change."
            },
            {
                "step": 3,
                "label": "Separation of Variables & Integration",
                "formula": "\\int_{v_0}^v dv = -u_{rel} \\int_{m_0}^m \\frac{dm}{m} - g \\int_0^t dt",
                "note": "Integrating both sides between initial mass $m_0$ and burnout mass $m$."
            },
            {
                "step": 4,
                "label": "Final Tsiolkovsky Velocity Formula",
                "formula": "v(t) = v_0 + u_{rel} \\ln\\left(\\frac{m_0}{m(t)}\\right) - g t",
                "note": "In gravity-free space: $\\Delta v = u_{rel} \\ln(m_0/m)$. Mass ratio determines maximum stage velocity."
            }
        ]
    }

def solve_symbolic_expression(math_input: str):
    """Parses and computes symbolic derivatives, integrals, and limits via SymPy."""
    x = symbols('x')
    try:
        expr = sp.sympify(math_input)
        deriv = diff(expr, x)
        integ = integrate(expr, x)
        lim_zero = limit(expr, x, 0)

        roots = []
        try:
            sol = sp.solve(expr, x)
            if sol:
                roots = [latex(s) for s in sol]
        except Exception:
            pass

        return {
            "status": "success",
            "expression_latex": latex(expr),
            "derivative_latex": latex(deriv),
            "integral_latex": latex(integ) + " + C",
            "limit_x0_latex": latex(lim_zero),
            "roots_latex": roots
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# ----------------- 2. ORGANIC REACTION MECHANISMS VISUALIZER -----------------

ORGANIC_MECHANISMS_DB = [
    {
        "id": "aldol_condensation",
        "name": "Aldol & Cross-Aldol Condensation Mechanism",
        "category": "Carbonyl Compounds (12th Board & JEE Adv)",
        "reactants": "$\\text{CH}_3\\text{CHO} + \\text{CH}_3\\text{CHO} \\xrightarrow{\\text{OH}^-}$",
        "product": "$\\text{CH}_3\\text{-CH=CH-CHO}$ (Crotonaldehyde)",
        "reaction_steps": [
            {
                "step_num": 1,
                "title": "Deprotonation of $\\alpha$-Hydrogen",
                "mechanism_text": "Base ($\\text{OH}^-$) abstracts acidic $\\alpha$-hydrogen from acetaldehyde forming a resonance-stabilized enolate ion.",
                "chemical_equation": "\\text{CH}_3\\text{CHO} + \\text{OH}^- \\rightleftharpoons [:^-\\text{CH}_2-\\text{CH=O} \\leftrightarrow \\text{CH}_2=\\text{CH-O}^-] + \\text{H}_2\\text{O}"
            },
            {
                "step_num": 2,
                "title": "Nucleophilic Addition on Second Carbonyl",
                "mechanism_text": "Enolate carbanion attacks the electrophilic carbonyl carbon of an un-ionized second acetaldehyde molecule.",
                "chemical_equation": "\\text{CH}_3-\\text{CHO} + ^-\\text{CH}_2-\\text{CHO} \\longrightarrow \\text{CH}_3-\\text{CH(O}^-)-\\text{CH}_2-\\text{CHO}"
            },
            {
                "step_num": 3,
                "title": "Protonation forming $\\beta$-Hydroxy Aldehyde (Aldol)",
                "mechanism_text": "Alkoxide ion abstracts a proton from water to regenerate $\\text{OH}^-$ catalyst.",
                "chemical_equation": "\\text{CH}_3-\\text{CH(O}^-)-\\text{CH}_2-\\text{CHO} + \\text{H}_2\\text{O} \\longrightarrow \\text{CH}_3-\\text{CH(OH)}-\\text{CH}_2-\\text{CHO} + \\text{OH}^-"
            },
            {
                "step_num": 4,
                "title": "Dehydration upon Mild Warming ($\\text{E1cB}$ mechanism)",
                "mechanism_text": "Elimination of water creates an $\\alpha,\\beta$-unsaturated aldehyde stabilized by extended conjugated $\\pi$-system.",
                "chemical_equation": "\\text{CH}_3-\\text{CH(OH)}-\\text{CH}_2-\\text{CHO} \\xrightarrow{\\Delta, -\\text{H}_2\\text{O}} \\text{CH}_3-\\text{CH=CH-CHO}"
            }
        ],
        "iit_trap": "In Cross-Aldol with Benzaldehyde (no $\\alpha$-H), Benzaldehyde is ALWAYS the electrophile and ketone/aldehyde is the nucleophile (Claisen-Schmidt)."
    },
    {
        "id": "pinacol_pinacolone",
        "name": "Pinacol-Pinacolone Rearrangement",
        "category": "Alcohols & Carbocation Rearrangements (JEE Advanced)",
        "reactants": "2,3-Dimethylbutane-2,3-diol $\\xrightarrow{\\text{H}^+}$",
        "product": "3,3-Dimethylbutan-2-one (Pinacolone)",
        "reaction_steps": [
            {
                "step_num": 1,
                "title": "Protonation of more basic/stable hydroxyl group",
                "mechanism_text": "Acid protonates one of the tertiary $-\\text{OH}$ groups forming an oxonium ion $-\\text{OH}_2^+$.",
                "chemical_equation": "(\\text{CH}_3)_2\\text{C(OH)}-\\text{C(OH)}(\\text{CH}_3)_2 + \\text{H}^+ \\longrightarrow (\\text{CH}_3)_2\\text{C(OH)}-\\text{C(OH}_2^+)(\\text{CH}_3)_2"
            },
            {
                "step_num": 2,
                "title": "Loss of Water molecule forming Carbocation",
                "mechanism_text": "Water leaves yielding a stable tertiary carbocation at C-3.",
                "chemical_equation": "\\longrightarrow (\\text{CH}_3)_2\\text{C(OH)}-\\text{C}^+(\\text{CH}_3)_2 + \\text{H}_2\\text{O}"
            },
            {
                "step_num": 3,
                "title": "1,2-Methyl Shift driven by Oxygen Lone Pair",
                "mechanism_text": "One methyl group migrates with its electron pair. Driving force is formation of an octet-complete oxonium intermediate.",
                "chemical_equation": "\\longrightarrow (\\text{CH}_3)_3\\text{C}-\\text{C}(=\\text{O}^+-\\text{H})-\\text{CH}_3"
            },
            {
                "step_num": 4,
                "title": "Deprotonation forming Pinacolone",
                "mechanism_text": "Loss of proton gives the ketone product.",
                "chemical_equation": "\\longrightarrow (\\text{CH}_3)_3\\text{C}-\\text{CO}-\\text{CH}_3 + \\text{H}^+"
            }
        ],
        "iit_trap": "Migratory aptitude in unsymmetrical pinacols: $\\text{Ar} > \\text{Alkyl} > \\text{H}$ or electron-rich Aryl ($p\\text{-anisyl} > p\\text{-tolyl} > \\text{phenyl} > p\\text{-chlorophenyl}$)."
    }
]

def get_organic_mechanisms():
    """Returns list of curated interactive organic mechanisms."""
    return ORGANIC_MECHANISMS_DB


# ----------------- 3. DYNAMIC SVG PLOTTING (MATPLOTLIB) -----------------

def generate_wave_optics_plot() -> str:
    """Generates an SVG plot of Young's Double Slit Interference Fringe Intensity."""
    theta = np.linspace(-3*np.pi, 3*np.pi, 500)
    # Intensity I = 4 I_0 cos^2(delta / 2)
    intensity = 4 * (np.cos(theta / 2)) ** 2

    plt.figure(figsize=(7, 3), facecolor='#090e1a')
    ax = plt.subplot(111)
    ax.set_facecolor('#0f172a')

    ax.plot(theta, intensity, color='#f59e0b', linewidth=2.2, label=r'$I = 4I_0 \cos^2(\delta/2)$')
    ax.fill_between(theta, intensity, color='#f59e0b', alpha=0.15)

    ax.set_title("YDSE Interference Fringe Intensity Profile", color='#f8fafc', fontsize=11, fontweight='bold', pad=10)
    ax.set_xlabel(r"Phase Difference $\delta$ (radians)", color='#94a3b8', fontsize=9)
    ax.set_ylabel(r"Intensity $I / I_0$", color='#94a3b8', fontsize=9)
    ax.tick_params(colors='#64748b', labelsize=8)

    ax.spines['bottom'].set_color('#334155')
    ax.spines['top'].set_color('#334155')
    ax.spines['left'].set_color('#334155')
    ax.spines['right'].set_color('#334155')
    ax.grid(True, linestyle='--', alpha=0.2, color='#475569')

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='svg', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf.getvalue().decode('utf-8')

def generate_electric_field_plot() -> str:
    """Generates an SVG plot of E-field inside and outside uniformly charged insulating sphere."""
    R = 2.0
    r_in = np.linspace(0, R, 200)
    r_out = np.linspace(R, 6.0, 300)

    E_in = r_in / (R**3) # E proportional to r
    E_out = 1.0 / (r_out**2) # E proportional to 1/r^2

    plt.figure(figsize=(7, 3), facecolor='#090e1a')
    ax = plt.subplot(111)
    ax.set_facecolor('#0f172a')

    ax.plot(r_in, E_in, color='#06b6d4', linewidth=2.5, label=r'$E \propto r \quad (r \le R)$')
    ax.plot(r_out, E_out, color='#38bdf8', linewidth=2.5, linestyle='-', label=r'$E \propto 1/r^2 \quad (r > R)$')
    ax.axvline(x=R, color='#f43f5e', linestyle=':', label=r'Surface $r = R$')

    ax.set_title("Electric Field E(r) of Uniformly Charged Non-Conducting Sphere", color='#f8fafc', fontsize=11, fontweight='bold', pad=10)
    ax.set_xlabel(r"Distance $r$ from Center", color='#94a3b8', fontsize=9)
    ax.set_ylabel(r"Electric Field $E$", color='#94a3b8', fontsize=9)
    ax.tick_params(colors='#64748b', labelsize=8)
    ax.legend(facecolor='#1e293b', edgecolor='#334155', labelcolor='#e2e8f0', fontsize=8)

    ax.spines['bottom'].set_color('#334155')
    ax.spines['top'].set_color('#334155')
    ax.spines['left'].set_color('#334155')
    ax.spines['right'].set_color('#334155')
    ax.grid(True, linestyle='--', alpha=0.2, color='#475569')

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='svg', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf.getvalue().decode('utf-8')
