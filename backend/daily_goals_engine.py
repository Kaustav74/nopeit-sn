"""
Daily AIR-1 Goal Engine
Calibrated to the student's authentic Diagnostic Test results,
CBSE 12th Board 95%+ milestones, and Kota HOD exam temperament training.
"""

import json
from datetime import datetime
from .database import get_db

HIGH_YIELD_DERIVATIONS = [
    {
        "key": "lens_maker",
        "title": "Lens Maker's Formula from Refraction at Spherical Surfaces",
        "subject": "Physics",
        "desc": "Derive 1/f = (mu - 1)(1/R1 - 1/R2) with ray diagram, Cartesian sign convention, and small aperture approximations."
    },
    {
        "key": "gauss_sphere",
        "title": "Electric Field of Non-Conducting & Conducting Spheres (Gauss's Law)",
        "subject": "Physics",
        "desc": "Integrate enclosed charge for variable density rho(r) and prove field discontinuities at boundary."
    },
    {
        "key": "skew_lines",
        "title": "Shortest Distance Between Skew Lines in 3D Space",
        "subject": "Mathematics",
        "desc": "Derive d = |(a2 - a1) . (b1 x b2)| / |b1 x b2| using orthogonal vector projections."
    },
    {
        "key": "integrated_rate",
        "title": "Integrated Rate Laws & Half-Life for 1st Order Kinetics",
        "subject": "Chemistry",
        "desc": "Derive k = (2.303/t) log([A]0/[A]) and plot log[A] vs time slope for board practicals."
    },
    {
        "key": "nernst_eq",
        "title": "Nernst Equation & Cell Potential Thermodynamics",
        "subject": "Chemistry",
        "desc": "Derive E_cell = E0_cell - (2.303RT/nF) log Q and relate with Gibbs free energy delta G = -nFE."
    }
]

def get_or_generate_daily_goals(date_str=None):
    """
    Returns today's 4 calibrated goals. If not yet created for today,
    generates them dynamically using the latest diagnostic test lags.
    """
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    conn = get_db()
    cursor = conn.cursor()

    # Check if goals already exist for this date
    cursor.execute("""
    SELECT id, goal_date, goal_type, title, description, subject, linked_topic, notes_key, action_type, action_payload, status, xp_reward, completed_at
    FROM daily_goals
    WHERE goal_date = ?
    ORDER BY id ASC
    """, (date_str,))
    rows = cursor.fetchall()

    if rows:
        goals = [dict(r) for r in rows]
        conn.close()
        return goals

    # Need to generate fresh goals based on diagnostic test
    cursor.execute("""
    SELECT weak_topics, strong_topics, error_distribution, board_vs_jee_gap, ai_recommendation
    FROM diagnostic_evaluations
    ORDER BY id DESC LIMIT 1
    """)
    diag_row = cursor.fetchone()

    weak_topics = []
    if diag_row and diag_row["weak_topics"]:
        try:
            weak_topics = json.loads(diag_row["weak_topics"])
        except Exception:
            weak_topics = []

    new_goals = []

    if weak_topics:
        # Student has completed diagnostic test and has identified lags!
        # Weak topic 1
        top_lag_raw = weak_topics[0]
        # Clean topic string e.g. "Rotational Mechanics (Physics)"
        topic_name = top_lag_raw.split("(")[0].strip() if "(" in top_lag_raw else top_lag_raw
        sub = "Physics"
        if "Chem" in top_lag_raw:
            sub = "Chemistry"
        elif "Math" in top_lag_raw:
            sub = "Mathematics"

        new_goals.append({
            "goal_type": "weakness_remedy",
            "title": f"🎯 Leak Plug: {topic_name}",
            "description": f"Master core concepts & formulas in {topic_name}. Review high-yield notes and shortcuts to eliminate your diagnostic lag.",
            "subject": sub,
            "linked_topic": topic_name,
            "notes_key": topic_name,
            "action_type": "notes",
            "action_payload": topic_name,
            "xp_reward": 50
        })

        # Weak topic 2 or next priority
        second_lag_raw = weak_topics[1] if len(weak_topics) > 1 else weak_topics[0]
        topic_2_name = second_lag_raw.split("(")[0].strip() if "(" in second_lag_raw else second_lag_raw
        sub_2 = "Chemistry" if "Chem" in second_lag_raw else ("Mathematics" if "Math" in second_lag_raw else "Physics")

        new_goals.append({
            "goal_type": "active_recall",
            "title": f"⚡ Active Recall Drill: {topic_2_name}",
            "description": f"Solve 3 precision micro-questions on {topic_2_name}. Maintain zero algebraic slips and verify all steps.",
            "subject": sub_2,
            "linked_topic": topic_2_name,
            "notes_key": topic_2_name,
            "action_type": "sololearn",
            "action_payload": "drill",
            "xp_reward": 50
        })
    else:
        # Diagnostic test not taken yet!
        new_goals.append({
            "goal_type": "weakness_remedy",
            "title": "🩺 Diagnostic Baseline: Take 12-Question Test",
            "description": "Evaluate your current mastery across Physics, Chemistry, and Mathematics to reveal exact calculation leaks and conceptual lags.",
            "subject": "All Subjects",
            "linked_topic": "Baseline Diagnostic",
            "notes_key": "Diagnostic",
            "action_type": "diagnostic",
            "action_payload": "diagnostic",
            "xp_reward": 100
        })

        new_goals.append({
            "goal_type": "active_recall",
            "title": "⚡ Mechanics Precision: Rolling & Constraints",
            "description": "Master constraint relations a_p = a_c + R*alpha for rolling on moving planks. Eliminate the #1 JEE Advanced mechanics trap.",
            "subject": "Physics",
            "linked_topic": "Rotational Mechanics",
            "notes_key": "Rotational Mechanics",
            "action_type": "notes",
            "action_payload": "Rotational Mechanics",
            "xp_reward": 50
        })

    # Goal 3: CBSE 12th Board 95%+ Derivation
    day_idx = datetime.now().toordinal() % len(HIGH_YIELD_DERIVATIONS)
    deriv = HIGH_YIELD_DERIVATIONS[day_idx]
    new_goals.append({
        "goal_type": "cbse_derivation",
        "title": f"📐 12th Board Derivation: {deriv['title']}",
        "description": f"{deriv['desc']} (Write full proof on paper with neat diagram and SI units).",
        "subject": deriv["subject"],
        "linked_topic": deriv["title"],
        "notes_key": deriv["key"],
        "action_type": "derivation" if deriv["key"] in ["lens_maker", "rocket"] else "notes",
        "action_payload": deriv["key"],
        "xp_reward": 50
    })

    # Goal 4: Mental Fortitude & Exam Psychology
    fortitude_prompts = [
        ("🧠 Exam Strategy: The Kota 3-Round Sweep", "Practice Round 1 (no hesitation 60 min), Round 2 (deep synthesis 80 min), and Round 3 (tough 40 min). Never get trapped in 1 problem for >3 min."),
        ("🛡️ Negative Marking Autopsy", "Review your last mistake. Classify it strictly: Conceptual Deficit vs Calculation Panic vs Misread. Write a 1-line rule to prevent it."),
        ("🧘 Pre-Exam Psychological Priming", "Take 5 minutes of box breathing (4s in, 4s hold, 4s out, 4s hold). Remember: AIR-1 is won through steady composure under surprise questions."),
        ("⏱️ Time Allocation Discipline", "Commit to allocating max 45 min Chemistry, 60 min Physics, 75 min Mathematics on upcoming mocks to preserve energy.")
    ]
    fort_idx = datetime.now().toordinal() % len(fortitude_prompts)
    f_title, f_desc = fortitude_prompts[fort_idx]

    new_goals.append({
        "goal_type": "mental_fortitude",
        "title": f_title,
        "description": f_desc,
        "subject": "Mindset",
        "linked_topic": "Mental Fortitude",
        "notes_key": "kota_notes",
        "action_type": "mentor",
        "action_payload": "mentor",
        "xp_reward": 50
    })

    # Insert into DB
    for g in new_goals:
        cursor.execute("""
        INSERT INTO daily_goals (goal_date, goal_type, title, description, subject, linked_topic, notes_key, action_type, action_payload, status, xp_reward)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
        """, (
            date_str,
            g["goal_type"],
            g["title"],
            g["description"],
            g["subject"],
            g.get("linked_topic", ""),
            g.get("notes_key", ""),
            g.get("action_type", "notes"),
            g.get("action_payload", ""),
            g.get("xp_reward", 50)
        ))

    conn.commit()

    # Fetch inserted goals with auto IDs
    cursor.execute("""
    SELECT id, goal_date, goal_type, title, description, subject, linked_topic, notes_key, action_type, action_payload, status, xp_reward, completed_at
    FROM daily_goals
    WHERE goal_date = ?
    ORDER BY id ASC
    """, (date_str,))
    rows = cursor.fetchall()
    goals = [dict(r) for r in rows]
    conn.close()

    return goals

def complete_daily_goal(goal_id: int):
    """
    Marks a goal as completed, increments student XP, updates streak if all completed,
    and returns completion summary.
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM daily_goals WHERE id = ?", (goal_id,))
    goal = cursor.fetchone()
    if not goal:
        conn.close()
        return {"status": "error", "message": "Goal not found"}

    if goal["status"] == "completed":
        conn.close()
        return {"status": "already_completed", "message": "Goal was already marked complete"}

    now_iso = datetime.now().isoformat()
    xp_earned = goal["xp_reward"] or 50

    cursor.execute("""
    UPDATE daily_goals
    SET status = 'completed', completed_at = ?
    WHERE id = ?
    """, (now_iso, goal_id))

    # Update student profile XP
    cursor.execute("""
    UPDATE student_profile
    SET xp = COALESCE(xp, 0) + ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = 1
    """, (xp_earned,))

    # Check if all goals for today are completed
    cursor.execute("""
    SELECT COUNT(*) as total, SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as done
    FROM daily_goals
    WHERE goal_date = ?
    """, (goal["goal_date"],))
    count_row = cursor.fetchone()
    all_done = (count_row["total"] == count_row["done"])

    bonus_xp = 0
    if all_done:
        bonus_xp = 50
        cursor.execute("""
        UPDATE student_profile
        SET streak_days = COALESCE(streak_days, 0) + 1,
            xp = COALESCE(xp, 0) + ?,
            mental_fortitude_rating = MIN(10.0, COALESCE(mental_fortitude_rating, 9.0) + 0.1),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = 1
        """, (bonus_xp,))

    conn.commit()

    # Get updated profile
    cursor.execute("SELECT xp, streak_days, mental_fortitude_rating FROM student_profile WHERE id = 1")
    prof = cursor.fetchone()
    conn.close()

    return {
        "status": "success",
        "goal_id": goal_id,
        "xp_earned": xp_earned + bonus_xp,
        "all_goals_done": all_done,
        "new_profile_stats": {
            "xp": prof["xp"] if prof else xp_earned,
            "streak_days": prof["streak_days"] if prof else 1,
            "fortitude": prof["mental_fortitude_rating"] if prof else 9.1
        }
    }

def reset_and_regenerate_goals_for_today():
    """
    Clears today's goals and regenerates them to adapt to new diagnostic results.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM daily_goals WHERE goal_date = ?", (today_str,))
    conn.commit()
    conn.close()
    return get_or_generate_daily_goals(today_str)
