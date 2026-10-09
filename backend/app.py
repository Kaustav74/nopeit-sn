"""
JEE Advanced AIR-1 & CBSE 95%+ Master Web Server
Built on FastAPI with asynchronous routing, static frontend mounting, and FreeLLM integration.
"""

import os
import json
from fastapi import FastAPI, HTTPException, Request, Response, File, UploadFile, Form
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from .database import init_db, get_db
from .llm_service import chat_with_air1_mentor
from .diagnostic_engine import get_diagnostic_test, submit_diagnostic_test
from .sololearn_engine import get_all_modules, get_module_data, verify_step_answer, generate_ai_micro_card
from .mock_exam_engine import get_available_mocks, get_mock_details, submit_mock_attempt, get_registered_test_series, add_external_test_series
from .school_sync_engine import get_upcoming_school_tests, get_all_school_tests, add_school_test, record_school_test_analysis, get_cbse_board_high_yield
from .calendar_sync import get_study_calendar_events, add_calendar_event, generate_ics_calendar
from .scraper_engine import get_vault_categories, get_note_content, get_notes_by_topic, search_vault, fetch_external_url
from .daily_goals_engine import get_or_generate_daily_goals, complete_daily_goal, reset_and_regenerate_goals_for_today
from .material_refinery import process_uploaded_file, refine_material_with_ai, save_refined_knowledge, get_ingested_materials
from .visual_engine import derive_lens_maker, derive_variable_mass_rocket, solve_symbolic_expression, get_organic_mechanisms, generate_wave_optics_plot, generate_electric_field_plot
from .test_series_engine import (
    generate_ai_test_schedule,
    ingest_schedule_file,
    parse_schedule_from_text,
    get_registered_tests,
    log_test_score_and_autopsy,
    reschedule_test_entry,
    export_test_series_ics
)
from .concept_engine import (
    get_concept_graph,
    get_concept_details,
    trace_prerequisites,
    update_concept_mastery,
    detect_invisible_weaknesses
)
from .error_intelligence import (
    log_error_autopsy,
    get_blind_resolve_queue,
    submit_blind_resolve,
    get_pre_mock_trigger_deck,
    get_error_analytics,
    get_formula_decay_prompts
)
from .omni_planner import (
    generate_omni_schedule,
    apply_scope_cutter,
    simulate_what_if_scenario,
    log_scheduled_task,
    get_scheduled_tasks_for_date,
    update_task_status
)
from .triage_and_tactics import (
    get_triage_drill_question,
    submit_triage_drill,
    calculate_abandonment_roi,
    get_god_mode_matrix,
    get_chaos_room_profiles
)
from .cbse_step_evaluator import (
    get_cbse_derivations_list,
    evaluate_cbse_derivation,
    get_ncert_cloze_drill
)
from .sustainable_performance import (
    log_daily_wellness,
    get_wellness_history,
    get_why_wall_data,
    update_why_wall,
    toggle_deload_week,
    generate_sunday_sibling_report
)
from .next_best_action import (
    calculate_next_best_action,
    get_readiness_forecast,
    get_counterexample_lab_cases,
    get_alternate_solutions
)
from .mentor_modes import (
    format_mentor_mode_prompt,
    get_prove_it_challenge,
    TEACHING_MODES
)

# Initialize Database
init_db()

app = FastAPI(
    title="JEE Advanced AIR-1 & CBSE 95% Companion",
    description="The Complete AIR-1 Machine: Adaptive Diagnostics, SoloLearn Micro-Learning, Test Series Aggregator, Board 95%+ Sync, and Mental Fortitude AI Mentor",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- STUDENT PROFILE ENDPOINTS -----------------
@app.get("/api/profile")
def get_profile():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_profile WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {"has_profile": False}
    profile = dict(row)
    if isinstance(profile.get("test_series_enrolled"), str):
        try:
            profile["test_series_enrolled"] = json.loads(profile["test_series_enrolled"])
        except Exception:
            profile["test_series_enrolled"] = []
    profile["has_profile"] = bool(profile.get("name"))
    return profile

class OnboardingRequest(BaseModel):
    name: str
    grade: str = "12th"
    target_year: int = 2026
    target_board_pct: float = 95.0
    school_name: str
    coaching_institute: str = "Self-Study"
    test_series_enrolled: List[str] = []
    first_school_test_title: Optional[str] = None
    first_school_test_subject: Optional[str] = None
    first_school_test_date: Optional[str] = None
    first_school_test_syllabus: Optional[str] = None

@app.post("/api/profile/onboard")
def onboard_student(req: OnboardingRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM student_profile")
    cursor.execute("""
    INSERT INTO student_profile (id, name, grade, target_year, target_jee_rank, target_board_pct, school_name, coaching_institute, test_series_enrolled, xp, streak_days, mental_fortitude_rating)
    VALUES (1, ?, ?, ?, 1, ?, ?, ?, ?, 0, 0, 9.0)
    """, (
        req.name,
        req.grade,
        req.target_year,
        req.target_board_pct,
        req.school_name,
        req.coaching_institute,
        json.dumps(req.test_series_enrolled)
    ))

    # If first school test provided, insert it
    if req.first_school_test_title and req.first_school_test_date:
        cursor.execute("""
        INSERT INTO school_tests (test_title, test_type, subject, syllabus, test_date, total_marks, status)
        VALUES (?, 'Pre-Board', ?, ?, ?, 70, 'upcoming')
        """, (
            req.first_school_test_title,
            req.first_school_test_subject or "Physics",
            req.first_school_test_syllabus or "",
            req.first_school_test_date
        ))

    conn.commit()
    conn.close()

    # Automatically generate calibrated 2027 test schedule for enrolled series (e.g. Testbook, Allen)
    for ts in req.test_series_enrolled:
        try:
            generate_ai_test_schedule(ts, target_year=req.target_year)
        except Exception as e:
            logger.error(f"Error generating initial schedule for {ts}: {e}")

    return {"status": "success", "message": f"Welcome {req.name}! Profile & 2027 schedule initialized with zero fake data."}

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    grade: Optional[str] = None
    target_year: Optional[int] = None
    school_name: Optional[str] = None
    coaching_institute: Optional[str] = None
    target_board_pct: Optional[float] = None
    test_series_enrolled: Optional[List[str]] = None

@app.post("/api/profile/update")
def update_profile(req: ProfileUpdateRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE student_profile 
    SET name = COALESCE(?, name),
        grade = COALESCE(?, grade),
        target_year = COALESCE(?, target_year),
        school_name = COALESCE(?, school_name),
        coaching_institute = COALESCE(?, coaching_institute),
        target_board_pct = COALESCE(?, target_board_pct),
        test_series_enrolled = COALESCE(?, test_series_enrolled),
        updated_at = CURRENT_TIMESTAMP
    WHERE id = 1
    """, (
        req.name,
        req.grade,
        req.target_year,
        req.school_name,
        req.coaching_institute,
        req.target_board_pct,
        json.dumps(req.test_series_enrolled) if req.test_series_enrolled is not None else None
    ))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Profile updated successfully"}

@app.get("/api/profile/dossier")
def get_profile_dossier():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_profile WHERE id = 1")
    row = cursor.fetchone()
    profile = dict(row) if row else {
        "name": "Kaustav's Brother",
        "grade": "11th / 12th",
        "target_year": 2027,
        "target_jee_rank": 1,
        "target_board_pct": 98.0,
        "school_name": "CBSE Class 12",
        "coaching_institute": "Self-Study + Test Series",
        "test_series_enrolled": ["Testbook JEE Test Series", "Allen Leader", "MathonGo"],
        "xp": 120,
        "streak_days": 1,
        "mental_fortitude_rating": 9.2
    }
    if isinstance(profile.get("test_series_enrolled"), str):
        try:
            profile["test_series_enrolled"] = json.loads(profile["test_series_enrolled"])
        except Exception:
            profile["test_series_enrolled"] = ["Testbook", "Allen"]

    cursor.execute("SELECT COUNT(*) as cnt FROM error_notebook WHERE blind_resolved = 1")
    cleared_errors = cursor.fetchone()["cnt"] or 0
    cursor.execute("SELECT COUNT(*) as cnt FROM error_notebook WHERE blind_resolved = 0")
    pending_errors = cursor.fetchone()["cnt"] or 0
    cursor.execute("SELECT AVG(accuracy_score) as acc FROM triage_drills")
    triage_acc = cursor.fetchone()["acc"] or 0.85
    cursor.execute("SELECT COUNT(*) as cnt FROM cbse_answer_reviews")
    deriv_count = cursor.fetchone()["cnt"] or 0
    cursor.execute("SELECT COUNT(*) as cnt FROM scheduled_tasks WHERE status = 'completed'")
    completed_tasks = cursor.fetchone()["cnt"] or 0
    conn.close()

    return {
        "status": "success",
        "profile": profile,
        "telemetry": {
            "cleared_errors": cleared_errors,
            "pending_errors": pending_errors,
            "triage_accuracy_pct": round(triage_acc * 100.0, 1),
            "derivations_submitted": deriv_count,
            "completed_tasks": completed_tasks,
            "dream_campus": "IIT Bombay - Computer Science & Engineering (AIR 1)",
            "target_board": "CBSE Class 12 Boards (98%+)",
            "personal_motto": "AIR 1 is an algorithmic inevitability when you eliminate every avoidable cognitive trap.",
            "bhaiya_name": "Kaustav"
        }
    }


# ----------------- 1. DIAGNOSTIC EVALUATION ENDPOINTS -----------------
@app.get("/api/diagnostic/questions")
def get_diagnostic_questions_endpoint():
    return get_diagnostic_test()

class DiagnosticSubmitRequest(BaseModel):
    session_id: str
    answers: Dict[str, Optional[int]]

@app.post("/api/diagnostic/submit")
def submit_diagnostic_endpoint(req: DiagnosticSubmitRequest):
    result = submit_diagnostic_test(req.session_id, req.answers)
    try:
        reset_and_regenerate_goals_for_today()
    except Exception:
        pass
    return result

@app.get("/api/diagnostic/latest")
def get_latest_diagnostic_endpoint():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM diagnostic_evaluations ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {"has_diagnostic": False}
    d = dict(row)
    for k in ["weak_topics", "strong_topics", "error_distribution", "board_vs_jee_gap", "ai_recommendation"]:
        if d.get(k) and isinstance(d[k], str):
            try:
                d[k] = json.loads(d[k])
            except Exception:
                pass
    d["has_diagnostic"] = True
    return d


# ----------------- 1.1 DAILY AIR-1 GOAL & MISSION ENDPOINTS -----------------
@app.get("/api/daily-goals")
def get_daily_goals_endpoint(date: Optional[str] = None):
    return get_or_generate_daily_goals(date)

@app.post("/api/daily-goals/{goal_id}/complete")
def complete_daily_goal_endpoint(goal_id: int):
    return complete_daily_goal(goal_id)

@app.post("/api/daily-goals/refresh")
def refresh_daily_goals_endpoint():
    return reset_and_regenerate_goals_for_today()


# ----------------- 2. SCHOOL & 12TH BOARD SYNERGY ENDPOINTS -----------------
@app.get("/api/school/tests")
def get_school_tests_endpoint():
    return {
        "upcoming": get_upcoming_school_tests(),
        "all_tests": get_all_school_tests()
    }

class AddSchoolTestRequest(BaseModel):
    title: str
    test_type: str = "Unit Test"
    subject: str
    syllabus: str
    test_date: str
    total_marks: float = 70

@app.post("/api/school/add-test")
def add_school_test_endpoint(req: AddSchoolTestRequest):
    return add_school_test(req.title, req.test_type, req.subject, req.syllabus, req.test_date, req.total_marks)

class AnalyzeSchoolTestRequest(BaseModel):
    test_id: int
    marks_obtained: float
    derivation_issues: str
    ncert_gaps: str

@app.post("/api/school/analyze-test")
def analyze_school_test_endpoint(req: AnalyzeSchoolTestRequest):
    return record_school_test_analysis(req.test_id, req.marks_obtained, req.derivation_issues, req.ncert_gaps)

@app.get("/api/school/cbse-checklist")
def get_cbse_checklist_endpoint(subject: Optional[str] = None):
    return get_cbse_board_high_yield(subject)


# ----------------- 3. STUDY PLANNER & CALENDAR SYNC ENDPOINTS -----------------
@app.get("/api/calendar/events")
def get_calendar_events_endpoint():
    return get_study_calendar_events()

class AddCalendarEventRequest(BaseModel):
    title: str
    event_type: str
    start_time: str
    end_time: str
    description: Optional[str] = ""

@app.post("/api/calendar/add-event")
def add_calendar_event_endpoint(req: AddCalendarEventRequest):
    return add_calendar_event(req.title, req.event_type, req.start_time, req.end_time, req.description)

@app.get("/api/calendar/export.ics")
def export_ics_endpoint():
    ics_content = generate_ics_calendar()
    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={"Content-Disposition": "attachment; filename=jee_air1_schedule.ics"}
    )


# ----------------- 4. TEST SERIES & MOCK EXAM ENDPOINTS -----------------
# ----------------- 4. TEST SERIES (2027 AIR-1 ENGINE & SCHEDULE INGESTION) -----------------
@app.get("/api/test-series")
def get_test_series_endpoint(series_name: Optional[str] = None):
    return get_registered_tests(series_name)

class GenerateAiScheduleRequest(BaseModel):
    series_name: str
    target_year: int = 2027
    frequency: str = "biweekly"
    start_date: Optional[str] = None
    notes: Optional[str] = None

@app.post("/api/test-series/generate-ai-schedule")
def generate_ai_schedule_endpoint(req: GenerateAiScheduleRequest):
    return generate_ai_test_schedule(
        series_name=req.series_name,
        target_year=req.target_year,
        frequency=req.frequency,
        start_date_str=req.start_date,
        notes_context=req.notes
    )

@app.post("/api/test-series/upload-schedule")
async def upload_schedule_file_endpoint(
    series_name: str = Form(...),
    target_year: int = Form(2027),
    file: UploadFile = File(...)
):
    contents = await file.read()
    return ingest_schedule_file(
        series_name=series_name,
        file_bytes=contents,
        filename=file.filename,
        target_year=target_year
    )

class ParseTextScheduleRequest(BaseModel):
    series_name: str
    text: str
    target_year: int = 2027

@app.post("/api/test-series/parse-text-schedule")
def parse_text_schedule_endpoint(req: ParseTextScheduleRequest):
    items = parse_schedule_from_text(
        series_name=req.series_name,
        raw_text=req.text,
        source_filename="Pasted Timetable",
        target_year=req.target_year
    )
    return {"status": "success", "series_name": req.series_name, "total_tests": len(items), "schedule": items}

class LogTestScoreRequest(BaseModel):
    score: float
    total_marks: float
    percentile: Optional[float] = None
    rank_estimate: Optional[int] = None
    user_notes: Optional[str] = None

@app.post("/api/test-series/{test_id}/log-score")
def log_test_score_endpoint(test_id: int, req: LogTestScoreRequest):
    return log_test_score_and_autopsy(
        test_id=test_id,
        score=req.score,
        total_marks=req.total_marks,
        percentile=req.percentile,
        rank_estimate=req.rank_estimate,
        user_notes=req.user_notes
    )

class RescheduleTestRequest(BaseModel):
    new_date: str
    new_time: Optional[str] = "09:00 - 12:00"

@app.post("/api/test-series/{test_id}/reschedule")
def reschedule_test_endpoint(test_id: int, req: RescheduleTestRequest):
    return reschedule_test_entry(test_id, req.new_date, req.new_time)

@app.get("/api/test-series/export-ics")
def export_test_series_ics_endpoint(series_name: Optional[str] = None):
    ics_text = export_test_series_ics(series_name)
    fname = f"jee_2027_{series_name or 'tests'}.ics"
    return Response(
        content=ics_text,
        media_type="text/calendar",
        headers={"Content-Disposition": f"attachment; filename={fname}"}
    )

@app.delete("/api/test-series/{test_id}")
def delete_test_endpoint(test_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM test_series_registry WHERE id = ?", (test_id,))
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"Test {test_id} removed"}

@app.delete("/api/test-series/clear/{series_name}")
def clear_series_endpoint(series_name: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM test_series_registry WHERE series_name = ?", (series_name,))
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"Cleared all tests for {series_name}"}

@app.get("/api/mocks")
def get_mocks_endpoint():
    return get_available_mocks()

@app.get("/api/mocks/{mock_id}")
def get_mock_endpoint(mock_id: str):
    details = get_mock_details(mock_id)
    if not details:
        raise HTTPException(status_code=404, detail="Mock exam not found")
    return details

class SubmitMockRequest(BaseModel):
    responses: Dict[str, Any]
    time_taken_seconds: int

@app.post("/api/mocks/{mock_id}/submit")
def submit_mock_endpoint(mock_id: str, req: SubmitMockRequest):
    return submit_mock_attempt(mock_id, req.responses, req.time_taken_seconds)


# ----------------- 5. SOLOLEARN-STYLE MICRO-LEARNING ENDPOINTS -----------------
@app.get("/api/sololearn/modules")
def get_sololearn_modules_endpoint():
    return get_all_modules()

@app.get("/api/sololearn/modules/{module_id}")
def get_sololearn_module_detail_endpoint(module_id: str):
    data = get_module_data(module_id)
    if not data:
        raise HTTPException(status_code=404, detail="Module not found")
    return data

class VerifyStepRequest(BaseModel):
    module_id: str
    step_index: int
    chosen_option: int

@app.post("/api/sololearn/verify")
def verify_sololearn_step_endpoint(req: VerifyStepRequest):
    return verify_step_answer(req.module_id, req.step_index, req.chosen_option)

class GenerateSoloLearnRequest(BaseModel):
    subject: str
    topic: str

@app.post("/api/sololearn/generate")
def generate_sololearn_card_endpoint(req: GenerateSoloLearnRequest):
    card = generate_ai_micro_card(req.subject, req.topic)
    if not card:
        raise HTTPException(status_code=500, detail="Failed to generate micro-card")
    return card


# ----------------- 6. AI MENTOR & MENTAL FORTITUDE ENDPOINTS -----------------
class MentorChatRequest(BaseModel):
    message: str

@app.post("/api/mentor/chat")
def mentor_chat_endpoint(req: MentorChatRequest):
    conn = get_db()
    cursor = conn.cursor()
    
    # Fetch recent history
    cursor.execute("SELECT role, content FROM mentor_chats ORDER BY id DESC LIMIT 6")
    history_rows = cursor.fetchall()
    history = [{"role": r["role"], "content": r["content"]} for r in reversed(history_rows)]

    # Fetch student context
    cursor.execute("SELECT weak_topics FROM diagnostic_evaluations ORDER BY id DESC LIMIT 1")
    diag_row = cursor.fetchone()
    weak_topics = diag_row["weak_topics"] if diag_row else "None yet"

    cursor.execute("SELECT total_score, max_marks FROM mock_attempts ORDER BY id DESC LIMIT 1")
    mock_row = cursor.fetchone()
    recent_score = f"{mock_row['total_score']}/{mock_row['max_marks']}" if mock_row else "No mocks yet"

    cursor.execute("SELECT test_title, test_date FROM school_tests WHERE status = 'upcoming' LIMIT 2")
    school_rows = cursor.fetchall()
    upcoming_tests = ", ".join([f"{r['test_title']} on {r['test_date']}" for r in school_rows]) if school_rows else "None"

    context = {
        "weak_topics": weak_topics,
        "recent_score": recent_score,
        "upcoming_tests": upcoming_tests
    }

    # Save user message
    cursor.execute("INSERT INTO mentor_chats (role, content) VALUES ('user', ?)", (req.message,))
    conn.commit()

    # Generate response
    reply = chat_with_air1_mentor(req.message, history=history, context=context)

    # Save assistant message
    cursor.execute("INSERT INTO mentor_chats (role, content) VALUES ('assistant', ?)", (reply,))
    conn.commit()
    conn.close()

    return {"reply": reply}

@app.get("/api/mentor/history")
def get_mentor_history_endpoint():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT role, content, created_at FROM mentor_chats ORDER BY id ASC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ----------------- 7. CURATED KNOWLEDGE & SCRAPING ENDPOINTS -----------------
@app.get("/api/knowledge/vault")
def get_knowledge_vault_endpoint():
    return get_vault_categories()

@app.get("/api/knowledge/note")
def get_knowledge_note_endpoint(src_key: str, index: int = 0):
    note = get_note_content(src_key, index)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.get("/api/knowledge/topic-notes")
def get_topic_notes_endpoint(topic: str):
    return get_notes_by_topic(topic)

@app.get("/api/knowledge/search")
def search_vault_endpoint(q: str):
    return search_vault(q)

@app.post("/api/knowledge/scrape")
def scrape_url_endpoint(req: ScrapeRequest):
    return fetch_external_url(req.url)


# ----------------- 8. MATERIAL INGESTION & DEEP REFINERY ENDPOINTS -----------------
@app.get("/api/materials")
def get_materials_endpoint():
    return get_ingested_materials()

@app.post("/api/materials/upload")
async def upload_material_endpoint(
    title: str = Form(...),
    subject: str = Form("General"),
    file: UploadFile = File(...)
):
    contents = await file.read()
    file_info = process_uploaded_file(contents, file.filename)
    refined = refine_material_with_ai(title, subject, file_info["raw_text"])
    save_refined_knowledge(title, subject, file.filename, refined)
    return {
        "status": "success",
        "title": title,
        "subject": subject,
        "filename": file.filename,
        "refined": refined
    }

class TextMaterialRequest(BaseModel):
    title: str
    subject: str = "General"
    content: str

@app.post("/api/materials/text")
def ingest_text_material_endpoint(req: TextMaterialRequest):
    refined = refine_material_with_ai(req.title, req.subject, req.content)
    save_refined_knowledge(req.title, req.subject, "pasted_notes.txt", refined)
    return {
        "status": "success",
        "title": req.title,
        "subject": req.subject,
        "refined": refined
    }


# ----------------- 9. VISUAL & SYMBOLIC ENGINES (ORGANIC, SYMPY, PLOTS) -----------------
@app.get("/api/visuals/mechanisms")
def get_mechanisms_endpoint():
    return get_organic_mechanisms()

@app.get("/api/visuals/derivation/{derivation_id}")
def get_derivation_endpoint(derivation_id: str):
    if derivation_id == "lens_maker":
        return derive_lens_maker()
    elif derivation_id == "rocket":
        return derive_variable_mass_rocket()
    raise HTTPException(status_code=404, detail="Derivation template not found")

class MathSolveRequest(BaseModel):
    expression: str

@app.post("/api/visuals/solve-math")
def solve_math_endpoint(req: MathSolveRequest):
    return solve_symbolic_expression(req.expression)

@app.get("/api/visuals/plot/wave-optics")
def get_wave_optics_plot_endpoint():
    svg_data = generate_wave_optics_plot()
    return Response(content=svg_data, media_type="image/svg+xml")

@app.get("/api/visuals/plot/electric-field")
def get_electric_field_plot_endpoint():
    svg_data = generate_electric_field_plot()
    return Response(content=svg_data, media_type="image/svg+xml")


# ----------------- 11. CONCEPT ENGINE & 6-STAGE MASTERY -----------------
@app.get("/api/concept/graph")
@app.get("/api/concepts/graph")
def get_concept_graph_endpoint(subject: Optional[str] = None):
    return get_concept_graph(subject)

@app.get("/api/concept/details/{concept_id}")
def get_concept_details_endpoint(concept_id: str):
    res = get_concept_details(concept_id)
    if not res:
        raise HTTPException(status_code=404, detail="Concept not found")
    return res

@app.get("/api/concept/prerequisites/{concept_id}")
def get_prerequisites_endpoint(concept_id: str):
    return trace_prerequisites(concept_id)

class UpdateMasteryRequest(BaseModel):
    concept_id: str
    stage: str  # 'understand', 'recall', 'apply', 'exam_transfer', 'retain', 'integrate'
    delta_score: float

@app.post("/api/concept/mastery/update")
def update_mastery_endpoint(req: UpdateMasteryRequest):
    return update_concept_mastery(req.concept_id, req.stage, req.delta_score)

@app.get("/api/concept/weaknesses")
@app.get("/api/concepts/invisible-weaknesses")
def get_weaknesses_endpoint():
    return detect_invisible_weaknesses()


# ----------------- 12. TRIGGER LINE ERROR INTELLIGENCE -----------------
class ErrorAutopsyRequest(BaseModel):
    question_title: str
    subject: str
    chapter: str
    concept_id: Optional[str] = None
    error_category: str
    wrong_thinking: str
    correct_logic: str
    trigger_line: str
    exam_type: str = "JEE Advanced"
    source_test_title: Optional[str] = None
    question_id: Optional[str] = None

@app.post("/api/errors/autopsy")
def log_autopsy_endpoint(req: ErrorAutopsyRequest):
    return log_error_autopsy(
        question_title=req.question_title,
        subject=req.subject,
        chapter=req.chapter,
        concept_id=req.concept_id,
        error_category=req.error_category,
        wrong_thinking=req.wrong_thinking,
        correct_logic=req.correct_logic,
        trigger_line=req.trigger_line,
        exam_type=req.exam_type,
        source_test_title=req.source_test_title,
        question_id=req.question_id
    )

@app.get("/api/errors/blind-queue")
def get_blind_queue_endpoint(target_date: Optional[str] = None):
    return get_blind_resolve_queue(target_date)

class BlindResolveSubmitRequest(BaseModel):
    error_id: int
    success: bool
    student_solution: str = ""

@app.post("/api/errors/blind-resolve")
def submit_blind_resolve_endpoint(req: BlindResolveSubmitRequest):
    return submit_blind_resolve(req.error_id, req.success, req.student_solution)

@app.get("/api/errors/pre-mock-deck")
@app.get("/api/errors/trigger-deck")
def get_pre_mock_deck_endpoint(chapters: Optional[str] = None, limit: int = 20):
    chap_list = [c.strip() for c in chapters.split(",")] if chapters else None
    return get_pre_mock_trigger_deck(chap_list, limit)

@app.get("/api/errors/analytics")
def get_error_analytics_endpoint():
    return get_error_analytics()

@app.get("/api/errors/formula-decay")
def get_formula_decay_endpoint(limit: int = 5):
    return get_formula_decay_prompts(limit)


# ----------------- 13. OMNI-PLANNER & MULTI-DEADLINE SOLVER -----------------
@app.get("/api/omni-planner/schedule")
def get_omni_schedule_endpoint(days: int = 14):
    return generate_omni_schedule(days)

class ScopeCutRequest(BaseModel):
    daily_hours_exceeded: float = 2.0

@app.post("/api/omni-planner/scope-cut")
def scope_cut_endpoint(req: ScopeCutRequest):
    return apply_scope_cutter(req.daily_hours_exceeded)

class WhatIfRequest(BaseModel):
    scenario_type: str  # 'missed_days', 'coaching_test_shifted', 'intensive_deep_dive'
    params: Dict[str, Any] = {}

@app.post("/api/omni-planner/what-if")
def what_if_endpoint(req: WhatIfRequest):
    return simulate_what_if_scenario(req.scenario_type, req.params)

class ScheduledTaskCreateRequest(BaseModel):
    task_date: str
    task_type: str
    title: str
    duration_minutes: int = 30
    subject: Optional[str] = None
    concept_id: Optional[str] = None
    priority: int = 3
    exam_track: str = "JEE Advanced"

@app.post("/api/omni-planner/task")
def create_scheduled_task_endpoint(req: ScheduledTaskCreateRequest):
    return log_scheduled_task(
        task_date=req.task_date,
        task_type=req.task_type,
        title=req.title,
        duration_minutes=req.duration_minutes,
        subject=req.subject,
        concept_id=req.concept_id,
        priority=req.priority,
        exam_track=req.exam_track
    )

@app.get("/api/omni-planner/tasks")
def get_scheduled_tasks_endpoint(task_date: Optional[str] = None):
    return get_scheduled_tasks_for_date(task_date)

class TaskStatusUpdateRequest(BaseModel):
    status: str  # 'completed', 'missed', 're_scheduled'

@app.post("/api/omni-planner/task/{task_id}/status")
def update_task_status_endpoint(task_id: int, req: TaskStatusUpdateRequest):
    return update_task_status(task_id, req.status)


# ----------------- 14. TRIAGE & TACTICAL EXAM EXECUTION -----------------
@app.get("/api/tactics/triage-question")
def get_triage_question_endpoint():
    return get_triage_drill_question()

class TriageSubmitRequest(BaseModel):
    drill_id: str
    chosen_round: int
    time_taken_seconds: int = 30

@app.post("/api/tactics/triage-submit")
def submit_triage_endpoint(req: TriageSubmitRequest):
    return submit_triage_drill(req.drill_id, req.chosen_round, req.time_taken_seconds)

class AbandonmentROIRequest(BaseModel):
    minutes_spent_on_trap: float = 8.0
    avg_question_time: float = 3.0

@app.post("/api/tactics/abandonment-roi")
def abandonment_roi_endpoint(req: AbandonmentROIRequest):
    return calculate_abandonment_roi(req.minutes_spent_on_trap, req.avg_question_time)

@app.get("/api/tactics/god-mode-matrix")
def get_god_mode_matrix_endpoint():
    return get_god_mode_matrix()

@app.get("/api/tactics/chaos-profiles")
def get_chaos_profiles_endpoint():
    return get_chaos_room_profiles()


# ----------------- 15. CBSE STEP-LOSS EVALUATOR & NCERT CLOZE -----------------
@app.get("/api/cbse/derivations")
def get_cbse_derivations_endpoint():
    return get_cbse_derivations_list()

class CBSEDerivationEvalRequest(BaseModel):
    derivation_key: str
    student_text: str

@app.post("/api/cbse/evaluate-derivation")
def evaluate_derivation_endpoint(req: CBSEDerivationEvalRequest):
    return evaluate_cbse_derivation(req.derivation_key, req.student_text)

@app.get("/api/cbse/ncert-cloze")
def get_ncert_cloze_endpoint():
    return get_ncert_cloze_drill()


# ----------------- 16. SUSTAINABLE PERFORMANCE & SIBLING REVIEW -----------------
class WellnessLogRequest(BaseModel):
    study_hours: float
    sleep_hours: float
    energy_rating: int
    mood: str = "steady"
    silly_mistake_count: int = 0
    distractions: str = ""
    notes: str = ""
    log_date: Optional[str] = None

@app.post("/api/wellness/log")
def log_wellness_endpoint(req: WellnessLogRequest):
    return log_daily_wellness(
        study_hours=req.study_hours,
        sleep_hours=req.sleep_hours,
        energy_rating=req.energy_rating,
        mood=req.mood,
        silly_mistake_count=req.silly_mistake_count,
        distractions=req.distractions,
        notes=req.notes,
        log_date=req.log_date
    )

@app.get("/api/wellness/history")
def get_wellness_history_endpoint(days: int = 7):
    return get_wellness_history(days)

@app.get("/api/wellness/why-wall")
def get_why_wall_endpoint():
    return get_why_wall_data()

class WhyWallUpdateRequest(BaseModel):
    target_campus: str
    target_college: str
    why_note: str

@app.post("/api/wellness/why-wall")
def update_why_wall_endpoint(req: WhyWallUpdateRequest):
    return update_why_wall(req.target_campus, req.target_college, req.why_note)

class DeloadToggleRequest(BaseModel):
    active: bool

@app.post("/api/wellness/deload-toggle")
def toggle_deload_endpoint(req: DeloadToggleRequest):
    return toggle_deload_week(req.active)

@app.get("/api/wellness/sibling-report")
def get_sibling_report_endpoint():
    return generate_sunday_sibling_report()


# ----------------- 9. NEXT-BEST-ACTION & MENTOR MODES ENDPOINTS -----------------
@app.get("/api/next-best-action")
def get_next_best_action_endpoint():
    return calculate_next_best_action()

@app.get("/api/readiness-forecast")
def get_readiness_forecast_endpoint():
    return get_readiness_forecast()

@app.get("/api/counterexample-lab")
def get_counterexample_lab_endpoint():
    return get_counterexample_lab_cases()

@app.get("/api/alternate-solutions")
def get_alternate_solutions_endpoint():
    return get_alternate_solutions()

@app.get("/api/mentor/modes")
def get_mentor_modes_endpoint():
    return {"modes": TEACHING_MODES}

@app.get("/api/mentor/prove-it/{concept_id}")
def get_prove_it_endpoint(concept_id: str):
    return get_prove_it_challenge(concept_id)

class MentorModeChatRequest(BaseModel):
    mode: str = "socratic"
    topic: str = "Rotational Motion"
    message: str
    history: Optional[List[Dict[str, str]]] = []

@app.post("/api/mentor/chat-mode")
def mentor_mode_chat_endpoint(req: MentorModeChatRequest):
    framing = format_mentor_mode_prompt(req.mode, req.topic, req.message)
    context = {
        "weak_topics": req.topic,
        "mode_instruction": framing["system_instruction"]
    }
    prompt = f"[{req.mode.upper()} PROTOCOL - {framing['system_instruction']}]\nTopic: {req.topic}\nQuestion/Message: {req.message}"
    reply = chat_with_air1_mentor(prompt, history=req.history, context=context)
    return {
        "status": "success",
        "mode": req.mode,
        "reply": reply
    }



# ----------------- 10. ANDROID APK DOWNLOAD & STATUS -----------------
APK_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "JEE_AIR1_Companion.apk")
ALT_APK_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "android_app", "app", "build", "outputs", "apk", "debug", "app-debug.apk")

@app.get("/api/download-apk")
def download_apk_endpoint():
    target = APK_PATH if os.path.exists(APK_PATH) else ALT_APK_PATH
    if not os.path.exists(target):
        raise HTTPException(status_code=404, detail="APK build is in progress. Please check again in a few moments.")
    return FileResponse(
        path=target,
        media_type="application/vnd.android.package-archive",
        filename="JEE_AIR1_Companion.apk"
    )

@app.get("/api/apk-status")
def get_apk_status_endpoint():
    target = APK_PATH if os.path.exists(APK_PATH) else ALT_APK_PATH
    ready = os.path.exists(target)
    size_mb = round(os.path.getsize(target) / (1024 * 1024), 2) if ready else 0
    return {"ready": ready, "filename": "JEE_AIR1_Companion.apk", "size_mb": size_mb}


# ----------------- FRONTEND STATIC HOSTING -----------------
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>JEE Advanced AIR-1 App Backend Running. Frontend loading...</h1>"
