import streamlit as st
from groq import Groq
import json
import re
from datetime import datetime

st.set_page_config(
    page_title="AI Code Review Bot",
    page_icon="🔍",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Time new roman', sans-serif;
    }

    /* Dark gradient background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        min-height: 100vh;
    }

    /* Hide default streamlit header */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main title */
    .main-title {
        text-align: center;
        padding: 2rem 0 0.5rem;
    }
    .main-title h1 {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .main-title p {
        color: #94a3b8;
        font-size: 1rem;
        margin-top: 0.4rem;
    }

    /* Glassmorphism cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
    }

    /* Section headers */
    .section-header {
        color: #e2e8f0;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Score cards */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .metric-label {
        font-size: 0.72rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Bug / security / good items */
    .bug-item {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 10px;
        padding: 12px 16px;
        margin: 8px 0;
        color: #fca5a5;
    }
    .bug-item strong { color: #f87171; }
    .bug-item small  { color: #fcd34d; }

    .sec-item {
        background: rgba(234, 179, 8, 0.1);
        border: 1px solid rgba(234, 179, 8, 0.3);
        border-radius: 10px;
        padding: 12px 16px;
        margin: 8px 0;
        color: #fde68a;
    }
    .sec-item strong { color: #fbbf24; }
    .sec-item small  { color: #86efac; }

    .good-item {
        background: rgba(52, 211, 153, 0.1);
        border: 1px solid rgba(52, 211, 153, 0.25);
        border-radius: 10px;
        padding: 10px 16px;
        margin: 6px 0;
        color: #6ee7b7;
    }

    .suggest-item {
        background: rgba(96, 165, 250, 0.08);
        border: 1px solid rgba(96, 165, 250, 0.2);
        border-radius: 10px;
        padding: 10px 16px;
        margin: 6px 0;
        color: #93c5fd;
    }

    /* Result section titles */
    .result-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #e2e8f0;
        margin: 1.2rem 0 0.5rem;
        padding-bottom: 6px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: rgba(15, 12, 41, 0.9) !important;
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown p {
        color: #cbd5e1 !important;
    }

    /* Inputs */
    .stTextArea textarea {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 13px !important;
    }
    .stTextInput input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: #e2e8f0 !important;
        border-radius: 10px !important;
    }
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: #e2e8f0 !important;
        border-radius: 10px !important;
    }

    /* Analyze button */
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4) !important;
    }

    /* Download button */
    .stDownloadButton > button {
        background: rgba(52, 211, 153, 0.15) !important;
        color: #34d399 !important;
        border: 1px solid rgba(52, 211, 153, 0.4) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        width: 100% !important;
        margin-top: 1rem !important;
    }

    /* Code blocks */
    .stCode {
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }

    /* Info box */
    .stAlert {
        background: rgba(96, 165, 250, 0.08) !important;
        border: 1px solid rgba(96, 165, 250, 0.2) !important;
        border-radius: 12px !important;
        color: #93c5fd !important;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #7c3aed !important;
    }

    /* Divider */
    hr {
        border-color: rgba(255,255,255,0.08) !important;
    }

    /* Column subheaders */
    h3 { color: #e2e8f0 !important; }

    /* Feature list in info box */
    .feature-list {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-top: 1rem;
    }
    .feature-item {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        color: #94a3b8;
    }

    /* Language badge */
    .lang-badge {
        display: inline-block;
        background: rgba(167, 139, 250, 0.2);
        border: 1px solid rgba(167, 139, 250, 0.4);
        color: #c4b5fd;
        border-radius: 20px;
        padding: 2px 12px;
        font-size: 12px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────
st.markdown("""
<div class="main-title">
    <h1>🔍 AI Code Review Bot</h1>
    <p>Powered by Groq AI &nbsp;·&nbsp; DevZone Innovation &nbsp;·&nbsp; Conference Edition</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    st.markdown("<small style='color:#64748b'>Get free key → [console.groq.com](https://console.groq.com)</small>", unsafe_allow_html=True)
    st.divider()
    language = st.selectbox("🌍 Language", [
        "Auto-detect", "Python", "JavaScript", "TypeScript",
        "Java", "C++", "C#", "Go", "Rust", "PHP", "SQL", "Bash"
    ])
    review_depth = st.selectbox("🔬 Review Depth", ["Standard", "Deep (slower)"])
    st.divider()
    st.markdown("**✨ 8 Features**")
    st.markdown("""
<div style='font-size:13px; color:#94a3b8; line-height:2'>
🐛 Bug detection<br>
🔒 Security scanning<br>
📊 Quality score (1–10)<br>
⏱ Time & space complexity<br>
✨ Auto-refactored code<br>
📝 Docstring generator<br>
🌍 Multi-language support<br>
📄 Downloadable report
</div>
""", unsafe_allow_html=True)

# ── Main layout ──────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📋 Paste Your Code")
    sample_code = '''def find_user(users, target_id):
    for i in range(len(users)):
        if users[i]["id"] == target_id:
            password = users[i]["password"]
            print(f"Found user, password is: {password}")
            return users[i]
    return None

def calculate_average(numbers):
    total = 0
    for n in numbers:
        total = total + n
    avg = total / len(numbers)
    return avg
'''
    code_input = st.text_area(
        "code",
        value=sample_code,
        height=380,
        label_visibility="collapsed"
    )
    analyze_btn = st.button("🚀  Analyze My Code", use_container_width=True)

with col2:
    st.markdown("### 📊 Review Results")

    if analyze_btn:
        if not api_key:
            st.error("⚠️ Please enter your Groq API key in the sidebar.")
            st.stop()
        if not code_input.strip():
            st.error("⚠️ Please paste some code to review.")
            st.stop()

        lang_hint  = "" if language == "Auto-detect" else f"The code is written in {language}."
        depth_hint = "Be thorough and detailed." if review_depth == "Deep (slower)" else ""

        prompt = f"""You are an expert code reviewer. Analyze the following code and return a JSON object ONLY — no markdown, no explanation outside the JSON.

{lang_hint} {depth_hint}

Code to review:
```
{code_input}
```

Return this exact JSON structure:
{{
  "language": "detected language name",
  "quality_score": <integer 1-10>,
  "quality_label": "<Excellent|Good|Fair|Poor>",
  "time_complexity": "<e.g. O(n)>",
  "space_complexity": "<e.g. O(1)>",
  "bugs": [
    {{"line": "<line number or range>", "severity": "<critical|warning>", "description": "<clear description>", "fix": "<how to fix>"}}
  ],
  "security_issues": [
    {{"type": "<issue type>", "description": "<what is wrong>", "recommendation": "<how to fix>"}}
  ],
  "strengths": ["<strength 1>", "<strength 2>"],
  "suggestions": ["<improvement 1>", "<improvement 2>", "<improvement 3>"],
  "refactored_code": "<full refactored version of the code with all issues fixed>",
  "docstring": "<a proper docstring or comment block for the main function/class>"
}}"""

        with st.spinner("🤖  Analyzing your code with AI..."):
            try:
                client  = Groq(api_key=api_key)
                message = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000
                )
                raw    = message.choices[0].message.content.strip()
                raw    = re.sub(r"^```(?:json)?", "", raw).strip()
                raw    = re.sub(r"```$", "", raw).strip()
                result = json.loads(raw)

                score       = result.get("quality_score", 5)
                score_color = "#34d399" if score >= 7 else "#fbbf24" if score >= 4 else "#f87171"

                # ── Metric cards ──
                st.markdown(f"""
<div class="metric-grid">
  <div class="metric-card">
    <div class="metric-value" style="color:{score_color}">{score}/10</div>
    <div class="metric-label">{result.get("quality_label","Quality")}</div>
  </div>
  <div class="metric-card">
    <div class="metric-value" style="color:#60a5fa">{result.get("time_complexity","?")}</div>
    <div class="metric-label">Time complexity</div>
  </div>
  <div class="metric-card">
    <div class="metric-value" style="color:#a78bfa">{result.get("space_complexity","?")}</div>
    <div class="metric-label">Space complexity</div>
  </div>
  <div class="metric-card">
    <div class="metric-value" style="font-size:1rem;color:#94a3b8;padding-top:6px">
      <span class="lang-badge">{result.get("language","?")}</span>
    </div>
    <div class="metric-label" style="margin-top:8px">Language</div>
  </div>
</div>
""", unsafe_allow_html=True)

                # ── Bugs ──
                bugs = result.get("bugs", [])
                if bugs:
                    st.markdown(f'<div class="result-title">🐛 Bugs Found &nbsp;<span style="color:#f87171;font-size:13px">({len(bugs)} issues)</span></div>', unsafe_allow_html=True)
                    for bug in bugs:
                        icon = "🔴" if bug.get("severity") == "critical" else "🟡"
                        st.markdown(f'<div class="bug-item"><strong>{icon} Line {bug.get("line","?")} — {bug.get("description","")}</strong><br><small>💡 Fix: {bug.get("fix","")}</small></div>', unsafe_allow_html=True)

                # ── Security ──
                secs = result.get("security_issues", [])
                if secs:
                    st.markdown(f'<div class="result-title">🔒 Security Issues &nbsp;<span style="color:#fbbf24;font-size:13px">({len(secs)} found)</span></div>', unsafe_allow_html=True)
                    for sec in secs:
                        st.markdown(f'<div class="sec-item"><strong>⚠️ {sec.get("type","Issue")} — {sec.get("description","")}</strong><br><small>✅ Fix: {sec.get("recommendation","")}</small></div>', unsafe_allow_html=True)

                # ── Strengths ──
                if result.get("strengths"):
                    st.markdown('<div class="result-title">✅ Strengths</div>', unsafe_allow_html=True)
                    for s in result["strengths"]:
                        st.markdown(f'<div class="good-item">👍 {s}</div>', unsafe_allow_html=True)

                # ── Suggestions ──
                if result.get("suggestions"):
                    st.markdown('<div class="result-title">💡 Suggestions</div>', unsafe_allow_html=True)
                    for i, sug in enumerate(result["suggestions"], 1):
                        st.markdown(f'<div class="suggest-item"><strong style="color:#60a5fa">{i}.</strong> {sug}</div>', unsafe_allow_html=True)

                # ── Refactored code ──
                if result.get("refactored_code"):
                    st.markdown('<div class="result-title">✨ Refactored Code</div>', unsafe_allow_html=True)
                    st.code(result["refactored_code"], language=result.get("language","python").lower())

                # ── Docstring ──
                if result.get("docstring"):
                    st.markdown('<div class="result-title">📝 Generated Docstring</div>', unsafe_allow_html=True)
                    st.code(result["docstring"], language="python")

                # ── Download report ──
                report = "\n".join([
                    "# AI Code Review Report",
                    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    f"\n## Score: {score}/10 ({result.get('quality_label','')})",
                    f"- Language: {result.get('language','')}",
                    f"- Time Complexity: {result.get('time_complexity','')}",
                    f"- Space Complexity: {result.get('space_complexity','')}",
                    f"\n## Bugs ({len(bugs)})",
                    *[f"- Line {b.get('line','?')}: {b.get('description','')} | Fix: {b.get('fix','')}" for b in bugs],
                    f"\n## Security Issues ({len(secs)})",
                    *[f"- {s.get('type','')}: {s.get('description','')} | Fix: {s.get('recommendation','')}" for s in secs],
                    "\n## Suggestions",
                    *[f"- {sg}" for sg in result.get("suggestions", [])],
                    f"\n## Refactored Code\n```\n{result.get('refactored_code','')}\n```"
                ])
                st.download_button(
                    "📄  Download Full Report",
                    data=report,
                    file_name=f"code_review_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            except json.JSONDecodeError:
                st.error("❌ Could not parse AI response. Please try again.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    else:
        st.markdown("""
<div style="text-align:center; padding: 3rem 1rem; color: #475569;">
  <div style="font-size: 4rem; margin-bottom: 1rem;">🔍</div>
  <div style="font-size: 1.1rem; font-weight: 600; color: #94a3b8; margin-bottom: 0.5rem;">Ready to review your code</div>
  <div style="font-size: 0.9rem; color: #475569;">Paste your code on the left and click Analyze</div>
</div>
<div class="feature-list">
  <div class="feature-item">🐛 Bug detection</div>
  <div class="feature-item">🔒 Security scan</div>
  <div class="feature-item">📊 Quality score</div>
  <div class="feature-item">⏱ Complexity</div>
  <div class="feature-item">✨ Auto-refactor</div>
  <div class="feature-item">📝 Docstrings</div>
  <div class="feature-item">🌍 10+ languages</div>
  <div class="feature-item">📄 PDF report</div>
</div>
""", unsafe_allow_html=True)
