# 🏆 JEE Advanced AIR-1 & CBSE 95%+ Master Platform

An AI-powered preparation platform engineered for students targeting **All India Rank 1 (AIR-1)** in JEE Main & JEE Advanced while securing **95%+ in the CBSE Class 12 Board Examinations**.

---

## 🌟 Key Architecture & Capabilities

### 1. 🩺 Adaptive Baseline Diagnostic Evaluation
- **Where does the student lag exactly?**
  - Multi-tier baseline assessment across Physics, Chemistry, and Mathematics.
  - Pinpoints conceptual holes (e.g., pure rolling non-inertial frames, cross-Cannizzaro vs aldol, Leibniz differentiation under moving limits) vs calculation/silly slips vs time-pressure panic.
  - Generates a surgical **AIR-1 Recovery Plan** and board-synergy gap report.

### 2. ⚡ SoloLearn-Style Micro-Learning Engine
- **Algorithm:**
  1. **Concept Nugget:** 60-second high-yield bite with core equations and an **IIT-JEE Trap Alert**.
  2. **Immediate Active Recall PYQ Patch:** Authentic question from JEE Advanced, JEE Main, or CBSE 12th Board directly reinforcing that nugget.
  3. **Instant Validation & XP:** Real-time feedback with full derivation, $+25\text{ XP}$ streak rewards, and progression unlocks.
  4. **On-the-Fly AI Generator:** Generate new micro-cards on any specific topic or doubt using FreeLLM.

### 3. 🖥️ Authentic JEE CBT Mock Simulator & Test Series Aggregator
- **Anytime Mock Exam Portal:**
  - Full-length and sprint mocks formatted in the authentic IIT CBT pattern (Single Choice $+4/-1$, Multi-Correct with partial $+1/+2/+3$ and $-2$, and Numerical/Integer $+4/0$).
  - Question Palette (Visited, Not Visited, Answered, Marked for Review).
  - External Test Series Registry: Track schedules for Allen Leader, FIITJEE AITS, MathonGo, Resonance, etc.
  - **Post-Mock AI Autopsy:** Diagnoses question selection efficiency, negative mark leaks, and endurance drops.

### 4. 🏫 School & 12th Board Hub (95%+ Target)
- **Pre-Board & Practical Tracker:** Log school tests and analyze marks lost in subjective papers.
- **CBSE 12th Board High-Yield Checklist:** Guaranteed 5-mark derivations and theory questions across Physics (Lens Maker, Huygens proofs, AC Generator), Chemistry (Reaction mechanisms, VBT/CFT), and Mathematics (Shortest distance between skew lines, King's rule integrals, Bayes' theorem).
- **Subjective Step-Marking Audit:** AI action plan to ensure school answer-writing reinforces JEE clarity without stealing time.

### 5. 📅 Google Calendar & Smart Study Planner
- **Spaced Repetition & Daily Blocks:** Morning high-retention drills, school hours, afternoon deep work, evening mocks, and night reviews.
- **1-Click Google Calendar Sync:** Direct clickable URLs to add study blocks and exam dates into your Google Calendar.
- **RFC `.ics` Export:** Export complete schedule for Google Calendar, Apple Calendar, or Outlook.

### 6. 🧠 AIR-1 AI Mentor & Mental Fortitude Fortress
- **Powered by FreeLLM API** (`https://my-freellmapi-server.onrender.com/v1`, models: `auto`, `gemini-3.8-flash`, `deepseek-v4-flash`, etc.).
- Persona: Elite Kota Head of Department + Sports Performance Psychologist.
- Features: Instant panic defuser for mock test anxiety, deep conceptual doubt breakdown, and daily mental conditioning.

### 7. 📚 Curated Knowledge Vault & Live Web Scraper
- Pre-loaded high-yield cheat sheets from **DexterChem** (EAS directing codes, Spectrochemical series), **JEE Archive & JEEBOOKS.IN** (45-year problem blueprints), **Kota Classroom Notes** (3-round paper attempt strategy), and official **NTA / CBSE** 2026 syllabi.
- Built-in web scraper to ingest and summarize educational notes from public URLs.

---

## 🚀 How to Run the Application

### Prerequisites:
- Python 3.10+ (Pre-installed with `fastapi`, `uvicorn`, `beautifulsoup4`, `requests`)

### Starting the Server:
```bash
python run_app.py
```
Open your browser at:
👉 **[http://localhost:8000](http://localhost:8000)**
