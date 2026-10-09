"""
SoloLearn-Style Micro-Learning Engine for JEE Main/Advanced & CBSE 12th
Algorithm:
1. Deliver 1 concise, high-yield concept nugget (theory, master formula, or IIT trap).
2. Immediately fire an active recall question or authentic PYQ patch.
3. Provide instant interactive feedback, XP boost, and unlock next concept step.
"""

import json
from .database import get_db
from .llm_service import call_llm, extract_json_from_llm

CURATED_SOLOLEARN_MODULES = [
    {
        "module_id": "phy_pure_rolling",
        "subject": "Physics",
        "topic": "Rotational Mechanics",
        "title": "Instantaneous Axis of Rotation (IAOR) & Pure Rolling",
        "xp_reward": 100,
        "steps": [
            {
                "step_index": 0,
                "type": "concept_nugget",
                "title": "The Golden Rule of Pure Rolling",
                "content": """
### ⚡ Core Concept: Pure Rolling Condition
When a body of radius $R$ rolls without slipping on a surface moving with velocity $v_s$:
$$\\vec{v}_{contact} = \\vec{v}_{surface}$$
If the surface is at rest:
$$v_{cm} - R\\omega = 0 \\implies v_{cm} = R\\omega$$

> **⚠️ IIT-JEE Trap Alert:** 
> Friction does **ZERO work** in pure rolling because the point of contact is *instantaneously at rest* ($ds = 0$). 
> Never use $W = f \\cdot s$ for static friction! Total mechanical energy is conserved unless slipping occurs.
""",
                "key_takeaway": "$v_{cm} = R\\omega$ and static friction does no mechanical work."
            },
            {
                "step_index": 1,
                "type": "active_recall",
                "pyq_source": "JEE Advanced 2021 / Pathfinder Physics",
                "question": "A solid sphere rolls without slipping down an inclined plane of inclination $\\theta$. What is the magnitude and direction of the friction force acting on it?",
                "options": [
                    "$f = \\frac{2}{7} mg \\sin\\theta$ up the incline",
                    "$f = \\frac{1}{3} mg \\sin\\theta$ down the incline",
                    "$f = \\frac{5}{7} mg \\sin\\theta$ up the incline",
                    "$f = 0$ because rolling is pure"
                ],
                "correct_option": 0,
                "explanation": "Equation for CM: $mg\\sin\\theta - f = ma_{cm}$. Torque about CM: $f R = I_{cm} \\alpha = \\left(\\frac{2}{5}mR^2\\right)\\left(\\frac{a_{cm}}{R}\\right) \\implies f = \\frac{2}{5} m a_{cm}$. Substitute: $mg\\sin\\theta - \\frac{2}{5}m a_{cm} = m a_{cm} \\implies a_{cm} = \\frac{5}{7}g\\sin\\theta$. Thus $f = \\frac{2}{7}mg\\sin\\theta$ directed upwards to oppose rotation.",
                "xp": 25
            },
            {
                "step_index": 2,
                "type": "concept_nugget",
                "title": "Instantaneous Axis of Rotation (IAOR)",
                "content": """
### 🔍 Instantaneous Center of Zero Velocity (IAOR)
For any rigid body undergoing general planar motion:
- There exists an axis about which the entire body is in **pure rotation**.
- For pure rolling on stationary ground, the IAOR is the **point of contact** ($P$).
- Kinetic Energy can be written in one single stroke:
$$K_{total} = \\frac{1}{2} I_{IAOR} \\omega^2$$
No need to separate into $\\frac{1}{2}mv_{cm}^2 + \\frac{1}{2}I_{cm}\\omega^2$! By Parallel Axis Theorem: $I_{IAOR} = I_{cm} + mR^2$.
""",
                "key_takeaway": "Using IAOR eliminates unknown normal forces and friction when taking torques!"
            },
            {
                "step_index": 3,
                "type": "active_recall",
                "pyq_source": "JEE Main 2023 / CBSE 12th Board Concept",
                "question": "A ring of mass $M$ and radius $R$ rolls without slipping with speed $v$. What is its total kinetic energy calculated using IAOR?",
                "options": [
                    "$M v^2$",
                    "$\\frac{1}{2} M v^2$",
                    "$\\frac{3}{4} M v^2$",
                    "$2 M v^2$"
                ],
                "correct_option": 0,
                "explanation": "About IAOR (contact point), by parallel axis theorem: $I_P = I_{cm} + M R^2 = M R^2 + M R^2 = 2 M R^2$. Since $\\omega = v/R$, $K = \\frac{1}{2} I_P \\omega^2 = \\frac{1}{2}(2MR^2)(v/R)^2 = M v^2$.",
                "xp": 25
            }
        ]
    },
    {
        "module_id": "chem_aldol_cannizzaro",
        "subject": "Chemistry",
        "topic": "Organic Chemistry - Carbonyl Reactions",
        "title": "Aldol vs Cannizzaro vs Benzoin Condensations",
        "xp_reward": 100,
        "steps": [
            {
                "step_index": 0,
                "type": "concept_nugget",
                "title": "Alpha-Hydrogen Decision Matrix (DexterChem Rule)",
                "content": """
### 🧪 The Decisive Test for Carbonyls with Base
When an aldehyde/ketone is treated with alkali ($\\text{OH}^-$):
1. **Has $\\alpha$-H?** $\\rightarrow$ **Aldol Condensation**.
   - Base abstracts acidic $\\alpha$-H $\\rightarrow$ Enolate ion $\\rightarrow$ Nucleophilic addition on another carbonyl $\\rightarrow$ $\\beta$-hydroxy carbonyl (Aldol) $\\xrightarrow{\\Delta} \\alpha,\\beta$-unsaturated carbonyl.
2. **NO $\\alpha$-H?** (e.g., $\\text{HCHO}$, $\\text{PhCHO}$, $\\text{Me}_3\\text{C-CHO}$):
   - With dilute/conc. base $\\rightarrow$ **Cannizzaro Reaction** (Disproportionation: one molecule reduces to alcohol, one oxidizes to carboxylate).
   - Rate equation: Rate $= k [\\text{ArCHO}]^2 [\\text{OH}^-]$ (or $[\\text{OH}^-]^2$ for very strong base).
""",
                "key_takeaway": "Presence of acidic $\\alpha$-H always drives Aldol because proton transfer is $10^4\\times$ faster than hydride shift."
            },
            {
                "step_index": 1,
                "type": "active_recall",
                "pyq_source": "JEE Advanced 2022 / CBSE Class 12 Boards",
                "question": "What is the major product when Formaldehyde ($\\text{HCHO}$) and Benzaldehyde ($\\text{PhCHO}$) are treated with $50\\%\\;\\text{NaOH}$ (Cross-Cannizzaro)?",
                "options": [
                    "Sodium formate ($\\text{HCOONa}$) and Benzyl alcohol ($\\text{PhCH}_2\\text{OH}$)",
                    "Sodium benzoate ($\\text{PhCOONa}$) and Methanol ($\\text{CH}_3\\text{OH}$)",
                    "Chalcone and Formic acid",
                    "Benzyl benzoate only"
                ],
                "correct_option": 0,
                "explanation": "In Cross-Cannizzaro, the more reactive aldehyde ($\\text{HCHO}$) undergoes nucleophilic attack by $\\text{OH}^-$ faster due to less steric hindrance and greater positive charge on carbon. It then transfers hydride ($H^-$) to Benzaldehyde. Hence $\\text{HCHO}$ oxidizes to Formate, while $\\text{PhCHO}$ reduces to Benzyl alcohol.",
                "xp": 25
            },
            {
                "step_index": 2,
                "type": "concept_nugget",
                "title": "Intramolecular Aldol Ring Size Stability",
                "content": """
### 🧬 Intramolecular Ring Closure Hierarchy
When a dicarbonyl molecule has multiple $\\alpha$-positions:
- 5-membered and 6-membered rings form preferentially due to negligible ring strain.
- 3-membered and 4-membered rings NEVER form in aldol.
- 7-membered rings form very slowly due to unfavorable entropy of activation.
$$\\text{Rate of Formation: } 5 \\approx 6 \\gg 7 \\gg 8$$
""",
                "key_takeaway": "Always count carbon skeleton to ensure the resulting cyclic enone has 5 or 6 carbons in the ring."
            },
            {
                "step_index": 3,
                "type": "active_recall",
                "pyq_source": "JEE Advanced 2020",
                "question": "When 2,6-Heptanedione is heated with aqueous $\\text{KOH}$, which cyclic product is predominantly isolated?",
                "options": [
                    "3-Methylcyclohex-2-en-1-one",
                    "1-(2-Methylcyclopent-1-en-1-yl)ethan-1-one",
                    "Cyclohept-2-en-1-one",
                    "3-Methylcyclopent-2-en-1-one"
                ],
                "correct_option": 0,
                "explanation": "2,6-Heptanedione has 7 carbons. Attack of C-1 methyl carbanion onto C-6 carbonyl forms a 6-membered ring (3-methylcyclohex-2-en-1-one). Attack from C-3 onto C-6 would form a strained 4-membered ring, which is strictly disfavored.",
                "xp": 25
            }
        ]
    },
    {
        "module_id": "math_definite_integrals",
        "subject": "Mathematics",
        "topic": "Definite Integration & King's Property",
        "title": "Mastering King's Rule & Symmetry Integrals",
        "xp_reward": 100,
        "steps": [
            {
                "step_index": 0,
                "type": "concept_nugget",
                "title": "The Supreme King's Property",
                "content": """
### 👑 King's Property ($a+b-x$)
For any integrable function on $[a, b]$:
$$I = \\int_a^b f(x) dx = \\int_a^b f(a + b - x) dx$$
Adding both expressions:
$$2I = \\int_a^b [f(x) + f(a + b - x)] dx$$

> **💡 The AIR-1 Observation:**
> If $f(x) + f(a + b - x) = C$ (a constant), then in a single line:
> $$I = \\frac{C(b - a)}{2}$$
> This single observation solves over $40\\%$ of definite integral PYQs in JEE Main and Advanced!
""",
                "key_takeaway": "Always test $f(x) + f(a+b-x)$. If it simplifies or becomes symmetric, the integral collapses instantly."
            },
            {
                "step_index": 1,
                "type": "active_recall",
                "pyq_source": "JEE Main 2024 / CBSE 12th Board Standard",
                "question": "Evaluate: $I = \\int_0^{\\pi/2} \\frac{\\sin^{2026} x}{\\sin^{2026} x + \\cos^{2026} x} dx$.",
                "options": [
                    "$\\frac{\\pi}{4}$",
                    "$\\frac{\\pi}{2}$",
                    "$0$",
                    "$1$"
                ],
                "correct_option": 0,
                "explanation": "Using King's rule with $a+b-x = \\frac{\\pi}{2} - x$: $\\sin(\\pi/2 - x) = \\cos x$. Adding both integrals yields $2I = \\int_0^{\\pi/2} 1 dx = \\frac{\\pi}{2} \\implies I = \\frac{\\pi}{4}$.",
                "xp": 25
            },
            {
                "step_index": 2,
                "type": "concept_nugget",
                "title": "Newton-Leibniz Differentiation Rule",
                "content": """
### ⚡ Differentiating Variable Integral Limits
If $F(x) = \\int_{u(x)}^{v(x)} g(x, t) dt$, then:
$$F'(x) = g(x, v(x)) \\cdot v'(x) - g(x, u(x)) \\cdot u'(x) + \\int_{u(x)}^{v(x)} \\frac{\\partial g}{\\partial x}(x, t) dt$$
If $g$ depends only on $t$:
$$\\frac{d}{dx}\\left(\\int_{u(x)}^{v(x)} f(t) dt\\right) = f(v(x)) v'(x) - f(u(x)) u'(x)$$
""",
                "key_takeaway": "Always remember the chain rule factors $v'(x)$ and $u'(x)$!"
            },
            {
                "step_index": 3,
                "type": "active_recall",
                "pyq_source": "JEE Advanced 2023",
                "question": "Find $\\lim_{x \\to 0} \\frac{\\int_0^{x^2} \\sin(\\sqrt{t}) dt}{x^3}$.",
                "options": [
                    "$\\frac{2}{3}$",
                    "$\\frac{1}{3}$",
                    "$1$",
                    "$0$"
                ],
                "correct_option": 0,
                "explanation": "This is in $0/0$ indeterminate form. Apply L'Hôpital's Rule: Numerator derivative by Leibniz Rule is $\\sin(\\sqrt{x^2}) \\cdot (2x) = \\sin(x) \\cdot 2x$. Denominator derivative is $3x^2$. Limit becomes $\\lim_{x \\to 0} \\frac{2x \\sin x}{3x^2} = \\frac{2}{3} \\lim_{x \\to 0} \\frac{\\sin x}{x} = \\frac{2}{3}$.",
                "xp": 25
            }
        ]
    }
]

def get_all_modules():
    """Returns overview of all SoloLearn-style modules."""
    summary = []
    for m in CURATED_SOLOLEARN_MODULES:
        summary.append({
            "module_id": m["module_id"],
            "subject": m["subject"],
            "topic": m["topic"],
            "title": m["title"],
            "total_steps": len(m["steps"]),
            "xp_reward": m["xp_reward"]
        })
    return summary

def get_module_data(module_id):
    """Fetches full steps for a given module."""
    for m in CURATED_SOLOLEARN_MODULES:
        if m["module_id"] == module_id:
            return m
    return None

def verify_step_answer(module_id, step_index, chosen_option):
    """Verifies student answer, awards XP, and updates streak."""
    module = get_module_data(module_id)
    if not module:
        return {"error": "Module not found"}
    
    if step_index >= len(module["steps"]):
        return {"error": "Step out of range"}
    
    step = module["steps"][step_index]
    if step["type"] != "active_recall":
        return {"error": "Step is not an active recall question"}
    
    is_correct = (chosen_option == step["correct_option"])
    xp_earned = step["xp"] if is_correct else 5 # Effort XP

    # Update student profile XP
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE student_profile SET xp = xp + ? WHERE id = 1", (xp_earned,))
    conn.commit()
    conn.close()

    return {
        "is_correct": is_correct,
        "correct_option": step["correct_option"],
        "explanation": step["explanation"],
        "xp_earned": xp_earned
    }

def generate_ai_micro_card(subject, topic):
    """Uses FreeLLM to generate a custom SoloLearn micro-card on the fly."""
    prompt = f"""
Create a SoloLearn-style micro-learning concept card for JEE Main/Advanced:
Subject: {subject}
Topic: {topic}

Provide strict JSON format:
{{
  "title": "Short punchy title",
  "concept_nugget": "Crisp 80-word high yield explanation with formulas in KaTeX ($...$) and 1 IIT-JEE trap warning",
  "key_takeaway": "1 sentence punchline",
  "pyq_question": "Challenging authentic JEE style question",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct_option_index": 0,
  "explanation": "Step-by-step rigorous derivation"
}}
Strict JSON only.
"""
    raw = call_llm([{"role": "user", "content": prompt}], temperature=0.4)
    if raw:
        parsed = extract_json_from_llm(raw)
        if parsed and isinstance(parsed, dict):
            return parsed
    return None
