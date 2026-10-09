"""
Concept Dependency Graph & 6-Stage Mastery Engine
Provides atomic concept decomposition, prerequisite tracing,
multi-dimensional mastery assessment, and false-mastery detection.
"""

import json
from datetime import datetime, timedelta
from .database import get_db

# Initial high-fidelity concept hierarchy across PCM with explicit prerequisites & ROI
CORE_CONCEPT_GRAPH = [
    # --- PHYSICS: ELECTROSTATICS & MECHANICS ---
    {
        "concept_id": "phy_nl_01",
        "subject": "Physics",
        "chapter": "Newton's Laws of Motion",
        "topic": "Constraint Relations & Frames",
        "title": "Kinematic Constraint Relations",
        "description": "Connecting accelerations of coupled bodies across pulleys, wedges, and planks.",
        "prerequisites": [],
        "weightage_pct": 4.0,
        "roi_priority": "High",
        "formula_definition": r"\sum \vec{T} \cdot \vec{a} = 0 \text{ (virtual work method)}",
        "assumptions_conditions": "Inextensible string, massless ideal pulleys.",
        "limiting_cases": "When mass of string tends to zero, tension is uniform along continuous segment.",
        "common_misconceptions": "Assuming tension is identical across an accelerating pulley with moment of inertia."
    },
    {
        "concept_id": "phy_we_01",
        "subject": "Physics",
        "chapter": "Work Power Energy",
        "topic": "Work-Energy Theorem & Conservative Fields",
        "title": "Work Energy Theorem & Potential Energy Gradient",
        "description": "Relating work done by all forces to kinetic energy change, and conservative force field F = -grad(U).",
        "prerequisites": ["phy_nl_01"],
        "weightage_pct": 5.0,
        "roi_priority": "High",
        "formula_definition": r"W_{all} = \Delta K, \quad \vec{F}_{cons} = -\nabla U",
        "assumptions_conditions": "Valid in inertial frames; add pseudo-work in non-inertial frames.",
        "limiting_cases": "If net external work is zero, mechanical energy is conserved.",
        "common_misconceptions": "Forgetting that static friction can do non-zero work on an individual component of a system."
    },
    {
        "concept_id": "phy_rot_01",
        "subject": "Physics",
        "chapter": "Rotational Mechanics",
        "topic": "Rigid Body Dynamics",
        "title": "Pure Rolling on Accelerated Moving Planks",
        "description": "No-slipping condition a_p = a_c + R*alpha connecting linear acceleration of plank, cylinder center, and angular acceleration.",
        "prerequisites": ["phy_nl_01", "phy_we_01"],
        "weightage_pct": 7.0,
        "roi_priority": "High",
        "formula_definition": r"a_{\text{contact}} = a_c \pm R\alpha = a_{\text{surface}}",
        "assumptions_conditions": "Static friction f <= mu_s * N; pure rolling without sliding.",
        "limiting_cases": "If plank is stationary, a_c = R*alpha.",
        "common_misconceptions": "Thinking static friction always opposes the direction of linear motion in rolling."
    },
    {
        "concept_id": "phy_es_01",
        "subject": "Physics",
        "chapter": "Electrostatics",
        "topic": "Electric Potential & Superposition",
        "title": "Electric Potential due to Continuous Charge Distributions",
        "description": "Scalar superposition of electrostatic potential V = (1/4pi eps0) int (dq/r) and relation E = -dV/dr.",
        "prerequisites": ["phy_we_01"],
        "weightage_pct": 6.5,
        "roi_priority": "High",
        "formula_definition": r"V(r) = \frac{1}{4\pi\varepsilon_0}\int \frac{dq}{r}, \quad \vec{E} = -\vec{\nabla} V",
        "assumptions_conditions": "Reference at infinity (unless infinite charge distribution is present).",
        "limiting_cases": "For r >> size of distribution, system behaves as a monopole point charge.",
        "common_misconceptions": "Assuming potential inside any charged conductor is zero (it is constant, equal to surface potential)."
    },
    {
        "concept_id": "phy_es_02",
        "subject": "Physics",
        "chapter": "Electrostatics",
        "topic": "Gauss's Law",
        "title": "Gauss's Flux Theorem with Variable Density rho(r)",
        "description": "Flux integration over closed Gaussian surfaces and enclosed charge calculation q_enc = int 4pi r^2 rho(r) dr.",
        "prerequisites": ["phy_es_01"],
        "weightage_pct": 6.0,
        "roi_priority": "High",
        "formula_definition": r"\oint \vec{E} \cdot d\vec{A} = \frac{q_{\text{enclosed}}}{\varepsilon_0}",
        "assumptions_conditions": "High spatial symmetry (spherical, cylindrical, planar) to extract E outside the integral.",
        "limiting_cases": "At r -> 0 inside non-conducting sphere, E -> 0 if density is finite.",
        "common_misconceptions": "Believing that E in Gauss's law is only due to charges inside the surface (E is due to all charges, flux is due to enclosed only)."
    },

    # --- CHEMISTRY: ORGANIC & COORDINATION ---
    {
        "concept_id": "chem_org_01",
        "subject": "Chemistry",
        "chapter": "Aldehydes & Ketones",
        "topic": "Carbonyl Condensations",
        "title": "Crossed Aldol & Claisen-Schmidt Condensation",
        "description": "Enolate generation from alpha-hydrogen donor and nucleophilic attack onto more electrophilic non-enolizable carbonyl acceptor.",
        "prerequisites": [],
        "weightage_pct": 6.0,
        "roi_priority": "High",
        "formula_definition": r"\text{Enolate generation} \rightarrow \text{Nucleophilic addition} \rightarrow \text{E1cB Dehydration}",
        "assumptions_conditions": "Dilute aqueous base (dil. NaOH/KOH); alpha-H presence in at least one partner.",
        "limiting_cases": "Without heat, aldol alcohol intermediate (beta-hydroxy carbonyl) is isolated.",
        "common_misconceptions": "Thinking Cannizzaro can occur when alpha-hydrogens are present (aldol is orders of magnitude faster)."
    },
    {
        "concept_id": "chem_coord_01",
        "subject": "Chemistry",
        "chapter": "Coordination Compounds",
        "topic": "Crystal Field Theory (CFT)",
        "title": "Crystal Field Splitting Delta_o and Electron Pairing Rules",
        "description": "Octahedral t2g and eg orbital splitting, spectrochemical series ligand field strength, and magnetic moment calculation.",
        "prerequisites": [],
        "weightage_pct": 5.5,
        "roi_priority": "High",
        "formula_definition": r"\Delta_o > P \implies \text{Low Spin (Pairing)}, \quad \mu = \sqrt{n(n+2)} \text{ BM}",
        "assumptions_conditions": "Electrostatic crystal field splitting model; point charge approximation.",
        "limiting_cases": "For d1, d2, d3 and d8, d9, d10, electron configuration is identical regardless of ligand field strength.",
        "common_misconceptions": "Assuming NH3 is always a strong field ligand (with Fe2+ it is weak field, with Co3+ it is strong field)."
    },

    # --- MATHEMATICS: CALCULUS & VECTORS ---
    {
        "concept_id": "math_calc_01",
        "subject": "Mathematics",
        "chapter": "Definite Integrals",
        "topic": "Newton-Leibniz Differentiation",
        "title": "Newton-Leibniz Formula for Variable Limit Integrals",
        "description": "Differentiating integrals with variable upper and lower boundaries and differential functional equations.",
        "prerequisites": [],
        "weightage_pct": 7.0,
        "roi_priority": "High",
        "formula_definition": r"\frac{d}{dx}\int_{u(x)}^{v(x)} f(t)dt = f(v(x))v'(x) - f(u(x))u'(x)",
        "assumptions_conditions": "f(t) continuous on interval [u(x), v(x)]; u(x) and v(x) differentiable.",
        "limiting_cases": "If limits are constant, derivative is identically zero.",
        "common_misconceptions": "Forgetting the chain rule derivative factor v'(x) when the upper bound is a non-linear function like x^2."
    },
    {
        "concept_id": "math_vec_01",
        "subject": "Mathematics",
        "chapter": "Vectors & 3D Geometry",
        "topic": "Lines in Space",
        "title": "Shortest Distance Between Skew Lines",
        "description": "Vector projection along common perpendicular unit vector n_hat = (b1 x b2)/|b1 x b2|.",
        "prerequisites": [],
        "weightage_pct": 6.0,
        "roi_priority": "High",
        "formula_definition": r"d = \frac{|(\vec{a}_2 - \vec{a}_1) \cdot (\vec{b}_1 \times \vec{b}_2)|}{|\vec{b}_1 \times \vec{b}_2|}",
        "assumptions_conditions": "Lines are non-intersecting and non-parallel (b1 x b2 != 0).",
        "limiting_cases": "If lines intersect, d = 0 (scalar triple product vanishes).",
        "common_misconceptions": "Using the skew line formula for parallel lines (where b1 x b2 = 0 leads to division by zero; use parallel line formula instead)."
    }
]

def init_concept_graph():
    """Initializes the concept nodes and default mastery states in DB."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM concept_nodes")
    count = cursor.fetchone()[0]

    if count == 0:
        for c in CORE_CONCEPT_GRAPH:
            cursor.execute("""
            INSERT INTO concept_nodes 
            (concept_id, subject, chapter, topic, title, description, prerequisites, weightage_pct, roi_priority, formula_definition, assumptions_conditions, limiting_cases, common_misconceptions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                c["concept_id"],
                c["subject"],
                c["chapter"],
                c["topic"],
                c["title"],
                c["description"],
                json.dumps(c["prerequisites"]),
                c["weightage_pct"],
                c["roi_priority"],
                c["formula_definition"],
                c["assumptions_conditions"],
                c["limiting_cases"],
                c["common_misconceptions"]
            ))

            # Initialize mastery state
            cursor.execute("""
            INSERT OR IGNORE INTO mastery_states
            (concept_id, subject, chapter, understand_score, recall_score, apply_score, exam_transfer_score, retain_score, integrate_score, state, decay_risk_pct, confidence_calibration_pct)
            VALUES (?, ?, ?, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 'Introduced', 10.0, 100.0)
            """, (c["concept_id"], c["subject"], c["chapter"]))

        conn.commit()
    conn.close()

def get_concept_graph(subject=None):
    """Returns all concepts with hierarchy, prerequisites, and mastery states."""
    init_concept_graph()
    conn = get_db()
    cursor = conn.cursor()

    if subject:
        cursor.execute("""
        SELECT c.concept_id, c.subject, c.chapter, c.topic, c.title, c.description, c.prerequisites, c.weightage_pct, c.roi_priority,
               c.formula_definition, c.assumptions_conditions, c.limiting_cases, c.common_misconceptions,
               COALESCE(m.understand_score, 0) as understand_score,
               COALESCE(m.recall_score, 0) as recall_score,
               COALESCE(m.apply_score, 0) as apply_score,
               COALESCE(m.exam_transfer_score, 0) as exam_transfer_score,
               COALESCE(m.retain_score, 0) as retain_score,
               COALESCE(m.integrate_score, 0) as integrate_score,
               COALESCE(m.state, 'Introduced') as mastery_state,
               COALESCE(m.decay_risk_pct, 0) as decay_risk_pct,
               COALESCE(m.confidence_calibration_pct, 100) as confidence_calibration_pct
        FROM concept_nodes c
        LEFT JOIN mastery_states m ON c.concept_id = m.concept_id
        WHERE c.subject = ?
        ORDER BY c.subject, c.chapter, c.id
        """, (subject,))
    else:
        cursor.execute("""
        SELECT c.concept_id, c.subject, c.chapter, c.topic, c.title, c.description, c.prerequisites, c.weightage_pct, c.roi_priority,
               c.formula_definition, c.assumptions_conditions, c.limiting_cases, c.common_misconceptions,
               COALESCE(m.understand_score, 0) as understand_score,
               COALESCE(m.recall_score, 0) as recall_score,
               COALESCE(m.apply_score, 0) as apply_score,
               COALESCE(m.exam_transfer_score, 0) as exam_transfer_score,
               COALESCE(m.retain_score, 0) as retain_score,
               COALESCE(m.integrate_score, 0) as integrate_score,
               COALESCE(m.state, 'Introduced') as mastery_state,
               COALESCE(m.decay_risk_pct, 0) as decay_risk_pct,
               COALESCE(m.confidence_calibration_pct, 100) as confidence_calibration_pct
        FROM concept_nodes c
        LEFT JOIN mastery_states m ON c.concept_id = m.concept_id
        ORDER BY c.subject, c.chapter, c.id
        """)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        d = dict(r)
        if d.get("prerequisites") and isinstance(d["prerequisites"], str):
            try:
                d["prerequisites"] = json.loads(d["prerequisites"])
            except Exception:
                d["prerequisites"] = []
        result.append(d)
    return result

def get_concept_details(concept_id: str):
    """Returns single concept details with mastery scores and prerequisites."""
    init_concept_graph()
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT c.concept_id, c.subject, c.chapter, c.topic, c.title, c.description, c.prerequisites, c.weightage_pct, c.roi_priority,
           c.formula_definition, c.assumptions_conditions, c.limiting_cases, c.common_misconceptions,
           COALESCE(m.understand_score, 0) as understand_score,
           COALESCE(m.recall_score, 0) as recall_score,
           COALESCE(m.apply_score, 0) as apply_score,
           COALESCE(m.exam_transfer_score, 0) as exam_transfer_score,
           COALESCE(m.retain_score, 0) as retain_score,
           COALESCE(m.integrate_score, 0) as integrate_score,
           COALESCE(m.state, 'Introduced') as mastery_state,
           COALESCE(m.decay_risk_pct, 0) as decay_risk_pct,
           COALESCE(m.confidence_calibration_pct, 100) as confidence_calibration_pct
    FROM concept_nodes c
    LEFT JOIN mastery_states m ON c.concept_id = m.concept_id
    WHERE c.concept_id = ?
    """, (concept_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None
    d = dict(row)
    if d.get("prerequisites") and isinstance(d["prerequisites"], str):
        try:
            d["prerequisites"] = json.loads(d["prerequisites"])
        except Exception:
            d["prerequisites"] = []
    return d

def trace_prerequisites(concept_id: str):
    """
    Traces back the prerequisite chain for a given concept.
    Returns the root dependencies required before mastering this node.
    """
    init_concept_graph()
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT prerequisites, title, chapter, subject FROM concept_nodes WHERE concept_id = ?", (concept_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return []

    prereq_ids = json.loads(row["prerequisites"]) if row["prerequisites"] else []
    chain = []

    for pid in prereq_ids:
        cursor.execute("""
        SELECT c.concept_id, c.title, c.chapter, c.subject, m.state as mastery_state, m.understand_score, m.apply_score
        FROM concept_nodes c
        LEFT JOIN mastery_states m ON c.concept_id = m.concept_id
        WHERE c.concept_id = ?
        """, (pid,))
        prow = cursor.fetchone()
        if prow:
            p_dict = dict(prow)
            chain.append(p_dict)
            # Recursive check
            sub_chain = trace_prerequisites(pid)
            chain.extend([sc for sc in sub_chain if sc["concept_id"] != pid])

    conn.close()
    return chain

def update_concept_mastery(concept_id: str, dimension: str, delta: float, test_type: str = "practice", confidence_stated: float = None):
    """
    Updates specific mastery dimension:
    dimension: 'understand', 'recall', 'apply', 'exam_transfer', 'retain', 'integrate'
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM mastery_states WHERE concept_id = ?", (concept_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"status": "error", "message": "Mastery state not found"}

    curr = dict(row)
    dim_col = f"{dimension}_score"
    new_score = max(0.0, min(100.0, (curr.get(dim_col) or 0.0) + delta))

    # Evaluate new state based on 6 dimensions
    understand = new_score if dimension == 'understand' else curr.get('understand_score', 0)
    recall = new_score if dimension == 'recall' else curr.get('recall_score', 0)
    apply_s = new_score if dimension == 'apply' else curr.get('apply_score', 0)
    transfer = new_score if dimension == 'exam_transfer' else curr.get('exam_transfer_score', 0)
    retain = new_score if dimension == 'retain' else curr.get('retain_score', 0)
    integrate = new_score if dimension == 'integrate' else curr.get('integrate_score', 0)

    avg_score = (understand + recall + apply_s + transfer + retain + integrate) / 6.0

    new_state = curr.get('state', 'Introduced')
    if avg_score >= 85 and retain >= 80 and transfer >= 80:
        new_state = "Exam-Ready"
    elif retain >= 75 and apply_s >= 75:
        new_state = "Retained"
    elif apply_s >= 65 and understand >= 70:
        new_state = "Provisional"
    elif understand >= 40 or recall >= 40:
        new_state = "Practising"
    else:
        new_state = "Introduced"

    # Check for decay risk: if delta was negative or test failed, mark Needs Review
    if delta < 0:
        new_state = "Needs Review"
        curr['decay_risk_pct'] = min(100.0, curr.get('decay_risk_pct', 0) + 25.0)
    else:
        curr['decay_risk_pct'] = max(0.0, curr.get('decay_risk_pct', 0) - 15.0)

    # Next review due date calculation (Spaced Repetition intervals: 1d, 3d, 7d, 21d)
    interval_days = 1
    if new_state == "Retained":
        interval_days = 21
    elif new_state == "Provisional":
        interval_days = 7
    elif new_state == "Practising":
        interval_days = 3

    next_review = (datetime.now() + timedelta(days=interval_days)).isoformat()

    # Confidence calibration tracking: if confident (e.g. 90%) but failed (delta < 0), calibration drops!
    conf_cal = curr.get('confidence_calibration_pct', 100.0)
    if confidence_stated is not None:
        if delta < 0 and confidence_stated > 70:
            # Overconfident mistake!
            conf_cal = max(20.0, conf_cal - 15.0)
        elif delta > 0 and confidence_stated > 70:
            conf_cal = min(100.0, conf_cal + 5.0)

    cursor.execute(f"""
    UPDATE mastery_states
    SET {dim_col} = ?,
        state = ?,
        last_tested = CURRENT_TIMESTAMP,
        next_review_due = ?,
        decay_risk_pct = ?,
        confidence_calibration_pct = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE concept_id = ?
    """, (new_score, new_state, next_review, curr['decay_risk_pct'], conf_cal, concept_id))

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "concept_id": concept_id,
        "dimension": dimension,
        "new_score": new_score,
        "new_state": new_state,
        "next_review_due": next_review,
        "decay_risk_pct": curr['decay_risk_pct'],
        "confidence_calibration": conf_cal
    }

def detect_invisible_weaknesses():
    """
    Hidden Gap Scanner:
    Finds concepts where confidence calibration is low, decay risk is high,
    or prerequisites have failed while current node appears Practising.
    """
    init_concept_graph()
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT c.concept_id, c.title, c.chapter, c.subject, c.prerequisites,
           m.state, m.decay_risk_pct, m.confidence_calibration_pct, m.understand_score, m.apply_score, m.retain_score
    FROM concept_nodes c
    JOIN mastery_states m ON c.concept_id = m.concept_id
    WHERE m.decay_risk_pct > 30 OR m.confidence_calibration_pct < 70 OR m.state = 'Needs Review'
    ORDER BY m.decay_risk_pct DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    gaps = []
    for r in rows:
        d = dict(r)
        reason = []
        if d["confidence_calibration_pct"] < 70:
            reason.append("Overconfidence Trap: High self-rating but frequent application failure")
        if d["decay_risk_pct"] > 40:
            reason.append("Forgetting Decay: Long gap since last verified recall check")
        if d["state"] == "Needs Review":
            reason.append("Recent Test Deficit: Failed in recent mock or active recall drill")
        
        d["gap_reason"] = " | ".join(reason) if reason else "General Knowledge Gap"
        gaps.append(d)

    return gaps
