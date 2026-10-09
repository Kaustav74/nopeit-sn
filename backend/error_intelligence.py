"""
JEE AIR-1 Error Intelligence Engine
===================================
Implements the definitive Trigger Line autopsy system:
1. 3-Part Autopsy Micro-Form:
   - Part 1: Exactly which step did I go wrong? (Pivot Point)
   - Part 2: What false assumption did I make? (Mental Trap)
   - Part 3: What is the Trigger Line rule to never repeat it? (Actionable Law)
2. Mistake Recurrence Engine:
   - Tracks identical/similar concept slips across tests
   - Escalates recurring errors to high-priority alert
3. Blind Re-solve Gate:
   - Spaced repetition queue (+1d, +3d, +7d)
   - Requires solving from scratch without seeing original solution
4. Pre-Mock Trigger Line Deck:
   - Generates the top 20 personal high-risk trigger lines before any mock
5. Formula & Rule Decay Injector:
   - Active recall prompts for formulas at risk of memory decay
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
try:
    from .database import get_connection
except ImportError:
    from database import get_connection

ERROR_CATEGORIES = [
    "Conceptual Deficit",
    "Calculation Error",
    "Misread Question",
    "Formula Slip",
    "Time Panic",
    "Strategy Error"
]

def log_error_autopsy(
    question_title: str,
    subject: str,
    chapter: str,
    concept_id: Optional[str],
    error_category: str,
    wrong_thinking: str,
    correct_logic: str,
    trigger_line: str,
    exam_type: str = "JEE Advanced",
    source_test_title: Optional[str] = None,
    question_id: Optional[str] = None
) -> Dict:
    """
    Saves a 3-part Trigger Line autopsy and checks for repeat mistake recurrence.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Normalize category
    if error_category not in ERROR_CATEGORIES:
        error_category = "Conceptual Deficit"

    # Check for existing recurrence in same concept or same chapter with similar trigger
    cursor.execute("""
        SELECT id, recurrence_count, trigger_line FROM error_notebook
        WHERE subject = ? AND chapter = ? AND (
            (concept_id IS NOT NULL AND concept_id = ?) OR 
            (error_category = ? AND question_title = ?)
        )
    """, (subject, chapter, concept_id or "", error_category, question_title))
    existing = cursor.fetchone()

    recurrence_count = 1
    recurrence_alert = False

    if existing:
        recurrence_count = (existing["recurrence_count"] or 1) + 1
        recurrence_alert = True
        # Update existing record recurrence or create new linked entry
        cursor.execute("""
            UPDATE error_notebook
            SET recurrence_count = ?,
                blind_resolve_due = ?,
                blind_resolved = 0
            WHERE id = ?
        """, (
            recurrence_count,
            (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            existing["id"]
        ))
        inserted_id = existing["id"]
    else:
        # Schedule first blind re-solve for tomorrow (+1 day)
        blind_due = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        cursor.execute("""
            INSERT INTO error_notebook (
                question_id, question_title, subject, chapter, concept_id,
                exam_type, error_category, wrong_thinking, correct_logic,
                trigger_line, blind_resolve_due, blind_resolved, recurrence_count,
                source_test_title
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 1, ?)
        """, (
            question_id or f"ERR-{int(datetime.now().timestamp())}",
            question_title,
            subject,
            chapter,
            concept_id,
            exam_type,
            error_category,
            wrong_thinking,
            correct_logic,
            trigger_line,
            blind_due,
            source_test_title or "Self Practice"
        ))
        inserted_id = cursor.lastrowid

    # If concept_id is known, record decay or deficiency in mastery_states
    if concept_id:
        cursor.execute("""
            UPDATE mastery_states
            SET decay_risk_pct = MIN(100.0, decay_risk_pct + 25.0),
                exam_transfer_score = MAX(0.0, exam_transfer_score - 15.0),
                state = 'Needs Review'
            WHERE concept_id = ?
        """, (concept_id,))

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "error_id": inserted_id,
        "recurrence_count": recurrence_count,
        "recurrence_alert": recurrence_alert,
        "trigger_line": trigger_line,
        "blind_resolve_due": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "message": "Recurring trap detected! Escalated for immediate blind re-solve." if recurrence_alert else "Autopsy logged. Scheduled for tomorrow's Blind Re-solve Gate."
    }

def get_blind_resolve_queue(target_date: Optional[str] = None) -> List[Dict]:
    """
    Returns items currently due for blind re-solving.
    """
    conn = get_connection()
    cursor = conn.cursor()
    query_date = target_date or datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT * FROM error_notebook
        WHERE blind_resolved = 0 AND (blind_resolve_due <= ? OR blind_resolve_due IS NULL)
        ORDER BY recurrence_count DESC, id ASC
    """, (query_date,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def submit_blind_resolve(error_id: int, success: bool, student_solution: str = "") -> Dict:
    """
    Process student's attempt to re-solve an error question blindly without looking at the answer.
    If success: schedule next spaced review (+3d, then +7d, then mark master).
    If fail: reset schedule to tomorrow and increment recurrence count.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM error_notebook WHERE id = ?", (error_id,))
    err = cursor.fetchone()
    if not err:
        conn.close()
        return {"status": "error", "message": "Error record not found."}

    err = dict(err)
    rec_count = err.get("recurrence_count", 1)

    if success:
        # Spaced repetition advancement:
        # If successfully resolved 2 times, mark permanently resolved (blind_resolved = 1)
        if rec_count <= 1:
            next_due = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
            cursor.execute("""
                UPDATE error_notebook
                SET blind_resolve_due = ?, blind_resolved = 0, recurrence_count = 1
                WHERE id = ?
            """, (next_due, error_id))
            status_msg = "Passed Stage 1! Next blind check scheduled in 3 days."
        else:
            # Fully mastered
            cursor.execute("""
                UPDATE error_notebook
                SET blind_resolved = 1, blind_resolve_due = NULL
                WHERE id = ?
            """, (error_id,))
            status_msg = "CLEARED! You have eliminated this trap from your subconscious."
    else:
        # Failed re-solve
        next_due = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        cursor.execute("""
            UPDATE error_notebook
            SET recurrence_count = recurrence_count + 1,
                blind_resolve_due = ?,
                blind_resolved = 0
            WHERE id = ?
        """, (next_due, error_id))
        status_msg = "Trap caught you again! Re-analyzed and re-queued for tomorrow."

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "resolved": success,
        "message": status_msg
    }

def get_pre_mock_trigger_deck(syllabus_chapters: Optional[List[str]] = None, limit: int = 20) -> List[Dict]:
    """
    Generates the top Trigger Lines to review 30-60 minutes before a mock test.
    This primes the student's brain to avoid known cognitive pitfalls during exam conditions.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if syllabus_chapters and len(syllabus_chapters) > 0:
        placeholders = ",".join("?" for _ in syllabus_chapters)
        cursor.execute(f"""
            SELECT id, question_title, subject, chapter, error_category, trigger_line, recurrence_count
            FROM error_notebook
            WHERE chapter IN ({placeholders})
            ORDER BY recurrence_count DESC, id DESC
            LIMIT ?
        """, (*syllabus_chapters, limit))
    else:
        cursor.execute("""
            SELECT id, question_title, subject, chapter, error_category, trigger_line, recurrence_count
            FROM error_notebook
            ORDER BY recurrence_count DESC, id DESC
            LIMIT ?
        """, (limit,))

    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_error_analytics() -> Dict:
    """
    Comprehensive diagnostic analytics of student error patterns.
    AIR-1 is built on eliminating recurrent slips and understanding trap distributions.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Category breakdown
    cursor.execute("""
        SELECT error_category, COUNT(*) as count
        FROM error_notebook
        GROUP BY error_category
        ORDER BY count DESC
    """)
    category_counts = {r["error_category"]: r["count"] for r in cursor.fetchall()}

    # Subject breakdown
    cursor.execute("""
        SELECT subject, COUNT(*) as count
        FROM error_notebook
        GROUP BY subject
    """)
    subject_counts = {r["subject"]: r["count"] for r in cursor.fetchall()}

    # Most error-prone chapters
    cursor.execute("""
        SELECT chapter, subject, COUNT(*) as count, SUM(recurrence_count) as total_slips
        FROM error_notebook
        GROUP BY chapter, subject
        ORDER BY total_slips DESC
        LIMIT 5
    """)
    top_vulnerable_chapters = [dict(r) for r in cursor.fetchall()]

    # Total counts
    cursor.execute("SELECT COUNT(*) as total FROM error_notebook")
    total_logged = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as pending FROM error_notebook WHERE blind_resolved = 0")
    pending_resolve = cursor.fetchone()["pending"]

    cursor.execute("SELECT COUNT(*) as recurring FROM error_notebook WHERE recurrence_count > 1")
    recurring_traps = cursor.fetchone()["recurring"]

    conn.close()

    return {
        "total_errors_logged": total_logged,
        "pending_blind_resolves": pending_resolve,
        "recurring_traps_count": recurring_traps,
        "category_distribution": category_counts,
        "subject_distribution": subject_counts,
        "vulnerable_chapters": top_vulnerable_chapters
    }

def get_formula_decay_prompts(limit: int = 5) -> List[Dict]:
    """
    Injects high-yield formula active recall prompts for chapters with high decay risk.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch concepts with highest decay_risk_pct or untested for longest time
    cursor.execute("""
        SELECT cn.concept_id, cn.subject, cn.chapter, cn.title, cn.formula_definition, 
               cn.limiting_cases, cn.common_misconceptions, ms.decay_risk_pct
        FROM concept_nodes cn
        LEFT JOIN mastery_states ms ON cn.concept_id = ms.concept_id
        WHERE cn.formula_definition IS NOT NULL AND cn.formula_definition != ''
        ORDER BY COALESCE(ms.decay_risk_pct, 50.0) DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    prompts = []
    for r in rows:
        prompts.append({
            "concept_id": r["concept_id"],
            "subject": r["subject"],
            "chapter": r["chapter"],
            "title": r["title"],
            "decay_risk_pct": r.get("decay_risk_pct", 50.0),
            "prompt_question": f"State the exact formula and limiting conditions for: {r['title']}",
            "formula_definition": r["formula_definition"],
            "limiting_cases": r["limiting_cases"],
            "trap_to_avoid": r["common_misconceptions"]
        })
    return prompts
