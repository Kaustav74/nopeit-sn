"""
Database models and storage engine for JEE Advanced AIR-1 App
Uses SQLite with optimized JSON support for rich analytics, test results, and schedules.
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "jee_air1.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

get_connection = get_db

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()

    # 1. Student Profile
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT DEFAULT 'AIR-1 Aspirant',
        grade TEXT DEFAULT '11th',
        target_year INTEGER DEFAULT 2027,
        target_jee_rank INTEGER DEFAULT 1,
        target_board_pct REAL DEFAULT 96.0,
        school_name TEXT DEFAULT '',
        coaching_institute TEXT DEFAULT '',
        test_series_enrolled TEXT DEFAULT '["Testbook JEE Test Series", "Allen Leader", "MathonGo Mock Series"]',
        xp INTEGER DEFAULT 0,
        streak_days INTEGER DEFAULT 0,
        mental_fortitude_rating REAL DEFAULT 9.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM student_profile")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO student_profile (id, name, grade, target_year, target_jee_rank, target_board_pct, school_name, coaching_institute, test_series_enrolled, xp, streak_days, mental_fortitude_rating)
        VALUES (1, 'Kaustav''s Brother', '12th', 2027, 1, 98.0, 'Delhi Public School', 'Self-Study + Test Series', '["Testbook JEE Test Series", "Allen Leader", "MathonGo Mock Series"]', 120, 1, 9.2)
        """)


    # 2. Diagnostic Evaluations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS diagnostic_evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT UNIQUE,
        total_score REAL,
        max_score REAL,
        physics_score REAL,
        chemistry_score REAL,
        maths_score REAL,
        weak_topics TEXT, -- JSON array of topics lagging
        strong_topics TEXT, -- JSON array
        error_distribution TEXT, -- JSON { "conceptual": 40, "calculation": 30, "time_panic": 20, "misread": 10 }
        board_vs_jee_gap TEXT, -- JSON analysis
        ai_recommendation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 3. School Tests & 12th Board Tracker
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS school_tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_title TEXT NOT NULL,
        test_type TEXT DEFAULT 'Unit Test', -- 'Unit Test', 'Pre-Board 1', 'Pre-Board 2', 'Half-Yearly', 'Board Practical', 'Final Board'
        subject TEXT NOT NULL,
        syllabus TEXT,
        test_date TEXT NOT NULL,
        total_marks REAL DEFAULT 70,
        marks_obtained REAL,
        status TEXT DEFAULT 'upcoming', -- 'upcoming', 'completed'
        derivation_issues TEXT,
        ncert_gaps TEXT,
        action_plan TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 4. Test Series Registry (Scheduled & On-Demand)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_series_registry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        series_name TEXT NOT NULL,
        exam_type TEXT DEFAULT 'JEE Advanced', -- 'JEE Main', 'JEE Advanced', '12th Board'
        test_number TEXT NOT NULL,
        test_title TEXT DEFAULT '',
        scheduled_date TEXT,
        scheduled_time TEXT DEFAULT '09:00 - 12:00',
        syllabus TEXT,
        status TEXT DEFAULT 'pending', -- 'pending', 'attempted', 'skipped'
        score REAL,
        total_marks REAL,
        rank_estimate INTEGER,
        percentile REAL,
        notes TEXT,
        is_ai_scheduled INTEGER DEFAULT 0,
        target_year INTEGER DEFAULT 2027,
        source_filename TEXT,
        ai_autopsy TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Ensure dynamic columns exist if table was already created
    cursor.execute("PRAGMA table_info(test_series_registry)")
    cols = [c[1] for c in cursor.fetchall()]
    new_cols = [
        ("test_title", "TEXT DEFAULT ''"),
        ("syllabus", "TEXT"),
        ("is_ai_scheduled", "INTEGER DEFAULT 0"),
        ("target_year", "INTEGER DEFAULT 2027"),
        ("source_filename", "TEXT"),
        ("ai_autopsy", "TEXT")
    ]
    for col_name, col_def in new_cols:
        if col_name not in cols:
            cursor.execute(f"ALTER TABLE test_series_registry ADD COLUMN {col_name} {col_def}")

    # 5. Mock Attempts (In-App Simulator)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mock_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attempt_id TEXT UNIQUE,
        mock_id TEXT NOT NULL,
        mock_title TEXT NOT NULL,
        exam_type TEXT NOT NULL,
        total_score REAL,
        max_marks REAL,
        physics_score REAL,
        chemistry_score REAL,
        maths_score REAL,
        time_taken_seconds INTEGER,
        accuracy_pct REAL,
        response_data TEXT, -- Full question response JSON
        ai_autopsy TEXT, -- Post test autopsy insights
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 6. SoloLearn Micro-Learning Progress
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sololearn_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        module_id TEXT NOT NULL,
        subject TEXT NOT NULL,
        topic TEXT NOT NULL,
        card_index INTEGER DEFAULT 0,
        total_cards INTEGER DEFAULT 1,
        questions_solved INTEGER DEFAULT 0,
        accuracy_rate REAL DEFAULT 100.0,
        status TEXT DEFAULT 'in_progress', -- 'in_progress', 'completed'
        last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 7. Calendar Events (Study Planner & Google Calendar sync)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS calendar_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        event_type TEXT NOT NULL, -- 'school_test', 'mock_exam', 'sololearn_drill', 'deep_work', 'revision'
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        description TEXT,
        google_cal_synced INTEGER DEFAULT 0,
        completed INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 8. AI Mentor Chat History & Mental Fortitude Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mentor_chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL, -- 'user', 'assistant'
        content TEXT NOT NULL,
        mood_tag TEXT, -- 'anxious', 'determined', 'burnout', 'confident', 'curious'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 9. Daily AIR-1 Goals & Diagnostic-Calibrated Missions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goal_date TEXT NOT NULL, -- YYYY-MM-DD
        goal_type TEXT NOT NULL, -- 'weakness_remedy', 'active_recall', 'cbse_derivation', 'mental_fortitude'
        title TEXT NOT NULL,
        description TEXT,
        subject TEXT, -- 'Physics', 'Chemistry', 'Mathematics', 'Mindset'
        linked_topic TEXT,
        notes_key TEXT,
        action_type TEXT DEFAULT 'notes', -- 'notes', 'sololearn', 'derivation', 'mentor', 'diagnostic'
        action_payload TEXT,
        status TEXT DEFAULT 'pending', -- 'pending', 'completed'
        xp_reward INTEGER DEFAULT 50,
        completed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 10. Concept Dependency Graph & Syllabus Hierarchy
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS concept_nodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        concept_id TEXT UNIQUE NOT NULL,
        subject TEXT NOT NULL,
        chapter TEXT NOT NULL,
        topic TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        prerequisites TEXT, -- JSON array of concept_ids
        weightage_pct REAL DEFAULT 5.0,
        roi_priority TEXT DEFAULT 'Medium', -- 'High', 'Medium', 'Low'
        formula_definition TEXT,
        assumptions_conditions TEXT,
        limiting_cases TEXT,
        common_misconceptions TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 11. Multi-Dimensional 6-Stage Mastery Engine
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mastery_states (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        concept_id TEXT UNIQUE NOT NULL,
        subject TEXT NOT NULL,
        chapter TEXT NOT NULL,
        understand_score REAL DEFAULT 0.0,
        recall_score REAL DEFAULT 0.0,
        apply_score REAL DEFAULT 0.0,
        exam_transfer_score REAL DEFAULT 0.0,
        retain_score REAL DEFAULT 0.0,
        integrate_score REAL DEFAULT 0.0,
        state TEXT DEFAULT 'Introduced', -- 'Introduced', 'Practising', 'Provisional', 'Retained', 'Exam-Ready', 'Needs Review'
        last_tested TIMESTAMP,
        next_review_due TIMESTAMP,
        decay_risk_pct REAL DEFAULT 0.0,
        confidence_calibration_pct REAL DEFAULT 100.0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 12. Trigger Line Error Notebook & Mistake Recurrence Engine
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS error_notebook (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id TEXT,
        question_title TEXT NOT NULL,
        subject TEXT NOT NULL,
        chapter TEXT NOT NULL,
        concept_id TEXT,
        exam_type TEXT DEFAULT 'JEE Advanced',
        error_category TEXT NOT NULL, -- 'Conceptual Deficit', 'Calculation Error', 'Misread Question', 'Formula Slip', 'Time Panic', 'Strategy Error'
        wrong_thinking TEXT NOT NULL,
        correct_logic TEXT NOT NULL,
        trigger_line TEXT NOT NULL,
        blind_resolve_due TEXT, -- YYYY-MM-DD
        blind_resolved INTEGER DEFAULT 0,
        recurrence_count INTEGER DEFAULT 1,
        source_test_title TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 13. Omni-Planner Solved Tasks
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scheduled_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_date TEXT NOT NULL,
        task_type TEXT NOT NULL, -- 'new_learn', 'problem_practice', 'error_correction', 'scheduled_revision', 'test_prep', 'cbse_derivation', 'rest_recovery'
        title TEXT NOT NULL,
        duration_minutes INTEGER DEFAULT 30,
        subject TEXT,
        concept_id TEXT,
        priority INTEGER DEFAULT 3,
        deadline_date TEXT,
        status TEXT DEFAULT 'pending', -- 'pending', 'completed', 'missed', 're_scheduled'
        exam_track TEXT DEFAULT 'JEE Advanced', -- 'JEE Main', 'JEE Advanced', 'CBSE Boards', 'Tuition', 'School'
        completed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 14. Sustainable Performance & Daily Wellness Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_wellness_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date TEXT UNIQUE NOT NULL,
        study_hours REAL DEFAULT 0.0,
        sleep_hours REAL DEFAULT 7.5,
        energy_rating INTEGER DEFAULT 8,
        mood TEXT DEFAULT 'steady', -- 'drained', 'steady', 'sharp', 'unstoppable'
        silly_mistake_count INTEGER DEFAULT 0,
        cognitive_fatigue_alert INTEGER DEFAULT 0,
        distractions TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 15. Question Triage & Tactical Drills
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS triage_drills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_title TEXT NOT NULL,
        subject TEXT NOT NULL,
        topic TEXT NOT NULL,
        chosen_round INTEGER NOT NULL, -- 1 (Immediate <2.5m), 2 (Heavy Calc 3-6m), 3 (Trap/Skip)
        correct_round INTEGER NOT NULL,
        time_taken_seconds INTEGER DEFAULT 30,
        accuracy_score REAL DEFAULT 0.0,
        feedback TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 16. CBSE Board Step-Loss & Rubric Evaluator
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cbse_answer_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        derivation_key TEXT NOT NULL,
        subject TEXT NOT NULL,
        title TEXT NOT NULL,
        submitted_steps TEXT, -- JSON
        max_marks REAL DEFAULT 5.0,
        marks_awarded REAL DEFAULT 5.0,
        rubric_feedback TEXT, -- JSON
        missing_elements TEXT, -- JSON array
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 17. Ensure student_profile has personal cockpit fields
    cursor.execute("PRAGMA table_info(student_profile)")
    prof_cols = [c[1] for c in cursor.fetchall()]
    profile_new_cols = [
        ("target_college", "TEXT DEFAULT 'IIT Bombay - Computer Science'"),
        ("target_iit_campus", "TEXT DEFAULT 'IIT Bombay'"),
        ("why_wall_note", "TEXT DEFAULT 'To secure AIR 1 through flawless daily execution and zero recurring mistakes.'"),
        ("sibling_contact", "TEXT DEFAULT 'Bhaiya (Kaustav)'"),
        ("focus_mode_active", "INTEGER DEFAULT 0"),
        ("deload_week_active", "INTEGER DEFAULT 0"),
        ("streak_freezes_left", "INTEGER DEFAULT 2")
    ]
    for col_name, col_def in profile_new_cols:
        if col_name not in prof_cols:
            cursor.execute(f"ALTER TABLE student_profile ADD COLUMN {col_name} {col_def}")

    # Tables are ready for authentic student onboarding and data.
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized with clean schema at:", DB_PATH)
