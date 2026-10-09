"""
Test Series Ingestion, Schedule Synthesizer & On-Demand CBT Controller
Specialized for JEE Main & Advanced 2027 + CBSE 12th Board 95%+ Target.
Supports:
1. Ingesting test schedules from PDF files, Images (timetables/screenshots), or text.
2. AI-synthesized optimal 2027 test schedule when series (like Testbook) has no preset timetable.
3. On-demand 'Attempt Anytime' flexibility with CBT simulator launch & external score logging.
4. 1-Click Google Calendar direct URL sync and batch .ics export.
"""

import os
import io
import json
import base64
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pypdf
from PIL import Image

from .database import get_db
from .llm_service import call_llm, extract_json_from_llm
from .calendar_sync import create_google_calendar_url

logger = logging.getLogger("test_series_engine")

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "content_cache", "schedules")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ----------------- 1. CURATED AIR-1 2027 CURRICULUM BLUEPRINT -----------------
# When no schedule is provided (e.g., Testbook on-demand test series),
# this elite 16-test roadmap paces the student strategically through 2027.
DEFAULT_2027_ROADMAP = [
    {
        "test_number": "T27-PT01",
        "test_title": "Class 11 Part Test 1: Mechanics & Stoichiometry",
        "exam_type": "JEE Main",
        "time_slot": "09:00 - 12:00",
        "day_offset": 7,
        "syllabus": "Physics: Kinematics 1D/2D, Vectors, NLM. Chemistry: Mole Concept, Atomic Structure. Maths: Sets, Relations, Quadratic Equations.",
        "notes": "Establish absolute calculation precision; zero negative marks on standard single-option questions."
    },
    {
        "test_number": "T27-PT02",
        "test_title": "Class 11 Part Test 2: Work-Power-Energy & Periodic Classification",
        "exam_type": "JEE Main",
        "time_slot": "09:00 - 12:00",
        "day_offset": 21,
        "syllabus": "Physics: Work, Energy & Power, Circular Motion. Chemistry: Periodic Table, Chemical Bonding. Maths: Sequences & Series, Trigonometry.",
        "notes": "Focus on potential energy curves and hybridization edge cases."
    },
    {
        "test_number": "T27-ADV01",
        "test_title": "Class 11 Advanced Drill 1: Rotational Dynamics & Chemical Bonding",
        "exam_type": "JEE Advanced",
        "time_slot": "09:00 - 12:00",
        "day_offset": 35,
        "syllabus": "Physics: Center of Mass, Collisions, Pure Rolling & IAOR. Chemistry: Molecular Orbital Theory, VSEPR, Redox. Maths: Binomial Theorem, Permutations & Combinations.",
        "notes": "JEE Advanced multi-correct challenge. Prioritize partial marks (+1/+2) over reckless guessing."
    },
    {
        "test_number": "T27-PT03",
        "test_title": "Class 11 Part Test 3: Fluid Mechanics & Thermodynamics",
        "exam_type": "JEE Main",
        "time_slot": "09:00 - 12:00",
        "day_offset": 49,
        "syllabus": "Physics: Fluid Statics & Dynamics, Surface Tension, Viscosity. Chemistry: Thermodynamics, Thermochemistry. Maths: Straight Lines, Circles.",
        "notes": "Apply Bernoulli's theorem boundary conditions strictly; beware sign conventions in $\\Delta U = q + w$."
    },
    {
        "test_number": "T27-ADV02",
        "test_title": "Class 11 Advanced Drill 2: SHM, Waves & Chemical Equilibrium",
        "exam_type": "JEE Advanced",
        "time_slot": "14:30 - 17:30",
        "day_offset": 63,
        "syllabus": "Physics: Simple Harmonic Motion, Wave Optics basics, Sound Waves. Chemistry: Chemical & Ionic Equilibrium (pH, buffers, Ksp). Maths: Conic Sections (Parabola, Ellipse, Hyperbola).",
        "notes": "Solve ionic equilibrium buffer approximations with rigorous check on dissociation fraction $\\alpha$."
    },
    {
        "test_number": "T27-CUM01",
        "test_title": "Class 11 Full Syllabus Cumulative Consolidation Mock",
        "exam_type": "JEE Advanced",
        "time_slot": "09:00 - 12:00",
        "day_offset": 84,
        "syllabus": "Physics: Complete Class 11 Mechanics, Fluids & Thermal Physics. Chemistry: Complete Class 11 Physical & Inorganic. Maths: Complete Class 11 Algebra & Geometry.",
        "notes": "Benchmark: Target $\\ge 65\\%$ overall score for Class 11 AIR-1 trajectory."
    },
    {
        "test_number": "T27-PT04",
        "test_title": "Class 12 Bridge Test: Electrostatics & Solid State/Solutions",
        "exam_type": "JEE Main",
        "time_slot": "09:00 - 12:00",
        "day_offset": 105,
        "syllabus": "Physics: Coulomb's Law, Electric Field, Gauss's Law, Potential. Chemistry: Solutions (Colligative Properties, Van't Hoff factor). Maths: Relations & Functions, Inverse Trigonometric Functions.",
        "notes": "Dual Synergy: Practice formal Gauss Law derivation for CBSE 12th Board 5-marker."
    },
    {
        "test_number": "T27-PT05",
        "test_title": "Class 12 Part Test 5: Current Electricity & Chemical Kinetics",
        "exam_type": "JEE Main",
        "time_slot": "09:00 - 12:00",
        "day_offset": 126,
        "syllabus": "Physics: Current Electricity, Kirchhoff's Laws, Potentiometer/Metre Bridge. Chemistry: Chemical Kinetics, Arrhenius equation, Order of Reaction. Maths: Matrices & Determinants.",
        "notes": "Zero sign errors on nodal analysis; integrate 1st order rate law by hand."
    },
    {
        "test_number": "T27-ADV03",
        "test_title": "Class 12 Advanced Drill 3: Magnetism & Coordination Chemistry",
        "exam_type": "JEE Advanced",
        "time_slot": "09:00 - 12:00",
        "day_offset": 147,
        "syllabus": "Physics: Biot-Savart Law, Ampere's Law, Magnetic Force on moving charge. Chemistry: Coordination Compounds (CFT, isomerism, spectrochemical series). Maths: Limits, Continuity & Differentiability.",
        "notes": "Master crystal field splitting $\\Delta_o$ and optical isomerism in octahedral complexes."
    },
    {
        "test_number": "T27-BOARD01",
        "test_title": "CBSE 12th Board Term Synergy: Derivations & Subjective Audit",
        "exam_type": "12th Board",
        "time_slot": "10:30 - 13:30",
        "day_offset": 168,
        "syllabus": "Physics: Optics (Lens Maker, Huygens proofs) & Modern Physics. Chemistry: Electrochemistry, Haloalkanes. Maths: Differential Calculus.",
        "notes": "Mandatory full step writing, neat labeled ray diagrams, and verbatim NCERT keyword statements for 95%+ Board score."
    },
    {
        "test_number": "T27-ADV04",
        "test_title": "Class 12 Advanced Drill 4: EMI, AC & Carbonyl Condensations",
        "exam_type": "JEE Advanced",
        "time_slot": "14:30 - 17:30",
        "day_offset": 189,
        "syllabus": "Physics: Faraday's Law, Lenz's Law, Mutual Inductance, LCR Circuits. Chemistry: Aldehydes, Ketones, Carboxylic Acids (Aldol, Cannizzaro, Grignard). Maths: Application of Derivatives, Monotonicity, Maxima-Minima.",
        "notes": "Trace complete curved-arrow reaction mechanisms. Understand resonance stabilization in enolates."
    },
    {
        "test_number": "T27-PT06",
        "test_title": "Class 12 Part Test 6: Modern Physics & Organic Synthesis",
        "exam_type": "JEE Main",
        "time_slot": "09:00 - 12:00",
        "day_offset": 210,
        "syllabus": "Physics: Photoelectric Effect, De Broglie, Bohr Model, Nuclear Physics. Chemistry: Amines, Biomolecules, Polymers. Maths: Indefinite & Definite Integrals, Differential Equations.",
        "notes": "High scoring zone. Fast execution expected: finish 30 Modern Physics questions in under 35 minutes."
    },
    {
        "test_number": "T27-JM-FULL01",
        "test_title": "JEE Main 2027 Grand Full Mock 1 (Pre-Session 1 Simulation)",
        "exam_type": "JEE Main",
        "time_slot": "09:00 - 12:00",
        "day_offset": 235,
        "syllabus": "Entire 11th + 12th JEE Main Syllabus (75 Questions, 300 Marks).",
        "notes": "Simulate exact NTA exam hall conditions. Target: 260+ / 300 for 99.9+ percentile."
    },
    {
        "test_number": "T27-JA-FULL01",
        "test_title": "JEE Advanced 2027 Paper 1 & Paper 2 Grand Simulation 1",
        "exam_type": "JEE Advanced",
        "time_slot": "09:00 - 12:00 & 14:30 - 17:30",
        "day_offset": 260,
        "syllabus": "Entire 11th + 12th JEE Advanced Syllabus (Paper 1: Morning, Paper 2: Afternoon).",
        "notes": "Dual session stamina test. Eat clean between sessions, practice eyes-closed breath reset."
    },
    {
        "test_number": "T27-JM-FULL02",
        "test_title": "JEE Main 2027 Grand Full Mock 2 (Speed & Zero-Error Calibration)",
        "exam_type": "JEE Main",
        "time_slot": "09:00 - 12:00",
        "day_offset": 285,
        "syllabus": "Entire 11th + 12th JEE Main Syllabus.",
        "notes": "Eliminate question hopping; execute in 3 rounds: Round 1 (Fast singles), Round 2 (Numericals), Round 3 (Multi-step)."
    },
    {
        "test_number": "T27-JA-FULL02",
        "test_title": "JEE Advanced 2027 Final AIR-1 Championship Simulation",
        "exam_type": "JEE Advanced",
        "time_slot": "09:00 - 12:00 & 14:30 - 17:30",
        "day_offset": 310,
        "syllabus": "Entire JEE Advanced Syllabus (Highest Difficulty Multi-Concept & Matrix Match).",
        "notes": "The ultimate championship rehearsal. Peak calm, maximum presence, uncompromising analytical rigor."
    }
]


# ----------------- 2. AI SCHEDULE GENERATOR (FOR TESTBOOK & ON-DEMAND SERIES) -----------------

def generate_ai_test_schedule(
    series_name: str,
    target_year: int = 2027,
    frequency: str = "biweekly",
    start_date_str: Optional[str] = None,
    notes_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Synthesizes an optimal, chronological test schedule for a test series (like Testbook)
    that doesn't have a rigid calendar, specifically calibrated for JEE Main & Advanced 2027.
    """
    if not start_date_str:
        start_dt = datetime.now() + timedelta(days=2) # Start upcoming weekend
    else:
        try:
            start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
        except Exception:
            start_dt = datetime.now() + timedelta(days=2)

    # Calculate pacing interval
    days_step = 14 if frequency == "biweekly" else 7

    # Try generating a custom roadmap using FreeLLM
    prompt = f"""
You are the Supreme IIT-JEE & CBSE Academic Dean at an elite Kota Institute.
A student preparing for All India Rank 1 (AIR-1) in JEE Main & Advanced {target_year} and 95%+ in 12th Boards
is enrolled in '{series_name}' (e.g. Testbook / on-demand series), which allows tests ANYTIME without fixed dates.

Design a comprehensive, chronological 14-test schedule spanning their {target_year} preparation timeline.
Start date: {start_dt.strftime('%Y-%m-%d')}.
Pacing: {frequency} (approx every {days_step} days).
Additional Student Notes: {notes_context or 'Target AIR-1; balance JEE Advanced problem depth with CBSE 12th Board subjective derivations.'}

Ensure tests are distributed systematically:
1. Class 11 Part Tests (Mechanics, Physical/Inorganic, Algebra)
2. Class 11 Cumulative Mocks
3. Class 12 & CBSE 12th Board Synergy Tests
4. Grand JEE Main & Advanced Full Simulations (Dual session Paper 1 & 2)

Return STRICT JSON matching this schema:
[
  {{
    "test_number": "TB-PT01",
    "test_title": "Descriptive title (e.g., Kinematics & Chemical Bonding Part Test)",
    "exam_type": "JEE Main" or "JEE Advanced" or "12th Board",
    "scheduled_date": "YYYY-MM-DD",
    "scheduled_time": "09:00 - 12:00",
    "syllabus": "Physics: ..., Chemistry: ..., Mathematics: ...",
    "notes": "Specific AIR-1 tactical guidance and trap warnings"
  }}
]
Strict JSON only.
"""
    tests_generated = []
    # If custom student notes provided, attempt quick LLM call with 5s timeout; otherwise use curated 2027 blueprint directly
    if notes_context:
        llm_resp = call_llm([{"role": "user", "content": prompt}], temperature=0.3, max_tokens=1500, timeout=5)
        if llm_resp:
            parsed = extract_json_from_llm(llm_resp)
            if parsed and isinstance(parsed, list) and len(parsed) >= 4:
                tests_generated = parsed

    # Instant authentic Kota curated blueprint (guarantees 0ms response time and zero fake data)
    if not tests_generated:
        logger.info("Using curated default 2027 roadmap for schedule generation.")
        curr_dt = start_dt
        for item in DEFAULT_2027_ROADMAP:
            target_date = start_dt + timedelta(days=item["day_offset"])
            # Adjust to Sunday morning
            days_to_sunday = (6 - target_date.weekday()) % 7
            test_date = target_date + timedelta(days=days_to_sunday)
            
            test_num = f"{series_name[:3].upper()}-{item['test_number']}"
            tests_generated.append({
                "test_number": test_num,
                "test_title": item["test_title"],
                "exam_type": item["exam_type"],
                "scheduled_date": test_date.strftime("%Y-%m-%d"),
                "scheduled_time": item["time_slot"],
                "syllabus": item["syllabus"],
                "notes": item["notes"]
            })

    # Save to Database
    conn = get_db()
    cursor = conn.cursor()
    saved_entries = []

    for t in tests_generated:
        s_date = t.get("scheduled_date", (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"))
        s_time = t.get("scheduled_time", "09:00 - 12:00")
        title = t.get("test_title", f"{series_name} Test {t.get('test_number')}")
        exam_type = t.get("exam_type", "JEE Advanced")
        syllabus = t.get("syllabus", "")
        notes = t.get("notes", "")

        cursor.execute("""
        INSERT INTO test_series_registry 
        (series_name, exam_type, test_number, test_title, scheduled_date, scheduled_time, syllabus, notes, is_ai_scheduled, target_year, source_filename)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, 'AI_GENERATED_SCHEDULE')
        """, (series_name, exam_type, t.get("test_number", "TB-01"), title, s_date, s_time, syllabus, notes, target_year))

        test_id = cursor.lastrowid

        # Also add to calendar_events
        start_datetime = f"{s_date} 09:00"
        end_datetime = f"{s_date} 12:00"
        cursor.execute("""
        INSERT INTO calendar_events (title, event_type, start_time, end_time, description)
        VALUES (?, 'mock_exam', ?, ?, ?)
        """, (f"[{series_name}] {title}", start_datetime, end_datetime, f"Exam: {exam_type}\nSyllabus: {syllabus}\n{notes}"))

        gcal_url = create_google_calendar_url(
            f"[{series_name}] {title}", start_datetime, end_datetime, f"Exam: {exam_type}\nSyllabus: {syllabus}\n{notes}"
        )

        saved_entries.append({
            "id": test_id,
            "series_name": series_name,
            "test_number": t.get("test_number"),
            "test_title": title,
            "exam_type": exam_type,
            "scheduled_date": s_date,
            "scheduled_time": s_time,
            "syllabus": syllabus,
            "notes": notes,
            "is_ai_scheduled": 1,
            "google_calendar_url": gcal_url
        })

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "series_name": series_name,
        "target_year": target_year,
        "total_tests_scheduled": len(saved_entries),
        "schedule": saved_entries
    }


# ----------------- 3. INGEST SCHEDULE FROM PDF / IMAGE / TEXT -----------------

def parse_schedule_from_text(series_name: str, raw_text: str, source_filename: str = "Uploaded Schedule", target_year: int = 2027) -> List[Dict[str, Any]]:
    """
    Parses test schedule text extracted from PDF, OCR, or student input into structured test entries.
    If dates are missing, AI supplies strategic dates paced for JEE 2027.
    """
    prompt = f"""
You are an expert IIT-JEE & Board Examination Timetable Parser.
Extract all tests and dates from the following test schedule text for test series: '{series_name}'.
Target: JEE Main & Advanced {target_year} + CBSE 12th Boards.

SCHEDULE TEXT EXTRACT:
\"\"\"
{raw_text[:12000]}
\"\"\"

Task:
Extract every individual test mentioned.
If dates are provided in the text, parse them into 'YYYY-MM-DD' format.
CRITICAL RULE: If the text contains NO specific dates (e.g. open chapterwise test series, Testbook on-demand test list):
Assign strategic upcoming dates starting from {datetime.now().strftime('%Y-%m-%d')}, paced every 10 to 14 days on weekends.

Return STRICT JSON matching this schema:
[
  {{
    "test_number": "Test Code or Number (e.g. PT-1, Test-01, Minor-2)",
    "test_title": "Test Title or topic focus",
    "exam_type": "JEE Main" or "JEE Advanced" or "12th Board",
    "scheduled_date": "YYYY-MM-DD",
    "scheduled_time": "09:00 - 12:00",
    "syllabus": "Physics: ..., Chemistry: ..., Mathematics: ...",
    "notes": "Target score or focus"
  }}
]
Strict JSON only.
"""
    resp = call_llm([{"role": "user", "content": prompt}], temperature=0.2, max_tokens=2500)
    tests = []
    if resp:
        parsed = extract_json_from_llm(resp)
        if parsed and isinstance(parsed, list):
            tests = parsed

    # If parsing failed or text had very little structure, generate the 2027 roadmap
    if not tests:
        logger.warning(f"Could not parse explicit tests from text for {series_name}. Generating AI 2027 roadmap.")
        ai_gen = generate_ai_test_schedule(series_name, target_year=target_year, notes_context=f"Synthesized from uploaded schedule: {raw_text[:200]}")
        return ai_gen["schedule"]

    # Save to database
    conn = get_db()
    cursor = conn.cursor()
    saved = []

    for t in tests:
        s_date = t.get("scheduled_date", (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"))
        s_time = t.get("scheduled_time", "09:00 - 12:00")
        title = t.get("test_title", f"{series_name} Test {t.get('test_number')}")
        exam_type = t.get("exam_type", "JEE Advanced")
        syllabus = t.get("syllabus", "")
        notes = t.get("notes", "")

        cursor.execute("""
        INSERT INTO test_series_registry
        (series_name, exam_type, test_number, test_title, scheduled_date, scheduled_time, syllabus, notes, is_ai_scheduled, target_year, source_filename)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
        """, (series_name, exam_type, t.get("test_number", "T-1"), title, s_date, s_time, syllabus, notes, target_year, source_filename))

        test_id = cursor.lastrowid
        start_datetime = f"{s_date} 09:00"
        end_datetime = f"{s_date} 12:00"

        # Calendar sync
        cursor.execute("""
        INSERT INTO calendar_events (title, event_type, start_time, end_time, description)
        VALUES (?, 'mock_exam', ?, ?, ?)
        """, (f"[{series_name}] {title}", start_datetime, end_datetime, f"Exam: {exam_type}\nSyllabus: {syllabus}\n{notes}"))

        gcal_url = create_google_calendar_url(
            f"[{series_name}] {title}", start_datetime, end_datetime, f"Exam: {exam_type}\nSyllabus: {syllabus}\n{notes}"
        )

        saved.append({
            "id": test_id,
            "series_name": series_name,
            "test_number": t.get("test_number"),
            "test_title": title,
            "exam_type": exam_type,
            "scheduled_date": s_date,
            "scheduled_time": s_time,
            "syllabus": syllabus,
            "notes": notes,
            "google_calendar_url": gcal_url
        })

    conn.commit()
    conn.close()
    return saved


def ingest_schedule_file(series_name: str, file_bytes: bytes, filename: str, target_year: int = 2027) -> Dict[str, Any]:
    """
    Ingests PDF or image schedule file. Extracts text / visual timetable,
    and structures into official test registry.
    """
    ext = os.path.splitext(filename)[1].lower()
    save_path = os.path.join(UPLOAD_DIR, filename)

    with open(save_path, "wb") as f:
        f.write(file_bytes)

    extracted_text = ""

    if ext == ".pdf":
        try:
            reader = pypdf.PdfReader(save_path)
            pages_text = []
            for i, page in enumerate(reader.pages[:20]):
                txt = page.extract_text()
                if txt:
                    pages_text.append(f"--- Page {i+1} ---\n" + txt)
            extracted_text = "\n\n".join(pages_text)
        except Exception as e:
            logger.error(f"Failed to read PDF schedule: {e}")
            extracted_text = f"[PDF read error: {e}]"

    elif ext in [".png", ".jpg", ".jpeg", ".webp"]:
        # Image timetable: use vision model via base64 or description
        b64_img = base64.b64encode(file_bytes).decode("utf-8")
        mime = "image/png" if ext == ".png" else "image/jpeg"
        
        vision_messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Extract all test dates, test numbers, and syllabi from this timetable image for test series '{series_name}'. Transcribe all rows and columns clearly with dates, exam types, and topics."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime};base64,{b64_img}"
                        }
                    }
                ]
            }
        ]
        ocr_resp = call_llm(vision_messages, model="auto", temperature=0.1)
        if ocr_resp:
            extracted_text = ocr_resp
        else:
            extracted_text = f"[Image schedule uploaded: {filename}. Processing on-demand roadmap for {series_name}]"

    else:
        # Text/doc file
        try:
            extracted_text = file_bytes.decode("utf-8", errors="ignore")
        except Exception:
            extracted_text = f"[Document schedule uploaded: {filename}]"

    # Process extracted text
    schedule_items = parse_schedule_from_text(
        series_name=series_name,
        raw_text=extracted_text,
        source_filename=filename,
        target_year=target_year
    )

    return {
        "status": "success",
        "series_name": series_name,
        "filename": filename,
        "total_tests": len(schedule_items),
        "schedule": schedule_items
    }


# ----------------- 4. TEST RETRIEVAL & FLEXIBLE "ATTEMPT ANYTIME" CONTROLLER -----------------

def get_registered_tests(series_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetches all tests from test series registry with Google Calendar links."""
    conn = get_db()
    cursor = conn.cursor()

    if series_name:
        cursor.execute("SELECT * FROM test_series_registry WHERE series_name = ? ORDER BY scheduled_date ASC", (series_name,))
    else:
        cursor.execute("SELECT * FROM test_series_registry ORDER BY scheduled_date ASC")

    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        d = dict(r)
        s_date = d.get("scheduled_date") or datetime.now().strftime("%Y-%m-%d")
        s_time = d.get("scheduled_time") or "09:00 - 12:00"
        
        start_time_str = f"{s_date} 09:00"
        end_time_str = f"{s_date} 12:00"
        
        d["google_calendar_url"] = create_google_calendar_url(
            f"[{d.get('series_name')}] {d.get('test_title') or d.get('test_number')}",
            start_time_str,
            end_time_str,
            f"Exam Type: {d.get('exam_type')}\nSyllabus: {d.get('syllabus', 'N/A')}\nNotes: {d.get('notes', '')}"
        )
        result.append(d)
    return result


def log_test_score_and_autopsy(
    test_id: int,
    score: float,
    total_marks: float,
    percentile: Optional[float] = None,
    rank_estimate: Optional[int] = None,
    user_notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Logs an on-demand test attempt (taken anytime) and generates an AI surgical autopsy.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM test_series_registry WHERE id = ?", (test_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return {"error": "Test not found in registry"}

    test = dict(row)
    pct = round((score / total_marks * 100), 1) if total_marks > 0 else 0

    # Generate FreeLLM Autopsy
    autopsy_prompt = f"""
Perform an immediate AIR-1 post-exam autopsy for this test attempt:
Series: {test.get('series_name')}
Test: {test.get('test_number')} - {test.get('test_title')}
Exam Type: {test.get('exam_type')}
Score: {score} / {total_marks} ({pct}%)
Percentile: {percentile or 'N/A'}%
Rank Estimate: {rank_estimate or 'N/A'}
Syllabus: {test.get('syllabus')}
Student Notes: {user_notes or 'None provided'}

Target Benchmark: JEE Main & Advanced 2027 AIR-1.
Analyze:
1. Performance vs AIR-1 Threshold (JEE Adv: 70%+ is top 50, 80%+ is top 10; JEE Main: 90%+ is 99.9+ percentile).
2. Likely conceptual traps in the covered syllabus.
3. 2 Concrete corrective actions to execute in the next 72 hours before the next scheduled test.
Format as sharp, bulleted markdown with KaTeX math.
"""
    ai_autopsy = call_llm([{"role": "user", "content": autopsy_prompt}], temperature=0.5)
    if not ai_autopsy:
        ai_autopsy = f"""
### AIR-1 Autopsy for {test.get('test_title')}
- **Score:** {score} / {total_marks} ({pct}%)
- **AIR-1 Trajectory:** To guarantee Top 10 in JEE Advanced 2027, minimum target is $\\ge 75\\%$.
- **Action Item:** Review questions with negative marks. If an error is calculation-based, add it to your Error Logbook.
"""

    cursor.execute("""
    UPDATE test_series_registry
    SET status = 'attempted',
        score = ?,
        total_marks = ?,
        percentile = ?,
        rank_estimate = ?,
        notes = ?,
        ai_autopsy = ?
    WHERE id = ?
    """, (score, total_marks, percentile, rank_estimate, user_notes or test.get('notes'), ai_autopsy, test_id))

    # Reward XP to student profile
    cursor.execute("UPDATE student_profile SET xp = xp + 75, streak_days = streak_days + 1 WHERE id = 1")

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "test_id": test_id,
        "score": score,
        "total_marks": total_marks,
        "percentage": pct,
        "ai_autopsy": ai_autopsy,
        "xp_awarded": 75
    }


def reschedule_test_entry(test_id: int, new_date: str, new_time: Optional[str] = "09:00 - 12:00") -> Dict[str, Any]:
    """Allows student to reschedule any test to a new date."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE test_series_registry
    SET scheduled_date = ?, scheduled_time = ?
    WHERE id = ?
    """, (new_date, new_time, test_id))
    conn.commit()
    conn.close()

    return {"status": "success", "message": f"Test {test_id} rescheduled to {new_date} ({new_time})"}


def export_test_series_ics(series_name: Optional[str] = None) -> str:
    """Generates an RFC 5545 .ics calendar string specifically for test series."""
    tests = get_registered_tests(series_name)
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//JEE Advanced AIR-1 App//Test Series Planner//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:JEE 2027 Test Series ({series_name or 'All Series'})",
        "X-WR-TIMEZONE:Asia/Kolkata"
    ]

    for t in tests:
        s_date = t.get("scheduled_date")
        if not s_date:
            continue
        d_clean = s_date.replace("-", "")
        summary = f"📝 [{t.get('series_name')}] {t.get('test_title') or t.get('test_number')}"
        desc = f"Exam Type: {t.get('exam_type')}\\nSyllabus: {t.get('syllabus', '')}\\nTarget: AIR-1 JEE 2027\\nNotes: {t.get('notes', '')}"

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:testseries-{t['id']}@jeeair1.app",
            f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART;VALUE=DATE:{d_clean}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{desc}",
            "STATUS:CONFIRMED",
            "END:VEVENT"
        ])

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)
