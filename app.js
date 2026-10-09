
function localChemCard(subject, topic) {
  const t = (topic || '').toLowerCase();
  if (t.includes('electro') || t.includes('nernst') || t.includes('cell')) {
    return {
      title: 'Nernst equation, not a waiting spinner',
      concept_nugget: 'At 298 K, $E = E^\\circ - \\dfrac{0.059}{n}\\log Q$. Q uses the same form as K, but with the actual concentrations. A tenfold change in Q moves E by $0.059/n$ volt. Trap: n is electrons in the balanced cell reaction, not the stoichiometric coefficient you first see.',
      key_takeaway: 'As the cell runs, Q rises and E falls. At equilibrium E = 0 and Q = K.',
      pyq_question: 'Zn|Zn2+(0.01 M)||Cu2+(1 M)|Cu has E° = 1.10 V. What is E at 298 K?',
      options: ['1.16 V', '1.04 V', '1.10 V', '0.99 V'],
      correct_option_index: 0,
      explanation: 'n = 2. Q = [Zn2+]/[Cu2+] = 0.01. E = 1.10 - (0.059/2) log(0.01) = 1.10 - 0.0295(-2) = 1.10 + 0.059 = 1.159 V.'
    };
  }
  return {
    title: subject + ': ' + topic,
    concept_nugget: 'Pages cannot run the Python generator, so this card is built on the device. State the defining relation, the condition where it fails, and one JEE trap before you look at a solution.',
    key_takeaway: 'A card is not finished until you answer the check without the notes.',
    pyq_question: 'Which condition makes the standard result for ' + topic + ' fail?',
    options: ['The assumption in the derivation is dropped', 'The formula is memorised', 'The unit is SI', 'The chapter name matches'],
    correct_option_index: 0,
    explanation: 'FreeLLM did not return JSON in time. Use this check, then retry. Do not treat this as a past-paper question.'
  };
}
async function generateCardFast(subject, topic) {
  const local = localChemCard(subject, topic);
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 8000);
  try {
    const res = await fetch('https://my-freellmapi-server.onrender.com/v1/chat/completions', {
      method: 'POST',
      signal: ctrl.signal,
      headers: {
        'Authorization': 'Bearer freellmapi-aee0bcf8947be1ae92447fee0175f33e3277b275372f2931',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'auto',
        temperature: 0.3,
        max_tokens: 500,
        messages: [{role:'user', content:'Return strict JSON only with keys title, concept_nugget, key_takeaway, pyq_question, options, correct_option_index, explanation. Subject: '+subject+'. Topic: '+topic+'. Under 160 words. Not a past-paper claim.'}]
      })
    });
    const text = await res.text();
    if (!text.trim().startsWith('{') && !text.trim().startsWith('[')) return local;
    const data = JSON.parse(text);
    const raw = data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content || '';
    const start = raw.indexOf('{');
    const end = raw.lastIndexOf('}');
    if (start < 0 || end < start) return local;
    const card = JSON.parse(raw.slice(start, end+1));
    return card.title ? card : local;
  } catch (e) {
    return local;
  } finally {
    clearTimeout(timer);
  }
}
/**
 * JEE Advanced AIR-1 & CBSE 95%+ Companion Client Application
 * Handles diagnostic tests, SoloLearn micro-learning loop, CBT mock simulator,
 * school tracker, Google calendar links, and FreeLLM mentor chat.
 */

// Global Application State
const state = {
  currentTab: 'dashboard',
  profile: null,
  diagnosticQuestions: [],
  diagnosticIndex: 0,
  diagnosticAnswers: {},
  soloModule: null,
  soloStepIndex: 0,
  activeMock: null,
  cbtResponses: {},
  cbtStatus: {}, // 'not_visited', 'not_answered', 'answered', 'review', 'answered_review'
  cbtCurrentIndex: 0,
  cbtCurrentSection: 'Physics',
  cbtTimerInterval: null,
  cbtSecondsRemaining: 0,
  chatHistory: []
};

// Markdown parser that protects LaTeX formulas from underscore/asterisk mangling
function renderMarkdownSafe(text) {
  if (!text) return '';
  const mathBlocks = [];

  // Protect $$ ... $$
  let protectedText = text.replace(/\$\$([\s\S]+?)\$\$/g, (_, math) => {
    mathBlocks.push({ display: true, math });
    return `%%%MATH_BLOCK_${mathBlocks.length - 1}%%%`;
  });

  // Protect $ ... $
  protectedText = protectedText.replace(/(?<!\\)\$([^\$\n]+?)(?<!\\)\$/g, (_, math) => {
    mathBlocks.push({ display: false, math });
    return `%%%MATH_INLINE_${mathBlocks.length - 1}%%%`;
  });

  // Protect \[ ... \]
  protectedText = protectedText.replace(/\\\[([\s\S]+?)\\\]/g, (_, math) => {
    mathBlocks.push({ display: true, math });
    return `%%%MATH_BLOCK_${mathBlocks.length - 1}%%%`;
  });

  // Protect \( ... \)
  protectedText = protectedText.replace(/\\\(([\s\S]+?)\\\)/g, (_, math) => {
    mathBlocks.push({ display: false, math });
    return `%%%MATH_INLINE_${mathBlocks.length - 1}%%%`;
  });

  let html = (window.marked && typeof marked.parse === 'function') ? marked.parse(protectedText) : protectedText;

  // Restore math blocks
  html = html.replace(/%%%MATH_BLOCK_(\d+)%%%/g, (_, idx) => {
    const item = mathBlocks[parseInt(idx)];
    return item ? `$$${item.math}$$` : '';
  });
  html = html.replace(/%%%MATH_INLINE_(\d+)%%%/g, (_, idx) => {
    const item = mathBlocks[parseInt(idx)];
    return item ? `$${item.math}$` : '';
  });

  return html;
}

// Scans text nodes in a DOM element and automatically wraps bare LaTeX math
function autoWrapBareLatex(container) {
  if (!container || !container.childNodes) return;
  const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, null, false);
  const textNodes = [];
  while (walker.nextNode()) {
    const node = walker.currentNode;
    const parent = node.parentNode;
    if (!parent) continue;
    const tag = parent.nodeName.toLowerCase();
    if (['script', 'style', 'textarea', 'pre', 'code'].includes(tag)) continue;
    if (parent.classList && (parent.classList.contains('katex') || parent.classList.contains('katex-html'))) continue;
    const val = node.nodeValue;
    // Check if contains bare LaTeX commands not enclosed in $ or $$
    if (val && /\\[a-zA-Z]+/.test(val)) {
      if (!val.includes('$') && !val.includes('\\(') && !val.includes('\\[')) {
        textNodes.push(node);
      }
    }
  }

  for (const node of textNodes) {
    let text = node.nodeValue;
    const mathCmdRegex = /(\\(?:frac|sum|int|vec|sqrt|alpha|beta|gamma|theta|lambda|Delta|mu|sigma|omega|oint|nabla|text|times|pm|cdot|partial|in|infty|approx|leq|geq|le|ge|neq|equiv|rightarrow|leftarrow|implies|sin|cos|tan|ln|log|exp)\b[^\n$]*)/g;
    if (mathCmdRegex.test(text)) {
      const span = document.createElement('span');
      span.innerHTML = text.replace(mathCmdRegex, (match) => `$${match.trim()}$`);
      if (node.parentNode) {
        node.parentNode.replaceChild(span, node);
      }
    }
  }
}

// Auto-render Math with KaTeX
function renderMath(target = document.body) {
  if (!target) return;
  autoWrapBareLatex(target);

  if (window.renderMathInElement) {
    try {
      window.renderMathInElement(target, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '$', right: '$', display: false },
          { left: '\\[', right: '\\]', display: true },
          { left: '\\(', right: '\\)', display: false },
          { left: '\\\\(', right: '\\\\)', display: false },
          { left: '\\\\[', right: '\\\\]', display: true }
        ],
        ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'],
        throwOnError: false
      });
    } catch (err) {
      console.warn('KaTeX render error:', err);
    }
  } else {
    setTimeout(() => renderMath(target), 120);
  }
}

// Initial Boot
document.addEventListener('DOMContentLoaded', async () => {
  if (window.lucide) lucide.createIcons();
  await loadProfile();
  await loadDashboardData();
  renderMath();
  startCbtQuestionTimer();
});

// Tab Router
function switchTab(tabId) {
  state.currentTab = tabId;
  document.querySelectorAll('.tab-pane').forEach(el => el.classList.add('hidden'));
  document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
  
  document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
  
  const targetPane = document.getElementById(`tab-${tabId}`);
  const targetNav = document.getElementById(`nav-${tabId}`);
  if (targetPane) {
    targetPane.classList.remove('hidden');
    targetPane.classList.add('active');
  }
  if (targetNav) targetNav.classList.add('active');

  // Trigger lazy loading of tab content
  if (tabId === 'diagnostic') loadDiagnosticTab();
  else if (tabId === 'sololearn') loadSoloLearnTab();
  else if (tabId === 'mock-exam') loadMockExamTab();
  else if (tabId === 'materials') loadMaterialsTab();
  else if (tabId === 'visuals') loadVisualsTab();
  else if (tabId === 'school-sync') loadSchoolSyncTab();
  else if (tabId === 'calendar-plan') loadCalendarTab();
  else if (tabId === 'mentor') loadMentorTab();
  else if (tabId === 'knowledge-vault') loadKnowledgeVaultTab();
  else if (tabId === 'tactics') loadTacticsTab();
  else if (tabId === 'errors') loadErrorsTab();
  else if (tabId === 'omni-planner') loadOmniPlannerTab();
  else if (tabId === 'cbse-studio') loadCbseStudioTab();
  else if (tabId === 'wellness') loadWellnessTab();
  else if (tabId === 'profile') loadProfileTab();
  else if (tabId === 'dashboard') loadDashboardData();

  // Highlight mobile nav button if exists
  document.querySelectorAll('nav.md\\:hidden button').forEach(b => {
    b.classList.remove('text-amber-400', 'text-sky-400', 'font-bold');
    b.classList.add('text-slate-400');
  });
  const mBtn = document.getElementById(`m-nav-${tabId}`);
  if (mBtn) {
    mBtn.classList.remove('text-slate-400');
    mBtn.classList.add('text-amber-400', 'font-bold');
  }

  if (window.lucide) lucide.createIcons();
  setTimeout(renderMath, 100);
}

// ----------------- PROFILE & DASHBOARD -----------------
async function loadProfile() {
  try {
    const res = await fetch('/api/profile');
    state.profile = await res.json();
    if (state.profile && state.profile.has_profile && state.profile.name) {
      document.getElementById('profile-name').innerText = state.profile.name;
      document.getElementById('streak-counter').innerText = `${state.profile.streak_days !== undefined ? state.profile.streak_days : 0} Days`;
      document.getElementById('xp-counter').innerText = `${state.profile.xp !== undefined ? state.profile.xp : 0} XP`;
      document.getElementById('fortitude-rating').innerText = `${state.profile.mental_fortitude_rating !== undefined ? state.profile.mental_fortitude_rating : 10.0} / 10`;
    } else {
      console.log('No profile detected. Brother may click Re-Onboard on Profile Tab or header.');
    }
  } catch (err) {
    console.error('Failed to load profile:', err);
  }
}

async function loadDashboardData() {
  try {
    // 0. Load Daily AIR-1 Missions (Diagnostic-calibrated)
    await loadDailyGoals();

    // 1. Check latest diagnostic
    const diagRes = await fetch('/api/diagnostic/latest');
    const diag = await diagRes.json();
    if (diag.has_diagnostic) {
      document.getElementById('dash-diag-badge').innerText = 'Completed';
      document.getElementById('dash-diag-badge').className = 'text-xs bg-emerald-500/10 text-emerald-400 px-2.5 py-1 rounded-full border border-emerald-500/30';
      document.getElementById('dash-diag-score').innerText = `${diag.total_score} / ${diag.max_score}`;
      const pct = Math.round((diag.total_score / diag.max_score) * 100);
      document.getElementById('dash-diag-bar').style.width = `${pct}%`;
      const weak = diag.weak_topics || [];
      document.getElementById('dash-diag-desc').innerText = `Weak Lags detected: ${weak.slice(0, 2).join(', ')}`;
    } else {
      document.getElementById('dash-diag-badge').innerText = 'Pending';
      document.getElementById('dash-diag-badge').className = 'text-xs bg-amber-500/10 text-amber-400 px-2.5 py-1 rounded-full border border-amber-500/30';
      document.getElementById('dash-diag-score').innerText = 'Not Taken Yet';
      document.getElementById('dash-diag-bar').style.width = '0%';
      document.getElementById('dash-diag-desc').innerText = 'Click below to take your 12-question Baseline Diagnostic.';
    }

    // 2. Upcoming School Test
    const schoolRes = await fetch('/api/school/tests');
    const schoolData = await schoolRes.json();
    if (schoolData.upcoming && schoolData.upcoming.length > 0) {
      const nextTest = schoolData.upcoming[0];
      document.getElementById('dash-next-school').innerText = `${nextTest.test_title} (${nextTest.test_date})`;
    } else {
      document.getElementById('dash-next-school').innerText = 'None logged yet';
    }

    // 3. Calendar events
    const calRes = await fetch('/api/calendar/events');
    const events = await calRes.json();
    const container = document.getElementById('dash-events-list');
    container.innerHTML = '';
    if (events.length === 0) {
      container.innerHTML = `
        <div class="p-3.5 bg-slate-950 rounded-xl border border-slate-800 text-xs text-slate-400 flex items-center justify-between">
          <span>No scheduled events yet. Add your study blocks or sync with Google Calendar.</span>
          <button onclick="switchTab('calendar-plan')" class="text-blue-400 hover:underline font-bold">+ Schedule</button>
        </div>
      `;
    } else {
      events.slice(0, 3).forEach(ev => {
        const div = document.createElement('div');
        div.className = 'flex items-center justify-between p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-xs';
        div.innerHTML = `
          <div class="flex items-center gap-3">
            <div class="w-2 h-2 rounded-full bg-amber-400"></div>
            <div>
              <div class="font-bold text-slate-200">${ev.title}</div>
              <div class="text-[11px] text-slate-400 font-mono">${ev.start_time} - ${ev.end_time}</div>
            </div>
          </div>
          <a href="${ev.google_calendar_url}" target="_blank" class="px-2.5 py-1 bg-blue-500/10 text-blue-400 hover:bg-blue-500 hover:text-white rounded-lg border border-blue-500/30 text-[11px] font-semibold transition-all">
            + Google Cal
          </a>
        `;
        container.appendChild(div);
      });
    }
  } catch (err) {
    console.error('Failed to load dashboard data:', err);
  }
}

// ----------------- 1. DIAGNOSTIC EVALUATION -----------------
async function loadDiagnosticTab() {
  const res = await fetch('/api/diagnostic/latest');
  const diag = await res.json();
  if (diag.has_diagnostic) {
    renderDiagnosticResults(diag);
  }
}

async function startDiagnosticTest() {
  try {
    const res = await fetch('/api/diagnostic/questions');
    state.diagnosticQuestions = await res.json();
    state.diagnosticIndex = 0;
    state.diagnosticAnswers = {};

    document.getElementById('btn-start-diag').classList.add('hidden');
    document.getElementById('diag-runner').classList.remove('hidden');
    document.getElementById('diag-results-view').classList.add('hidden');

    renderDiagnosticQuestion();
  } catch (err) {
    alert('Failed to load diagnostic questions: ' + err.message);
  }
}

function renderDiagnosticQuestion() {
  const q = state.diagnosticQuestions[state.diagnosticIndex];
  if (!q) return;

  document.getElementById('diag-q-index').innerText = `Question ${state.diagnosticIndex + 1} of ${state.diagnosticQuestions.length}`;
  document.getElementById('diag-subject-badge').innerText = q.subject;
  document.getElementById('diag-level-badge').innerText = q.level;
  document.getElementById('diag-topic-name').innerHTML = `${q.topic} • <span class="text-amber-400 font-mono font-bold">${q.official_pyq_source || 'Authentic Official Exam'}</span>`;

  document.getElementById('diag-question-text').innerHTML = q.question;

  const optContainer = document.getElementById('diag-options-container');
  optContainer.innerHTML = '';

  const chosen = state.diagnosticAnswers[q.id];

  q.options.forEach((optText, idx) => {
    const btn = document.createElement('div');
    const isSelected = chosen === idx;
    btn.className = `p-4 rounded-xl border cursor-pointer text-xs flex items-center justify-between transition-all ${
      isSelected 
        ? 'bg-cyan-500/10 border-cyan-400 text-cyan-200 shadow-md shadow-cyan-500/10' 
        : 'bg-slate-950 border-slate-800 text-slate-300 hover:border-slate-700'
    }`;
    btn.innerHTML = `
      <div class="flex items-center gap-3">
        <span class="w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs ${isSelected ? 'bg-cyan-400 text-slate-950' : 'bg-slate-800 text-slate-400'}">
          ${String.fromCharCode(65 + idx)}
        </span>
        <span class="math-content">${optText}</span>
      </div>
      ${isSelected ? '<i data-lucide="check-circle" class="w-4 h-4 text-cyan-400"></i>' : ''}
    `;
    btn.onclick = () => {
      state.diagnosticAnswers[q.id] = idx;
      renderDiagnosticQuestion();
    };
    optContainer.appendChild(btn);
  });

  document.getElementById('btn-prev-diag').disabled = (state.diagnosticIndex === 0);
  if (window.lucide) lucide.createIcons();
  renderMath();
  startCbtQuestionTimer();
}

function nextDiagQuestion() {
  if (state.diagnosticIndex < state.diagnosticQuestions.length - 1) {
    state.diagnosticIndex++;
    renderDiagnosticQuestion();
  }
}

function prevDiagQuestion() {
  if (state.diagnosticIndex > 0) {
    state.diagnosticIndex--;
    renderDiagnosticQuestion();
  }
}

async function submitDiagnosticForm() {
  if (!confirm('Ready to submit your diagnostic test and generate your AIR-1 lag analysis?')) return;

  const sessionId = 'diag_' + Date.now();
  try {
    document.getElementById('btn-submit-diag').innerText = 'Analyzing with FreeLLM AI...';
    document.getElementById('btn-submit-diag').disabled = true;

    const res = await fetch('/api/diagnostic/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: jsonFormat({
        session_id: sessionId,
        answers: state.diagnosticAnswers
      })
    });
    const result = await res.json();

    document.getElementById('diag-runner').classList.add('hidden');
    document.getElementById('btn-start-diag').classList.remove('hidden');
    document.getElementById('btn-start-diag').innerText = 'Retake Diagnostic Test';
    document.getElementById('diag-results-view').classList.remove('hidden');

    renderDiagnosticResults(result);
    loadProfile();
  } catch (err) {
    alert('Error submitting test: ' + err.message);
  } finally {
    document.getElementById('btn-submit-diag').innerText = 'Submit Test & Generate AI Diagnosis';
    document.getElementById('btn-submit-diag').disabled = false;
  }
}

function renderDiagnosticResults(data) {
  const container = document.getElementById('diag-results-view');
  const summary = data.score_summary || {
    total_score: data.total_score,
    max_score: data.max_score,
    percentage: Math.round((data.total_score / data.max_score) * 100),
    physics: data.physics_score,
    chemistry: data.chemistry_score,
    maths: data.maths_score
  };

  const ai = data.ai_report || data.ai_recommendation || {};
  const weak = data.weak_topics || [];
  const strong = data.strong_topics || [];

  container.innerHTML = `
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-slate-900 border border-cyan-500/30 rounded-2xl p-5 text-center">
        <span class="text-xs text-slate-400">Total Diagnostic Score</span>
        <div class="text-3xl font-black text-cyan-400 mt-1">${summary.total_score} <span class="text-sm text-slate-500">/ ${summary.max_score}</span></div>
        <span class="text-xs text-cyan-300 font-mono mt-1 inline-block">${summary.percentage}% Accuracy</span>
      </div>
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 text-center">
        <span class="text-xs text-slate-400">Physics</span>
        <div class="text-2xl font-bold text-white mt-1">${summary.physics}</div>
      </div>
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 text-center">
        <span class="text-xs text-slate-400">Chemistry</span>
        <div class="text-2xl font-bold text-white mt-1">${summary.chemistry}</div>
      </div>
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 text-center">
        <span class="text-xs text-slate-400">Mathematics</span>
        <div class="text-2xl font-bold text-white mt-1">${summary.maths}</div>
      </div>
    </div>

    <!-- AI Verdict & Weak Topics Breakdown -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-4">
        <h4 class="font-bold text-sm text-amber-400 flex items-center gap-2">
          <i data-lucide="zap" class="w-4 h-4"></i> Critical Conceptual Lags Detected
        </h4>
        <div class="space-y-2">
          ${weak.map(t => `
            <div class="flex items-center justify-between p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-xs">
              <span class="font-semibold text-red-300">${t}</span>
              <span class="text-red-400 text-[11px] font-mono">Lagging</span>
            </div>
          `).join('') || '<p class="text-xs text-slate-400">No major lags detected!</p>'}
        </div>

        <h4 class="font-bold text-sm text-emerald-400 flex items-center gap-2 pt-2">
          <i data-lucide="shield-check" class="w-4 h-4"></i> Solidified Strength Areas
        </h4>
        <div class="space-y-2">
          ${strong.map(t => `
            <div class="flex items-center justify-between p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-xs">
              <span class="font-semibold text-emerald-300">${t}</span>
              <span class="text-emerald-400 text-[11px] font-mono">Solid</span>
            </div>
          `).join('') || '<p class="text-xs text-slate-400">Keep practicing.</p>'}
        </div>
      </div>

      <!-- AI Plan & Board Gap -->
      <div class="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-4">
        <h4 class="font-bold text-sm text-cyan-400 flex items-center gap-2">
          <i data-lucide="sparkles" class="w-4 h-4"></i> AI Mentor Strategic Prescription
        </h4>
        <p class="text-xs text-slate-300 leading-relaxed italic bg-slate-950 p-4 rounded-xl border border-slate-800">
          "${ai.overall_verdict || 'Evaluation recorded.'}"
        </p>

        <div class="space-y-2 text-xs">
          <span class="font-bold text-pink-400 block">Board 95%+ Synergy Impact:</span>
          <p class="text-slate-300 bg-pink-500/5 border border-pink-500/20 p-3 rounded-xl leading-relaxed">
            ${ai.board_synergy_gap || ai.board_vs_jee_gap || 'Focus on written derivations alongside numerical speed.'}
          </p>
        </div>

        <div class="space-y-2 text-xs pt-2">
          <span class="font-bold text-amber-400 block">7-Day Recovery Plan:</span>
          <ul class="list-disc list-inside text-slate-300 space-y-1">
            ${(ai.air1_recovery_plan || []).map(p => `<li>${p}</li>`).join('')}
          </ul>
        </div>
      </div>
    </div>
  `;
  if (window.lucide) lucide.createIcons();
  renderMath();
  startCbtQuestionTimer();
}


// ----------------- 2. SOLOLEARN MICRO-LEARNING -----------------
async function loadSoloLearnTab() {
  try {
    const res = await fetch('/api/sololearn/modules');
    const modules = await res.json();
    const container = document.getElementById('sololearn-modules-list');
    container.innerHTML = '';

    modules.forEach(m => {
      const card = document.createElement('div');
      card.className = 'bg-slate-900/70 border border-slate-800 hover:border-emerald-500/50 rounded-2xl p-5 space-y-3 cursor-pointer transition-all card-glow-cyan';
      card.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">${m.subject}</span>
          <span class="text-xs text-amber-400 font-bold flex items-center gap-1"><i data-lucide="zap" class="w-3.5 h-3.5"></i> ${m.xp_reward} XP</span>
        </div>
        <h3 class="font-bold text-sm text-white">${m.title}</h3>
        <p class="text-xs text-slate-400">${m.topic}</p>
        <div class="pt-2 flex justify-between items-center text-xs text-slate-400 border-t border-slate-800">
          <span>${m.total_steps} Bite-Sized Steps</span>
          <span class="text-emerald-400 font-bold">Start Drill $\\rightarrow$</span>
        </div>
      `;
      card.onclick = () => launchSoloModule(m.module_id);
      container.appendChild(card);
    });
    if (window.lucide) lucide.createIcons();
    renderMath();
  } catch (err) {
    console.error('Failed to load modules:', err);
  }
}

async function launchSoloModule(moduleId) {
  try {
    const res = await fetch(`/api/sololearn/modules/${moduleId}`);
    state.soloModule = await res.json();
    state.soloStepIndex = 0;

    document.getElementById('sololearn-player').classList.remove('hidden');
    renderSoloStep();
    window.scrollTo({ top: document.getElementById('sololearn-player').offsetTop - 80, behavior: 'smooth' });
  } catch (err) {
    alert('Failed to launch module: ' + err.message);
  }
}

function renderSoloStep() {
  const m = state.soloModule;
  if (!m) return;
  const step = m.steps[state.soloStepIndex];
  if (!step) return;

  document.getElementById('solo-step-indicator').innerText = `Step ${state.soloStepIndex + 1} of ${m.steps.length}`;
  const badge = document.getElementById('solo-step-badge');
  const contentBox = document.getElementById('solo-content-box');
  const feedbackBox = document.getElementById('solo-feedback-box');
  feedbackBox.classList.add('hidden');

  if (step.type === 'concept_nugget') {
    badge.innerText = '⚡ High-Yield Concept Nugget';
    badge.className = 'px-2.5 py-1 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 text-xs font-mono font-bold';
    
    contentBox.innerHTML = `
      <h3 class="text-lg font-bold text-white">${step.title}</h3>
      <div class="text-sm text-slate-200 leading-relaxed space-y-3 math-content">
        ${renderMarkdownSafe(step.content)}
      </div>
      <div class="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs text-amber-300 flex items-center gap-2">
        <i data-lucide="lightbulb" class="w-4 h-4 text-amber-400 shrink-0"></i>
        <span><strong>Key Takeaway:</strong> ${step.key_takeaway}</span>
      </div>
    `;
    document.getElementById('btn-solo-next').innerText = 'Got It! Next Question $\\rightarrow$';
    document.getElementById('btn-solo-next').disabled = false;
  } else if (step.type === 'active_recall') {
    badge.innerText = `🎯 Active Recall PYQ Patch (${step.pyq_source})`;
    badge.className = 'px-2.5 py-1 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 text-xs font-mono font-bold';

    contentBox.innerHTML = `
      <div class="text-base text-slate-100 font-medium leading-relaxed math-content mb-4">
        ${step.question}
      </div>
      <div class="space-y-3" id="solo-options-list">
        ${step.options.map((opt, idx) => `
          <button onclick="handleSoloOptionClick(${idx})" class="w-full text-left p-4 rounded-xl border border-slate-800 bg-slate-950 hover:border-slate-700 text-xs text-slate-200 flex items-center gap-3 transition-all" id="solo-opt-${idx}">
            <span class="w-6 h-6 rounded-full bg-slate-800 flex items-center justify-center font-bold text-xs">${String.fromCharCode(65 + idx)}</span>
            <span class="math-content flex-1">${opt}</span>
          </button>
        `).join('')}
      </div>
    `;
    document.getElementById('btn-solo-next').innerText = 'Continue $\\rightarrow$';
    document.getElementById('btn-solo-next').disabled = true; // Wait for answer selection
  }

  document.getElementById('btn-solo-prev').disabled = (state.soloStepIndex === 0);
  if (window.lucide) lucide.createIcons();
  renderMath();
  startCbtQuestionTimer();
}

async function handleSoloOptionClick(chosenIdx) {
  const m = state.soloModule;
  const step = m.steps[state.soloStepIndex];

  try {
    const res = await fetch('/api/sololearn/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: jsonFormat({
        module_id: m.module_id,
        step_index: state.soloStepIndex,
        chosen_option: chosenIdx
      })
    });
    const result = await res.json();

    // Disable all options
    step.options.forEach((_, idx) => {
      const btn = document.getElementById(`solo-opt-${idx}`);
      if (btn) btn.disabled = true;
    });

    const chosenBtn = document.getElementById(`solo-opt-${chosenIdx}`);
    const correctBtn = document.getElementById(`solo-opt-${result.correct_option}`);

    if (result.is_correct) {
      if (chosenBtn) {
        chosenBtn.className = 'w-full text-left p-4 rounded-xl border border-emerald-500 bg-emerald-500/10 text-xs text-emerald-200 flex items-center gap-3';
      }
    } else {
      if (chosenBtn) {
        chosenBtn.className = 'w-full text-left p-4 rounded-xl border border-red-500 bg-red-500/10 text-xs text-red-200 flex items-center gap-3';
      }
      if (correctBtn) {
        correctBtn.className = 'w-full text-left p-4 rounded-xl border border-emerald-500 bg-emerald-500/10 text-xs text-emerald-200 flex items-center gap-3';
      }
    }

    const feedbackBox = document.getElementById('solo-feedback-box');
    feedbackBox.classList.remove('hidden');
    feedbackBox.className = `p-4 rounded-xl text-xs space-y-2 border ${result.is_correct ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-red-500/10 border-red-500/30 text-red-300'}`;
    feedbackBox.innerHTML = `
      <div class="font-bold flex items-center gap-2">
        <i data-lucide="${result.is_correct ? 'check-circle' : 'alert-circle'}" class="w-4 h-4"></i>
        ${result.is_correct ? `Spot On! +${result.xp_earned} XP Added` : `IIT-JEE Trap Caught! (+5 Effort XP)`}
      </div>
      <p class="text-slate-300 math-content">${result.explanation}</p>
    `;

    document.getElementById('btn-solo-next').disabled = false;
    loadProfile();
    if (window.lucide) lucide.createIcons();
    renderMath();
  } catch (err) {
    alert('Verification error: ' + err.message);
  }
}

function nextSoloStep() {
  if (state.soloStepIndex < state.soloModule.steps.length - 1) {
    state.soloStepIndex++;
    renderSoloStep();
  } else {
    alert('🎉 Brilliant! Module completed. Your mastery rank has increased.');
    document.getElementById('sololearn-player').classList.add('hidden');
    loadProfile();
  }
}

function prevSoloStep() {
  if (state.soloStepIndex > 0) {
    state.soloStepIndex--;
    renderSoloStep();
  }
}


// ----------------- 3. CBT MOCK EXAM ENGINE -----------------
async function loadMockExamTab() {
  try {
    const res = await fetch('/api/mocks');
    const mocks = await res.json();
    const container = document.getElementById('available-mocks-container');
    container.innerHTML = '';

    mocks.forEach(m => {
      const card = document.createElement('div');
      card.className = 'bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-4 hover:border-indigo-500/40 transition-all';
      card.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="text-xs px-2.5 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 font-bold">${m.exam_type}</span>
          <span class="text-xs text-slate-400 font-mono"><i data-lucide="clock" class="w-3.5 h-3.5 inline"></i> ${m.total_time_minutes} Mins</span>
        </div>
        <h3 class="text-base font-bold text-white">${m.title}</h3>
        <p class="text-xs text-slate-400">${m.description}</p>
        <div class="flex items-center justify-between pt-2 border-t border-slate-800 text-xs">
          <span class="text-slate-300 font-semibold">${m.total_marks} Marks</span>
          <button onclick="launchMockCbt('${m.mock_id}')" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl shadow-lg shadow-indigo-600/20">
            Launch CBT Test
          </button>
        </div>
      `;
      container.appendChild(card);
    });

    // Registered test series
    const seriesRes = await fetch('/api/test-series');
    state.allTestSeries = await seriesRes.json();
    populateSeriesFilterOptions();
    renderRegisteredSeriesList();

    if (window.lucide) lucide.createIcons();
    renderMath();
  } catch (err) {
    console.error('Failed to load mocks:', err);
  }
}

function escapeJs(str) {
  if (!str) return '';
  return String(str).replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

function populateSeriesFilterOptions() {
  const select = document.getElementById('series-filter-select');
  if (!select || !state.allTestSeries) return;
  const seriesNames = [...new Set(state.allTestSeries.map(s => s.series_name).filter(Boolean))];
  select.innerHTML = `<option value="ALL">All Enrolled Series (${state.allTestSeries.length} tests)</option>`;
  seriesNames.forEach(name => {
    const count = state.allTestSeries.filter(s => s.series_name === name).length;
    select.innerHTML += `<option value="${name}">${name} (${count} tests)</option>`;
  });
  if (state.selectedSeriesFilter && seriesNames.includes(state.selectedSeriesFilter)) {
    select.value = state.selectedSeriesFilter;
  }
}

function filterTestSeries(val) {
  state.selectedSeriesFilter = val;
  renderRegisteredSeriesList();
}

function renderRegisteredSeriesList() {
  const container = document.getElementById('registered-series-list');
  if (!container) return;
  container.innerHTML = '';

  const filter = state.selectedSeriesFilter || 'ALL';
  const list = (filter === 'ALL')
    ? (state.allTestSeries || [])
    : (state.allTestSeries || []).filter(s => s.series_name === filter);

  if (list.length === 0) {
    container.innerHTML = `
      <div class="text-center py-8 text-slate-500 text-xs border border-dashed border-slate-800 rounded-xl space-y-2">
        <i data-lucide="calendar-x" class="w-7 h-7 mx-auto text-slate-600"></i>
        <p class="font-medium text-slate-400">No test series schedule registered yet.</p>
        <p class="text-[11px] text-slate-500">
          Click <strong class="text-amber-400">"Generate AI 2027 Schedule"</strong> (e.g. for Testbook or on-demand series) or <strong class="text-indigo-400">"Ingest Schedule"</strong> (PDF / Timetable Image).
        </p>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
    return;
  }

  list.forEach(s => {
    const isAttempted = (s.status === 'attempted');
    const card = document.createElement('div');
    card.className = `p-4 rounded-xl border transition-all space-y-3 ${
      isAttempted ? 'bg-emerald-950/20 border-emerald-500/30' : 'bg-slate-950/90 border-slate-800 hover:border-slate-700'
    }`;

    const aiBadge = s.is_ai_scheduled 
      ? '<span class="px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30 text-[10px] font-mono">⚡ AI 2027 Schedule</span>'
      : '<span class="px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 text-[10px] font-mono">📄 Timetable Extract</span>';

    const examBadge = `<span class="px-2 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/30 text-[10px] font-bold">${s.exam_type}</span>`;

    const statusBadge = isAttempted
      ? `<span class="px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-[10px] font-bold">✅ Scored: ${s.score}/${s.total_marks} (${Math.round((s.score/s.total_marks)*100)}%)</span>`
      : `<span class="px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 text-[10px] font-medium">🕒 Scheduled</span>`;

    card.innerHTML = `
      <div class="flex items-center justify-between flex-wrap gap-2">
        <div class="flex items-center gap-2">
          <span class="font-bold text-white text-xs">${s.series_name}</span>
          <span class="font-mono text-slate-400 text-xs">#${s.test_number}</span>
          ${examBadge}
        </div>
        <div class="flex items-center gap-2">
          ${aiBadge}
          ${statusBadge}
        </div>
      </div>

      <div>
        <h4 class="text-sm font-bold text-slate-100">${s.test_title || s.test_number}</h4>
        <div class="text-[11px] text-slate-400 flex items-center gap-3 mt-1 flex-wrap">
          <span class="font-mono text-amber-400 font-semibold">📅 ${s.scheduled_date || 'Flexible'} (${s.scheduled_time || '09:00 - 12:00'})</span>
          <span class="text-slate-500 font-medium">🎯 Target: JEE 2027 AIR-1</span>
        </div>
      </div>

      ${s.syllabus ? `
        <div class="bg-slate-900/90 border border-slate-800/80 rounded-lg p-2.5 text-[11px] text-slate-300">
          <span class="font-bold text-slate-400 block mb-0.5">📚 Syllabus:</span>
          ${s.syllabus}
        </div>
      ` : ''}

      ${s.notes ? `
        <div class="text-[11px] text-slate-400 italic">
          💡 <span class="text-slate-300 font-medium">AIR-1 Benchmark:</span> ${s.notes}
        </div>
      ` : ''}

      <div class="flex items-center justify-between pt-2 border-t border-slate-800/80 flex-wrap gap-2 text-xs">
        <div class="flex items-center gap-2 flex-wrap">
          <button onclick="launchMockCbt('jm_mock1')" class="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-lg text-xs flex items-center gap-1 shadow-md shadow-indigo-600/20">
            <i data-lucide="play" class="w-3.5 h-3.5"></i> Attempt Anytime (CBT)
          </button>
          <button onclick="openLogScoreModal(${s.id}, '${escapeJs(s.test_title || s.test_number)}', ${s.total_marks || 300})" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-medium rounded-lg text-xs flex items-center gap-1">
            <i data-lucide="clipboard-check" class="w-3.5 h-3.5 text-emerald-400"></i> ${isAttempted ? 'Update Score' : 'Log External Marks'}
          </button>
          ${isAttempted && s.ai_autopsy ? `
            <button onclick="openViewAutopsyModal(${s.id})" class="px-3 py-1.5 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 font-bold rounded-lg text-xs flex items-center gap-1">
              <i data-lucide="activity" class="w-3.5 h-3.5"></i> View AI Autopsy
            </button>
          ` : ''}
        </div>

        <div class="flex items-center gap-2">
          ${s.google_calendar_url ? `
            <a href="${s.google_calendar_url}" target="_blank" rel="noopener noreferrer" class="px-2.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 rounded-lg text-xs flex items-center gap-1 hover:text-white" title="Sync to Google Calendar">
              <i data-lucide="calendar-plus" class="w-3.5 h-3.5 text-amber-400"></i> Cal
            </a>
          ` : ''}
          <button onclick="openRescheduleModal(${s.id}, '${s.scheduled_date}', '${s.scheduled_time || '09:00 - 12:00'}')" class="px-2.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 rounded-lg text-xs flex items-center gap-1 hover:text-white" title="Reschedule Test">
            <i data-lucide="clock" class="w-3.5 h-3.5 text-sky-400"></i>
          </button>
          <button onclick="deleteTestSeriesEntry(${s.id})" class="px-2 py-1.5 text-slate-500 hover:text-red-400 text-xs" title="Delete Test">
            <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
          </button>
        </div>
      </div>
    `;

    container.appendChild(card);
  });

  if (window.lucide) lucide.createIcons();
  renderMath();
  startCbtQuestionTimer();
}

async function launchMockCbt(mockId) {
  try {
    const res = await fetch(`/api/mocks/${mockId}`);
    state.activeMock = await res.json();
    state.cbtResponses = {};
    state.cbtStatus = {};
    state.cbtCurrentIndex = 0;
    state.cbtCurrentSection = state.activeMock.sections[0] || 'Physics';
    state.cbtSecondsRemaining = state.activeMock.total_time_minutes * 60;

    // Initialize statuses
    state.activeMock.questions.forEach(q => {
      state.cbtStatus[q.id] = 'not_visited';
    });

    document.getElementById('mock-list-view').classList.add('hidden');
    document.getElementById('mock-autopsy-view').classList.add('hidden');
    document.getElementById('mock-cbt-portal').classList.remove('hidden');

    document.getElementById('cbt-mock-title').innerText = state.activeMock.title;

    startCbtTimer();
    renderCbtQuestion();
    renderCbtPalette();
  } catch (err) {
    alert('Failed to launch CBT: ' + err.message);
  }
}

function startCbtTimer() {
  clearInterval(state.cbtTimerInterval);
  state.cbtTimerInterval = setInterval(() => {
    if (state.cbtSecondsRemaining > 0) {
      state.cbtSecondsRemaining--;
      const hrs = String(Math.floor(state.cbtSecondsRemaining / 3600)).padStart(2, '0');
      const mins = String(Math.floor((state.cbtSecondsRemaining % 3600) / 60)).padStart(2, '0');
      const secs = String(state.cbtSecondsRemaining % 60).padStart(2, '0');
      document.getElementById('cbt-timer').innerText = `${hrs}:${mins}:${secs}`;
    } else {
      clearInterval(state.cbtTimerInterval);
      alert('Time is up! Submitting exam automatically.');
      submitMockCbt();
    }
  }, 1000);
}

function switchCbtSection(sec) {
  state.cbtCurrentSection = sec;
  document.querySelectorAll('.cbt-sec-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(`sec-${sec}`).classList.add('active');

  // Find first question of this section
  const idx = state.activeMock.questions.findIndex(q => q.section === sec);
  if (idx !== -1) {
    state.cbtCurrentIndex = idx;
    renderCbtQuestion();
    renderCbtPalette();
  }
}

function renderCbtQuestion() {
  const q = state.activeMock.questions[state.cbtCurrentIndex];
  if (!q) return;

  if (state.cbtStatus[q.id] === 'not_visited') {
    state.cbtStatus[q.id] = 'not_answered';
  }

  // Update Section Button
  state.cbtCurrentSection = q.section;
  document.querySelectorAll('.cbt-sec-btn').forEach(b => b.classList.remove('active'));
  const secBtn = document.getElementById(`sec-${q.section}`);
  if (secBtn) secBtn.classList.add('active');

  document.getElementById('cbt-q-number').innerText = `Question ${state.cbtCurrentIndex + 1} (${q.section})`;
  
  const m = q.marking;
  document.getElementById('cbt-marking-scheme').innerText = `+${m.correct}, ${m.negative}`;
  document.getElementById('cbt-q-text').innerHTML = q.question;

  const canvas = document.getElementById('cbt-options-canvas');
  canvas.innerHTML = '';

  const resp = state.cbtResponses[q.id];

  if (q.type === 'single_choice') {
    q.options.forEach((optText, idx) => {
      const isChecked = resp === idx;
      const row = document.createElement('label');
      row.className = `flex items-center gap-3 p-3.5 rounded-xl border cursor-pointer text-xs transition-all ${
        isChecked ? 'bg-indigo-500/10 border-indigo-400 text-indigo-200' : 'bg-slate-950 border-slate-800 text-slate-300'
      }`;
      row.innerHTML = `
        <input type="radio" name="cbt-opt" value="${idx}" ${isChecked ? 'checked' : ''} class="text-indigo-500">
        <span class="math-content">${optText}</span>
      `;
      row.querySelector('input').onchange = () => {
        state.cbtResponses[q.id] = idx;
        state.cbtStatus[q.id] = 'answered';
        renderCbtPalette();
      };
      canvas.appendChild(row);
    });
  } else if (q.type === 'multi_correct') {
    const arr = Array.isArray(resp) ? resp : [];
    q.options.forEach((optText, idx) => {
      const isChecked = arr.includes(idx);
      const row = document.createElement('label');
      row.className = `flex items-center gap-3 p-3.5 rounded-xl border cursor-pointer text-xs transition-all ${
        isChecked ? 'bg-indigo-500/10 border-indigo-400 text-indigo-200' : 'bg-slate-950 border-slate-800 text-slate-300'
      }`;
      row.innerHTML = `
        <input type="checkbox" value="${idx}" ${isChecked ? 'checked' : ''} class="text-indigo-500">
        <span class="math-content">${optText}</span>
      `;
      row.querySelector('input').onchange = (e) => {
        let curr = state.cbtResponses[q.id] || [];
        if (e.target.checked) {
          curr.push(idx);
        } else {
          curr = curr.filter(i => i !== idx);
        }
        state.cbtResponses[q.id] = curr;
        state.cbtStatus[q.id] = curr.length > 0 ? 'answered' : 'not_answered';
        renderCbtPalette();
      };
      canvas.appendChild(row);
    });
  } else if (q.type === 'numerical') {
    canvas.innerHTML = `
      <div class="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2">
        <label class="text-xs text-slate-400 block font-mono">Enter Numerical Answer (Round to nearest integer or 2 decimals):</label>
        <input type="number" step="any" id="cbt-num-input" value="${resp !== undefined ? resp : ''}" class="bg-slate-900 border border-slate-700 px-4 py-2.5 rounded-xl text-sm font-mono text-white focus:outline-none focus:border-indigo-400 w-48">
      </div>
    `;
    const inp = document.getElementById('cbt-num-input');
    inp.oninput = (e) => {
      const val = e.target.value.trim();
      if (val !== '') {
        state.cbtResponses[q.id] = val;
        state.cbtStatus[q.id] = 'answered';
      } else {
        delete state.cbtResponses[q.id];
        state.cbtStatus[q.id] = 'not_answered';
      }
      renderCbtPalette();
    };
  }

  renderCbtPalette();
  renderMath();
  startCbtQuestionTimer();
}

function renderCbtPalette() {
  const grid = document.getElementById('cbt-palette-grid');
  grid.innerHTML = '';

  state.activeMock.questions.forEach((q, idx) => {
    const btn = document.createElement('button');
    const st = state.cbtStatus[q.id] || 'not_visited';
    let colorClass = 'bg-slate-800 text-slate-400';

    if (st === 'answered') colorClass = 'bg-emerald-600 text-white font-bold';
    else if (st === 'not_answered') colorClass = 'bg-red-600 text-white font-bold';
    else if (st === 'review') colorClass = 'bg-purple-600 text-white font-bold';
    else if (st === 'answered_review') colorClass = 'bg-purple-600 text-emerald-300 font-bold border-2 border-emerald-400';

    if (idx === state.cbtCurrentIndex) {
      colorClass += ' ring-2 ring-amber-400';
    }

    btn.className = `w-10 h-10 rounded-xl text-xs flex items-center justify-center transition-all ${colorClass}`;
    btn.innerText = idx + 1;
    btn.onclick = () => {
      state.cbtCurrentIndex = idx;
      renderCbtQuestion();
    };
    grid.appendChild(btn);
  });
}

function cbtSaveAndNext() {
  const q = state.activeMock.questions[state.cbtCurrentIndex];
  if (state.cbtResponses[q.id] !== undefined) {
    state.cbtStatus[q.id] = 'answered';
  } else {
    state.cbtStatus[q.id] = 'not_answered';
  }
  if (state.cbtCurrentIndex < state.activeMock.questions.length - 1) {
    state.cbtCurrentIndex++;
    renderCbtQuestion();
  }
}

function cbtMarkForReview() {
  const q = state.activeMock.questions[state.cbtCurrentIndex];
  if (state.cbtResponses[q.id] !== undefined) {
    state.cbtStatus[q.id] = 'answered_review';
  } else {
    state.cbtStatus[q.id] = 'review';
  }
  if (state.cbtCurrentIndex < state.activeMock.questions.length - 1) {
    state.cbtCurrentIndex++;
    renderCbtQuestion();
  }
}

function cbtClearResponse() {
  const q = state.activeMock.questions[state.cbtCurrentIndex];
  delete state.cbtResponses[q.id];
  state.cbtStatus[q.id] = 'not_answered';
  renderCbtQuestion();
}

async function submitMockCbt() {
  if (!confirm('Are you sure you want to finish and submit the test?')) return;
  clearInterval(state.cbtTimerInterval);

  const timeTaken = (state.activeMock.total_time_minutes * 60) - state.cbtSecondsRemaining;

  try {
    const res = await fetch(`/api/mocks/${state.activeMock.mock_id}/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: jsonFormat({
        responses: state.cbtResponses,
        time_taken_seconds: timeTaken
      })
    });
    const result = await res.json();

    document.getElementById('mock-cbt-portal').classList.add('hidden');
    document.getElementById('mock-autopsy-view').classList.remove('hidden');

    renderMockAutopsy(result);
    loadProfile();
  } catch (err) {
    alert('Error submitting mock: ' + err.message);
  }
}

function renderMockAutopsy(result) {
  const container = document.getElementById('mock-autopsy-view');
  container.innerHTML = `
    <div class="flex items-center justify-between border-b border-slate-800 pb-4">
      <div>
        <h3 class="text-xl font-black text-white">Post-Mock Performance Autopsy</h3>
        <p class="text-xs text-slate-400">${result.mock_title} • ${result.exam_type}</p>
      </div>
      <button onclick="switchTab('mock-exam')" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-xs rounded-xl font-medium">
        Back to Test Portal
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-slate-900 border border-amber-500/30 rounded-2xl p-5 text-center">
        <span class="text-xs text-slate-400">Total Marks</span>
        <div class="text-3xl font-black text-amber-400 mt-1">${result.total_score} <span class="text-sm text-slate-500">/ ${result.max_marks}</span></div>
        <span class="text-xs text-amber-300 font-mono mt-1 inline-block">${result.accuracy_pct}% Accuracy</span>
      </div>
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 text-center">
        <span class="text-xs text-slate-400">Physics</span>
        <div class="text-2xl font-bold text-white mt-1">${result.physics_score}</div>
      </div>
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 text-center">
        <span class="text-xs text-slate-400">Chemistry</span>
        <div class="text-2xl font-bold text-white mt-1">${result.chemistry_score}</div>
      </div>
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 text-center">
        <span class="text-xs text-slate-400">Mathematics</span>
        <div class="text-2xl font-bold text-white mt-1">${result.maths_score}</div>
      </div>
    </div>

    <!-- AI Autopsy Insights -->
    <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
      <h4 class="font-bold text-sm text-amber-400 flex items-center gap-2">
        <i data-lucide="sparkles" class="w-4 h-4"></i> AIR-1 Exam Temperament Autopsy
      </h4>
      <div class="text-xs text-slate-200 leading-relaxed math-content space-y-3 bg-slate-950 p-6 rounded-xl border border-slate-800">
        ${renderMarkdownSafe(result.ai_autopsy)}
      </div>
    </div>
  `;
  if (window.lucide) lucide.createIcons();
  renderMath();
  startCbtQuestionTimer();
}


// ----------------- 4. SCHOOL & 12TH BOARD HUB -----------------
async function loadSchoolSyncTab() {
  try {
    const res = await fetch('/api/school/tests');
    const data = await res.json();
    const table = document.getElementById('school-tests-table');
    table.innerHTML = '';

    (data.all_tests || []).forEach(t => {
      const isCompleted = t.status === 'completed';
      const div = document.createElement('div');
      div.className = 'p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-xs';
      div.innerHTML = `
        <div>
          <div class="flex items-center gap-2">
            <span class="font-bold text-slate-200">${t.test_title}</span>
            <span class="px-2 py-0.5 rounded text-[10px] ${isCompleted ? 'bg-emerald-500/10 text-emerald-400' : 'bg-pink-500/10 text-pink-400'}">${t.test_type}</span>
          </div>
          <p class="text-[11px] text-slate-400 mt-1">${t.syllabus}</p>
        </div>
        <div class="flex items-center gap-4">
          <span class="font-mono text-slate-400">${t.test_date}</span>
          ${isCompleted 
            ? `<span class="font-bold text-emerald-400">${t.marks_obtained}/${t.total_marks}</span>`
            : `<button onclick="openLogSchoolMarksModal(${t.id})" class="px-3 py-1.5 bg-pink-500/10 text-pink-400 border border-pink-500/30 hover:bg-pink-500 hover:text-black rounded-lg font-bold">Log Marks & Audit</button>`
          }
        </div>
      `;
      table.appendChild(div);
    });

    // Checklists
    const clRes = await fetch('/api/school/cbse-checklist');
    const clData = await clRes.json();
    const clContainer = document.getElementById('cbse-derivation-list');
    clContainer.innerHTML = '';

    Object.entries(clData).forEach(([subj, items]) => {
      const block = document.createElement('div');
      block.className = 'space-y-1.5';
      block.innerHTML = `
        <h5 class="font-bold text-slate-300 text-xs text-pink-400">${subj} Core Derivations:</h5>
        ${items.map(it => `
          <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80 text-[11px] flex justify-between">
            <span class="text-slate-300">${it.item}</span>
            <span class="text-amber-400 font-mono">${it.frequency}</span>
          </div>
        `).join('')}
      `;
      clContainer.appendChild(block);
    });

    if (window.lucide) lucide.createIcons();
    renderMath();
  } catch (err) {
    console.error('Failed to load school tests:', err);
  }
}


// ----------------- 5. GOOGLE CALENDAR & PLANNER -----------------
async function loadCalendarTab() {
  try {
    const res = await fetch('/api/calendar/events');
    const events = await res.json();
    const container = document.getElementById('calendar-events-container');
    container.innerHTML = '';

    events.forEach(ev => {
      const div = document.createElement('div');
      div.className = 'p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-xs hover:border-blue-500/40 transition-all';
      div.innerHTML = `
        <div class="space-y-1">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-blue-400"></span>
            <span class="font-bold text-white text-sm">${ev.title}</span>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">${ev.event_type}</span>
          </div>
          <p class="text-slate-400 text-[11px]">${ev.description || ''}</p>
          <div class="text-[11px] font-mono text-slate-500">${ev.start_time} - ${ev.end_time}</div>
        </div>
        <a href="${ev.google_calendar_url}" target="_blank" class="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold flex items-center gap-1.5 shadow-lg shadow-blue-600/20">
          <i data-lucide="calendar-plus" class="w-4 h-4"></i> Add to Google Calendar
        </a>
      `;
      container.appendChild(div);
    });

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error('Failed to load calendar events:', err);
  }
}


// ----------------- 6. AIR-1 AI MENTOR -----------------
async function loadMentorTab() {
  try {
    const res = await fetch('/api/mentor/history');
    const history = await res.json();
    const box = document.getElementById('mentor-chat-box');
    box.innerHTML = '';

    if (history.length === 0) {
      appendMentorMessage('assistant', `
**AIR-1 Command Protocol Initiated.**

Welcome. I am your Head of Department & Performance Psychologist. Here, we do not entertain wishful thinking; we operate on ruthless conceptual precision and unshakeable psychological armor.

Whether you're facing a stubborn multivariable calculus proof, feeling anxious after a mock score dip, or balancing CBSE 12th board derivations with JEE Advanced, lay it on the table.

What is your objective today?
      `);
    } else {
      history.forEach(m => appendMentorMessage(m.role, m.content));
    }
  } catch (err) {
    console.error('Failed to load mentor chat:', err);
  }
}

function appendMentorMessage(role, text) {
  const box = document.getElementById('mentor-chat-box');
  const msg = document.createElement('div');
  const isUser = role === 'user';

  msg.className = `flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`;
  msg.innerHTML = `
    ${!isUser ? `<div class="w-8 h-8 rounded-full bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400 shrink-0 font-bold text-xs"><i data-lucide="sparkles" class="w-4 h-4"></i></div>` : ''}
    <div class="max-w-[78%] rounded-2xl p-4 text-xs leading-relaxed math-content ${
      isUser ? 'bg-amber-500 text-slate-950 font-medium' : 'bg-slate-950 border border-slate-800 text-slate-200'
    }">
      ${renderMarkdownSafe(text)}
    </div>
    ${isUser ? `<div class="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-slate-300 shrink-0 font-bold text-xs">U</div>` : ''}
  `;
  box.appendChild(msg);
  box.scrollTop = box.scrollHeight;
  if (window.lucide) lucide.createIcons();
  renderMath();
  startCbtQuestionTimer();
}

async function sendMentorMessage() {
  const inp = document.getElementById('mentor-user-input');
  const text = inp.value.trim();
  if (!text) return;

  inp.value = '';
  appendMentorMessage('user', text);

  // Loading indicator
  const box = document.getElementById('mentor-chat-box');
  const loader = document.createElement('div');
  loader.id = 'mentor-loading-indicator';
  loader.className = 'flex gap-3 text-xs text-amber-400 items-center';
  loader.innerHTML = '<span class="animate-pulse">AIR-1 Mentor formulating tactical response...</span>';
  box.appendChild(loader);
  box.scrollTop = box.scrollHeight;

  try {
    const mentorEndpoint = currentMentorMode === 'standard' ? '/api/mentor/chat' : '/api/mentor/chat-mode';
    const payload = currentMentorMode === 'standard' ? { message: text } : { mode: currentMentorMode, topic: 'JEE Core', message: text };
    const res = await fetch(mentorEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    loader.remove();
    appendMentorMessage('assistant', data.reply);
  } catch (err) {
    loader.remove();
    appendMentorMessage('assistant', 'Error communicating with mentor AI. Please check internet connection.');
  }
}

function quickMentorAsk(prompt) {
  document.getElementById('mentor-user-input').value = prompt;
  sendMentorMessage();
}

function sendQuickMentorMessage() {
  const inp = document.getElementById('dash-quick-mentor-input');
  const val = inp.value.trim();
  if (!val) return;
  inp.value = '';
  switchTab('mentor');
  setTimeout(() => {
    quickMentorAsk(val);
  }, 200);
}


// ----------------- 0. DAILY AIR-1 MISSIONS (DIAGNOSTIC-CALIBRATED) -----------------
async function loadDailyGoals() {
  const container = document.getElementById('daily-goals-container');
  if (!container) return;

  try {
    const res = await fetch('/api/daily-goals');
    const goals = await res.json();

    if (!Array.isArray(goals) || goals.length === 0) {
      container.innerHTML = '<div class="col-span-2 text-center text-xs text-slate-500 py-4">No daily missions active. Click refresh to calibrate.</div>';
      return;
    }

    const completedCount = goals.filter(g => g.status === 'completed').length;
    const totalCount = goals.length;
    const pct = Math.round((completedCount / totalCount) * 100);

    const progText = document.getElementById('daily-goals-progress-text');
    if (progText) progText.innerText = `${completedCount} / ${totalCount} Done (${pct}%)`;

    const progBar = document.getElementById('daily-goals-progress-bar');
    if (progBar) progBar.style.width = `${pct}%`;

    const dateLabel = document.getElementById('daily-goals-date-label');
    if (dateLabel && goals[0] && goals[0].goal_date) {
      dateLabel.innerText = `${goals[0].goal_date}`;
    }

    container.innerHTML = '';
    goals.forEach(g => {
      const isDone = (g.status === 'completed');
      const card = document.createElement('div');
      card.className = `p-4 rounded-2xl border transition-all ${
        isDone 
          ? 'bg-emerald-950/20 border-emerald-500/40' 
          : 'bg-slate-900/80 border-slate-800 hover:border-amber-500/30'
      }`;

      let subColor = 'bg-slate-800 text-slate-300 border-slate-700';
      if (g.subject === 'Physics') subColor = 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30';
      else if (g.subject === 'Chemistry') subColor = 'bg-teal-500/10 text-teal-400 border-teal-500/30';
      else if (g.subject === 'Mathematics') subColor = 'bg-violet-500/10 text-violet-400 border-violet-500/30';
      else if (g.subject === 'Mindset') subColor = 'bg-amber-500/10 text-amber-400 border-amber-500/30';

      let actionBtnHtml = '';
      if (g.action_type === 'notes') {
        const t = (g.linked_topic || g.notes_key || 'Physics');
        actionBtnHtml = `<button onclick="openTopicNotesModal('${t.replace(/'/g, "\\'")}')" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-amber-300 text-[11px] font-semibold rounded-lg border border-slate-700 flex items-center gap-1.5"><i data-lucide="book-open" class="w-3 h-3"></i> Read Notes</button>`;
      } else if (g.action_type === 'sololearn') {
        actionBtnHtml = `<button onclick="switchTab('sololearn')" class="px-3 py-1.5 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 text-[11px] font-semibold rounded-lg border border-emerald-500/30 flex items-center gap-1.5"><i data-lucide="play" class="w-3 h-3"></i> Solve Drill</button>`;
      } else if (g.action_type === 'derivation') {
        actionBtnHtml = `<button onclick="openDerivationModal('${g.action_payload || 'lens_maker'}')" class="px-3 py-1.5 bg-pink-500/20 hover:bg-pink-500/30 text-pink-300 text-[11px] font-semibold rounded-lg border border-pink-500/30 flex items-center gap-1.5"><i data-lucide="compass" class="w-3 h-3"></i> Blueprint</button>`;
      } else if (g.action_type === 'diagnostic') {
        actionBtnHtml = `<button onclick="switchTab('diagnostic')" class="px-3 py-1.5 bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 text-[11px] font-semibold rounded-lg border border-cyan-500/30 flex items-center gap-1.5"><i data-lucide="stethoscope" class="w-3 h-3"></i> Take Test</button>`;
      } else if (g.action_type === 'mentor') {
        actionBtnHtml = `<button onclick="switchTab('mentor')" class="px-3 py-1.5 bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 text-[11px] font-semibold rounded-lg border border-amber-500/30 flex items-center gap-1.5"><i data-lucide="sparkles" class="w-3 h-3"></i> AI Mentor</button>`;
      }

      card.innerHTML = `
        <div class="flex items-center justify-between mb-2">
          <span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border ${subColor}">
            ${g.subject}
          </span>
          <span class="text-[11px] font-mono text-amber-400 font-bold flex items-center gap-1">
            <i data-lucide="zap" class="w-3 h-3"></i> +${g.xp_reward || 50} XP
          </span>
        </div>
        <h4 class="font-bold text-sm ${isDone ? 'text-emerald-300 line-through' : 'text-white'} leading-snug">
          ${g.title}
        </h4>
        <p class="text-xs text-slate-400 mt-1 mb-3 leading-relaxed">
          ${g.description}
        </p>
        <div class="flex items-center justify-between pt-2 border-t border-slate-800/80">
          <div>${actionBtnHtml}</div>
          <div>
            ${
              isDone
                ? `<span class="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-3 py-1.5 rounded-lg"><i data-lucide="check-circle-2" class="w-3.5 h-3.5"></i> Claimed</span>`
                : `<button onclick="completeDailyGoal(${g.id})" class="inline-flex items-center gap-1 text-[11px] font-bold text-slate-950 bg-gradient-to-r from-amber-400 to-amber-300 hover:from-amber-300 hover:to-amber-200 px-3.5 py-1.5 rounded-lg shadow-md shadow-amber-500/20 transition-all"><i data-lucide="check" class="w-3.5 h-3.5"></i> Mark Done</button>`
            }
          </div>
        </div>
      `;
      container.appendChild(card);
    });

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error('Failed to load daily goals:', err);
  }
}

async function completeDailyGoal(goalId) {
  try {
    const res = await fetch(`/api/daily-goals/${goalId}/complete`, { method: 'POST' });
    const data = await res.json();
    if (data.status === 'success') {
      await loadProfile();
      await loadDailyGoals();
      if (data.all_goals_done) {
        alert('🎉 LEGENDARY! All 4 daily AIR-1 missions completed today! +1 Day Streak & +50 Bonus XP awarded!');
      }
    }
  } catch (err) {
    alert('Failed to mark goal complete: ' + err.message);
  }
}

async function refreshDailyGoals() {
  try {
    await fetch('/api/daily-goals/refresh', { method: 'POST' });
    await loadDailyGoals();
  } catch (err) {
    console.error('Failed to refresh daily goals:', err);
  }
}

async function openTopicNotesModal(topicName) {
  try {
    const res = await fetch(`/api/knowledge/topic-notes?topic=${encodeURIComponent(topicName)}`);
    const notes = await res.json();
    if (notes && notes.length > 0) {
      const topNote = notes[0];
      openGenericModal(topNote.title, renderMarkdownSafe(topNote.content));
    } else {
      const sRes = await fetch(`/api/knowledge/search?q=${encodeURIComponent(topicName)}`);
      const sNotes = await sRes.json();
      if (sNotes && sNotes.length > 0) {
        viewVaultNote(sNotes[0].src_key, sNotes[0].index);
      } else {
        switchTab('knowledge-vault');
      }
    }
  } catch (err) {
    alert('Failed to load topic notes: ' + err.message);
  }
}

async function openDerivationModal(derivKey) {
  if (derivKey === 'lens_maker' || derivKey === 'rocket') {
    switchVisualSubTab('derivations');
    switchTab('visuals');
  } else {
    openTopicNotesModal(derivKey);
  }
}

// ----------------- 7. KNOWLEDGE VAULT & SCRAPER -----------------
let cachedVaultItems = [];
let currentVaultFilter = 'all';

async function loadKnowledgeVaultTab() {
  try {
    const res = await fetch('/api/knowledge/vault');
    cachedVaultItems = await res.json();
    renderVaultNotesGrid(cachedVaultItems);
  } catch (err) {
    console.error('Failed to load vault:', err);
  }
}

function renderVaultNotesGrid(items) {
  const grid = document.getElementById('vault-notes-grid');
  if (!grid) return;
  grid.innerHTML = '';

  if (!items || items.length === 0) {
    grid.innerHTML = '<div class="col-span-2 text-center text-xs text-slate-500 py-6">No matching notes found. Try another search or filter.</div>';
    return;
  }

  items.forEach(it => {
    const card = document.createElement('div');
    card.className = 'bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-3 hover:border-violet-500/40 transition-all flex flex-col justify-between';
    card.innerHTML = `
      <div class="space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-[11px] font-mono px-2 py-0.5 rounded bg-violet-500/10 text-violet-400 border border-violet-500/30 font-bold">${it.source}</span>
          <span class="text-[11px] text-slate-400">${it.category}</span>
        </div>
        <h4 class="font-bold text-sm text-white">${it.title}</h4>
        ${it.topics && it.topics.length ? `
          <div class="flex flex-wrap gap-1 pt-1">
            ${it.topics.map(t => `<span class="text-[10px] bg-slate-950 text-slate-400 px-2 py-0.5 rounded border border-slate-800">${t}</span>`).join('')}
          </div>
        ` : ''}
      </div>
      <div class="pt-2 border-t border-slate-800/80">
        <button onclick="viewVaultNote('${it.src_key}', ${it.index || 0})" class="w-full py-2 bg-slate-800 hover:bg-slate-700 text-xs text-violet-300 font-semibold rounded-xl flex items-center justify-center gap-1.5 transition-all">
          <i data-lucide="book-open" class="w-3.5 h-3.5"></i> Read In-Depth Note & Formulas &rarr;
        </button>
      </div>
    `;
    grid.appendChild(card);
  });

  if (window.lucide) lucide.createIcons();
}

function filterVaultNotes(filterKey) {
  currentVaultFilter = filterKey;
  document.querySelectorAll('.vault-chip').forEach(btn => {
    btn.classList.remove('active', 'bg-violet-600', 'text-white');
    btn.classList.add('bg-slate-800', 'text-slate-300');
  });
  if (event && event.target) {
    event.target.classList.add('active', 'bg-violet-600', 'text-white');
    event.target.classList.remove('bg-slate-800', 'text-slate-300');
  }

  if (filterKey === 'all') {
    renderVaultNotesGrid(cachedVaultItems);
  } else {
    const filtered = cachedVaultItems.filter(it => it.src_key === filterKey);
    renderVaultNotesGrid(filtered);
  }
}

function handleVaultSearch(query) {
  const q = (query || '').toLowerCase().trim();
  if (!q) {
    filterVaultNotes(currentVaultFilter);
    return;
  }
  const filtered = cachedVaultItems.filter(it => {
    return (
      it.title.toLowerCase().includes(q) ||
      it.category.toLowerCase().includes(q) ||
      it.source.toLowerCase().includes(q) ||
      (it.topics && it.topics.some(t => t.toLowerCase().includes(q)))
    );
  });
  renderVaultNotesGrid(filtered);
}

async function viewVaultNote(srcKey, index = 0) {
  try {
    const res = await fetch(`/api/knowledge/note?src_key=${srcKey}&index=${index}`);
    const note = await res.json();
    openGenericModal(note.title, renderMarkdownSafe(note.content));
  } catch (err) {
    alert('Failed to load note: ' + err.message);
  }
}

async function scrapeExternalPage() {
  const urlInp = document.getElementById('scrape-url-input');
  const url = urlInp.value.trim();
  if (!url) return;

  const out = document.getElementById('scrape-output');
  out.classList.remove('hidden');
  out.innerHTML = '<span class="text-cyan-400 animate-pulse">Scraping and analyzing webpage content...</span>';

  try {
    const res = await fetch('/api/knowledge/scrape', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: jsonFormat({ url })
    });
    const data = await res.json();
    if (data.status === 'success') {
      out.innerHTML = `
        <h4 class="font-bold text-white text-sm">${data.title}</h4>
        <p class="text-slate-300 text-xs leading-relaxed whitespace-pre-wrap">${data.extracted_text}</p>
      `;
    } else {
      out.innerHTML = `<span class="text-red-400">Failed: ${data.message}</span>`;
    }
  } catch (err) {
    out.innerHTML = `<span class="text-red-400">Scraping failed: ${err.message}</span>`;
  }
}


// ----------------- MODALS -----------------
function openGenericModal(title, contentHtml) {
  const modal = document.getElementById('modal-container');
  const inner = document.getElementById('modal-content');
  inner.innerHTML = `
    <div class="flex items-center justify-between border-b border-slate-800 pb-3">
      <h3 class="text-base font-bold text-white">${title}</h3>
      <button onclick="closeModal()" class="text-slate-400 hover:text-white">&times;</button>
    </div>
    <div class="max-h-[70vh] overflow-y-auto text-xs text-slate-200 leading-relaxed math-content space-y-3">
      ${contentHtml}
    </div>
  `;
  modal.classList.remove('hidden');
  renderMath();
  startCbtQuestionTimer();
}

function openAddSchoolTestModal() {
  const modal = document.getElementById('modal-container');
  const inner = document.getElementById('modal-content');
  inner.innerHTML = `
    <div class="flex items-center justify-between border-b border-slate-800 pb-3">
      <h3 class="text-base font-bold text-white">Add Upcoming School Test / Pre-Board</h3>
      <button onclick="closeModal()" class="text-slate-400 hover:text-white">&times;</button>
    </div>
    <div class="space-y-3 text-xs">
      <div>
        <label class="block text-slate-400 mb-1">Test Title</label>
        <input type="text" id="m-school-title" placeholder="e.g. Pre-Board 2: Chemistry" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-slate-400 mb-1">Subject</label>
          <select id="m-school-subject" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
            <option>Physics</option>
            <option>Chemistry</option>
            <option>Mathematics</option>
          </select>
        </div>
        <div>
          <label class="block text-slate-400 mb-1">Test Date</label>
          <input type="date" id="m-school-date" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
        </div>
      </div>
      <div>
        <label class="block text-slate-400 mb-1">Syllabus Chapters</label>
        <textarea id="m-school-syllabus" rows="2" placeholder="e.g. Full Organic Chemistry + Coordination" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white"></textarea>
      </div>
      <button onclick="submitNewSchoolTest()" class="w-full py-2.5 bg-pink-500 hover:bg-pink-400 text-slate-950 font-bold rounded-xl mt-2">
        Save & Add to Study Plan
      </button>
    </div>
  `;
  modal.classList.remove('hidden');
}

async function submitNewSchoolTest() {
  const title = document.getElementById('m-school-title').value.trim();
  const subject = document.getElementById('m-school-subject').value;
  const test_date = document.getElementById('m-school-date').value;
  const syllabus = document.getElementById('m-school-syllabus').value.trim();
  if (!title || !test_date) return alert('Please enter title and date');

  try {
    await fetch('/api/school/add-test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: jsonFormat({
        title, subject, test_date, syllabus, test_type: 'Pre-Board', total_marks: 70
      })
    });
    closeModal();
    loadSchoolSyncTab();
  } catch (err) {
    alert('Error adding test: ' + err.message);
  }
}

function openLogSchoolMarksModal(testId) {
  const modal = document.getElementById('modal-container');
  const inner = document.getElementById('modal-content');
  inner.innerHTML = `
    <div class="flex items-center justify-between border-b border-slate-800 pb-3">
      <h3 class="text-base font-bold text-white">Audit School Test Marks & Derivations</h3>
      <button onclick="closeModal()" class="text-slate-400 hover:text-white">&times;</button>
    </div>
    <div class="space-y-3 text-xs">
      <div>
        <label class="block text-slate-400 mb-1">Marks Obtained (out of 70/80)</label>
        <input type="number" id="m-audit-marks" placeholder="e.g. 62" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
      </div>
      <div>
        <label class="block text-slate-400 mb-1">Derivation Flaws / Where did teacher deduct marks?</label>
        <textarea id="m-audit-derivations" rows="2" placeholder="e.g. Missing ray diagram arrows, incomplete statement of Lenz law" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white"></textarea>
      </div>
      <div>
        <label class="block text-slate-400 mb-1">NCERT Intext / Exemplar Gaps</label>
        <textarea id="m-audit-ncert" rows="2" placeholder="e.g. Intext numerical calculations were unattempted" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white"></textarea>
      </div>
      <button onclick="submitSchoolTestAudit(${testId})" class="w-full py-2.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl mt-2">
        Generate AI 95%+ Recovery Plan
      </button>
    </div>
  `;
  modal.classList.remove('hidden');
}

async function submitSchoolTestAudit(testId) {
  const marks = parseFloat(document.getElementById('m-audit-marks').value);
  const derivations = document.getElementById('m-audit-derivations').value.trim();
  const ncert = document.getElementById('m-audit-ncert').value.trim();

  try {
    const res = await fetch('/api/school/analyze-test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: jsonFormat({
        test_id: testId,
        marks_obtained: marks,
        derivation_issues: derivations,
        ncert_gaps: ncert
      })
    });
    const data = await res.json();
    closeModal();
    openGenericModal('AI 95%+ Board Prescription', renderMarkdownSafe(data.action_plan));
    loadSchoolSyncTab();
  } catch (err) {
    alert('Audit failed: ' + err.message);
  }
}

function openAddEventModal() {
  const modal = document.getElementById('modal-container');
  const inner = document.getElementById('modal-content');
  inner.innerHTML = `
    <div class="flex items-center justify-between border-b border-slate-800 pb-3">
      <h3 class="text-base font-bold text-white">Schedule Study / Mock Slot</h3>
      <button onclick="closeModal()" class="text-slate-400 hover:text-white">&times;</button>
    </div>
    <div class="space-y-3 text-xs">
      <div>
        <label class="block text-slate-400 mb-1">Event Title</label>
        <input type="text" id="m-event-title" placeholder="e.g. Advanced Mechanics Problem Set (Pathfinder)" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-slate-400 mb-1">Start Time (YYYY-MM-DD HH:MM)</label>
          <input type="text" id="m-event-start" placeholder="2026-10-12 16:00" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white font-mono">
        </div>
        <div>
          <label class="block text-slate-400 mb-1">End Time (YYYY-MM-DD HH:MM)</label>
          <input type="text" id="m-event-end" placeholder="2026-10-12 18:30" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white font-mono">
        </div>
      </div>
      <button onclick="submitNewEvent()" class="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl mt-2">
        Create & Generate Google Calendar Link
      </button>
    </div>
  `;
  modal.classList.remove('hidden');
}

async function submitNewEvent() {
  const title = document.getElementById('m-event-title').value.trim();
  const start_time = document.getElementById('m-event-start').value.trim();
  const end_time = document.getElementById('m-event-end').value.trim();
  if (!title || !start_time || !end_time) return alert('Please enter all fields');

  try {
    await fetch('/api/calendar/add-event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: jsonFormat({
        title, start_time, end_time, event_type: 'deep_work', description: 'AIR-1 Deep Work Slot'
      })
    });
    closeModal();
    loadCalendarTab();
  } catch (err) {
    alert('Error adding event: ' + err.message);
  }
}

function openAddSeriesModal() {
  const modal = document.getElementById('modal-container');
  const inner = document.getElementById('modal-content');
  inner.innerHTML = `
    <div class="flex items-center justify-between border-b border-slate-800 pb-3">
      <h3 class="text-base font-bold text-white">Register External Test Series</h3>
      <button onclick="closeModal()" class="text-slate-400 hover:text-white">&times;</button>
    </div>
    <div class="space-y-3 text-xs">
      <div>
        <label class="block text-slate-400 mb-1">Series Name</label>
        <input type="text" id="m-series-name" placeholder="e.g. Allen Leader / MathonGo / FIITJEE AITS" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-slate-400 mb-1">Test # / Name</label>
          <input type="text" id="m-series-number" placeholder="Test 05" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
        </div>
        <div>
          <label class="block text-slate-400 mb-1">Exam Type</label>
          <select id="m-series-type" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
            <option>JEE Advanced</option>
            <option>JEE Main</option>
            <option>12th Board</option>
          </select>
        </div>
      </div>
      <div>
        <label class="block text-slate-400 mb-1">Scheduled Date (Optional)</label>
        <input type="date" id="m-series-date" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
      </div>
      <button onclick="submitNewSeries()" class="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl mt-2">
        Register Test Series
      </button>
    </div>
  `;
  modal.classList.remove('hidden');
}

async function submitNewSeries() {
  const series_name = document.getElementById('m-series-name').value.trim();
  const test_number = document.getElementById('m-series-number').value.trim();
  const exam_type = document.getElementById('m-series-type').value;
  const scheduled_date = document.getElementById('m-series-date').value || 'Flexible';
  if (!series_name || !test_number) return alert('Please enter series name and test number');

  try {
    await fetch('/api/test-series/generate-ai-schedule', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: jsonFormat({
        series_name, target_year: 2027, frequency: 'biweekly'
      })
    });
    closeModal();
    loadMockExamTab();
  } catch (err) {
    alert('Error registering series: ' + err.message);
  }
}

// ----------------- AI TEST SERIES MODALS (2027 AIR-1 ROADMAP) -----------------

function openGenerateAiScheduleModal() {
  const modal = document.getElementById('modal-container');
  const inner = document.getElementById('modal-content');
  inner.innerHTML = `
    <div class="flex items-center justify-between border-b border-slate-800 pb-3">
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold text-xs"><i data-lucide="sparkles" class="w-4 h-4"></i></div>
        <h3 class="text-base font-bold text-white">Synthesize AIR-1 2027 Test Schedule</h3>
      </div>
      <button onclick="closeModal()" class="text-slate-400 hover:text-white">&times;</button>
    </div>

    <p class="text-xs text-slate-300">
      If your test series (such as <strong>Testbook</strong>) doesn't have a preset schedule and allows on-demand attempts, our AI Academic Dean creates an optimal 16-test roadmap paced strategically across 2027.
    </p>

    <div class="space-y-3 text-xs">
      <div>
        <label class="block text-slate-400 mb-1 font-semibold">Test Series Name</label>
        <input type="text" id="ai-sch-name" value="Testbook JEE Test Series" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-amber-400">
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-slate-400 mb-1 font-semibold">Target Exam Year</label>
          <select id="ai-sch-year" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white">
            <option value="2027" selected>JEE 2027 (AIR-1 Target)</option>
            <option value="2026">JEE 2026</option>
            <option value="2028">JEE 2028</option>
          </select>
        </div>
        <div>
          <label class="block text-slate-400 mb-1 font-semibold">Pacing Frequency</label>
          <select id="ai-sch-freq" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white">
            <option value="biweekly" selected>Bi-Weekly (Every 14 Days - Recommended)</option>
            <option value="weekly">Weekly (Every 7 Days)</option>
          </select>
        </div>
      </div>

      <div>
        <label class="block text-slate-400 mb-1 font-semibold">Start Date (First Test)</label>
        <input type="date" id="ai-sch-start" value="${new Date(Date.now() + 86400000 * 2).toISOString().split('T')[0]}" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-amber-400">
      </div>

      <div>
        <label class="block text-slate-400 mb-1 font-semibold">Strategic Notes / Personal Focus (Optional)</label>
        <textarea id="ai-sch-notes" rows="2" placeholder="e.g. Focus on Class 11 mechanics first, then synchronize with CBSE 12th Board derivations" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-white focus:outline-none focus:border-amber-400"></textarea>
      </div>

      <button onclick="submitGenerateAiSchedule()" id="btn-submit-ai-sch" class="w-full py-3 bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-400 hover:to-amber-300 text-slate-950 font-bold rounded-xl text-xs flex items-center justify-center gap-2 mt-2 shadow-lg shadow-amber-500/20">
        <i data-lucide="sparkles" class="w-4 h-4"></i> Generate Full 2027 Roadmap & Sync Calendar
      </button>
    </div>
  `;
  if (window.lucide) lucide.createIcons();
  modal.classList.remove('hidden');
}

async function submitGenerateAiSchedule() {
  const series_name = document.getElementById('ai-sch-name').value.trim();
  const target_year = parseInt(document.getElementById('ai-sch-year').value);
  const frequency = document.getElementById('ai-sch-freq').value;
  const start_date = document.getElementById('ai-sch-start').value;
  const notes = document.getElementById('ai-sch-notes').value.trim();

  if (!series_name) return alert('Please enter a test series name');

  const btn = document.getElementById('btn-submit-ai-sch');
  btn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Synthesizing AIR-1 2027 Curriculum...';
  btn.disabled = true;

  try {
    const res = await fetch('/api/test-series/generate-ai-schedule', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: jsonFormat({ series_name, target_year, frequency, start_date, notes })
    });
    const data = await res.json();
    closeModal();
    alert(`🎉 Successfully scheduled ${data.total_tests_scheduled} tests for ${series_name} calibrated for JEE ${target_year}!`);
    await loadMockExamTab();
  } catch (err) {
    alert('Failed to generate schedule: ' + err.message);
  }
}

function openUploadScheduleModal() {
  const modal = document.getElementById('modal-container');
  const inner = document.getElementById('modal-content');
  inner.innerHTML = `
    <div class="flex items-center justify-between border-b border-slate-800 pb-3">
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-xs"><i data-lucide="upload-cloud" class="w-4 h-4"></i></div>
        <h3 class="text-base font-bold text-white">Ingest Test Series Timetable</h3>
      </div>
      <button onclick="closeModal()" class="text-slate-400 hover:text-white">&times;</button>
    </div>

    <p class="text-xs text-slate-300">
      Upload your coaching test series schedule (PDF document, screenshot, or timetable photo).
      If the schedule has no fixed dates (open/on-demand tests), the AI will pace them automatically for <strong>JEE 2027</strong>.
    </p>

    <div class="space-y-3 text-xs">
      <div>
        <label class="block text-slate-400 mb-1 font-semibold">Test Series Name</label>
        <input type="text" id="up-sch-name" placeholder="e.g. Allen Leader 2027 / FIITJEE AITS / Testbook Mocks" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-indigo-400">
      </div>

      <div class="border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-xl p-5 text-center cursor-pointer bg-slate-950/60" onclick="document.getElementById('sch-file-input').click()">
        <i data-lucide="file-up" class="w-8 h-8 mx-auto text-indigo-400 mb-2"></i>
        <p class="font-medium text-slate-200">Click to select PDF or Timetable Image</p>
        <p class="text-[11px] text-slate-500 mt-1">Supports .PDF, .PNG, .JPG, .JPEG</p>
        <input type="file" id="sch-file-input" accept=".pdf,image/*,.txt" class="hidden" onchange="updateScheduleFileName(this)">
        <p id="sch-selected-filename" class="text-amber-400 text-xs font-mono mt-2 hidden"></p>
      </div>

      <div class="text-[11px] text-slate-400">
        <label class="block text-slate-400 mb-1 font-semibold">Or Paste Timetable Text Directly</label>
        <textarea id="up-sch-text" rows="2" placeholder="Optional: Paste text table if you don't have a file" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-white"></textarea>
      </div>

      <button onclick="submitUploadScheduleFile()" id="btn-submit-up-sch" class="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/20">
        <i data-lucide="check" class="w-4 h-4"></i> Ingest & Add to 2027 Master Plan
      </button>
    </div>
  `;
  if (window.lucide) lucide.createIcons();
  modal.classList.remove('hidden');
}

function updateScheduleFileName(input) {
  const lbl = document.getElementById('sch-selected-filename');
  if (input.files && input.files[0]) {
    lbl.innerText = `Selected: ${input.files[0].name} (${(input.files[0].size/1024).toFixed(1)} KB)`;
    lbl.classList.remove('hidden');
  }
}

async function submitUploadScheduleFile() {
  const series_name = document.getElementById('up-sch-name').value.trim();
  const fileInput = document.getElementById('sch-file-input');
  const textInput = document.getElementById('up-sch-text').value.trim();

  if (!series_name) return alert('Please enter the test series name');

  const btn = document.getElementById('btn-submit-up-sch');
  btn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Parsing Timetable with AI...';
  btn.disabled = true;

  try {
    if (fileInput.files && fileInput.files[0]) {
      const formData = new FormData();
      formData.append('series_name', series_name);
      formData.append('target_year', 2027);
      formData.append('file', fileInput.files[0]);

      const res = await fetch('/api/test-series/upload-schedule', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      closeModal();
      alert(`✅ Extracted & scheduled ${data.total_tests} tests from ${fileInput.files[0].name}!`);
    } else if (textInput) {
      const res = await fetch('/api/test-series/parse-text-schedule', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: jsonFormat({ series_name, text: textInput, target_year: 2027 })
      });
      const data = await res.json();
      closeModal();
      alert(`✅ Extracted & scheduled ${data.total_tests} tests!`);
    } else {
      btn.innerHTML = '<i data-lucide="check" class="w-4 h-4"></i> Ingest & Add to 2027 Master Plan';
      btn.disabled = false;
      return alert('Please select a PDF/image file or paste timetable text');
    }
    await loadMockExamTab();
  } catch (err) {
    alert('Failed to parse schedule: ' + err.message);
  } finally {
    btn.disabled = false;
  }
}

function openLogScoreModal(testId, testTitle, totalMarks) {
  const modal = document.getElementById('modal-container');
  const inner = document.getElementById('modal-content');
  inner.innerHTML = `
    <div class="flex items-center justify-between border-b border-slate-800 pb-3">
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs"><i data-lucide="award" class="w-4 h-4"></i></div>
        <h3 class="text-base font-bold text-white">Log Score: ${testTitle}</h3>
      </div>
      <button onclick="closeModal()" class="text-slate-400 hover:text-white">&times;</button>
    </div>

    <p class="text-xs text-slate-300">
      Record your score from the external coaching / Testbook app. The AI Dean will generate an immediate autopsy calibrated to the <strong>JEE 2027 AIR-1 threshold</strong>.
    </p>

    <div class="space-y-3 text-xs">
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-slate-400 mb-1 font-semibold">Marks Obtained</label>
          <input type="number" id="log-score-val" step="0.5" placeholder="e.g. 215" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white font-mono focus:border-emerald-400">
        </div>
        <div>
          <label class="block text-slate-400 mb-1 font-semibold">Total Marks</label>
          <input type="number" id="log-total-val" value="${totalMarks || 300}" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white font-mono">
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-slate-400 mb-1 font-semibold">Percentile (Optional)</label>
          <input type="number" id="log-pct-val" step="0.01" placeholder="e.g. 99.45" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white font-mono">
        </div>
        <div>
          <label class="block text-slate-400 mb-1 font-semibold">Estimated Rank (Optional)</label>
          <input type="number" id="log-rank-val" placeholder="e.g. 42" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white font-mono">
        </div>
      </div>

      <div>
        <label class="block text-slate-400 mb-1 font-semibold">Silly Mistakes / Areas Where Marks Leaked</label>
        <textarea id="log-notes-val" rows="2" placeholder="e.g. Calculation error in Rotational Mechanics; misread IUPAC stereochemistry condition" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-white"></textarea>
      </div>

      <button onclick="submitLogScore(${testId})" id="btn-submit-log-score" class="w-full py-3 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl text-xs flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20">
        <i data-lucide="activity" class="w-4 h-4"></i> Submit & Generate AI Autopsy
      </button>
    </div>
  `;
  if (window.lucide) lucide.createIcons();
  modal.classList.remove('hidden');
}

async function submitLogScore(testId) {
  const score = parseFloat(document.getElementById('log-score-val').value);
  const total_marks = parseFloat(document.getElementById('log-total-val').value);
  const percentile = parseFloat(document.getElementById('log-pct-val').value) || null;
  const rank_estimate = parseInt(document.getElementById('log-rank-val').value) || null;
  const user_notes = document.getElementById('log-notes-val').value.trim();

  if (isNaN(score) || isNaN(total_marks)) {
    return alert('Please enter valid numerical marks');
  }

  const btn = document.getElementById('btn-submit-log-score');
  btn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Generating Surgical AI Autopsy...';
  btn.disabled = true;

  try {
    const res = await fetch(`/api/test-series/${testId}/log-score`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: jsonFormat({ score, total_marks, percentile, rank_estimate, user_notes })
    });
    const data = await res.json();
    closeModal();
    openAutopsyPopup(data);
    await loadMockExamTab();
    await loadProfile();
  } catch (err) {
    alert('Failed to log score: ' + err.message);
  }
}

function openAutopsyPopup(data) {
  const modal = document.getElementById('modal-container');
  const inner = document.getElementById('modal-content');
  inner.innerHTML = `
    <div class="flex items-center justify-between border-b border-slate-800 pb-3">
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs"><i data-lucide="activity" class="w-4 h-4"></i></div>
        <h3 class="text-base font-bold text-white">AIR-1 Surgical Autopsy (+${data.xp_awarded} XP)</h3>
      </div>
      <button onclick="closeModal()" class="text-slate-400 hover:text-white">&times;</button>
    </div>

    <div class="flex items-center gap-4 bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs">
      <div><span class="text-slate-400">Score:</span> <strong class="text-emerald-400 font-mono text-sm">${data.score} / ${data.total_marks}</strong></div>
      <div><span class="text-slate-400">Accuracy / Pct:</span> <strong class="text-amber-400 font-mono text-sm">${data.percentage}%</strong></div>
    </div>

    <div class="text-xs text-slate-200 space-y-2 max-h-[50vh] overflow-y-auto pr-1 math-content">
      ${data.ai_autopsy ? data.ai_autopsy.replace(/\\n/g, '<br>') : 'Analysis complete.'}
    </div>

    <button onclick="closeModal()" class="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-white font-bold rounded-xl text-xs">
      Acknowledge & Continue Training
    </button>
  `;
  if (window.lucide) lucide.createIcons();
  renderMath();
  modal.classList.remove('hidden');
}

function openViewAutopsyModal(testId) {
  const t = (state.allTestSeries || []).find(x => x.id === testId);
  if (!t || !t.ai_autopsy) return alert('No autopsy found for this test');
  openAutopsyPopup({
    score: t.score,
    total_marks: t.total_marks,
    percentage: Math.round((t.score / t.total_marks) * 100),
    ai_autopsy: t.ai_autopsy,
    xp_awarded: 0
  });
}

function openRescheduleModal(testId, currentDate, currentTime) {
  const modal = document.getElementById('modal-container');
  const inner = document.getElementById('modal-content');
  inner.innerHTML = `
    <div class="flex items-center justify-between border-b border-slate-800 pb-3">
      <h3 class="text-base font-bold text-white">Reschedule Test</h3>
      <button onclick="closeModal()" class="text-slate-400 hover:text-white">&times;</button>
    </div>
    <div class="space-y-3 text-xs">
      <div>
        <label class="block text-slate-400 mb-1">New Target Date</label>
        <input type="date" id="resch-date" value="${currentDate !== 'Flexible' ? currentDate : ''}" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white">
      </div>
      <div>
        <label class="block text-slate-400 mb-1">Time Slot</label>
        <select id="resch-time" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white">
          <option value="09:00 - 12:00">Morning Shift (09:00 - 12:00)</option>
          <option value="14:30 - 17:30">Afternoon Shift (14:30 - 17:30)</option>
        </select>
      </div>
      <button onclick="submitReschedule(${testId})" class="w-full py-2.5 bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold rounded-xl text-xs">
        Update Schedule Date
      </button>
    </div>
  `;
  modal.classList.remove('hidden');
}

async function submitReschedule(testId) {
  const new_date = document.getElementById('resch-date').value;
  const new_time = document.getElementById('resch-time').value;
  if (!new_date) return alert('Please select a valid date');

  try {
    await fetch(`/api/test-series/${testId}/reschedule`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: jsonFormat({ new_date, new_time })
    });
    closeModal();
    await loadMockExamTab();
  } catch (err) {
    alert('Failed to reschedule: ' + err.message);
  }
}

async function deleteTestSeriesEntry(testId) {
  if (!confirm('Are you sure you want to remove this test from your schedule?')) return;
  try {
    await fetch(`/api/test-series/${testId}`, { method: 'DELETE' });
    await loadMockExamTab();
  } catch (err) {
    alert('Failed to delete: ' + err.message);
  }
}

function exportTestSeriesIcs() {
  const filter = state.selectedSeriesFilter || 'ALL';
  const url = (filter === 'ALL')
    ? '/api/test-series/export-ics'
    : `/api/test-series/export-ics?series_name=\${encodeURIComponent(filter)}`;
  window.open(url, '_blank');
}

function openCustomCardModal() {
  const modal = document.getElementById('modal-container');
  const inner = document.getElementById('modal-content');
  inner.innerHTML = `
    <div class="flex items-center justify-between border-b border-slate-800 pb-3">
      <h3 class="text-base font-bold text-white">Generate SoloLearn Micro-Card via FreeLLM</h3>
      <button onclick="closeModal()" class="text-slate-400 hover:text-white">&times;</button>
    </div>
    <div class="space-y-3 text-xs">
      <div>
        <label class="block text-slate-400 mb-1">Subject</label>
        <select id="m-gen-subject" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
          <option>Physics</option>
          <option>Chemistry</option>
          <option>Mathematics</option>
        </select>
      </div>
      <div>
        <label class="block text-slate-400 mb-1">Topic or IIT Trap</label>
        <input type="text" id="m-gen-topic" placeholder="e.g. Variable Mass Rocket Equation or SN1 Stereochemistry" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
      </div>
      <button onclick="submitGenCustomCard()" id="btn-gen-card" class="w-full py-2.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl mt-2">
        Generate Interactive Micro-Card
      </button>
    </div>
  `;
  modal.classList.remove('hidden');
}

async function submitGenCustomCard() {
  const subject = document.getElementById('m-gen-subject').value;
  const topic = document.getElementById('m-gen-topic').value.trim();
  if (!topic) return alert('Please enter a topic');

  const btn = document.getElementById('btn-gen-card');
  btn.innerText = 'Synthesizing with FreeLLM AI...';
  btn.disabled = true;

  try {
    const card = await generateCardFast(subject, topic);
    closeModal();
    openGenericModal(card.title, `
      <div class="space-y-4">
        <div class="p-4 bg-slate-950 rounded-xl border border-slate-800">
          <span class="text-amber-400 font-bold text-xs uppercase block mb-1">Concept Nugget:</span>
          <p>${card.concept_nugget}</p>
          <p class="text-amber-300 font-bold mt-2">💡 ${card.key_takeaway}</p>
        </div>
        <div class="p-4 bg-slate-950 rounded-xl border border-slate-800">
          <span class="text-cyan-400 font-bold text-xs uppercase block mb-1">Active Recall Question:</span>
          <p class="font-medium text-white">${card.pyq_question}</p>
          <ul class="mt-2 space-y-1">
            ${(card.options || []).map((o, i) => `<li><strong>${String.fromCharCode(65+i)}:</strong> ${o}</li>`).join('')}
          </ul>
          <p class="text-emerald-400 mt-3"><strong>Correct Answer:</strong> ${card.options[card.correct_option_index]}</p>
          <p class="text-slate-400 text-[11px] mt-1">${card.explanation}</p>
        </div>
      </div>
    `);
  } catch (err) {
    alert('Failed to generate card: ' + err.message);
  }
}

function closeModal() {
  document.getElementById('modal-container').classList.add('hidden');
}

function jsonFormat(obj) {
  return JSON.stringify(obj);
}

// ----------------- PWA INSTALLATION HANDLER -----------------
let deferredPrompt = null;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  const btn = document.getElementById('btn-install-pwa');
  if (btn) btn.classList.remove('hidden');
});

function promptPwaInstall() {
  if (deferredPrompt) {
    deferredPrompt.prompt();
    deferredPrompt.userChoice.then(() => { deferredPrompt = null; });
  } else {
    alert("📱 To install as an Android Mobile App:\n1. Open this URL in Chrome on your Android phone.\n2. Tap the 3 dots (⋮) in the top-right corner of Chrome.\n3. Tap 'Install app' or 'Add to Home screen'.\n4. Enjoy the full-screen native Android AIR-1 experience with zero browser bars!");
  }
}

// ----------------- 8. MATERIAL INGESTION & DEEP REFINERY -----------------
let selectedUploadFile = null;

function handleFileSelected(e) {
  if (e.target.files && e.target.files[0]) {
    selectedUploadFile = e.target.files[0];
    document.getElementById('mat-file-label').innerText = `Selected: ${selectedUploadFile.name}`;
  }
}

async function loadMaterialsTab() {
  try {
    const res = await fetch('/api/materials');
    const list = await res.json();
    document.getElementById('mat-count-badge').innerText = `${list.length} Refined Items`;
    const container = document.getElementById('materials-feed-list');
    container.innerHTML = '';

    if (list.length === 0) {
      container.innerHTML = `
        <div class="p-8 text-center bg-slate-950 rounded-2xl border border-slate-800 text-xs text-slate-400">
          <i data-lucide="upload" class="w-8 h-8 text-sky-400 mx-auto mb-2"></i>
          Upload a coaching PDF, photo of your classroom notes, or test questions above to begin AI refinement.
        </div>
      `;
    } else {
      list.forEach(m => {
        const card = document.createElement('div');
        card.className = 'p-5 bg-slate-950 border border-slate-800 rounded-2xl space-y-3';
        const solo = m.sololearn_card_json || {};
        card.innerHTML = `
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="px-2.5 py-1 rounded bg-sky-500/10 text-sky-400 font-mono text-xs font-bold">${m.subject}</span>
              <h4 class="font-bold text-sm text-white">${m.title}</h4>
            </div>
            <span class="text-[11px] text-slate-500 font-mono">${m.filename || 'Pasted Note'}</span>
          </div>
          <div class="text-xs text-slate-200 math-content leading-relaxed space-y-2 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
            ${renderMarkdownSafe(m.summary || '')}
          </div>
          ${m.board_synergy ? `
            <div class="p-3 bg-pink-500/5 border border-pink-500/20 rounded-xl text-xs text-pink-300">
              <strong>CBSE 12th Board Synergy:</strong> ${m.board_synergy}
            </div>
          ` : ''}
          ${solo.question ? `
            <div class="p-3 bg-emerald-500/5 border border-emerald-500/20 rounded-xl text-xs text-emerald-300">
              <strong>Active Recall Check:</strong> ${solo.question}
            </div>
          ` : ''}
        `;
        container.appendChild(card);
      });
    }

    if (window.lucide) lucide.createIcons();
    renderMath();
  } catch (err) {
    console.error('Failed to load materials:', err);
  }
}

async function submitMaterialForRefinery() {
  const title = document.getElementById('mat-title-input').value.trim();
  const subject = document.getElementById('mat-subject-input').value;
  const rawText = document.getElementById('mat-text-input').value.trim();
  if (!title) return alert('Please enter a title for the material');
  const btn = document.getElementById('btn-refine-material');
  if (btn) btn.disabled = true;
  const isElectro = (title + ' ' + subject).toLowerCase().indexOf('electro') >= 0;
  const card = {
    title: title,
    subject: subject || 'Chemistry',
    filename: selectedUploadFile ? selectedUploadFile.name : 'Pasted note',
    summary: isElectro
      ? 'At 298 K, E = E° - (0.059/n) log Q. Write the cell reaction, n and Q before the number. For Zn|Zn2+(0.01 M)||Cu2+(1 M)|Cu with E° = 1.10 V, n = 2 and Q = 0.01, so E = 1.16 V.'
      : ('Refinery card for ' + title + '. ' + (rawText || 'Paste the note text if you want those lines used. A PDF cannot be read on this page.')),
    sololearn_card_json: {}
  };
  const key = 'air1-materials';
  const mats = JSON.parse(localStorage.getItem(key) || '[]');
  mats.unshift(card);
  localStorage.setItem(key, JSON.stringify(mats.slice(0, 20)));
  const container = document.getElementById('materials-feed-list');
  if (container) {
    container.innerHTML = '<div class="p-5 bg-slate-950 border border-slate-800 rounded-2xl space-y-3"><span class="px-2.5 py-1 rounded bg-sky-500/10 text-sky-400 font-mono text-xs font-bold">' + card.subject + '</span><h4 class="font-bold text-sm text-white">' + card.title + '</h4><p class="text-xs text-slate-200">' + card.summary + '</p></div>';
  }
  const badge = document.getElementById('mat-count-badge');
  if (badge) badge.innerText = mats.length + ' Refined Items';
  if (btn) btn.disabled = false;
  alert('Card saved on this page. No server call was made.');
}


// ----------------- 9. VISUAL & SYMBOLIC ENGINE (ORGANIC, SYMPY, PLOTS) -----------------
function switchVisualSubTab(sub) {
  ['mechanisms', 'derivations', 'plots'].forEach(s => {
    document.getElementById(`visual-sub-${s}`).classList.add('hidden');
    document.getElementById(`vtab-${s}`).classList.remove('active');
  });
  document.getElementById(`visual-sub-${sub}`).classList.remove('hidden');
  document.getElementById(`vtab-${sub}`).classList.add('active');

  if (sub === 'plots') loadSvgPlots();
  else if (sub === 'derivations') loadSympyDerivations();
}

async function loadVisualsTab() {
  await loadOrganicMechanisms();
  await loadSympyDerivations();
}

async function loadOrganicMechanisms() {
  try {
    const res = await fetch('/api/visuals/mechanisms');
    const list = await res.json();
    const container = document.getElementById('organic-mechanisms-container');
    container.innerHTML = '';

    list.forEach(m => {
      const card = document.createElement('div');
      card.className = 'bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-4';
      card.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="text-xs px-2.5 py-0.5 rounded bg-teal-500/10 text-teal-400 border border-teal-500/30 font-bold">${m.category}</span>
          <span class="text-xs text-amber-400 font-bold font-mono">AIR-1 Master Reaction</span>
        </div>
        <h3 class="font-bold text-base text-white">${m.name}</h3>
        <div class="text-xs text-slate-300 font-mono bg-slate-950 p-3 rounded-xl border border-slate-800 flex justify-between">
          <span>Reactants: ${m.reactants}</span>
          <span class="text-amber-400">Product: ${m.product}</span>
        </div>
        <div class="space-y-3 pt-2">
          ${m.reaction_steps.map(s => `
            <div class="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 text-xs space-y-1">
              <div class="font-bold text-teal-300 flex items-center gap-2">
                <span class="w-5 h-5 rounded-full bg-teal-500/20 text-teal-400 flex items-center justify-center text-[10px] font-bold">${s.step_num}</span>
                ${s.title}
              </div>
              <p class="text-slate-400">${s.mechanism_text}</p>
              <div class="text-xs text-amber-300 font-mono math-content pt-1">$$${s.chemical_equation}$$</div>
            </div>
          `).join('')}
        </div>
        <div class="p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-xs text-red-300 flex items-center gap-2">
          <i data-lucide="alert-triangle" class="w-4 h-4 text-red-400 shrink-0"></i>
          <span><strong>IIT-JEE Trap:</strong> ${m.iit_trap}</span>
        </div>
      `;
      container.appendChild(card);
    });
    if (window.lucide) lucide.createIcons();
    renderMath();
  } catch (err) {
    console.error('Failed to load mechanisms:', err);
  }
}

async function loadSympyDerivations() {
  const container = document.getElementById('sympy-derivation-cards');
  if (!container) return;
  try {
    const resLens = await fetch('/api/visuals/derivation/lens_maker');
    const lens = await resLens.json();

    const resRocket = await fetch('/api/visuals/derivation/rocket');
    const rocket = await resRocket.json();

    container.innerHTML = [lens, rocket].map(d => `
      <div class="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-3">
        <div class="flex items-center justify-between">
          <h4 class="font-bold text-sm text-amber-400">${d.title}</h4>
          <span class="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">${d.subject}</span>
        </div>
        <div class="space-y-2">
          ${d.steps.map(st => `
            <div class="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs space-y-1">
              <span class="text-slate-400 font-semibold">Step ${st.step}: ${st.label}</span>
              <div class="text-white font-mono math-content">$$${st.formula}$$</div>
              <p class="text-[11px] text-slate-400 italic">${st.note}</p>
            </div>
          `).join('')}
        </div>
      </div>
    `).join('');
    renderMath();
  } catch (err) {
    console.error('Failed to load derivations:', err);
  }
}

async function solveMathWithSympy() {
  const expr = document.getElementById('sympy-expr-input').value.trim();
  if (!expr) return;
  const box = document.getElementById('sympy-solution-box');
  box.innerHTML = '<span class="text-cyan-400 animate-pulse">Calculating derivatives, integrals & limits via SymPy...</span>';

  try {
    const res = await fetch('/api/visuals/solve-math', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: jsonFormat({ expression: expr })
    });
    const data = await res.json();
    if (data.status === 'success') {
      const rootsHtml = (data.roots_latex && data.roots_latex.length > 0)
        ? `<div><span class="text-purple-400 font-bold">Roots $f(x)=0$:</span> <div class="math-content">$$x \\in \\{${data.roots_latex.join(', ')}\\}$$</div></div>`
        : '';
      box.innerHTML = `
        <div class="space-y-2 text-xs">
          <div><span class="text-slate-400">Expression $f(x)$:</span> <div class="math-content">$$${data.expression_latex}$$</div></div>
          ${rootsHtml}
          <div><span class="text-emerald-400 font-bold">Derivative $f'(x)$:</span> <div class="math-content">$$${data.derivative_latex}$$</div></div>
          <div><span class="text-cyan-400 font-bold">Indefinite Integral $\\int f(x)dx$:</span> <div class="math-content">$$${data.integral_latex}$$</div></div>
          <div><span class="text-amber-400 font-bold">Limit $\\lim_{x \\to 0} f(x)$:</span> <div class="math-content">$$${data.limit_x0_latex}$$</div></div>
        </div>
      `;
      renderMath();
    } else {
      box.innerHTML = `<span class="text-red-400">SymPy parsing error: ${data.message}</span>`;
    }
  } catch (err) {
    box.innerHTML = `<span class="text-red-400">Computation error: ${err.message}</span>`;
  }
}

async function loadSvgPlots() {
  try {
    const resWave = await fetch('/api/visuals/plot/wave-optics');
    const svgWave = await resWave.text();
    document.getElementById('plot-wave-optics-container').innerHTML = svgWave;

    const resE = await fetch('/api/visuals/plot/electric-field');
    const svgE = await resE.text();
    document.getElementById('plot-electric-field-container').innerHTML = svgE;
  } catch (err) {
    console.error('Failed to load SVG plots:', err);
  }
}

// ----------------- REAL STUDENT ONBOARDING (ZERO FAKE DATA) -----------------
function openRealStudentOnboardingModal() {
  const modal = document.getElementById('modal-container');
  const inner = document.getElementById('modal-content');
  inner.innerHTML = `
    <div class="flex items-center justify-between border-b border-slate-800 pb-3">
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold text-xs">AIR</div>
        <h3 class="text-base font-bold text-white">AIR-1 Student Academic Setup</h3>
      </div>
      <button onclick="closeModal()" class="text-slate-400 hover:text-white">&times;</button>
    </div>

    <p class="text-xs text-slate-300">
      Zero fake data. Enter your real academic details so your study planner, school test sync, and AI mentor are 100% calibrated to you.
    </p>

    <div class="space-y-3 text-xs max-h-[65vh] overflow-y-auto pr-1">
      <div>
        <label class="block text-slate-400 mb-1 font-semibold">Your Full Name</label>
        <input type="text" id="onb-name" placeholder="Enter your full name" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-amber-400">
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-slate-400 mb-1 font-semibold">Class / Grade</label>
          <select id="onb-grade" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white">
            <option value="11th" selected>Class 11th</option>
            <option value="12th">Class 12th</option>
            <option value="Dropper">Dropper / Repeater</option>
          </select>
        </div>
        <div>
          <label class="block text-slate-400 mb-1 font-semibold">Target JEE Year</label>
          <select id="onb-year" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white">
            <option value="2027" selected>2027 (Target AIR-1)</option>
            <option value="2026">2026</option>
            <option value="2028">2028</option>
          </select>
        </div>
      </div>

      <div>
        <label class="block text-slate-400 mb-1 font-semibold">Your School Name</label>
        <input type="text" id="onb-school" placeholder="e.g. Kendriya Vidyalaya / DPS / State Board School" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-amber-400">
      </div>

      <div>
        <label class="block text-slate-400 mb-1 font-semibold">Coaching Institute</label>
        <input type="text" id="onb-coaching" placeholder="e.g. Allen / FIITJEE / Resonance / Chaitanya / Self-Study" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-amber-400">
      </div>

      <div>
        <label class="block text-slate-400 mb-1 font-semibold">Active Test Series (e.g. Testbook, Allen, MathonGo - Comma-separated)</label>
        <input type="text" id="onb-series" placeholder="e.g. Testbook JEE Test Series, Allen Leader, MathonGo Mocks" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-amber-400">
      </div>

      <div class="pt-2 border-t border-slate-800">
        <label class="block text-pink-400 mb-1 font-semibold">Next Upcoming School Test / Pre-Board (Optional)</label>
        <div class="grid grid-cols-2 gap-2 mb-2">
          <input type="text" id="onb-school-test-title" placeholder="Test Name (e.g. Unit Test 2)" class="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
          <input type="date" id="onb-school-test-date" class="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
        </div>
        <input type="text" id="onb-school-test-syllabus" placeholder="Syllabus (e.g. Optics & Electrostatics)" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
      </div>

      <button onclick="submitStudentOnboarding()" id="btn-submit-onb" class="w-full py-3 bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-400 hover:to-amber-300 text-slate-950 font-bold rounded-xl text-xs flex items-center justify-center gap-2 mt-3 shadow-lg shadow-amber-500/20">
        Verify Profile & Activate AIR-1 Engine
      </button>
    </div>
  `;
  modal.classList.remove('hidden');
}

async function submitStudentOnboarding() {
  const name = document.getElementById('onb-name').value.trim();
  const grade = document.getElementById('onb-grade').value;
  const target_year = parseInt(document.getElementById('onb-year').value);
  const school_name = document.getElementById('onb-school').value.trim();
  const coaching_institute = document.getElementById('onb-coaching').value.trim() || 'Self-Study';
  const seriesRaw = document.getElementById('onb-series').value.trim();
  const testSeries = seriesRaw ? seriesRaw.split(',').map(s => s.trim()).filter(Boolean) : [];

  const schoolTestTitle = document.getElementById('onb-school-test-title').value.trim();
  const schoolTestDate = document.getElementById('onb-school-test-date').value;
  const schoolTestSyllabus = document.getElementById('onb-school-test-syllabus').value.trim();

  if (!name || !school_name) {
    return alert('Please enter your Name and School Name to set up your real profile.');
  }

  const btn = document.getElementById('btn-submit-onb');
  btn.innerText = 'Initializing Profile...';
  btn.disabled = true;

  try {
    const res = await fetch('/api/profile/onboard', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: jsonFormat({
        name,
        grade,
        target_year,
        target_board_pct: 95.0,
        school_name,
        coaching_institute,
        test_series_enrolled: testSeries,
        first_school_test_title: schoolTestTitle || null,
        first_school_test_subject: 'Physics',
        first_school_test_date: schoolTestDate || null,
        first_school_test_syllabus: schoolTestSyllabus || null
      })
    });
    const data = await res.json();
    closeModal();
    alert(`🎯 Welcome ${name}! Your authentic AIR-1 profile is calibrated with zero fake data.`);
    await loadProfile();
    await loadDashboardData();
  } catch (err) {
    alert('Failed to set up profile: ' + err.message);
  } finally {
    btn.innerText = 'Verify Profile & Activate AIR-1 Engine';
    btn.disabled = false;
  }
}



// =========================================================================
// 11. TRIAGE, BAILOUT & TACTICAL EXECUTION ENGINE CONTROLLERS
// =========================================================================
state.triageTimer = null;
state.triageSeconds = 30;
state.currentTriageDrillId = null;
state.bailoutTimer = null;
state.bailoutSeconds = 90;
state.chaosAudioCtx = null;
state.chaosNoiseNode = null;

async function loadTacticsTab() {
  try {
    const res = await fetch('/api/tactics/god-mode-matrix');
    const data = await res.json();
    if (data.triage_accuracy_pct !== undefined) {
      const accEl = document.getElementById('triage-accuracy-val');
      if (accEl) accEl.innerText = data.triage_accuracy_pct + '%';
    }
  } catch (e) {
    console.error('Error loading god mode matrix:', e);
  }
  if (!state.currentTriageDrillId) {
    await loadTriageDrillQuestion();
  }
}

async function loadTriageDrillQuestion() {
  clearInterval(state.triageTimer);
  state.triageSeconds = 30;
  
  const timerDisplay = document.getElementById('triage-timer-display');
  const timerBar = document.getElementById('triage-timer-bar');
  const resultBox = document.getElementById('triage-result-box');
  if (timerDisplay) timerDisplay.innerText = '30s';
  if (timerBar) timerBar.style.width = '100%';
  if (resultBox) {
    resultBox.classList.add('hidden');
    resultBox.innerHTML = '';
  }

  try {
    const res = await fetch('/api/tactics/triage-question');
    const q = await res.json();
    state.currentTriageDrillId = q.drill_id;

    const subEl = document.getElementById('triage-q-subject');
    const topEl = document.getElementById('triage-q-topic');
    const titleEl = document.getElementById('triage-q-title');
    const textEl = document.getElementById('triage-q-text');

    if (subEl) subEl.innerText = q.subject;
    if (topEl) topEl.innerText = q.topic;
    if (titleEl) titleEl.innerText = q.question_title;
    if (textEl) textEl.innerText = q.question_text;

    renderMath();

    // Start 30s countdown
    state.triageTimer = setInterval(() => {
      state.triageSeconds--;
      if (timerDisplay) timerDisplay.innerText = `${state.triageSeconds}s`;
      if (timerBar) timerBar.style.width = `${(state.triageSeconds / 30) * 100}%`;
      if (state.triageSeconds <= 0) {
        clearInterval(state.triageTimer);
        if (timerDisplay) timerDisplay.innerText = '0s (Time Up!)';
      }
    }, 1000);
  } catch (err) {
    console.error('Error fetching triage question:', err);
  }
}

async function submitTriageChoice(round) {
  if (!state.currentTriageDrillId) return;
  clearInterval(state.triageTimer);
  const timeTaken = 30 - state.triageSeconds;

  try {
    const res = await fetch('/api/tactics/triage-submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        drill_id: state.currentTriageDrillId,
        chosen_round: round,
        time_taken_seconds: timeTaken > 0 ? timeTaken : 30
      })
    });
    const result = await res.json();
    const resultBox = document.getElementById('triage-result-box');
    if (resultBox) {
      resultBox.classList.remove('hidden');
      const roundNames = {
        1: 'ROUND 1: IMMEDIATE (<2.5m)',
        2: 'ROUND 2: HEAVY CALC (3-6m)',
        3: 'ROUND 3: TRAP / SKIP TO END'
      };

      if (result.is_accurate) {
        resultBox.innerHTML = `
          <div class="flex items-center gap-2 text-emerald-400 font-bold text-xs">
            <i data-lucide="check-circle" class="w-4 h-4"></i>
            TRIAGE MASTERY! You correctly evaluated this as ${roundNames[result.correct_round]} in ${result.time_taken_seconds}s.
          </div>
          <p class="text-xs text-slate-300 leading-relaxed">${result.rationale}</p>
          <div class="text-[11px] text-amber-400/90 font-mono mt-1">${result.tactical_insight}</div>
          <div class="pt-2 flex justify-end">
            <button onclick="loadTriageDrillQuestion()" class="px-4 py-1.5 bg-rose-500 hover:bg-rose-400 text-slate-950 font-bold text-xs rounded-lg transition-all">
              Next Triage Question →
            </button>
          </div>
        `;
      } else {
        resultBox.innerHTML = `
          <div class="flex items-center gap-2 text-rose-400 font-bold text-xs">
            <i data-lucide="alert-triangle" class="w-4 h-4"></i>
            TACTICAL MISALIGNMENT: You chose ${roundNames[result.chosen_round]}, but optimum is ${roundNames[result.correct_round]}.
          </div>
          <p class="text-xs text-slate-300 leading-relaxed">${result.rationale}</p>
          <div class="text-[11px] text-rose-300/80 font-mono mt-1">Review examiner intent: Misjudging Round 1 vs Round 3 causes either wasted time or forfeited easy marks.</div>
          <div class="pt-2 flex justify-end">
            <button onclick="loadTriageDrillQuestion()" class="px-4 py-1.5 bg-rose-500 hover:bg-rose-400 text-slate-950 font-bold text-xs rounded-lg transition-all">
              Try Another Question →
            </button>
          </div>
        `;
      }
      if (window.lucide) lucide.createIcons();
    }
    // Refresh accuracy KPI
    loadTacticsTab();
  } catch (err) {
    alert('Error submitting triage choice: ' + err.message);
  }
}

function startBailoutTimer() {
  clearInterval(state.bailoutTimer);
  state.bailoutSeconds = 90;
  const disp = document.getElementById('bailout-timer-display');
  const alertMsg = document.getElementById('bailout-alert-msg');
  const btn = document.getElementById('btn-bailout-toggle');
  if (alertMsg) alertMsg.classList.add('hidden');
  if (btn) btn.innerText = 'Running...';

  state.bailoutTimer = setInterval(() => {
    state.bailoutSeconds--;
    const mins = Math.floor(state.bailoutSeconds / 60);
    const secs = state.bailoutSeconds % 60;
    if (disp) disp.innerText = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

    if (state.bailoutSeconds <= 0) {
      clearInterval(state.bailoutTimer);
      if (disp) disp.innerText = '00:00';
      if (alertMsg) alertMsg.classList.remove('hidden');
      if (btn) btn.innerText = 'Start 90s Clock';
      // Audio chime if AudioContext available
      try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        osc.frequency.setValueAtTime(440, ctx.currentTime);
        osc.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.3);
      } catch (e) {}
    }
  }, 1000);
}

function resetBailoutTimer() {
  clearInterval(state.bailoutTimer);
  state.bailoutSeconds = 90;
  const disp = document.getElementById('bailout-timer-display');
  const alertMsg = document.getElementById('bailout-alert-msg');
  const btn = document.getElementById('btn-bailout-toggle');
  if (disp) disp.innerText = '01:30';
  if (alertMsg) alertMsg.classList.add('hidden');
  if (btn) btn.innerText = 'Start 90s Clock';
}

async function updateAbandonmentROI() {
  const slider = document.getElementById('roi-time-slider');
  if (!slider) return;
  const mins = parseFloat(slider.value);
  const sliderVal = document.getElementById('roi-slider-val');
  if (sliderVal) sliderVal.innerText = `${mins} Minutes`;

  try {
    const res = await fetch('/api/tactics/abandonment-roi', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ minutes_spent_on_trap: mins, avg_question_time: 3.0 })
    });
    const data = await res.json();
    const altQ = document.getElementById('roi-alt-questions');
    const marksG = document.getElementById('roi-marks-gained');
    const netDiff = document.getElementById('roi-net-diff');
    if (altQ) altQ.innerText = `${data.questions_you_could_solve_instead} Questions`;
    if (marksG) marksG.innerText = `+${data.potential_marks_gained} Marks`;
    if (netDiff) netDiff.innerText = `+${data.net_mark_differential} Marks Saved`;
  } catch (e) {
    console.error('Error calculating abandonment ROI:', e);
  }
}

function toggleChaosAudio() {
  const statusEl = document.getElementById('chaos-audio-status');
  if (state.chaosNoiseNode) {
    // Stop audio
    state.chaosNoiseNode.stop();
    state.chaosNoiseNode.disconnect();
    state.chaosNoiseNode = null;
    if (statusEl) statusEl.innerText = 'OFF';
    return;
  }

  // Synthesize pink/brown ambient noise using Web Audio API buffer
  try {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!state.chaosAudioCtx) state.chaosAudioCtx = new AudioCtx();
    const ctx = state.chaosAudioCtx;
    if (ctx.state === 'suspended') ctx.resume();

    const bufferSize = ctx.sampleRate * 2;
    const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    let lastOut = 0.0;
    for (let i = 0; i < bufferSize; i++) {
      const white = Math.random() * 2 - 1;
      data[i] = (lastOut + 0.02 * white) / 1.02; // Brown noise algorithm
      lastOut = data[i];
      data[i] *= 0.12; // gentle volume
    }

    const noise = ctx.createBufferSource();
    noise.buffer = buffer;
    noise.loop = true;
    noise.connect(ctx.destination);
    noise.start();
    state.chaosNoiseNode = noise;
    if (statusEl) statusEl.innerText = 'EXAM HALL AMBIENT (ON)';
  } catch (err) {
    alert('Web Audio API not supported on this browser: ' + err.message);
  }
}


// =========================================================================
// 12. TRIGGER LINE ERROR NOTEBOOK & BLIND RE-SOLVE GATES
// =========================================================================
async function loadErrorsTab() {
  try {
    const res = await fetch('/api/errors/analytics');
    const data = await res.json();
    const totalEl = document.getElementById('err-kpi-total');
    const pendingEl = document.getElementById('err-kpi-pending');
    const clearedEl = document.getElementById('err-kpi-cleared');
    const recurringEl = document.getElementById('err-kpi-recurring');

    if (totalEl) totalEl.innerText = data.total_errors_logged;
    if (pendingEl) pendingEl.innerText = data.pending_blind_resolves;
    if (recurringEl) recurringEl.innerText = data.recurring_traps_count;

    await loadBlindResolveQueue();
  } catch (e) {
    console.error('Error loading errors tab:', e);
  }
}

async function submitErrorAutopsy(event) {
  event.preventDefault();
  const subject = document.getElementById('autopsy-subject').value;
  const chapter = document.getElementById('autopsy-chapter').value;
  const category = document.getElementById('autopsy-category').value;
  const title = document.getElementById('autopsy-q-title').value;
  const part1 = document.getElementById('autopsy-part1').value;
  const part2 = document.getElementById('autopsy-part2').value;
  const part3 = document.getElementById('autopsy-part3').value;

  try {
    const res = await fetch('/api/errors/autopsy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question_title: title,
        subject,
        chapter,
        error_category: category,
        wrong_thinking: part1,
        correct_logic: part2,
        trigger_line: part3,
        exam_type: 'JEE Advanced'
      })
    });
    const result = await res.json();

    if (result.recurrence_alert) {
      const banner = document.getElementById('recurrence-alert-banner');
      const bannerText = document.getElementById('recurrence-alert-text');
      if (banner && bannerText) {
        bannerText.innerText = `You have slipped on this identical concept ${result.recurrence_count} times! Trigger Line locked for tomorrow's Blind Re-solve Gate.`;
        banner.classList.remove('hidden');
      }
    }

    alert('✅ Trigger Line Autopsy locked! Scheduled for tomorrow\'s Blind Re-solve Gate.');
    document.getElementById('form-error-autopsy').reset();
    await loadErrorsTab();
  } catch (err) {
    alert('Failed to log error autopsy: ' + err.message);
  }
}

async function loadBlindResolveQueue() {
  const container = document.getElementById('blind-queue-list');
  if (!container) return;
  try {
    const res = await fetch('/api/errors/blind-queue');
    const queue = await res.json();

    if (!queue || queue.length === 0) {
      container.innerHTML = `
        <div class="p-6 rounded-xl border border-dashed border-slate-800 text-center space-y-2">
          <i data-lucide="check-circle-2" class="w-8 h-8 text-emerald-400 mx-auto"></i>
          <h4 class="font-bold text-xs text-slate-200">Blind Re-solve Gate is 100% Cleared!</h4>
          <p class="text-[11px] text-slate-500">Zero traps pending resolution. Every past error has been re-tested and mastered.</p>
        </div>
      `;
      if (window.lucide) lucide.createIcons();
      return;
    }

    container.innerHTML = queue.map(err => `
      <div class="p-4 rounded-xl border border-slate-800 bg-[#090e1a] space-y-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 font-bold">${err.subject} • ${err.chapter}</span>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">${err.error_category}</span>
          </div>
          <span class="text-xs font-mono ${err.recurrence_count > 1 ? 'text-rose-400 font-bold' : 'text-slate-400'}">
            Recurrence: ${err.recurrence_count}x
          </span>
        </div>
        <h4 class="font-bold text-sm text-slate-200">${err.question_title}</h4>
        
        <div id="trigger-reveal-${err.id}" class="hidden p-3 rounded-lg bg-slate-900 border border-amber-500/30 text-xs space-y-1">
          <span class="text-amber-400 font-bold block text-[11px]">Actionable Trigger Line:</span>
          <p class="text-slate-300 font-mono">${err.trigger_line}</p>
        </div>

        <div class="flex items-center justify-between pt-2 border-t border-slate-800/80">
          <button onclick="document.getElementById('trigger-reveal-${err.id}').classList.toggle('hidden')" class="text-xs text-slate-400 hover:text-amber-300 font-mono flex items-center gap-1">
            <i data-lucide="eye" class="w-3.5 h-3.5"></i> Peek Trigger Rule
          </button>
          <div class="flex gap-2">
            <button onclick="submitBlindResolve(${err.id}, true)" class="px-3 py-1.5 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 text-xs font-bold rounded-lg transition-all">
              ✓ Solved Cleanly (Pass)
            </button>
            <button onclick="submitBlindResolve(${err.id}, false)" class="px-3 py-1.5 bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40 text-xs font-bold rounded-lg transition-all">
              ✗ Slipped Again (Re-queue)
            </button>
          </div>
        </div>
      </div>
    `).join('');

    if (window.lucide) lucide.createIcons();
  } catch (e) {
    container.innerHTML = `<div class="text-xs text-rose-400 p-4">Error loading blind queue: ${e.message}</div>`;
  }
}

async function submitBlindResolve(errorId, success) {
  try {
    const res = await fetch('/api/errors/blind-resolve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error_id: errorId, success })
    });
    const data = await res.json();
    alert(data.message);
    await loadErrorsTab();
  } catch (e) {
    alert('Error submitting blind resolve: ' + e.message);
  }
}

async function loadPreMockDeck() {
  const container = document.getElementById('pre-mock-deck-container');
  const cardsBox = document.getElementById('pre-mock-deck-cards');
  if (!container || !cardsBox) return;

  try {
    const res = await fetch('/api/errors/pre-mock-deck');
    const cards = await res.json();
    container.classList.remove('hidden');

    if (!cards || cards.length === 0) {
      cardsBox.innerHTML = `
        <div class="col-span-2 text-center text-xs text-slate-400 py-6">
          No error autopsies logged yet! Once you log errors from practice sets, this deck will auto-generate your top 20 trap rules.
        </div>
      `;
      return;
    }

    cardsBox.innerHTML = cards.map(c => `
      <div class="p-4 rounded-xl bg-[#090e1a] border border-amber-500/30 space-y-2">
        <div class="flex items-center justify-between text-[11px] font-mono">
          <span class="text-amber-400 font-bold">${c.subject} • ${c.chapter}</span>
          <span class="text-slate-500">${c.error_category}</span>
        </div>
        <h5 class="text-xs font-semibold text-slate-200">${c.question_title}</h5>
        <div class="p-2.5 rounded bg-slate-900 border border-slate-800 text-xs font-mono text-amber-300">
          ⚡ Trigger Line: ${c.trigger_line}
        </div>
      </div>
    `).join('');
  } catch (e) {
    alert('Error generating pre-mock deck: ' + e.message);
  }
}

async function loadFormulaDecayPrompts() {
  try {
    const res = await fetch('/api/errors/formula-decay');
    const prompts = await res.json();
    if (!prompts || prompts.length === 0) {
      openGenericModal('Formula Active Recall Check', '<div class="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-300 text-sm font-semibold">🎉 All core formulas verified in active synaptic memory! Zero decay detected.</div>');
      return;
    }
    const p = prompts[0];
    const html = `
      <div class="space-y-4">
        <div class="flex items-center justify-between text-xs text-slate-400">
          <span class="px-2 py-0.5 bg-amber-500/20 text-amber-300 font-bold rounded">${p.subject} • ${p.chapter}</span>
          <span class="text-rose-400 font-semibold flex items-center gap-1"><i data-lucide="flame" class="w-3.5 h-3.5"></i> Synaptic Decay Prompt</span>
        </div>
        <div class="p-3 bg-slate-900 border border-slate-800 rounded-xl">
          <p class="text-xs text-slate-400 uppercase font-bold tracking-wider mb-1">Active Recall Question</p>
          <div class="text-sm font-semibold text-white">${renderMarkdownSafe(p.prompt_question)}</div>
        </div>
        <div class="p-3 bg-emerald-950/30 border border-emerald-500/30 rounded-xl">
          <p class="text-xs text-emerald-400 uppercase font-bold tracking-wider mb-1">Governing Law / Formula</p>
          <div class="text-sm font-medium text-emerald-200 math-content">${renderMarkdownSafe(p.formula_definition)}</div>
        </div>
        <div class="p-3 bg-indigo-950/30 border border-indigo-500/30 rounded-xl">
          <p class="text-xs text-indigo-400 uppercase font-bold tracking-wider mb-1">Limiting Cases & Boundary Conditions</p>
          <div class="text-xs text-indigo-200 math-content">${renderMarkdownSafe(p.limiting_cases)}</div>
        </div>
        <div class="p-3 bg-rose-950/30 border border-rose-500/30 rounded-xl">
          <p class="text-xs text-rose-400 uppercase font-bold tracking-wider mb-1">Avoidable Cognitive Trap</p>
          <div class="text-xs text-rose-200">${renderMarkdownSafe(p.trap_to_avoid)}</div>
        </div>
      </div>
    `;
    openGenericModal('⚡ Formula Active Recall Check', html);
  } catch (e) {
    console.error('Error fetching formula decay prompts:', e);
  }
}


// =========================================================================
// 13. OMNI-PLANNER & MULTI-DEADLINE SOLVER CONTROLLERS
// =========================================================================
async function loadOmniPlannerTab() {
  const container = document.getElementById('omni-schedule-container');
  if (!container) return;

  try {
    const res = await fetch('/api/omni-planner/schedule?days=14');
    const data = await res.json();

    if (!data.schedule || data.schedule.length === 0) {
      container.innerHTML = '<div class="text-xs text-slate-400 p-6">No schedule generated yet.</div>';
      return;
    }

    container.innerHTML = data.schedule.map(day => `
      <div class="p-5 rounded-2xl border border-slate-800 bg-[#090e1a] space-y-3">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
          <div class="flex items-center gap-3">
            <span class="font-bold text-sm text-slate-200">${day.date} (${day.day})</span>
            <span class="text-xs font-mono px-2.5 py-0.5 rounded-full font-bold ${
              day.mode === 'EXAM_DAY' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
              day.mode === 'BOARD_PRIORITY_OVERRIDE' ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20' :
              day.mode === '72H_COACHING_LOCK' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' :
              'bg-amber-500/10 text-amber-400 border border-amber-500/20'
            }">
              ${day.mode_label}
            </span>
          </div>
          <span class="text-xs font-mono text-slate-400 font-bold">${day.total_hours} Total Hours Scheduled</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
          ${day.blocks.map(b => `
            <div class="p-3 rounded-xl bg-slate-900/80 border border-slate-800/80 flex items-start gap-3">
              <span class="text-[11px] font-mono font-bold text-amber-400 shrink-0 mt-0.5">${b.time_slot}</span>
              <div>
                <p class="text-xs font-medium text-slate-200">${b.activity}</p>
                <span class="text-[10px] text-slate-500 font-mono">${b.duration_min} mins</span>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `).join('');

    if (window.lucide) lucide.createIcons();
  } catch (e) {
    container.innerHTML = `<div class="text-xs text-rose-400 p-4">Error loading omni-schedule: ${e.message}</div>`;
  }
}

async function runScopeCutter() {
  try {
    const res = await fetch('/api/omni-planner/scope-cut', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ daily_hours_exceeded: 2.5 })
    });
    const data = await res.json();
    alert(`✂️ SCOPE-CUTTER EXECUTED!\n\nHours Trimmed: ${data.hours_trimmed}h\nRecommendation: ${data.recommendation}\n\nPreserved: Rotational Mechanics Level-3 Problems & CBSE 5-Mark Derivations.\nPruned: Passive rereading and low-ROI filler.`);
  } catch (e) {
    alert('Error running scope-cutter: ' + e.message);
  }
}

function openWhatIfModal() {
  const scenario = prompt('Simulate What-If Scenario:\n1: Missed 3 days due to illness\n2: Coaching moved mock test 4 days earlier\n\nEnter 1 or 2:');
  if (!scenario) return;

  if (scenario === '1') {
    fetch('/api/omni-planner/what-if', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario_type: 'missed_days', params: { days: 3 } })
    }).then(r => r.json()).then(data => {
      alert(`🔮 WHAT-IF SIMULATION: ${data.scenario}\n\nImpact: ${data.impact_analysis}\n\nTrajectory: ${data.projected_air1_trajectory}\n\nRecovery Steps:\n• ${data.recovery_strategy.join('\n• ')}`);
    });
  } else if (scenario === '2') {
    fetch('/api/omni-planner/what-if', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario_type: 'coaching_test_shifted', params: { days: 4, test_name: 'Thermodynamics Mock' } })
    }).then(r => r.json()).then(data => {
      alert(`🔮 WHAT-IF SIMULATION: ${data.scenario}\n\nImpact: ${data.impact_analysis}\n\nTrajectory: ${data.projected_air1_trajectory}\n\nRecovery Steps:\n• ${data.recovery_strategy.join('\n• ')}`);
    });
  }
}


// =========================================================================
// 14. CBSE BOARD STEP-LOSS & NCERT CLOZE CONTROLLERS
// =========================================================================
state.cbseDerivations = [];
state.selectedDerivationKey = 'PHY_DERIV_01';

async function loadCbseStudioTab() {
  const listContainer = document.getElementById('cbse-derivations-list');
  if (!listContainer) return;

  try {
    const res = await fetch('/api/cbse/derivations');
    state.cbseDerivations = await res.json();

    listContainer.innerHTML = state.cbseDerivations.map(d => `
      <button onclick="selectCbseDerivation('${d.derivation_key}')" class="w-full text-left p-3 rounded-xl border ${
        state.selectedDerivationKey === d.derivation_key ? 'border-purple-500 bg-purple-500/10' : 'border-slate-800 bg-[#090e1a] hover:border-slate-700'
      } transition-all space-y-1">
        <div class="flex items-center justify-between text-[10px] font-mono">
          <span class="text-purple-400 font-bold">${d.subject}</span>
          <span class="text-slate-400">${d.total_marks} Marks</span>
        </div>
        <h5 class="text-xs font-semibold text-slate-200 line-clamp-2">${d.title}</h5>
      </button>
    `).join('');
  } catch (e) {
    console.error('Error loading derivations:', e);
  }
}

function selectCbseDerivation(key) {
  state.selectedDerivationKey = key;
  const target = state.cbseDerivations.find(d => d.derivation_key === key);
  const titleEl = document.getElementById('cbse-selected-title');
  const inputEl = document.getElementById('cbse-derivation-input');
  const outputEl = document.getElementById('cbse-grading-output');
  const badgeEl = document.getElementById('cbse-score-badge');

  if (target && titleEl) titleEl.innerText = target.title;
  if (inputEl) inputEl.value = '';
  if (outputEl) outputEl.classList.add('hidden');
  if (badgeEl) badgeEl.classList.add('hidden');

  loadCbseStudioTab();
}

async function gradeCurrentDerivation() {
  const inputEl = document.getElementById('cbse-derivation-input');
  if (!inputEl || !inputEl.value.trim()) {
    alert('Please type or paste your written derivation steps first!');
    return;
  }

  try {
    const res = await fetch('/api/cbse/evaluate-derivation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        derivation_key: state.selectedDerivationKey,
        student_text: inputEl.value
      })
    });
    const data = await res.json();
    const outputEl = document.getElementById('cbse-grading-output');
    const badgeEl = document.getElementById('cbse-score-badge');

    if (badgeEl) {
      badgeEl.classList.remove('hidden');
      badgeEl.innerText = `Score: ${data.marks_awarded} / ${data.max_marks} (${data.percentage}%)`;
    }

    if (outputEl) {
      outputEl.classList.remove('hidden');
      outputEl.innerHTML = `
        <div class="border-b border-slate-800 pb-3">
          <h4 class="font-bold text-sm text-purple-300">Official CBSE Step Marking Breakdown</h4>
          <p class="text-xs text-slate-400 mt-0.5">Marks awarded strictly based on official CBSE marking rubrics.</p>
        </div>

        <div class="space-y-2 pt-2">
          ${data.rubric_breakdown.map(step => `
            <div class="p-3 rounded-lg bg-slate-900 border ${
              step.status === 'FULL' ? 'border-emerald-500/30' :
              step.status === 'PARTIAL' ? 'border-amber-500/30' : 'border-rose-500/30'
            } flex items-center justify-between text-xs">
              <div>
                <span class="font-medium text-slate-200 block">${step.criterion}</span>
                <span class="text-[10px] text-slate-500 font-mono">Matched: ${step.matched_keywords.join(', ') || 'None'}</span>
              </div>
              <span class="font-mono font-bold ${
                step.status === 'FULL' ? 'text-emerald-400' :
                step.status === 'PARTIAL' ? 'text-amber-400' : 'text-rose-400'
              }">${step.marks_awarded} / ${step.max_marks}</span>
            </div>
          `).join('')}
        </div>

        ${data.missing_elements && data.missing_elements.length > 0 ? `
          <div class="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-xs text-rose-300 space-y-1 mt-3">
            <span class="font-bold block">⚠️ Elements Lost in Step-Marking:</span>
            <ul class="list-disc list-inside space-y-0.5 text-[11px] text-rose-200/90">
              ${data.missing_elements.map(m => `<li>${m}</li>`).join('')}
            </ul>
          </div>
        ` : ''}

        <div class="text-[11px] font-mono text-amber-400/90 pt-2 border-t border-slate-800">
          Examiner Note: ${data.board_examiner_note}
        </div>
      `;
    }
  } catch (err) {
    alert('Error evaluating derivation: ' + err.message);
  }
}

async function loadNcertClozeCards() {
  const container = document.getElementById('ncert-cloze-container');
  const cardsBox = document.getElementById('ncert-cloze-cards');
  if (!container || !cardsBox) return;

  try {
    const res = await fetch('/api/cbse/ncert-cloze');
    const cards = await res.json();
    container.classList.remove('hidden');

    cardsBox.innerHTML = cards.map(c => `
      <div class="p-4 rounded-xl bg-[#090e1a] border border-purple-500/30 space-y-3">
        <div class="flex items-center justify-between text-[11px] font-mono">
          <span class="text-purple-400 font-bold">${c.subject}</span>
          <span class="text-slate-400">${c.chapter}</span>
        </div>
        <p class="text-xs text-slate-200 leading-relaxed font-sans">${c.prompt}</p>
        <div id="cloze-ans-${c.id}" class="hidden p-2.5 rounded bg-slate-900 border border-slate-800 text-xs space-y-1">
          <span class="font-bold text-emerald-400 block text-[11px]">Exact Blanks: ${c.blanks.join(' & ')}</span>
          <p class="text-slate-400 text-[11px]">${c.explanation}</p>
        </div>
        <button onclick="document.getElementById('cloze-ans-${c.id}').classList.toggle('hidden')" class="text-xs text-purple-400 hover:text-purple-300 font-mono">
          Reveal CBSE Keywords
        </button>
      </div>
    `).join('');
  } catch (e) {
    alert('Error loading NCERT cloze drill: ' + e.message);
  }
}


// =========================================================================
// 15. PEAK PERFORMANCE, WHY WALL & SIBLING REVIEW CONTROLLERS
// =========================================================================
async function loadWellnessTab() {
  try {
    // 1. Sibling report
    const sRes = await fetch('/api/wellness/sibling-report');
    const sData = await sRes.json();
    if (sData.weekly_metrics) {
      const wEl = document.getElementById('sib-work-hours');
      const slEl = document.getElementById('sib-sleep-hours');
      const clEl = document.getElementById('sib-cleared-traps');
      const trEl = document.getElementById('sib-triage-acc');
      const actEl = document.getElementById('sib-action-item');
      const badgeEl = document.getElementById('sibling-burnout-badge');

      if (wEl) wEl.innerText = `${sData.weekly_metrics.avg_daily_deep_work_hours} hrs`;
      if (slEl) slEl.innerText = `${sData.weekly_metrics.avg_daily_sleep_hours} hrs`;
      if (clEl) clEl.innerText = `${sData.weekly_metrics.traps_permanently_cleared} Traps`;
      if (trEl) trEl.innerText = sData.weekly_metrics.triage_appraisal_accuracy;
      if (actEl) actEl.innerText = `"${sData.recommended_sibling_action}"`;
      if (badgeEl) badgeEl.innerText = `Risk: ${sData.burnout_risk_index}`;
    }

    // 2. Why wall data
    const wRes = await fetch('/api/wellness/why-wall');
    const wData = await wRes.json();
    const collegeIn = document.getElementById('why-target-college');
    const sibIn = document.getElementById('why-sibling-contact');
    const noteIn = document.getElementById('why-note-input');
    const deloadStatus = document.getElementById('deload-status-text');

    if (collegeIn) collegeIn.value = wData.target_college || 'IIT Bombay - Computer Science (AIR 1)';
    if (sibIn) sibIn.value = wData.sibling_contact || 'Bhaiya (Kaustav)';
    if (noteIn) noteIn.value = wData.why_wall_note || 'To secure AIR 1 through flawless daily execution.';
    if (deloadStatus) deloadStatus.innerText = wData.deload_week_active ? 'ACTIVE' : 'OFF';

  } catch (e) {
    console.error('Error loading wellness tab:', e);
  }
}

async function submitDailyWellness(event) {
  event.preventDefault();
  const sleep = parseFloat(document.getElementById('well-sleep-hours').value);
  const study = parseFloat(document.getElementById('well-study-hours').value);
  const energy = parseInt(document.getElementById('well-energy-rating').value);
  const silly = parseInt(document.getElementById('well-silly-count').value);

  try {
    const res = await fetch('/api/wellness/log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        study_hours: study,
        sleep_hours: sleep,
        energy_rating: energy,
        silly_mistake_count: silly,
        mood: energy > 7 ? 'sharp' : 'steady'
      })
    });
    const result = await res.json();
    const badge = document.getElementById('kill-switch-badge');

    if (result.fatigue_alert) {
      if (badge) {
        badge.className = 'text-xs font-mono font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30 px-3 py-1 rounded-full';
        badge.innerText = 'Kill-Switch: ENGAGED (REST MANDATED)';
      }
      alert(`⚠️ COGNITIVE FATIGUE ALERT ENGAGED!\n\nReason: ${result.fatigue_reason}\n\nRecommendation: ${result.recommendation}\nFull mocks are locked for tonight. Sleep or do light NCERT reading.`);
    } else {
      if (badge) {
        badge.className = 'text-xs font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-3 py-1 rounded-full';
        badge.innerText = 'Kill-Switch: DISENGAGED (PEAK STATE)';
      }
      alert('🌿 Daily wellness logged! Optimal neurological state confirmed.');
    }

    await loadWellnessTab();
  } catch (err) {
    alert('Failed to log wellness: ' + err.message);
  }
}

async function saveWhyWall() {
  const college = document.getElementById('why-target-college').value;
  const note = document.getElementById('why-note-input').value;

  try {
    const res = await fetch('/api/wellness/why-wall', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target_campus: college.split('-')[0].trim(),
        target_college: college,
        why_note: note
      })
    });
    const data = await res.json();
    alert('🌟 Why Wall updated! Grounded in purpose.');
  } catch (e) {
    alert('Error updating Why Wall: ' + e.message);
  }
}

async function toggleDeloadWeekMode() {
  const statusEl = document.getElementById('deload-status-text');
  const currentActive = statusEl && statusEl.innerText === 'ACTIVE';
  const newActive = !currentActive;

  try {
    const res = await fetch('/api/wellness/deload-toggle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ active: newActive })
    });
    const data = await res.json();
    alert(data.message);
    if (statusEl) statusEl.innerText = newActive ? 'ACTIVE' : 'OFF';
  } catch (e) {
    alert('Error toggling deload week: ' + e.message);
  }
}


// =========================================================================
// 15. NEXT-BEST-ACTION & CALIBRATED READINESS FORECAST (FEATURE 10)
// =========================================================================
let nextBestActionTargetTab = 'sololearn';

async function loadNextBestAction() {
  const container = document.getElementById('nba-card-container');
  if (!container) return;
  try {
    const res = await fetch('/api/next-best-action');
    const data = await res.json();
    if (!data || data.status !== 'success') return;

    nextBestActionTargetTab = data.tab_target || 'sololearn';

    const pBadge = document.getElementById('nba-priority-badge');
    if (pBadge) pBadge.innerText = data.priority_level || 'RECOMMENDED';

    const tBadge = document.getElementById('nba-est-mins');
    if (tBadge) tBadge.innerText = data.estimated_minutes || 20;

    const titleEl = document.getElementById('nba-title');
    if (titleEl) titleEl.innerText = data.title;

    const subEl = document.getElementById('nba-subject-chapter');
    if (subEl) subEl.innerText = `${data.subject} • ${data.chapter}`;

    const whyEl = document.getElementById('nba-why');
    if (whyEl) whyEl.innerHTML = renderMarkdownSafe(data.why_selected);

    const metEl = document.getElementById('nba-metric');
    if (metEl) metEl.innerText = `Target: ${data.target_metric}`;

    const btnEl = document.getElementById('nba-btn-text');
    if (btnEl) btnEl.innerText = data.action_button || 'Execute Next Action';

    renderMath(container);
  } catch (err) {
    console.error('Failed to load Next-Best-Action:', err);
  }
}

function executeNextBestAction() {
  switchTab(nextBestActionTargetTab);
}

async function loadReadinessForecast() {
  const container = document.getElementById('readiness-forecast-card');
  if (!container) return;
  try {
    const res = await fetch('/api/readiness-forecast');
    const data = await res.json();
    if (!data || data.status !== 'success') return;

    const confBadge = document.getElementById('forecast-conf-badge');
    if (confBadge) confBadge.innerText = `${data.confidence_level} Conf`;

    const rankBand = document.getElementById('forecast-rank-band');
    if (rankBand) rankBand.innerText = data.projected_rank_band;

    const uncEl = document.getElementById('forecast-uncertainty');
    if (uncEl) uncEl.innerText = data.uncertainty_range;

    const barsContainer = document.getElementById('forecast-metrics-bars');
    if (barsContainer && data.readiness_metrics) {
      barsContainer.innerHTML = data.readiness_metrics.map(m => `
        <div>
          <div class="flex justify-between text-[11px] text-slate-300 mb-0.5">
            <span>${m.dimension}</span>
            <span class="font-bold ${m.score_pct >= 90 ? 'text-emerald-400' : 'text-amber-400'}">${m.score_pct}%</span>
          </div>
          <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div class="${m.score_pct >= 90 ? 'bg-emerald-500' : 'bg-amber-500'} h-full" style="width: ${m.score_pct}%"></div>
          </div>
        </div>
      `).join('');
    }
  } catch (err) {
    console.error('Failed to load Readiness Forecast:', err);
  }
}

// =========================================================================
// 16. SECTION 8: AI MENTOR 10 TEACHING MODES & PROVE-IT CHALLENGE
// =========================================================================
let currentMentorMode = 'socratic';
let currentMentorModeLabel = '1. Socratic (Guiding Questions)';

function setMentorMode(mode, label) {
  currentMentorMode = mode;
  currentMentorModeLabel = label;
  
  const lbl = document.getElementById('active-mentor-mode-label');
  if (lbl) lbl.innerText = label;

  document.querySelectorAll('.mentor-mode-chip').forEach(btn => {
    btn.classList.remove('active', 'bg-amber-500', 'text-slate-950');
    btn.classList.add('bg-slate-800', 'text-slate-300');
  });
  if (window.event && window.event.target) {
    window.event.target.classList.add('active', 'bg-amber-500', 'text-slate-950');
    window.event.target.classList.remove('bg-slate-800', 'text-slate-300');
  }

  appendMentorMessage('assistant', `**[Mode Switched: ${label}]**\nEngaged specialized pedagogy. Ask your question or paste a problem.`);
}

async function launchProveItChallenge(conceptId = 'phy_rot_01') {
  try {
    const res = await fetch(`/api/mentor/prove-it/${conceptId}`);
    const data = await res.json();
    const html = `
      <div class="space-y-4">
        <h4 class="font-black text-white text-base">${data.title}</h4>
        <div class="p-3 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-200 math-content">
          ${renderMarkdownSafe(data.prompt)}
        </div>
        <div class="p-3 bg-amber-950/30 border border-amber-500/30 rounded-xl">
          <p class="text-xs text-amber-400 font-bold mb-1">Limiting Case Test:</p>
          <div class="text-xs text-slate-300 math-content">${renderMarkdownSafe(data.limiting_test)}</div>
        </div>
        <div class="p-3 bg-emerald-950/30 border border-emerald-500/30 rounded-xl">
          <p class="text-xs text-emerald-400 font-bold mb-1">Expected Rigor Criteria:</p>
          <ul class="list-disc pl-4 text-xs text-slate-300 space-y-1 math-content">
            ${data.expected_criteria.map(c => `<li>${renderMarkdownSafe(c)}</li>`).join('')}
          </ul>
        </div>
      </div>
    `;
    openGenericModal('🏆 Prove-It Challenge', html);
  } catch (err) {
    console.error('Failed to launch Prove-It challenge:', err);
  }
}

// =========================================================================
// 17. COUNTEREXAMPLE LAB & ALTERNATE SOLUTIONS
// =========================================================================
async function loadCounterexampleLab() {
  const grid = document.getElementById('counterexample-cards-grid');
  if (!grid) return;
  try {
    const res = await fetch('/api/counterexample-lab');
    const cases = await res.json();
    if (!cases || cases.length === 0) return;

    grid.innerHTML = cases.map(c => `
      <div class="bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-col justify-between space-y-3 hover:border-rose-500/50 transition-all">
        <div>
          <div class="flex items-center justify-between text-[11px] mb-1">
            <span class="px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 font-bold border border-rose-500/30">${c.subject}</span>
            <span class="text-slate-400">${c.topic}</span>
          </div>
          <h4 class="font-bold text-xs text-white math-content mt-2">${renderMarkdownSafe(c.question)}</h4>
          <div class="mt-2.5 p-2.5 bg-rose-950/30 border border-rose-500/20 rounded-lg">
            <p class="text-[10px] font-bold text-rose-400 uppercase tracking-wide">Common Apparent Shortcut (Trap!):</p>
            <p class="text-xs text-rose-200/90 mt-0.5 line-through math-content">${renderMarkdownSafe(c.apparent_rule)}</p>
          </div>
          <div class="mt-2.5 p-2.5 bg-emerald-950/30 border border-emerald-500/20 rounded-lg">
            <p class="text-[10px] font-bold text-emerald-400 uppercase tracking-wide">Counterexample Reality:</p>
            <p class="text-xs text-emerald-200 mt-0.5 math-content">${renderMarkdownSafe(c.counterexample_reality)}</p>
          </div>
        </div>
        <div class="pt-2 border-t border-slate-800/80">
          <p class="text-[11px] font-mono text-amber-300/90"><span class="font-bold text-amber-400">Trigger Line:</span> ${c.trigger_line}</p>
        </div>
      </div>
    `).join('');

    renderMath(grid);
  } catch (err) {
    console.error('Failed to load Counterexample Lab:', err);
  }
}

async function loadAlternateSolutions() {
  const container = document.getElementById('alternate-solutions-grid');
  if (!container) return;
  try {
    const res = await fetch('/api/alternate-solutions');
    const cases = await res.json();
    if (!cases || cases.length === 0) return;

    container.innerHTML = cases.map(c => `
      <div class="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4 hover:border-indigo-500/50 transition-all">
        <h4 class="font-bold text-sm text-white math-content">${renderMarkdownSafe(c.title)}</h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Method 1 -->
          <div class="p-3.5 bg-slate-950 border border-rose-500/30 rounded-xl space-y-1.5">
            <div class="flex items-center justify-between text-xs">
              <span class="font-bold text-rose-400">${c.method_1.name}</span>
              <span class="text-rose-300 font-mono text-[11px]">~${c.method_1.time_minutes} min | ${c.method_1.error_probability} error risk</span>
            </div>
            <p class="text-xs text-slate-300 math-content">${renderMarkdownSafe(c.method_1.steps)}</p>
          </div>
          <!-- Method 2 -->
          <div class="p-3.5 bg-slate-950 border border-emerald-500/30 rounded-xl space-y-1.5">
            <div class="flex items-center justify-between text-xs">
              <span class="font-bold text-emerald-400">${c.method_2.name}</span>
              <span class="text-emerald-300 font-mono text-[11px]">~${c.method_2.time_minutes} min | ${c.method_2.error_probability} error risk</span>
            </div>
            <p class="text-xs text-slate-300 math-content">${renderMarkdownSafe(c.method_2.steps)}</p>
          </div>
        </div>
        <div class="p-2.5 bg-indigo-950/30 border border-indigo-500/30 rounded-xl text-xs text-indigo-300 font-mono flex items-center gap-2">
          <i data-lucide="compass" class="w-4 h-4 text-indigo-400 shrink-0"></i>
          <span>${c.strategic_takeaway}</span>
        </div>
      </div>
    `).join('');

    renderMath(container);
    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error('Failed to load Alternate Solutions:', err);
  }
}


// =========================================================================
// 18. 3-PASS EXAM STRATEGY, 90S BAILOUT & 6-HOUR ENDURANCE ENGINE
// =========================================================================
let cbtActivePass = 1;
let cbtQuestionSeconds = 0;
let cbtQuestionTimerInterval = null;

function setCbtPass(passNum) {
  cbtActivePass = passNum;
  document.getElementById('cbt-pass-1-btn').className = passNum === 1 ? 'px-2 py-0.5 rounded bg-amber-500 text-slate-950 font-bold text-[11px]' : 'px-2 py-0.5 rounded text-slate-400 hover:text-white text-[11px]';
  document.getElementById('cbt-pass-2-btn').className = passNum === 2 ? 'px-2 py-0.5 rounded bg-amber-500 text-slate-950 font-bold text-[11px]' : 'px-2 py-0.5 rounded text-slate-400 hover:text-white text-[11px]';

  if (passNum === 1) {
    alert('🎯 Pass 1 (Score Harvesting) Active:\nSweep through the paper solving only low-friction, direct formula problems (< 2.5 min). If any question stalls past 2 mins, mark it for Pass 2 and move immediately!');
  } else if (passNum === 2) {
    alert('⚡ Pass 2 (Heavy Lifting) Active:\nUnlock medium-hard multi-step questions and coordinate geometry computations that require 3-6 minutes of sustained derivation.');
  }
}

function startCbtQuestionTimer() {
  if (cbtQuestionTimerInterval) clearInterval(cbtQuestionTimerInterval);
  cbtQuestionSeconds = 0;
  const timerEl = document.getElementById('cbt-q-timer');
  const badgeEl = document.getElementById('cbt-bailout-indicator');
  if (timerEl) timerEl.innerText = '00:00';
  if (badgeEl) {
    badgeEl.className = 'px-3 py-1 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-cyan-300 flex items-center gap-1';
  }

  cbtQuestionTimerInterval = setInterval(() => {
    cbtQuestionSeconds++;
    const m = String(Math.floor(cbtQuestionSeconds / 60)).padStart(2, '0');
    const s = String(cbtQuestionSeconds % 60).padStart(2, '0');
    if (timerEl) timerEl.innerText = `${m}:${s}`;

    if (cbtQuestionSeconds >= 90 && badgeEl) {
      // 90s Bailout Alert
      badgeEl.className = 'px-3 py-1 bg-rose-950/80 border border-rose-500 rounded-lg text-xs font-mono text-rose-300 font-bold animate-pulse flex items-center gap-1';
      if (cbtQuestionSeconds === 90) {
        console.warn('90-Second Bailout Triggered: Sunk-cost avoidance protocol active.');
      }
    }
  }, 1000);
}

function openNegativeMarkingMathModal() {
  const html = `
    <div class="space-y-4">
      <div class="p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl text-xs text-amber-200">
        <strong>JEE Advanced Pass 3 Risk Management (Final 30 Minutes):</strong><br/>
        AIR 1 rankers do not guess blindly. They use expected value mathematics to determine whether to take a partial-knowledge gamble.
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- 4 Options Blind -->
        <div class="p-3.5 bg-slate-900 border border-rose-500/30 rounded-xl space-y-1">
          <h5 class="font-bold text-rose-400 text-xs">Blind 4-Option Guess (Zero Eliminated)</h5>
          <p class="text-xs text-slate-300 font-mono">$$\\mathbb{E} = \\frac{1}{4}(+4) + \\frac{3}{4}(-2) = +1.0 - 1.5 = -0.5$$</p>
          <p class="text-[11px] text-rose-300 font-bold">Verdict: STRICTLY FORBIDDEN (Eats Your Rank)</p>
        </div>

        <!-- 2 Options Eliminated -->
        <div class="p-3.5 bg-slate-900 border border-emerald-500/30 rounded-xl space-y-1">
          <h5 class="font-bold text-emerald-400 text-xs">50/50 Gamble (2 Options Eliminated)</h5>
          <p class="text-xs text-slate-300 font-mono">$$\\mathbb{E} = \\frac{1}{2}(+4) + \\frac{1}{2}(-2) = +2.0 - 1.0 = +1.0$$</p>
          <p class="text-[11px] text-emerald-300 font-bold">Verdict: STATISTICALLY FAVORABLE (+1.0 expected value!)</p>
        </div>

        <!-- Multi-Correct Partial -->
        <div class="p-3.5 bg-slate-900 border border-cyan-500/30 rounded-xl space-y-1">
          <h5 class="font-bold text-cyan-400 text-xs">Multi-Correct Partial Marking Strategy</h5>
          <p class="text-xs text-slate-300 font-mono">Any wrong option $\\implies -2$ penalty. Never guess unverified options.</p>
          <p class="text-[11px] text-cyan-300 font-bold">Verdict: Mark ONLY options you have rigorous mathematical proof for.</p>
        </div>

        <!-- Numerical Free Roll -->
        <div class="p-3.5 bg-slate-900 border border-purple-500/30 rounded-xl space-y-1">
          <h5 class="font-bold text-purple-400 text-xs">Numerical Type (0 Negative Marks)</h5>
          <p class="text-xs text-slate-300 font-mono">$$\\mathbb{E} \\ge 0$$ on all integer/numerical inputs.</p>
          <p class="text-[11px] text-purple-300 font-bold">Verdict: ALWAYS enter your dimensional estimate before submitting.</p>
        </div>
      </div>
    </div>
  `;
  openGenericModal('📊 Negative Marking Math & Pass 3 Risk Sieve', html);
}

function launchSixHourEnduranceModal() {
  const html = `
    <div class="space-y-4">
      <div class="p-3 bg-purple-500/10 border border-purple-500/30 rounded-xl text-xs text-purple-200">
        <strong>Circadian Exam Clock Synchronization:</strong><br/>
        JEE Advanced consists of two brutal 3-hour shifts on the same day. Top rankers train their central nervous system to peak twice without calculation burnout in Paper 2.
      </div>

      <div class="space-y-3">
        <div class="p-3 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-between text-xs">
          <div>
            <span class="font-bold text-slate-200 block">Shift 1: JEE Advanced Paper 1 (Full 3 Hours)</span>
            <span class="text-slate-400 text-[11px] font-mono">Official Window: 09:00 AM &ndash; 12:00 PM</span>
          </div>
          <span class="px-2 py-1 bg-emerald-500/20 text-emerald-300 rounded font-bold">Shift 1</span>
        </div>

        <div class="p-3 bg-slate-950 border border-indigo-500/30 rounded-xl flex items-center justify-between text-xs">
          <div>
            <span class="font-bold text-indigo-300 block">Mandatory 2-Hour Screen Cooling Break</span>
            <span class="text-slate-400 text-[11px] font-mono">Window: 12:00 PM &ndash; 02:30 PM (Zero doomscrolling, light nutrition, hydration)</span>
          </div>
          <span class="px-2 py-1 bg-indigo-500/20 text-indigo-300 rounded font-bold">Cooling Interval</span>
        </div>

        <div class="p-3 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-between text-xs">
          <div>
            <span class="font-bold text-slate-200 block">Shift 2: JEE Advanced Paper 2 (Full 3 Hours)</span>
            <span class="text-slate-400 text-[11px] font-mono">Official Window: 02:30 PM &ndash; 05:30 PM</span>
          </div>
          <span class="px-2 py-1 bg-purple-500/20 text-purple-300 rounded font-bold">Shift 2</span>
        </div>
      </div>

      <div class="pt-2 flex justify-end gap-2">
        <button onclick="closeModal(); switchTab('mock-exam'); alert('Ready to launch Paper 1! Ensure water bottle, blank rough scratchpad, and timer are set.');" class="px-4 py-2 bg-purple-500 hover:bg-purple-400 text-slate-950 font-bold rounded-xl text-xs">
          Start Paper 1 Lock-In
        </button>
      </div>
    </div>
  `;
  openGenericModal('⏱️ 6-Hour Dual-Shift Endurance Protocol', html);
}


// =========================================================================
// 19. BROTHER'S DEDICATED PROFILE COCKPIT CONTROLLER
// =========================================================================
async function loadProfileTab() {
  try {
    const res = await fetch('/api/profile/dossier');
    const data = await res.json();
    if (!data || data.status !== 'success') return;

    const p = data.profile;
    const t = data.telemetry;

    // Update Dossier Banner
    const nameEl = document.getElementById('prof-hero-name');
    if (nameEl) nameEl.innerText = p.name || "Kaustav's Brother";

    const subEl = document.getElementById('prof-hero-subtitle');
    if (subEl) subEl.innerHTML = `Target: <span class="text-amber-400 font-bold">AIR ${p.target_jee_rank || 1} in JEE Advanced ${p.target_year || 2027}</span> &bull; <span class="text-pink-400 font-bold">${p.target_board_pct || 98.0}%+ in CBSE Class 12 Boards</span>`;

    // Cards
    const yrEl = document.getElementById('prof-target-year-display');
    if (yrEl) yrEl.innerText = `JEE ${p.target_year || 2027} AIR ${p.target_jee_rank || 1}`;

    const bdEl = document.getElementById('prof-board-pct-display');
    if (bdEl) bdEl.innerText = `${p.target_board_pct || 98.0}% +`;

    const schEl = document.getElementById('prof-school-name-display');
    if (schEl) schEl.innerText = p.school_name ? `School: ${p.school_name}` : 'School: CBSE Class 12';

    const cchEl = document.getElementById('prof-coaching-display');
    if (cchEl) cchEl.innerText = p.coaching_institute || 'Self-Study + Test Series';

    const grdEl = document.getElementById('prof-grade-display');
    if (grdEl) grdEl.innerText = `${p.grade || '12th'} Grade`;

    const fortEl = document.getElementById('prof-fortitude-display');
    if (fortEl) fortEl.innerText = `${p.mental_fortitude_rating || 9.2} / 10`;

    const strkEl = document.getElementById('prof-streak-display');
    if (strkEl) strkEl.innerText = `${p.streak_days || 1} Day${p.streak_days === 1 ? '' : 's'}`;

    const xpEl = document.getElementById('prof-xp-display');
    if (xpEl) xpEl.innerText = `${p.xp || 120} XP`;

    // Test Series badges
    const seriesContainer = document.getElementById('prof-test-series-badges');
    if (seriesContainer && p.test_series_enrolled && p.test_series_enrolled.length > 0) {
      seriesContainer.innerHTML = p.test_series_enrolled.map(s => `
        <span class="px-3 py-1.5 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-bold flex items-center gap-1.5">
          <i data-lucide="check-circle-2" class="w-3.5 h-3.5 text-indigo-400"></i> ${s}
        </span>
      `).join('');
      if (window.lucide) lucide.createIcons();
    }
  } catch (err) {
    console.error('Failed to load Brother Profile Dossier:', err);
  }
}

function openEditBrotherProfileModal() {
  const modal = document.getElementById('modal-container');
  const inner = document.getElementById('modal-content');

  inner.innerHTML = `
    <div class="flex items-center justify-between border-b border-slate-800 pb-3">
      <h3 class="text-base font-bold text-white flex items-center gap-2">
        <i data-lucide="user-edit" class="w-4 h-4 text-amber-400"></i>
        Edit Brother's Profile & Target Year
      </h3>
      <button onclick="closeModal()" class="text-slate-400 hover:text-white">&times;</button>
    </div>

    <form onsubmit="saveBrotherProfileChanges(event)" class="space-y-4 text-xs">
      <div>
        <label class="block font-semibold text-slate-300 mb-1">Brother's Name</label>
        <input type="text" id="edit-brother-name" value="${document.getElementById('prof-hero-name')?.innerText || "Kaustav's Brother"}" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-100 focus:outline-none focus:border-amber-400">
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block font-semibold text-slate-300 mb-1">Target Exam Year</label>
          <select id="edit-brother-year" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-100 focus:outline-none focus:border-amber-400">
            <option value="2027" selected>2027 (Recommended)</option>
            <option value="2026">2026</option>
            <option value="2028">2028</option>
          </select>
        </div>
        <div>
          <label class="block font-semibold text-slate-300 mb-1">Target Board %</label>
          <input type="number" id="edit-brother-board-pct" step="0.5" min="75" max="100" value="98.0" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-100 focus:outline-none focus:border-amber-400">
        </div>
      </div>

      <div>
        <label class="block font-semibold text-slate-300 mb-1">School Name</label>
        <input type="text" id="edit-brother-school" placeholder="e.g. Delhi Public School" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-100 focus:outline-none focus:border-amber-400">
      </div>

      <div>
        <label class="block font-semibold text-slate-300 mb-1">Coaching / Institute</label>
        <input type="text" id="edit-brother-coaching" value="Self-Study + Test Series" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-100 focus:outline-none focus:border-amber-400">
      </div>

      <div class="flex justify-end gap-2 pt-3 border-t border-slate-800">
        <button type="button" onclick="closeModal()" class="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl font-medium">Cancel</button>
        <button type="submit" class="px-5 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl shadow-lg shadow-amber-500/20">
          Save Changes & Synchronize
        </button>
      </div>
    </form>
  `;

  modal.classList.remove('hidden');
  if (window.lucide) lucide.createIcons();
}

async function saveBrotherProfileChanges(e) {
  e.preventDefault();
  const name = document.getElementById('edit-brother-name').value.trim();
  const target_year = parseInt(document.getElementById('edit-brother-year').value);
  const target_board_pct = parseFloat(document.getElementById('edit-brother-board-pct').value);
  const school_name = document.getElementById('edit-brother-school').value.trim();
  const coaching_institute = document.getElementById('edit-brother-coaching').value.trim();

  try {
    const res = await fetch('/api/profile/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name,
        target_year,
        target_board_pct,
        school_name,
        coaching_institute
      })
    });
    const data = await res.json();
    if (data.status === 'success') {
      closeModal();
      await loadProfile();
      await loadProfileTab();
      alert(`🎉 Profile successfully updated for ${name}! Zero fake data maintained.`);
    }
  } catch (err) {
    alert('Failed to update profile: ' + err.message);
  }
}

async function exportAcademicDossier() {
  try {
    const res = await fetch('/api/profile/dossier');
    const data = await res.json();
    const str = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data, null, 2));
    const a = document.createElement('a');
    a.setAttribute("href", str);
    a.setAttribute("download", `JEE_AIR1_${(data.profile?.name || 'Brother').replace(/\s+/g, '_')}_Dossier.json`);
    document.body.appendChild(a);
    a.click();
    a.remove();
  } catch (err) {
    alert('Failed to export dossier: ' + err.message);
  }
}

const AIR1_ROADMAP = {
  Physics: {
    "Class 11": ["Physical World", "Units and Measurements", "Motion in a Straight Line", "Motion in a Plane", "Laws of Motion", "Work, Energy and Power", "System of Particles and Rotational Motion", "Gravitation", "Mechanical Properties of Solids", "Mechanical Properties of Fluids", "Thermal Properties of Matter", "Thermodynamics", "Kinetic Theory", "Oscillations", "Waves"],
    "Class 12": ["Electric Charges and Fields", "Electrostatic Potential and Capacitance", "Current Electricity", "Moving Charges and Magnetism", "Magnetism and Matter", "Electromagnetic Induction", "Alternating Current", "Electromagnetic Waves", "Ray Optics and Optical Instruments", "Wave Optics", "Dual Nature of Radiation and Matter", "Atoms", "Nuclei", "Semiconductor Electronics"]
  },
  Chemistry: {
    "Class 11": ["Some Basic Concepts of Chemistry", "Structure of Atom", "Classification of Elements and Periodicity", "Chemical Bonding and Molecular Structure", "Thermodynamics", "Equilibrium", "Redox Reactions", "Organic Chemistry: Basic Principles", "Hydrocarbons"],
    "Class 12": ["Solutions", "Electrochemistry", "Chemical Kinetics", "The d- and f-Block Elements", "Coordination Compounds", "Haloalkanes and Haloarenes", "Alcohols, Phenols and Ethers", "Aldehydes, Ketones and Carboxylic Acids", "Amines", "Biomolecules"]
  },
  Mathematics: {
    "Class 11": ["Sets", "Relations and Functions", "Trigonometric Functions", "Complex Numbers and Quadratic Equations", "Linear Inequalities", "Permutations and Combinations", "Binomial Theorem", "Sequences and Series", "Straight Lines", "Conic Sections", "Limits and Derivatives", "Statistics", "Probability"],
    "Class 12": ["Relations and Functions", "Inverse Trigonometric Functions", "Matrices", "Determinants", "Continuity and Differentiability", "Applications of Derivatives", "Integrals", "Applications of Integrals", "Differential Equations", "Vector Algebra", "Three Dimensional Geometry", "Linear Programming", "Probability"]
  }
};
function topicPack(subject, chapter) {
  const c = chapter.toLowerCase();
  if (c.indexOf("electrochem") >= 0) return [
    {name: "Cell representation", concept: "Write the oxidation half at the left anode and the reduction half at the right cathode. The salt bridge keeps the solutions electrically neutral.", easy: "Left side loses electrons. Right side gains electrons.", q: "In Zn|Zn2+||Cu2+|Cu, which electrode is the anode?", options: ["Zn", "Cu", "The salt bridge", "Cu2+"], answer: 0},
    {name: "Nernst equation", concept: "At 298 K, E = E° - (0.059/n) log Q. n is the electrons in the balanced cell reaction, and Q uses the concentrations now.", easy: "If the product concentration is smaller than the standard state, log Q is negative, so E is larger than E°.", q: "Zn|Zn2+(0.01 M)||Cu2+(1 M)|Cu, E° = 1.10 V. What is E at 298 K?", options: ["1.16 V", "1.04 V", "1.10 V", "0.99 V"], answer: 0}
  ];
  if (c.indexOf("rotational") >= 0) return [
    {name: "Torque and angular momentum", concept: "Torque is r cross F. For a rigid body, torque equals I alpha about the same axis.", easy: "A force through the axis gives zero torque because the lever arm is zero.", q: "A force acts through the centre of a wheel. The torque about the centre is", options: ["Zero", "Fr", "I alpha only", "mv"], answer: 0},
    {name: "Pure rolling", concept: "On a surface at rest, pure rolling means the contact point is instantaneously at rest, so v = R omega.", easy: "If v is larger than R omega, the contact point slips forward.", q: "The no-slip condition on a fixed surface is", options: ["v = R omega", "v = 2 R omega", "omega = 0", "v = 0"], answer: 0}
  ];
  if (subject === "Mathematics" && c.indexOf("derivative") >= 0) return [
    {name: "First derivative", concept: "dy/dx is the slope of the tangent. A positive derivative means the function is increasing at that point.", easy: "Slope up means the value rises as x rises.", q: "If f'(x) > 0 on an interval, f is", options: ["Increasing there", "Always constant", "Always concave", "Undefined"], answer: 0}
  ];
  return [
    {name: "Definition", concept: chapter + " starts from the definition and the quantity it constrains. Write the symbol, the unit, and the condition under which the relation holds.", easy: "Name the quantity first, then the condition. A formula without its condition is not the concept.", q: "Before using a formula from " + chapter + ", what must be checked?", options: ["The condition under which it was derived", "Only the chapter title", "Only the final unit", "The length of the answer"], answer: 0},
    {name: "Trap", concept: "The usual trap in " + chapter + " is using the standard result after the assumption has been dropped.", easy: "If the assumption is gone, the standard result is gone with it.", q: "A standard result fails when", options: ["Its assumption is dropped", "The chapter name matches", "The unit is written", "The answer is boxed"], answer: 0}
  ];
}
const soloState = {subject: null, grade: null, chapter: null, step: 0, wrong: false};
function soloBox(html) {
  const box = document.getElementById("sololearn-modules-list");
  if (!box) return;
  box.innerHTML = html;
}
function renderSoloSubjects() {
  soloState.subject = null;
  soloBox(`<div class="space-y-3"><h3 class="text-white font-bold">Choose a subject</h3><p class="text-xs text-slate-400">Class 11 and 12 chapters, then the topic roadmap. A wrong answer opens a simpler explanation.</p><div class="grid grid-cols-1 gap-3">${["Physics","Chemistry","Mathematics"].map(s => `<button onclick="openSoloSubject('${s}')" class="p-4 rounded-2xl bg-slate-900 border border-slate-700 text-left"><span class="text-amber-400 text-xs">${s}</span><div class="text-white font-bold">${s} tab</div></button>`).join("")}</div></div>`);
}
function openSoloSubject(subject) {
  soloState.subject = subject;
  const grades = AIR1_ROADMAP[subject];
  soloBox(`<div class="space-y-4"><button onclick="renderSoloSubjects()" class="text-xs text-slate-400">Back to subjects</button><h3 class="text-white font-bold">${subject}</h3>${Object.keys(grades).map(g => `<div><h4 class="text-amber-400 text-sm mb-2">${g}</h4><div class="grid grid-cols-1 gap-2">${grades[g].map(ch => `<button onclick="openSoloChapter('${subject}','${g}','${ch.replace(/'/g,"\\'")}')" class="p-3 rounded-xl bg-slate-950 border border-slate-800 text-left text-sm text-white">${ch}</button>`).join("")}</div></div>`).join("")}</div>`);
}
function openSoloChapter(subject, grade, chapter) {
  soloState.subject = subject; soloState.grade = grade; soloState.chapter = chapter; soloState.step = 0; soloState.wrong = false;
  const topics = topicPack(subject, chapter);
  soloBox(`<div class="space-y-3"><button onclick="openSoloSubject('${subject}')" class="text-xs text-slate-400">Back to chapters</button><h3 class="text-white font-bold">${grade} ${subject}: ${chapter}</h3><p class="text-xs text-slate-400">Topic roadmap. Do them in order.</p>${topics.map((t,i) => `<button onclick="openSoloTopic(${i})" class="w-full p-3 rounded-xl bg-slate-950 border border-slate-800 text-left"><span class="text-emerald-400 text-xs">Step ${i+1}</span><div class="text-white">${t.name}</div></button>`).join("")}</div>`);
}
function openSoloTopic(index) {
  soloState.step = index; soloState.wrong = false;
  const t = topicPack(soloState.subject, soloState.chapter)[index];
  soloBox(`<div class="space-y-3"><button onclick="openSoloChapter('${soloState.subject}','${soloState.grade}','${soloState.chapter.replace(/'/g,"\\'")}')" class="text-xs text-slate-400">Back to roadmap</button><p class="text-amber-400 text-xs">${soloState.grade} ${soloState.subject} · ${soloState.chapter} · Step ${index+1}</p><h3 class="text-white font-bold">${t.name}</h3><div class="p-4 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-200">${t.concept}</div><p class="text-xs text-slate-400">Check</p><p class="text-white">${t.q}</p>${t.options.map((o,i) => `<button onclick="answerSolo(${i})" class="w-full p-3 rounded-xl bg-slate-900 border border-slate-700 text-left text-sm">${String.fromCharCode(65+i)}. ${o}</button>`).join("")}</div>`);
}
function answerSolo(choice) {
  const topics = topicPack(soloState.subject, soloState.chapter);
  const t = topics[soloState.step];
  if (choice === t.answer) {
    const next = soloState.step + 1 < topics.length;
    soloBox(`<div class="space-y-3"><p class="text-emerald-400 font-bold">Correct. The concept held.</p><p class="text-slate-300 text-sm">${t.concept}</p>${next ? `<button onclick="openSoloTopic(${soloState.step+1})" class="w-full p-3 rounded-xl bg-emerald-500 text-slate-950 font-bold">Next topic</button>` : `<button onclick="openSoloChapter('${soloState.subject}','${soloState.grade}','${soloState.chapter.replace(/'/g,"\\'")}')" class="w-full p-3 rounded-xl bg-emerald-500 text-slate-950 font-bold">Chapter roadmap</button>`}</div>`);
  } else {
    soloBox(`<div class="space-y-3"><p class="text-amber-400 font-bold">Not yet. Simpler version:</p><div class="p-4 rounded-xl bg-slate-950 border border-amber-500/40 text-sm text-slate-200">${t.easy}</div><p class="text-slate-400 text-xs">The same check, after the simpler line.</p><button onclick="openSoloTopic(${soloState.step})" class="w-full p-3 rounded-xl bg-amber-400 text-slate-950 font-bold">Try the check again</button></div>`);
  }
}
loadSoloLearnTab = async function () { renderSoloSubjects(); };


async function readNoteFile(file) {
  const name = file.name || "note";
  if (/\.txt$|\.md$|\.csv$/i.test(name)) return await file.text();
  if (!window.pdfjsLib) {
    await new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js";
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });
    pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
  }
  const data = await file.arrayBuffer();
  const pdf = await pdfjsLib.getDocument({data: data}).promise;
  let text = "";
  const pages = Math.min(pdf.numPages, 12);
  for (let p = 1; p <= pages; p++) {
    const page = await pdf.getPage(p);
    const content = await page.getTextContent();
    text += content.items.map(item => item.str).join(" ") + "\n";
  }
  return text;
}
function noteKey() { return soloState.subject + "|" + soloState.chapter; }
function savedNotes() {
  const all = JSON.parse(localStorage.getItem("air1-chapter-notes") || "{}");
  return all[noteKey()] || "";
}
function saveNotes(text) {
  const all = JSON.parse(localStorage.getItem("air1-chapter-notes") || "{}");
  all[noteKey()] = text.slice(0, 20000);
  localStorage.setItem("air1-chapter-notes", JSON.stringify(all));
}
function noteTopics(text) {
  const parts = text.replace(/\s+/g, " ").split(/(?<=[.?!])\s+/).map(s => s.trim()).filter(s => s.length > 40).slice(0, 8);
  return parts.map((sentence, i) => ({
    name: "From your notes " + (i + 1),
    concept: sentence,
    easy: sentence.split(" ").slice(0, 14).join(" ") + ". Keep this line, then answer again.",
    q: "Which statement matches the note you uploaded?",
    options: [sentence, "The relation holds with no condition.", "The final number is enough without the unit.", "The assumption can be dropped and the result stays."],
    answer: 0
  }));
}
topicPack = function(subject, chapter) {
  const base = (chapter.toLowerCase().indexOf("electrochem") >= 0) ? [
    {name: "Cell representation", concept: "Write the oxidation half at the left anode and the reduction half at the right cathode.", easy: "Left side loses electrons. Right side gains electrons.", q: "In Zn|Zn2+||Cu2+|Cu, which electrode is the anode?", options: ["Zn", "Cu", "The salt bridge", "Cu2+"], answer: 0},
    {name: "Nernst equation", concept: "At 298 K, E = E° - (0.059/n) log Q. n is the electrons in the balanced cell reaction.", easy: "A product concentration below the standard state makes log Q negative, so E is larger than E°.", q: "Zn|Zn2+(0.01 M)||Cu2+(1 M)|Cu, E° = 1.10 V. What is E at 298 K?", options: ["1.16 V", "1.04 V", "1.10 V", "0.99 V"], answer: 0}
  ] : [
    {name: "Definition", concept: chapter + " starts from the definition and the condition under which the relation holds.", easy: "Name the quantity, then the condition. A formula without its condition is not the concept.", q: "Before using a formula from " + chapter + ", what must be checked?", options: ["The condition under which it was derived", "Only the chapter title", "Only the final unit", "The length of the answer"], answer: 0}
  ];
  return base.concat(noteTopics(savedNotes()));
};
async function refineChapterNotes(input) {
  const files = Array.from(input.files || []);
  const pasted = (document.getElementById("solo-note-paste") || {}).value || "";
  if (!files.length && !pasted.trim()) return alert("Choose your note files or paste the notes.");
  const box = document.getElementById("solo-refine-status");
  if (box) box.textContent = "Reading " + files.length + " file(s)...";
  let text = pasted.trim();
  for (const file of files) {
    try { text += "\n" + await readNoteFile(file); }
    catch (err) { text += "\n" + file.name + " could not be read. Paste that note if it is a photo."; }
  }
  saveNotes(text);
  if (box) box.textContent = "Refined. Your note lines are now steps on this roadmap.";
  openSoloChapter(soloState.subject, soloState.grade, soloState.chapter);
}
openSoloChapter = function(subject, grade, chapter) {
  soloState.subject = subject; soloState.grade = grade; soloState.chapter = chapter; soloState.step = 0;
  const topics = topicPack(subject, chapter);
  const noteCount = noteTopics(savedNotes()).length;
  soloBox(`<div class="space-y-3"><button onclick="openSoloSubject('${subject}')" class="text-xs text-slate-400">Back to chapters</button><h3 class="text-white font-bold">${grade} ${subject}: ${chapter}</h3><div class="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2"><p class="text-sm text-white">Upload notes to refine this chapter</p><p class="text-xs text-slate-400">Add your PDF or text notes. The readable lines become extra steps and checks. A wrong answer still opens the simpler line.</p><input id="solo-note-files" type="file" multiple accept=".pdf,.txt,.md,text/plain" class="text-xs text-slate-300"><textarea id="solo-note-paste" class="w-full p-2 rounded-lg bg-slate-900 border border-slate-700 text-xs" rows="3" placeholder="Or paste the notes here"></textarea><button onclick="refineChapterNotes(document.getElementById('solo-note-files'))" class="w-full p-3 rounded-xl bg-emerald-500 text-slate-950 font-bold">Refine notes into this roadmap</button><p id="solo-refine-status" class="text-xs text-amber-300">${noteCount ? noteCount + " note steps already added." : ""}</p></div><p class="text-xs text-slate-400">Topic roadmap. Do them in order.</p>${topics.map((t,i) => `<button onclick="openSoloTopic(${i})" class="w-full p-3 rounded-xl bg-slate-950 border border-slate-800 text-left"><span class="text-emerald-400 text-xs">Step ${i+1}</span><div class="text-white">${t.name}</div></button>`).join("")}</div>`);
};


let ROADMAP = [];
async function loadRoadmap() {
  if (ROADMAP.length) return ROADMAP;
  const res = await fetch("/nopeit-sn/roadmap.json?v=10");
  ROADMAP = await res.json();
  return ROADMAP;
}
function soloLevels(ch) {
  return [
    {tag: "CBSE", text: ch.cbse || "Board definition and the condition."},
    {tag: "JEE Main", text: ch.main || "The extra calculation the board stops before."},
    {tag: "JEE Advanced", text: ch.advanced || "The deeper case. Passing Main does not cover this."}
  ];
}
loadSoloLearnTab = async function () {
  await loadRoadmap();
  soloState.subject = null;
  renderSoloSubjects();
};
renderSoloSubjects = function () {
  soloBox(`<div class="space-y-4"><p class="text-xs uppercase tracking-widest text-amber-400">SoloLearn</p><h2 class="text-2xl font-bold text-white">Choose the subject</h2><p class="text-sm text-slate-400">Class 11 and 12, then the chapter. Each chapter has the board line, the Main extra, and the Advanced extra. A wrong check opens the simpler line.</p><div class="grid grid-cols-1 gap-3">${["Physics","Chemistry","Mathematics"].map(s => `<button onclick="openSoloSubject('${s}')" class="p-5 rounded-2xl bg-slate-900 border border-slate-700 text-left"><div class="text-amber-400 text-xs">${ROADMAP.filter(c => c.subject===s).length} chapters</div><div class="text-xl font-bold text-white">${s}</div></button>`).join("")}</div></div>`);
};
openSoloSubject = async function (subject) {
  await loadRoadmap();
  soloState.subject = subject;
  const grades = ["Class 11", "Class 12"];
  soloBox(`<div class="space-y-5"><button onclick="renderSoloSubjects()" class="text-xs text-slate-400">Subjects</button><h2 class="text-xl font-bold text-white">${subject}</h2>${grades.map(g => `<section><h3 class="text-amber-400 mb-2">${g}</h3><div class="grid grid-cols-1 gap-2">${ROADMAP.filter(c => c.subject===subject && c.grade===g).map(c => `<button onclick="openRoadChapter('${c.subject}','${c.grade}','${c.name.replace(/'/g,"\\'")}')" class="p-4 rounded-xl bg-slate-950 border border-slate-800 text-left"><div class="text-white font-semibold">${c.name}</div><div class="mt-2 flex gap-2 text-[11px]"><span class="px-2 py-0.5 rounded bg-sky-500/10 text-sky-300">CBSE</span><span class="px-2 py-0.5 rounded bg-amber-500/10 text-amber-300">Main</span><span class="px-2 py-0.5 rounded bg-rose-500/10 text-rose-300">Advanced</span></div></button>`).join("")}</div></section>`).join("")}</div>`);
};
openRoadChapter = async function (subject, grade, name) {
  await loadRoadmap();
  soloState.subject = subject; soloState.grade = grade; soloState.chapter = name; soloState.step = 0;
  const ch = ROADMAP.find(c => c.subject===subject && c.grade===grade && c.name===name) || {name, cbse:"", main:"", advanced:""};
  const levels = soloLevels(ch);
  soloBox(`<div class="space-y-3"><button onclick="openSoloSubject('${subject}')" class="text-xs text-slate-400">Back to ${subject}</button><p class="text-amber-400 text-xs">${grade} ${subject}</p><h2 class="text-xl font-bold text-white">${name}</h2>${levels.map((lv,i) => `<section class="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2"><p class="text-amber-300 text-xs">Concept · ${lv.tag}</p><p class="text-sm text-slate-100 leading-relaxed">${lv.text}</p><button onclick="openLevel(${i})" class="text-xs text-emerald-400">Check this concept</button></section>`).join("")}<div class="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2"><p class="text-sm text-white">Upload notes to refine this chapter</p><input id="solo-note-files" type="file" multiple accept=".pdf,.txt,.md" class="text-xs"><textarea id="solo-note-paste" rows="3" class="w-full p-2 rounded-lg bg-slate-900 border border-slate-700 text-xs" placeholder="Paste notes if a file is a photo"></textarea><button onclick="refineChapterNotes(document.getElementById('solo-note-files'))" class="w-full p-3 rounded-xl bg-emerald-500 text-slate-950 font-bold">Refine notes into this roadmap</button><p id="solo-refine-status" class="text-xs text-amber-300"></p></div></div>`);
};
openSoloChapter = openRoadChapter;
function openLevel(i) {
  const ch = ROADMAP.find(c => c.subject===soloState.subject && c.grade===soloState.grade && c.name===soloState.chapter);
  const lv = soloLevels(ch)[i];
  soloState.step = i;
  const q = i === 1 && /electrochem/i.test(ch.name)
    ? {q: "Zn|Zn2+(0.01 M)||Cu2+(1 M)|Cu, E° = 1.10 V. What is E at 298 K?", options: ["1.16 V", "1.04 V", "1.10 V", "0.99 V"], answer: 0, easy: "Q = 0.01 and n = 2, so the log term adds 0.059 V."}
    : {q: "This " + lv.tag + " step is done only if you can state:", options: ["The limit of this level and what it does not cover", "The chapter title only", "A final number without the condition", "That Main and Advanced are the same"], answer: 0, easy: lv.tag + " means: " + lv.text.split(".").slice(0,1)};
  soloBox(`<div class="space-y-3"><button onclick="openRoadChapter('${soloState.subject}','${soloState.grade}','${ch.name.replace(/'/g,"\\'")}')" class="text-xs text-slate-400">Roadmap</button><p class="text-amber-400 text-xs">${lv.tag}</p><h3 class="text-white font-bold">${ch.name}</h3><div class="p-4 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-200">${lv.text}</div><p class="text-white">${q.q}</p>${q.options.map((o,k) => `<button onclick="answerLevel(${k},${q.answer},${i})" class="w-full p-3 rounded-xl bg-slate-900 border border-slate-700 text-left text-sm">${String.fromCharCode(65+k)}. ${o}</button>`).join("")}</div>`);
  window._soloEasy = q.easy;
}
function answerLevel(choice, answer, i) {
  if (choice === answer) {
    soloBox(`<div class="space-y-3"><p class="text-emerald-400 font-bold">Correct for this level.</p><button onclick="openLevel(${Math.min(i+1,2)})" class="w-full p-3 rounded-xl bg-emerald-500 text-slate-950 font-bold">${i<2?"Next level":"Back to roadmap"}</button></div>`);
  } else {
    soloBox(`<div class="space-y-3"><p class="text-amber-400 font-bold">Not yet. Simpler line:</p><div class="p-4 rounded-xl border border-amber-500/40 text-sm">${window._soloEasy}</div><button onclick="openLevel(${i})" class="w-full p-3 rounded-xl bg-amber-400 text-slate-950 font-bold">Try the check again</button></div>`);
  }
}


let LESSONS = [];
async function loadLessons() {
  if (LESSONS.length) return LESSONS;
  const res = await fetch("/nopeit-sn/lessons.json?v=11");
  LESSONS = await res.json();
  return LESSONS;
}
function lessonAt(i) {
  return LESSONS.filter(l => l.subject===soloState.subject && l.grade===soloState.grade && l.chapter===soloState.chapter)[i];
}
openRoadChapter = async function(subject, grade, name) {
  await loadLessons();
  soloState.subject = subject; soloState.grade = grade; soloState.chapter = name;
  const rows = LESSONS.filter(l => l.subject===subject && l.grade===grade && l.chapter===name);
  soloBox(`<div class="space-y-3"><button onclick="openSoloSubject('${subject}')" class="text-xs text-slate-400">Back</button><p class="text-amber-400 text-xs">${grade} ${subject}</p><h2 class="text-xl font-bold">${name}</h2><p class="text-sm text-slate-400">Three SoloLearn steps. Each one shows the concept, then one question.</p>${rows.map((l,i)=>`<button onclick="openLesson(${i})" class="w-full p-4 rounded-2xl bg-slate-950 border border-slate-800 text-left"><div class="h-1.5 rounded bg-slate-800 mb-3"><div class="h-1.5 rounded bg-amber-400" style="width:${((i+1)/3)*100}%"></div></div><div class="text-xs text-amber-300">Step ${i+1} of 3 · ${l.level}</div><div class="text-white mt-1">${l.concept.slice(0,140)}...</div></button>`).join("")}<div class="p-4 rounded-xl border border-slate-800"><p class="text-sm">Upload notes to add more steps</p><input id="solo-note-files" type="file" multiple class="text-xs"><button onclick="refineChapterNotes(document.getElementById('solo-note-files'))" class="mt-2 w-full p-3 rounded-xl bg-emerald-500 text-slate-950 font-bold">Refine notes</button></div></div>`);
};
async function openLesson(i) {
  await loadLessons();
  const l = lessonAt(i);
  soloState.step = i;
  soloBox(`<div class="space-y-4"><div class="h-1.5 rounded bg-slate-800"><div class="h-1.5 rounded bg-emerald-400" style="width:${((i+1)/3)*100}%"></div></div><button onclick="openRoadChapter('${l.subject}','${l.grade}','${l.chapter.replace(/'/g,"\\'")}')" class="text-xs text-slate-400">Roadmap</button><p class="text-xs text-amber-300">${l.level} · step ${i+1} of 3</p><h2 class="text-lg font-bold">${l.chapter}</h2><div class="p-4 rounded-2xl bg-slate-950 border border-slate-800 text-sm leading-6">${l.concept}</div><p class="text-white font-semibold">${l.q}</p><div class="space-y-2">${l.options.map((o,k)=>`<button onclick="answerLesson(${i},${k})" class="w-full p-3 rounded-xl bg-slate-900 border border-slate-700 text-left">${String.fromCharCode(65+k)}. ${o}</button>`).join("")}</div></div>`);
}
function answerLesson(i, choice) {
  const l = lessonAt(i);
  if (choice === l.answer) {
    soloBox(`<div class="space-y-4"><p class="text-emerald-400 text-xl font-bold">Correct</p><p class="text-sm text-slate-300">${l.easy}</p><button onclick="${i<2?`openLesson(${i+1})`:`openRoadChapter('${l.subject}','${l.grade}','${l.chapter.replace(/'/g,"\\'")}')`}" class="w-full p-3 rounded-xl bg-emerald-500 text-slate-950 font-bold">${i<2?"Next concept":"Chapter done"}</button></div>`);
  } else {
    soloBox(`<div class="space-y-4"><p class="text-rose-400 text-xl font-bold">Not yet</p><p class="text-sm text-slate-200">${l.easy}</p><button onclick="openLesson(${i})" class="w-full p-3 rounded-xl bg-amber-400 text-slate-950 font-bold">Read it again and retry</button></div>`);
  }
}
loadSoloLearnTab = async function(){ await loadLessons(); renderSoloSubjects(); };
