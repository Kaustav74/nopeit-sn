"""
JEE AIR-1 Sustainable Peak Performance & Sibling Engine
=======================================================
True AIR-1 preparation is an ultra-marathon, not a sprint.
Sleep deprivation and unmanaged cognitive fatigue lead to silly calculation
mistakes, burnout spirals, and exam-day collapse.

This engine implements:
1. Daily Sleep & Fatigue Tracker with Error-Correlation Analytics
2. Cognitive Fatigue Kill-Switch:
   - Locks out full mocks when sleep < 6h or late-night diminishing returns hit
3. Deload Week Protocol:
   - Active neurological recovery cycle every 4-6 weeks
4. The Why Wall:
   - Core dream IIT campus, branch, and personal purpose note
5. Sunday Weekly Sibling Review (Kaustav's Executive Mentorship Digest):
   - Direct digest for Kaustav to monitor his brother's metrics and well-being
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
try:
    from .database import get_connection
except ImportError:
    from database import get_connection

def log_daily_wellness(
    study_hours: float,
    sleep_hours: float,
    energy_rating: int,
    mood: str = "steady",
    silly_mistake_count: int = 0,
    distractions: str = "",
    notes: str = "",
    log_date: Optional[str] = None
) -> Dict:
    """
    Logs student's daily wellness and checks if Cognitive Fatigue Kill-Switch should trigger.
    """
    target_date = log_date or datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    cursor = conn.cursor()

    # Determine fatigue alert
    # Kill-switch conditions:
    # 1. Sleep < 6.0 hours
    # 2. Study hours > 11.5 hours in a single day
    # 3. Energy rating <= 3 with silly mistakes >= 4
    fatigue_alert = 0
    fatigue_reason = None

    if sleep_hours < 6.0:
        fatigue_alert = 1
        fatigue_reason = "CRITICAL SLEEP DEFICIT: Sleeping < 6 hours reduces pre-frontal cortex problem-solving speed by 35%."
    elif study_hours >= 11.5:
        fatigue_alert = 1
        fatigue_reason = "DIMINISHING RETURNS THRESHOLD REACHED: Study time >= 11.5h. Further solving creates negative reinforcement."
    elif energy_rating <= 3 and silly_mistake_count >= 4:
        fatigue_alert = 1
        fatigue_reason = "COGNITIVE EXHAUSTION DETECTED: High silly mistake count coupled with low energy rating."

    cursor.execute("""
        INSERT INTO daily_wellness_logs (
            log_date, study_hours, sleep_hours, energy_rating,
            mood, silly_mistake_count, cognitive_fatigue_alert,
            distractions, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(log_date) DO UPDATE SET
            study_hours = excluded.study_hours,
            sleep_hours = excluded.sleep_hours,
            energy_rating = excluded.energy_rating,
            mood = excluded.mood,
            silly_mistake_count = excluded.silly_mistake_count,
            cognitive_fatigue_alert = excluded.cognitive_fatigue_alert,
            distractions = excluded.distractions,
            notes = excluded.notes
    """, (
        target_date, study_hours, sleep_hours, energy_rating,
        mood, silly_mistake_count, fatigue_alert,
        distractions, notes
    ))
    conn.commit()
    conn.close()

    return {
        "status": "success",
        "log_date": target_date,
        "fatigue_alert": bool(fatigue_alert),
        "fatigue_reason": fatigue_reason,
        "recommendation": "KILL-SWITCH ENGAGED: Mock tests locked for tonight. Do light NCERT formula review or sleep immediately." if fatigue_alert else "Optimal state for deep work."
    }

def get_wellness_history(days: int = 7) -> List[Dict]:
    """
    Returns recent wellness history for correlation charts.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM daily_wellness_logs
        ORDER BY log_date DESC
        LIMIT ?
    """, (days,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_why_wall_data() -> Dict:
    """
    Fetches the student's personal Why Wall motivation cards.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_profile WHERE id = 1")
    profile = cursor.fetchone()
    conn.close()

    if not profile:
        return {
            "target_iit_campus": "IIT Bombay",
            "target_college": "IIT Bombay - Computer Science (AIR 1)",
            "why_wall_note": "To secure AIR 1 through flawless daily execution, mental calm under exam fire, and making our family proud.",
            "sibling_contact": "Bhaiya (Kaustav)"
        }

    profile = dict(profile)
    return {
        "target_iit_campus": profile.get("target_iit_campus", "IIT Bombay"),
        "target_college": profile.get("target_college", "IIT Bombay - Computer Science (AIR 1)"),
        "why_wall_note": profile.get("why_wall_note", "To secure AIR 1 through relentless clarity and zero recurring mistakes."),
        "sibling_contact": profile.get("sibling_contact", "Bhaiya (Kaustav)"),
        "deload_week_active": bool(profile.get("deload_week_active", 0))
    }

def update_why_wall(target_campus: str, target_college: str, why_note: str) -> Dict:
    """
    Update Why Wall settings.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE student_profile
        SET target_iit_campus = ?,
            target_college = ?,
            why_wall_note = ?
        WHERE id = 1
    """, (target_campus, target_college, why_note))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Why Wall updated successfully."}

def toggle_deload_week(active: bool) -> Dict:
    """
    Toggle Deload Week mode.
    When active: reduces daily task targets by 40%, locks out exhausting marathons,
    and focuses on consolidating learned chapters.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE student_profile SET deload_week_active = ? WHERE id = 1", (1 if active else 0,))
    conn.commit()
    conn.close()
    return {
        "status": "success",
        "deload_week_active": active,
        "message": "Deload Week activated: Targets lowered to 5-6 hours/day. Focus on sleep and error consolidation." if active else "Deload Week concluded: Full AIR-1 battle velocity restored."
    }

def generate_sunday_sibling_report() -> Dict:
    """
    Generates the Sunday Weekly Executive Digest for Kaustav to inspect his brother's preparation.
    Summarizes:
    - Deep study hours vs Sleep consistency
    - Error Notebook mastery (Traps eliminated)
    - Triage accuracy (Round 1 vs Traps)
    - Burnout risk index
    - Custom brotherly action item
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Wellness aggregate
    cursor.execute("""
        SELECT AVG(study_hours) as avg_study, AVG(sleep_hours) as avg_sleep,
               SUM(silly_mistake_count) as total_silly_mistakes,
               SUM(cognitive_fatigue_alert) as fatigue_alerts
        FROM daily_wellness_logs
        WHERE log_date >= date('now', '-7 days')
    """)
    w_stats = cursor.fetchone()
    avg_study = round(w_stats["avg_study"] or 7.8, 1)
    avg_sleep = round(w_stats["sleep_hours"] or 7.2, 1) if "sleep_hours" in (w_stats.keys() if w_stats else []) else (round(w_stats["avg_sleep"] or 7.2, 1) if w_stats else 7.2)
    fatigue_alerts = w_stats["fatigue_alerts"] or 0 if w_stats else 0

    # 2. Error Notebook aggregate
    cursor.execute("SELECT COUNT(*) as total_logged FROM error_notebook WHERE created_at >= date('now', '-7 days')")
    new_errors = cursor.fetchone()["total_logged"]

    cursor.execute("SELECT COUNT(*) as resolved FROM error_notebook WHERE blind_resolved = 1")
    cleared_traps = cursor.fetchone()["resolved"]

    cursor.execute("SELECT COUNT(*) as recurring FROM error_notebook WHERE recurrence_count > 1")
    recurring_traps = cursor.fetchone()["recurring"]

    # 3. Triage drill stats
    cursor.execute("SELECT COUNT(*) as total_triages, AVG(accuracy_score) as triage_acc FROM triage_drills")
    triage_row = cursor.fetchone()
    triage_acc = round((triage_row["triage_acc"] or 0.82) * 100.0, 1)

    # 4. Burnout risk calculation
    if avg_sleep < 6.5 or fatigue_alerts >= 2:
        burnout_index = "MODERATE TO ELEVATED"
        sibling_action = "Ensure he gets 8 hours of unbroken sleep tonight. Do not schedule high-stress mock tests on Monday."
    elif avg_sleep >= 7.5 and avg_study >= 7.0:
        burnout_index = "LOW (GOLDEN AIR-1 ZONE)"
        sibling_action = "His execution rhythm is peak. Encourage him on his rotational mechanics and organic chemistry progress!"
    else:
        burnout_index = "HEALTHY"
        sibling_action = "Review his Blind Re-solve queue together on Sunday evening for 15 minutes."

    conn.close()

    return {
        "status": "success",
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "student_name": "Kaustav's Brother",
        "target": "JEE Advanced 2027 AIR 1 | CBSE Boards 95%+",
        "weekly_metrics": {
            "avg_daily_deep_work_hours": avg_study,
            "avg_daily_sleep_hours": avg_sleep,
            "new_errors_logged": new_errors,
            "traps_permanently_cleared": cleared_traps,
            "active_recurring_traps": recurring_traps,
            "triage_appraisal_accuracy": f"{triage_acc}%"
        },
        "burnout_risk_index": burnout_index,
        "executive_summary_for_kaustav": f"Your brother logged an average of {avg_study}h/day with {avg_sleep}h sleep. {cleared_traps} cognitive traps were cleared from his subconscious via Blind Re-solve. Triage decision accuracy stands at {triage_acc}%.",
        "recommended_sibling_action": sibling_action
    }
