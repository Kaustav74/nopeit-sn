"""
JEE AIR-1 CBSE Class 12 Board Step-Loss & Rubric Evaluator
==========================================================
JEE toppers frequently lose 10-15 marks in CBSE Boards due to:
- Missing labeled diagrams or missing directional arrows
- Skipping intermediate algebraic steps obvious to JEE students but required by CBSE rubrics
- Omitting explicit SI units or final boxed statements
- Leaving out statement of initial physical assumptions

This engine implements:
1. Standard 5-Mark & 3-Mark CBSE Official Marking Rubrics
2. Line-by-Line Step-Loss Grader
3. Curated High-Yield CBSE Derivations Library (Physics, Chemistry, Maths)
4. NCERT Verbatim Keyword Cloze Drill Bank
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
try:
    from .database import get_connection
except ImportError:
    from database import get_connection

CBSE_CORE_DERIVATIONS = [
    {
        "derivation_key": "PHY_DERIV_01",
        "subject": "Physics",
        "title": "Electric Field on the Axial and Equatorial Line of an Electric Dipole",
        "total_marks": 5.0,
        "rubric_steps": [
            {"criterion": "Statement of Dipole & Vector Definition (p = q * 2a)", "marks": 0.5, "keywords": ["dipole moment", "vector", "direction from -q to +q"]},
            {"criterion": "Neat labeled diagram with distance coordinates (r, a) and field vectors", "marks": 1.0, "keywords": ["diagram", "r", "2a", "E+", "E-"]},
            {"criterion": "Axial point field derivation using superposition principle", "marks": 1.5, "keywords": ["superposition", "E_net", "(r-a)^2", "(r+a)^2", "4*pi*epsilon_0"]},
            {"criterion": "Short dipole approximation (r >> a) showing E_axial = 2kp/r^3", "marks": 1.0, "keywords": ["r >> a", "2kp/r^3", "proportional to 1/r^3"]},
            {"criterion": "Vector relation and equatorial comparison (E_axial = 2 * E_equatorial)", "marks": 1.0, "keywords": ["vector notation", "E_axial = 2*E_equatorial", "opposite direction"]}
        ],
        "common_board_traps": "Students omit vector signs above E and p, or forget to state the short dipole limit r >> a, losing 1.5 marks instantly."
    },
    {
        "derivation_key": "PHY_DERIV_02",
        "subject": "Physics",
        "title": "Lens Maker's Formula for a Thin Convex Lens",
        "total_marks": 5.0,
        "rubric_steps": [
            {"criterion": "Assumptions stated (thin lens, small aperture, paraxial rays)", "marks": 0.5, "keywords": ["thin lens", "small aperture", "paraxial rays"]},
            {"criterion": "Complete ray diagram with normal, incident, refracted rays and center of curvature", "marks": 1.0, "keywords": ["ray diagram", "C1", "C2", "R1", "R2", "arrows"]},
            {"criterion": "Refraction at first spherical surface (n2/v1 - n1/u = (n2-n1)/R1)", "marks": 1.5, "keywords": ["first surface", "n2/v1", "n1/u", "(n2-n1)/R1"]},
            {"criterion": "Refraction at second spherical surface with virtual object", "marks": 1.0, "keywords": ["second surface", "virtual object", "n1/v", "n2/v1"]},
            {"criterion": "Summation and definition of focal length (1/f = (n-1)(1/R1 - 1/R2))", "marks": 1.0, "keywords": ["1/f", "(n-1)", "1/R1 - 1/R2", "box final result"]}
        ],
        "common_board_traps": "Examiners deduct 1 full mark if directional arrows are missing on ray lines or if sign convention isn't specified."
    },
    {
        "derivation_key": "PHY_DERIV_03",
        "subject": "Physics",
        "title": "Biot-Savart Law & Magnetic Field on the Axis of a Circular Current Loop",
        "total_marks": 5.0,
        "rubric_steps": [
            {"criterion": "Statement and vector equation of Biot-Savart Law dB = (mu_0/4pi) * (I dl x r) / r^3", "marks": 1.0, "keywords": ["biot savart", "mu_0/4pi", "I dl x r", "vector"]},
            {"criterion": "3D diagram of circular loop with axial point P and resolved components dB cos(theta) & dB sin(theta)", "marks": 1.0, "keywords": ["diagram", "dB sin", "dB cos", "resolved"]},
            {"criterion": "Symmetry argument explaining cancellation of diametrically opposite perpendicular components", "marks": 1.0, "keywords": ["symmetry", "cancels", "perpendicular", "summation"]},
            {"criterion": "Integration along circumference (integral dl = 2*pi*R)", "marks": 1.0, "keywords": ["integral dl", "2*pi*R", "sin(theta) = R/r"]},
            {"criterion": "Final expression B = (mu_0 * I * R^2) / [2(R^2 + x^2)^(3/2)] and field at center (x=0)", "marks": 1.0, "keywords": ["mu_0 * I * R^2 / 2(R^2+x^2)^(3/2)", "x=0", "mu_0*I/(2R)", "Tesla"]}
        ],
        "common_board_traps": "Failing to explain WHY dB cos(theta) integrates to zero loses 1 mark."
    },
    {
        "derivation_key": "CHEM_DERIV_01",
        "subject": "Chemistry",
        "title": "Integrated Rate Equation for a First Order Reaction & Half-Life",
        "total_marks": 3.0,
        "rubric_steps": [
            {"criterion": "Differential rate expression -d[R]/dt = k[R]", "marks": 0.5, "keywords": ["-d[R]/dt", "k[R]", "rate constant"]},
            {"criterion": "Integration with boundary conditions at t=0 ([R]=[R]0) and t=t", "marks": 1.0, "keywords": ["ln[R]", "-kt + I", "boundary conditions", "[R]0"]},
            {"criterion": "Conversion to log base 10 form: k = (2.303/t) * log([R]0/[R])", "marks": 1.0, "keywords": ["2.303/t", "log", "[R]0/[R]", "s^-1 units"]},
            {"criterion": "Derivation of t_1/2 = 0.693 / k showing independence from initial concentration", "marks": 0.5, "keywords": ["t_1/2 = 0.693/k", "independent of [R]0"]}
        ],
        "common_board_traps": "Leaving the formula in ln instead of log10, or forgetting units (s^-1)."
    }
]

NCERT_CLOZE_CARDS = [
    {
        "id": "NCERT-001",
        "subject": "Chemistry",
        "chapter": "Haloalkanes and Haloarenes",
        "prompt": "Complete the NCERT definition: In SN2 mechanism, the incoming nucleophile attacks from the side opposite to the leaving group, resulting in complete _____ of configuration, known as _____ inversion.",
        "blanks": ["inversion", "Walden"],
        "explanation": "CBSE answers must explicitly contain the keyword 'Walden inversion' to secure the full 1 mark."
    },
    {
        "id": "NCERT-002",
        "subject": "Physics",
        "chapter": "Electromagnetic Induction",
        "prompt": "Complete Lenz's Law: The polarity of induced emf is such that it tends to produce a current which _____ the change in magnetic flux that produces it. Lenz's law is a direct consequence of the principle of conservation of _____.",
        "blanks": ["opposes", "energy"],
        "explanation": "'Opposes' and 'energy' are the exact keywords searched by CBSE board evaluators."
    },
    {
        "id": "NCERT-003",
        "subject": "Physics",
        "chapter": "Wave Optics",
        "prompt": "State Huygens' Principle: Each point of a wavefront acts as a secondary source of spherical wavelets called _____. The new wavefront at any later time is the _____ envelope enclosing these wavelets.",
        "blanks": ["wavelets", "forward"],
        "explanation": "The word 'forward' is critical; backward wavelets have zero amplitude according to Huygens-Fresnel diffraction."
    }
]

def get_cbse_derivations_list() -> List[Dict]:
    """
    Returns available 5-mark and 3-mark CBSE derivations with rubrics.
    """
    return [
        {
            "derivation_key": d["derivation_key"],
            "subject": d["subject"],
            "title": d["title"],
            "total_marks": d["total_marks"],
            "steps_count": len(d["rubric_steps"]),
            "common_board_traps": d["common_board_traps"]
        } for d in CBSE_CORE_DERIVATIONS
    ]

def evaluate_cbse_derivation(derivation_key: str, student_text: str) -> Dict:
    """
    Evaluates student's written steps against the official CBSE step rubric.
    Searches for key phrases, formula structures, and essential terms.
    """
    target = next((d for d in CBSE_CORE_DERIVATIONS if d["derivation_key"] == derivation_key), None)
    if not target:
        return {"status": "error", "message": "Derivation not found in registry."}

    text_lower = student_text.lower()
    total_max = target["total_marks"]
    marks_awarded = 0.0
    rubric_feedback = []
    missing_elements = []

    for step in target["rubric_steps"]:
        keywords = step["keywords"]
        matches = [kw for kw in keywords if kw.lower() in text_lower]
        coverage = len(matches) / len(keywords)

        if coverage >= 0.5:
            step_marks = step["marks"]
            status = "FULL"
        elif coverage > 0.2:
            step_marks = round(step["marks"] * 0.5, 2)
            status = "PARTIAL"
            missing_elements.append(f"{step['criterion']} (Missing: {', '.join([k for k in keywords if k.lower() not in text_lower])})")
        else:
            step_marks = 0.0
            status = "OMITTED"
            missing_elements.append(f"{step['criterion']} (Completely omitted)")

        marks_awarded += step_marks
        rubric_feedback.append({
            "criterion": step["criterion"],
            "max_marks": step["marks"],
            "marks_awarded": step_marks,
            "status": status,
            "matched_keywords": matches
        })

    marks_awarded = min(total_max, marks_awarded)

    # Save to database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cbse_answer_reviews (
            derivation_key, subject, title, submitted_steps,
            max_marks, marks_awarded, rubric_feedback, missing_elements
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        derivation_key,
        target["subject"],
        target["title"],
        student_text,
        total_max,
        marks_awarded,
        json.dumps(rubric_feedback),
        json.dumps(missing_elements)
    ))
    conn.commit()
    conn.close()

    return {
        "status": "success",
        "derivation_title": target["title"],
        "max_marks": total_max,
        "marks_awarded": marks_awarded,
        "percentage": round((marks_awarded / total_max) * 100.0, 1),
        "rubric_breakdown": rubric_feedback,
        "missing_elements": missing_elements,
        "board_examiner_note": target["common_board_traps"]
    }

def get_ncert_cloze_drill() -> List[Dict]:
    """
    Returns NCERT verbatim keyword cloze cards.
    """
    return NCERT_CLOZE_CARDS
