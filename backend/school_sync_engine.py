"""
School & 12th Board Synergy Engine
Tracks upcoming school tests, pre-boards, board practicals, and analyzes
subjective answer-writing gaps to guarantee a 95%+ score in CBSE Class 12 Boards.
"""

from .database import get_db
from .llm_service import call_llm
import json

CBSE_HIGH_YIELD_CHECKLIST = {
    "Physics": [
        {"topic": "Wave Optics", "item": "Derivation of Huygens wave theory (Reflection & Refraction proofs)", "frequency": "Very High"},
        {"topic": "Ray Optics", "item": "Lens Maker Formula derivation & Compound Microscope ray diagram", "frequency": "Guaranteed 5-mark"},
        {"topic": "Current Electricity", "item": "Drift velocity derivation $v_d = -eE\\tau/m$ & Kirchhoff's Rules problem", "frequency": "High"},
        {"topic": "Electromagnetic Induction", "item": "AC Generator principle, diagram & derivation of $e = e_0\\sin\\omega t$", "frequency": "Very High"},
        {"topic": "Modern Physics", "item": "Einstein's Photoelectric equation explanation & graphs ($V_0$ vs $\\nu$)", "frequency": "Guaranteed 3-mark"}
    ],
    "Chemistry": [
        {"topic": "Organic Mechanisms", "item": "Nucleophilic addition mechanism in Aldehydes (Aldol, Cannizzaro, Clemmensen)", "frequency": "Guaranteed"},
        {"topic": "Coordination Compounds", "item": "VBT hybridization steps & CFT orbital splitting diagrams ($t_{2g}$ / $e_g$)", "frequency": "Guaranteed 4-mark"},
        {"topic": "Electrochemistry", "item": "Nernst equation numerical step presentation & Kohlrausch's law definition", "frequency": "Very High"},
        {"topic": "d and f Block", "item": "Reasoning questions on lanthanoid contraction & catalytic properties", "frequency": "Guaranteed 3-mark"},
        {"topic": "Biomolecules", "item": "Peptide linkage, denaturation of proteins & DNA/RNA structural differences", "frequency": "High"}
    ],
    "Mathematics": [
        {"topic": "3D Geometry", "item": "Vector & Cartesian equations of shortest distance between skew lines", "frequency": "Guaranteed 5-mark"},
        {"topic": "Definite Integrals", "item": "Proof of property $\\int_0^a f(x)dx = \\int_0^a f(a-x)dx$ & trigonometric evaluations", "frequency": "Guaranteed 5-mark"},
        {"topic": "Differential Equations", "item": "Homogeneous differential equations & Linear differential equation with IF", "frequency": "High"},
        {"topic": "Matrices & Determinants", "item": "Solving system of 3 linear equations using Matrix Inversion method", "frequency": "Guaranteed 5-mark"},
        {"topic": "Probability", "item": "Bayes' Theorem word problems with clear event definition statements", "frequency": "Guaranteed 5-mark"}
    ]
}

def get_upcoming_school_tests():
    """Fetches all upcoming school and pre-board tests."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM school_tests WHERE status = 'upcoming' ORDER BY test_date ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_school_tests():
    """Fetches all school tests including completed ones."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM school_tests ORDER BY test_date ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_school_test(title, test_type, subject, syllabus, test_date, total_marks=70):
    """Registers a new upcoming school test."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO school_tests (test_title, test_type, subject, syllabus, test_date, total_marks, status)
    VALUES (?, ?, ?, ?, ?, ?, 'upcoming')
    """, (title, test_type, subject, syllabus, test_date, total_marks))
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"School test '{title}' added on {test_date}"}

def record_school_test_analysis(test_id, marks_obtained, derivation_issues, ncert_gaps):
    """
    Logs marks and analyzes subjective presentation flaws that deduct marks in Boards.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM school_tests WHERE id = ?", (test_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"error": "Test not found"}
    
    test_dict = dict(row)
    total_marks = test_dict.get("total_marks", 70)
    pct = round((marks_obtained / total_marks) * 100, 1)

    # Generate AI Action Plan for 95%+ CBSE target
    prompt = f"""
The student scored {marks_obtained}/{total_marks} ({pct}%) in 12th CBSE School Exam:
Subject: {test_dict.get('subject')}
Test: {test_dict.get('test_title')}
Reported Derivation Flaws: {derivation_issues}
Reported NCERT Gaps: {ncert_gaps}

Generate a concise 3-point surgical action plan to ensure they achieve 95%+ in CBSE Boards without interrupting their JEE Advanced AIR-1 trajectory. Focus on presentation, step-marking, and NCERT keywords.
"""
    ai_plan = call_llm([{"role": "user", "content": prompt}], temperature=0.4)
    if not ai_plan:
        ai_plan = (
            f"1. **Step-Marking Rigor:** In {test_dict.get('subject')}, write initial formula and unit definitions before substituting values to secure full board marks.\n"
            f"2. **NCERT Verbatim Practice:** Spend 30 minutes twice a week reproducing key derivations by hand.\n"
            f"3. **Board Presentation Sheet:** Use sharp pencils for diagrams and highlight final answers in boxed rectangles."
        )

    cursor.execute("""
    UPDATE school_tests 
    SET marks_obtained = ?, status = 'completed', derivation_issues = ?, ncert_gaps = ?, action_plan = ?
    WHERE id = ?
    """, (marks_obtained, derivation_issues, ncert_gaps, ai_plan, test_id))
    conn.commit()
    conn.close()

    return {
        "status": "success",
        "marks_obtained": marks_obtained,
        "percentage": pct,
        "action_plan": ai_plan
    }

def get_cbse_board_high_yield(subject=None):
    """Returns high-frequency derivation & theory checklists for 95%+ CBSE score."""
    if subject and subject in CBSE_HIGH_YIELD_CHECKLIST:
        return {subject: CBSE_HIGH_YIELD_CHECKLIST[subject]}
    return CBSE_HIGH_YIELD_CHECKLIST
