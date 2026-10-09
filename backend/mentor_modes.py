"""
JEE AIR-1 Mentor Modes & Multi-Disciplinary Socratic Engine
===========================================================
Section 8: Build an AI tutor that teaches through questioning.
The tutor must distinguish between helping a student understand and simply handing
over the solution. It implements 10 distinct teaching modes:
1. Socratic mode (asks guiding questions to spark discovery)
2. Hint ladder (3 tiers of progressive hints without revealing the answer)
3. Concept repair (re-explains the missing prerequisite)
4. Worked-example mode (validated step-by-step reasoning)
5. Exam drill mode (minimal interruption, strict timing)
6. Teach-back mode (student explains in own words, AI probes assumptions)
7. Compare methods (explains valid alternative approaches and trade-offs)
8. Doubt resolution (grounded in verified NCERT and syllabus facts)
9. Board evaluation (rubric-based feedback on written derivations)
10. Oral viva (spoken/typed conceptual questions without multiple-choice crutches)
+ The "Prove-It" Challenge (justifying formulas, assumptions, and limiting cases)
"""

from typing import Dict, List, Optional

TEACHING_MODES = [
    "socratic",
    "hint_ladder",
    "concept_repair",
    "worked_example",
    "exam_drill",
    "teach_back",
    "compare_methods",
    "doubt_resolution",
    "board_evaluation",
    "oral_viva",
    "prove_it_challenge"
]

def format_mentor_mode_prompt(mode: str, topic: str, user_query: str) -> Dict:
    """
    Generates specialized pedagogic framing for each of the 10 teaching modes.
    """
    if mode == "socratic":
        system_instruction = (
            "You are an AIR-1 Socratic Mentor. DO NOT give the student the final equation or answer directly! "
            "Instead, ask 1 or 2 targeted, incisive questions about the physical constraints, free-body diagram, "
            "or coordinate frame to guide them to discover the law themselves."
        )
    elif mode == "hint_ladder":
        system_instruction = (
            "You are an AIR-1 Hint Ladder Engine. Break your assistance into 3 strict progressive tiers:\n"
            "• Tier 1: General Physical Principle (e.g. 'Consider conservation of mechanical energy')\n"
            "• Tier 2: Specific Mathematical Relation (e.g. 'Relate angular velocity to linear velocity using v = omega * R')\n"
            "• Tier 3: Coordinate Step (e.g. 'Set up the integral with limits from 0 to R/2')\n"
            "Only reveal Tier 1 first, prompting the student to attempt the next step."
        )
    elif mode == "teach_back":
        system_instruction = (
            "You are testing the student under the 'Teach-Back Challenge'. The student is explaining a concept. "
            "Evaluate their explanation strictly: check for (1) stated assumptions, (2) mathematical conditions, "
            "and (3) limiting edge cases. Probe where their intuition is loose."
        )
    elif mode == "prove_it_challenge":
        system_instruction = (
            "You are issuing the AIR-1 'Prove-It' Challenge. After learning a formula, require the student to: "
            "(1) State the exact physical assumptions under which it holds, "
            "(2) Test what happens in the extreme limit (e.g. m -> 0, or r -> infinity), "
            "(3) Verify dimensional homogeneity. Challenge them with a boundary test."
        )
    elif mode == "compare_methods":
        system_instruction = (
            "You are comparing two valid problem-solving approaches: "
            "Method A (Standard algebraic brute force) vs Method B (Symmetry / King's property / Energy method). "
            "Explain the algebraic trade-offs, computation time, and error probability of both."
        )
    elif mode == "oral_viva":
        system_instruction = (
            "Conduct an AIR-1 Oral Viva: Ask 3 rapid, deep conceptual questions with NO multiple-choice options. "
            "Require direct reasoning. Do not let them rely on MCQ option elimination."
        )
    else:
        system_instruction = (
            "You are Kaustav's Brother's AIR-1 Personal AI Mentor. Be rigorous, concise, mathematically exact, "
            "and encouraging. Keep responses focused on foundational mastery and exam-day precision."
        )

    return {
        "mode": mode,
        "topic": topic,
        "system_instruction": system_instruction,
        "prompt_template": f"[{mode.upper()} PROTOCOL]\nTopic: {topic}\nStudent says: {user_query}"
    }

def get_prove_it_challenge(concept_id: str) -> Dict:
    """
    Returns a customized Prove-It challenge for a given concept.
    """
    challenges = {
        "phy_rot_01": {
            "title": "Prove-It: Pure Rolling on Accelerating Planks",
            "prompt": "State the exact kinematic relation between $a_{cm}$, $\\alpha$, and $a_{plank}$. Under what friction condition does rolling transition to skidding?",
            "expected_criteria": ["$a_{contact} = a_{cm} \\pm R\\alpha = a_{plank}$", "Static friction $f_s \\le \\mu_s N$"],
            "limiting_test": "What happens if $\\mu_s = 0$?"
        },
        "phy_es_01": {
            "title": "Prove-It: Electric Potential Gradient",
            "prompt": "Prove that the electrostatic field is always perpendicular to equipotential surfaces using the relation $\\vec{E} = -\\vec{\\nabla} V$.",
            "expected_criteria": ["$dV = -\\vec{E} \\cdot d\\vec{r} = 0$ along equipotential surface", "$\\implies \\vec{E} \\perp d\\vec{r}$"],
            "limiting_test": "What is the electric field inside a hollow spherical conductor at static equilibrium?"
        }
    }
    return challenges.get(concept_id, {
        "title": "Prove-It: Foundational Sanity Check",
        "prompt": "State the limiting boundary conditions and verify the dimensional consistency of the governing formula.",
        "expected_criteria": ["Dimensional consistency", "Limiting cases at $t \\to 0$ and $t \\to \\infty$"],
        "limiting_test": "Does this law hold in non-inertial reference frames?"
    })
