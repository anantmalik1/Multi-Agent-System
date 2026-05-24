import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="M.A.I.S. — Multi Agent Intelligence System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session State ──────────────────────────────────────────────────────────────
for k, v in {
    "chat_history": [],
    "results": None,
    "active_nav": "new_chat",
    "running": False,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── CSS + Background ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&family=Exo+2:wght@300;400;500;600&display=swap');

/* RESET */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body { height: 100%; }

.stApp {
    font-family: 'Exo 2', sans-serif !important;
    background: #020610 !important;
    color: #c8d8f0 !important;
    min-height: 100vh;
}

/* NEURAL BG */
#neural-bg {
    position: fixed; inset: 0; z-index: 0;
    pointer-events: none;
}

/* HIDE STREAMLIT JUNK */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
.stDeployButton { visibility: hidden !important; height: 0 !important; }

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: rgba(2,6,20,0.97) !important;
    border-right: 1px solid rgba(0,180,255,0.12) !important;
    min-width: 240px !important; max-width: 240px !important;
    z-index: 50 !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
    background: transparent !important;
}
[data-testid="stSidebarCollapseButton"] { display: none !important; }

/* MAIN */
.block-container {
    padding: 20px 28px !important;
    max-width: 100% !important;
    position: relative; z-index: 10;
    background: transparent !important;
}

/* ── SIDEBAR ELEMENTS ── */
.sb-logo {
    padding: 22px 18px 14px;
    border-bottom: 1px solid rgba(0,180,255,0.1);
    margin-bottom: 6px;
}
.sb-logo-name {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.55rem; font-weight: 700;
    letter-spacing: 0.12em;
    background: linear-gradient(90deg, #00b4ff 0%, #7b2fff 50%, #00b4ff 100%);
    background-size: 200%;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: gflow 3s linear infinite;
}
@keyframes gflow { 0%{background-position:0%} 100%{background-position:200%} }
.sb-logo-sub {
    font-size: 0.58rem; letter-spacing: 0.18em;
    text-transform: uppercase; color: rgba(0,180,255,0.35);
    margin-top: 2px; line-height: 1.4;
}
.sb-section {
    font-size: 0.58rem; letter-spacing: 0.18em;
    text-transform: uppercase; color: rgba(255,255,255,0.18);
    padding: 14px 18px 5px;
}
.sb-agent-box {
    margin: 10px 12px 0;
    padding: 11px 13px;
    background: rgba(0,180,255,0.04);
    border: 1px solid rgba(0,180,255,0.1);
    border-radius: 10px;
}
.sb-agent-label {
    font-size: 0.58rem; letter-spacing: 0.18em;
    text-transform: uppercase; color: rgba(0,180,255,0.45);
    margin-bottom: 9px;
}
.sb-dots { display: flex; gap: 7px; flex-wrap: wrap; }
.sb-dot-wrap { display: flex; flex-direction: column; align-items: center; gap: 3px; }
.sb-dot {
    width: 30px; height: 30px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.68rem; font-weight: 700;
    background: rgba(0,255,136,0.1);
    border: 1px solid rgba(0,255,136,0.4);
    color: #00ff88;
    box-shadow: 0 0 8px rgba(0,255,136,0.25);
    animation: pdot 2s ease-in-out infinite;
}
@keyframes pdot {
    0%,100%{box-shadow:0 0 6px rgba(0,255,136,0.25)}
    50%{box-shadow:0 0 14px rgba(0,255,136,0.55)}
}
.sb-dot-lbl { font-size: 0.5rem; color: rgba(255,255,255,0.22); letter-spacing: 0.05em; }
.hist-row {
    padding: 8px 18px;
    font-size: 0.75rem;
    color: rgba(200,216,240,0.38);
    border-left: 2px solid transparent;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    cursor: pointer; transition: all .2s;
}
.hist-row:hover {
    background: rgba(0,180,255,0.05);
    color: rgba(200,216,240,0.7);
    border-left-color: rgba(0,180,255,0.3);
}

/* ── NAV BUTTONS ── */
section[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    background: transparent !important;
    border: none !important; border-radius: 0 !important;
    color: rgba(200,216,240,0.55) !important;
    font-family: 'Exo 2', sans-serif !important;
    font-size: 0.82rem !important; font-weight: 500 !important;
    text-align: left !important;
    padding: 10px 18px !important;
    transition: all .2s !important;
    border-left: 2px solid transparent !important;
    letter-spacing: 0.04em !important;
    display: block !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(0,180,255,0.07) !important;
    color: #c8e8ff !important;
    border-left-color: rgba(0,180,255,0.45) !important;
}
section[data-testid="stSidebar"] .stButton > button:focus {
    background: rgba(0,180,255,0.1) !important;
    color: #00b4ff !important;
    border-left-color: #00b4ff !important;
    box-shadow: none !important;
}

/* ── MAIN HEADER ── */
.m-header {
    display: flex; align-items: center; justify-content: space-between;
    padding-bottom: 14px;
    border-bottom: 1px solid rgba(0,180,255,0.1);
    margin-bottom: 20px;
}
.m-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem; font-weight: 600;
    letter-spacing: 0.18em; text-transform: uppercase;
    color: rgba(255,255,255,0.6);
}
.m-title b { color: #00b4ff; font-weight: 600; }
.m-pills { display: flex; gap: 8px; }
.pill {
    font-size: 0.6rem; letter-spacing: 0.12em; text-transform: uppercase;
    padding: 4px 11px; border-radius: 100px;
}
.pill-g { background: rgba(0,255,136,0.08); border:1px solid rgba(0,255,136,0.28); color:#00ff88; }
.pill-b { background: rgba(0,180,255,0.07); border:1px solid rgba(0,180,255,0.22); color:rgba(0,180,255,0.8); }

/* ── STEP CARDS ── */
.steps-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-bottom: 18px; }
.sc {
    padding: 13px 15px; border-radius: 12px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    position: relative; overflow: hidden; transition: all .3s;
}
.sc.active {
    background: rgba(0,180,255,0.06);
    border-color: rgba(0,180,255,0.35);
    box-shadow: 0 0 18px rgba(0,180,255,0.1);
}
.sc.done {
    background: rgba(0,255,136,0.04);
    border-color: rgba(0,255,136,0.22);
}
.sc.active::after {
    content:''; position:absolute; top:0; left:-100%; width:55%; height:100%;
    background: linear-gradient(90deg,transparent,rgba(0,180,255,0.07),transparent);
    animation: scanline 1.8s ease-in-out infinite;
}
@keyframes scanline { 0%{left:-60%} 100%{left:140%} }
.sc-num { font-family:'Share Tech Mono',monospace; font-size:0.58rem; color:rgba(255,255,255,0.2); margin-bottom:4px; }
.sc-name { font-size:0.8rem; font-weight:600; color:rgba(255,255,255,0.6); letter-spacing:.03em; }
.sc.active .sc-name { color:#00b4ff; }
.sc.done .sc-name { color:#00ff88; }
.sc-status { font-size:0.62rem; color:rgba(255,255,255,0.17); margin-top:2px; font-family:'Share Tech Mono',monospace; }
.sc.active .sc-status { color:rgba(0,180,255,0.65); }
.sc.done .sc-status { color:rgba(0,255,136,0.55); }

/* ── INPUT PANEL ── */
.inp-panel {
    background: rgba(0,180,255,0.025);
    border: 1px solid rgba(0,180,255,0.12);
    border-top-color: rgba(0,180,255,0.25);
    border-radius: 14px;
    padding: 18px 20px 14px;
    margin-bottom: 18px;
}
.inp-lbl {
    font-size: 0.6rem; letter-spacing:.2em; text-transform:uppercase;
    color:rgba(0,180,255,0.55); margin-bottom:8px;
    display:flex; align-items:center; gap:6px;
}
.inp-lbl::before {
    content:''; width:5px; height:5px; border-radius:50%;
    background:#00b4ff; box-shadow:0 0 5px #00b4ff;
    animation:blink 1.4s ease-in-out infinite;
}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.25}}

/* Streamlit input */
.stTextInput>div>div>input {
    background: rgba(0,0,0,0.45) !important;
    border: 1px solid rgba(0,180,255,0.18) !important;
    border-radius: 9px !important;
    color: #c8d8f0 !important;
    font-family: 'Exo 2', sans-serif !important;
    font-size: 0.88rem !important;
    padding: 11px 15px !important;
}
.stTextInput>div>div>input:focus {
    border-color: rgba(0,180,255,0.5) !important;
    box-shadow: 0 0 0 2px rgba(0,180,255,0.08), 0 0 16px rgba(0,180,255,0.1) !important;
    outline: none !important;
}
.stTextInput>div>div>input::placeholder { color:rgba(200,216,240,0.18) !important; }
.stTextInput label { display:none !important; }

/* ── EXECUTE BUTTON (main area) ── */
div[data-testid="column"] .stButton>button,
.main-btn .stButton>button {
    background: linear-gradient(135deg, rgba(0,180,255,0.14), rgba(123,47,255,0.14)) !important;
    border: 1px solid rgba(0,180,255,0.38) !important;
    border-top-color: rgba(0,180,255,0.6) !important;
    color: #00b4ff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.95rem !important; font-weight: 600 !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important;
    padding: 11px 22px !important;
    border-radius: 8px !important;
    transition: all .2s !important;
    box-shadow: 0 0 18px rgba(0,180,255,0.08) !important;
    width: 100% !important;
}
div[data-testid="column"] .stButton>button:hover,
.main-btn .stButton>button:hover {
    background: linear-gradient(135deg, rgba(0,180,255,0.24), rgba(123,47,255,0.24)) !important;
    box-shadow: 0 0 28px rgba(0,180,255,0.22) !important;
    transform: translateY(-1px) !important;
}

/* ── RESULT CARDS ── */
.rc {
    border-radius: 13px; padding: 16px 18px; margin-bottom: 11px;
    border: 1px solid rgba(0,180,255,0.1); border-top-color: rgba(0,180,255,0.2);
    background: rgba(0,6,20,0.7); backdrop-filter: blur(8px);
    box-shadow: 0 4px 18px rgba(0,0,0,0.4);
    position: relative; overflow: hidden;
}
.rc::before {
    content:''; position:absolute; left:0; top:0; bottom:0;
    width:2px; background: linear-gradient(180deg,#00b4ff,#7b2fff);
}
.rc-report { border-color:rgba(0,255,136,0.12); border-top-color:rgba(0,255,136,0.28); background:rgba(0,255,136,0.02); }
.rc-report::before { background: linear-gradient(180deg,#00ff88,#00b4ff); }
.rc-head { display:flex; align-items:center; gap:9px; margin-bottom:10px; padding-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.05); }
.rc-icon { width:28px;height:28px;border-radius:7px; background:rgba(0,180,255,0.1);border:1px solid rgba(0,180,255,0.2); display:flex;align-items:center;justify-content:center;font-size:0.8rem; }
.rc-title { font-family:'Rajdhani',sans-serif; font-size:0.7rem; letter-spacing:.18em; text-transform:uppercase; color:rgba(0,180,255,0.65); font-weight:600; }
.rc-report .rc-title { color:rgba(0,255,136,0.65); }
.rc-body { font-size:0.8rem; line-height:1.8; color:rgba(200,216,240,0.6); white-space:pre-wrap; font-family:'Exo 2',sans-serif; }

/* ── DIVIDER ── */
.cdiv {
    display:flex; align-items:center; gap:12px; margin:16px 0;
    font-family:'Share Tech Mono',monospace; font-size:0.58rem;
    letter-spacing:.18em; color:rgba(0,180,255,0.28); text-transform:uppercase;
}
.cdiv::before,.cdiv::after { content:''; flex:1; height:1px; background:linear-gradient(90deg,transparent,rgba(0,180,255,0.18),transparent); }

/* ── CLEAR BTN ── */
.clear-btn .stButton>button {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: rgba(200,216,240,0.4) !important;
    font-family:'Exo 2',sans-serif !important;
    font-size:0.78rem !important;
    padding:8px 18px !important;
    border-radius:8px !important;
    width:auto !important;
}

/* ── EMPTY STATE ── */
.empty-state {
    text-align:center; padding:60px 20px;
    color:rgba(200,216,240,0.18);
}
.empty-icon { font-size:2.2rem; margin-bottom:10px; }
.empty-title { font-family:'Rajdhani',sans-serif; font-size:0.95rem; letter-spacing:.2em; text-transform:uppercase; }
.empty-sub { font-size:0.75rem; margin-top:6px; opacity:.6; }

/* SCROLLBAR */
::-webkit-scrollbar { width:3px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:rgba(0,180,255,0.18); border-radius:2px; }

/* EXPANDER */
.streamlit-expanderHeader {
    background:rgba(0,0,0,0.3) !important;
    border:1px solid rgba(0,180,255,0.1) !important;
    border-radius:8px !important;
    color:rgba(200,216,240,0.45) !important;
    font-family:'Exo 2',sans-serif !important;
    font-size:0.78rem !important;
}

/* Spinner */
.stSpinner>div { border-top-color:rgba(0,180,255,0.8) !important; }
</style>

<!-- ANIMATED NEURAL NETWORK BACKGROUND -->
<canvas id="neural-bg"></canvas>
<script>
(function(){
    var c = document.getElementById('neural-bg');
    if(!c) return;
    var ctx = c.getContext('2d');
    var W, H, nodes=[];
    function resize(){ W=c.width=window.innerWidth; H=c.height=window.innerHeight; }
    resize();
    window.addEventListener('resize', function(){ resize(); init(); });
    function init(){
        nodes=[];
        var n = Math.floor(W*H/18000);
        for(var i=0;i<n;i++){
            nodes.push({
                x:Math.random()*W, y:Math.random()*H,
                vx:(Math.random()-.5)*.25, vy:(Math.random()-.5)*.25,
                r:Math.random()*1.5+.4,
                p:Math.random()*Math.PI*2,
                c:Math.random()>.5?[0,180,255]:[123,47,255]
            });
        }
    }
    init();
    function frame(){
        ctx.clearRect(0,0,W,H);
        for(var i=0;i<nodes.length;i++){
            for(var j=i+1;j<nodes.length;j++){
                var dx=nodes[i].x-nodes[j].x, dy=nodes[i].y-nodes[j].y;
                var d=Math.sqrt(dx*dx+dy*dy);
                if(d<150){
                    var a=(1-d/150)*.1;
                    var r=nodes[i].c[0],g=nodes[i].c[1],b=nodes[i].c[2];
                    ctx.strokeStyle='rgba('+r+','+g+','+b+','+a+')';
                    ctx.lineWidth=.5;
                    ctx.beginPath(); ctx.moveTo(nodes[i].x,nodes[i].y); ctx.lineTo(nodes[j].x,nodes[j].y); ctx.stroke();
                }
            }
        }
        for(var i=0;i<nodes.length;i++){
            var n=nodes[i];
            n.p+=.018;
            var glow=.4+Math.sin(n.p)*.28;
            ctx.beginPath(); ctx.arc(n.x,n.y,n.r,0,Math.PI*2);
            ctx.fillStyle='rgba('+n.c[0]+','+n.c[1]+','+n.c[2]+','+glow+')';
            ctx.fill();
            n.x+=n.vx; n.y+=n.vy;
            if(n.x<0||n.x>W) n.vx*=-1;
            if(n.y<0||n.y>H) n.vy*=-1;
        }
        requestAnimationFrame(frame);
    }
    frame();
})();
</script>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def clean(content):
    if isinstance(content, str): return content
    out = ""
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                out += item.get("text","") + "\n"
    return out.strip()

def step_cards(active):
    steps = [("01","Search Agent","Web Research"),("02","Reader Agent","Page Scraping"),
             ("03","Writer Chain","Drafting"),("04","Critic Agent","Review")]
    html = '<div class="steps-row">'
    for i,(num,name,desc) in enumerate(steps):
        if i < active: cls,st2 = "done","✓ COMPLETE"
        elif i == active: cls,st2 = "active","● RUNNING..."
        else: cls,st2 = "","— STANDBY"
        html += f'<div class="sc {cls}"><div class="sc-num">AGENT {num}</div><div class="sc-name">{name}</div><div class="sc-status">{st2}</div></div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

def res_card(icon, title, body, report=False):
    cls = "rc-report" if report else ""
    preview = str(body)[:2800] + "\n..." if len(str(body)) > 2800 else str(body)
    st.markdown(f"""
    <div class="rc {cls}">
        <div class="rc-head"><div class="rc-icon">{icon}</div><div class="rc-title">{title}</div></div>
        <div class="rc-body">{preview}</div>
    </div>""", unsafe_allow_html=True)


# ── SIDEBAR ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
        <div class="sb-logo-name">M.A.I.S.</div>
        <div class="sb-logo-sub">Multi Agent Intelligence System</div>
    </div>
    <div class="sb-section">Navigation</div>
    """, unsafe_allow_html=True)

    nav_items = [
        ("new_chat",  "＋  New Chat"),
        ("history",   "🕐  Chat History"),
        ("agents",    "⚙  AI Agents"),
        ("saved",     "💾  Saved Research"),
        ("settings",  "⚡  Settings"),
        ("memory",    "🧠  Memory"),
    ]
    for key, label in nav_items:
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.active_nav = key
            if key == "new_chat":
                st.session_state.results = None

    # Recent history
    if st.session_state.chat_history:
        st.markdown('<div class="sb-section" style="margin-top:10px;">Recent</div>', unsafe_allow_html=True)
        for item in st.session_state.chat_history[-4:][::-1]:
            t = item["topic"]
            short = t[:26]+"…" if len(t)>26 else t
            st.markdown(f'<div class="hist-row">📄 {short}</div>', unsafe_allow_html=True)

    # Agent status dots
    st.markdown("""
    <div class="sb-agent-box">
        <div class="sb-agent-label">Agent Status</div>
        <div class="sb-dots">
            <div class="sb-dot-wrap"><div class="sb-dot">S</div><div class="sb-dot-lbl">Search</div></div>
            <div class="sb-dot-wrap"><div class="sb-dot">R</div><div class="sb-dot-lbl">Reader</div></div>
            <div class="sb-dot-wrap"><div class="sb-dot">W</div><div class="sb-dot-lbl">Writer</div></div>
            <div class="sb-dot-wrap"><div class="sb-dot">C</div><div class="sb-dot-lbl">Critic</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── MAIN CONTENT ────────────────────────────────────────────────────────────────
nav = st.session_state.active_nav
titles = {
    "new_chat": "INTELLIGENT <b>WORKFLOW</b>",
    "history":  "CHAT <b>HISTORY</b>",
    "agents":   "AI <b>AGENTS</b>",
    "saved":    "SAVED <b>RESEARCH</b>",
    "settings": "SYSTEM <b>SETTINGS</b>",
    "memory":   "AGENT <b>MEMORY</b>",
}
st.markdown(f"""
<div class="m-header">
    <div class="m-title">{titles.get(nav, "INTELLIGENT <b>WORKFLOW</b>")}</div>
    <div class="m-pills">
        <div class="pill pill-g">● ONLINE</div>
        <div class="pill pill-b">MISTRAL AI</div>
    </div>
</div>""", unsafe_allow_html=True)


# ════════════════════════════════════════
# NEW CHAT
# ════════════════════════════════════════
if nav == "new_chat":

    # Step cards placeholder (empty at start)
    if st.session_state.results is None and not st.session_state.running:
        pass  # don't show steps until running
    
    # Input
    st.markdown('<div class="inp-panel"><div class="inp-lbl">Research Query</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([5, 1])
    with col1:
        topic = st.text_input("q", placeholder="Enter topic — e.g. 'Latest AI breakthroughs 2025'...",
                              label_visibility="collapsed", key="q")
    with col2:
        run = st.button("▶ EXECUTE", use_container_width=True, key="run")
    st.markdown('</div>', unsafe_allow_html=True)

    # RUN
    if run and topic.strip():
        st.markdown('<div class="cdiv">Pipeline Initializing</div>', unsafe_allow_html=True)
        ph_steps = st.empty()
        ph_spin  = st.empty()

        with ph_steps.container(): step_cards(0)
        with ph_spin.container():
            with st.spinner("Search Agent scanning the web..."):
                from agents import build_search_agent
                r = build_search_agent().invoke({"messages":[("user",f"Find recent, reliable and detailed information about: {topic}")]})
                search_res = clean(r["messages"][-1].content)

        with ph_steps.container(): step_cards(1)
        with ph_spin.container():
            with st.spinner("Reader Agent scraping top source..."):
                from agents import build_reader_agent
                r = build_reader_agent().invoke({"messages":[("user",
                    f"Based on search results about '{topic}':\n1. Pick MOST relevant URL\n2. Scrape it\n3. Return clean content\n\nSearch Results:\n{search_res[:1500]}")]})
                scraped = clean(r["messages"][-1].content)

        with ph_steps.container(): step_cards(2)
        with ph_spin.container():
            with st.spinner("Writer Chain composing report..."):
                from agents import writer_chain
                report = writer_chain.invoke({"topic":topic,"research":f"SEARCH:\n{search_res}\n\nSCRAPED:\n{scraped}"})

        with ph_steps.container(): step_cards(3)
        with ph_spin.container():
            with st.spinner("Critic Agent reviewing..."):
                from agents import critic_chain
                feedback = critic_chain.invoke({"report":report})

        with ph_steps.container(): step_cards(4)
        ph_spin.empty()

        result = {"topic":topic,"search_results":search_res,"scraped_content":scraped,
                  "report":report,"feedback":feedback,"timestamp":datetime.now().strftime("%d %b %Y, %H:%M")}
        st.session_state.results = result
        st.session_state.chat_history.append(result)

    elif run:
        st.warning("Please enter a research topic.")

    # Results
    if st.session_state.results:
        r = st.session_state.results
        st.markdown(f'<div class="cdiv">Results — {r["topic"]}</div>', unsafe_allow_html=True)
        res_card("📋", "Final Research Report", r["report"], report=True)
        res_card("🔍", "Critic Feedback", r["feedback"])
        with st.expander("🔎 Search Agent Raw Output"):
            st.markdown(f'<div class="rc-body" style="font-size:.75rem">{str(r["search_results"])[:3000]}</div>', unsafe_allow_html=True)
        with st.expander("🌐 Reader Agent Scraped Content"):
            st.markdown(f'<div class="rc-body" style="font-size:.75rem">{str(r["scraped_content"])[:3000]}</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
        if st.button("🔄 New Research", key="clear"):
            st.session_state.results = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════
# CHAT HISTORY
# ════════════════════════════════════════
elif nav == "history":
    if not st.session_state.chat_history:
        st.markdown('<div class="empty-state"><div class="empty-icon">📂</div><div class="empty-title">No History Yet</div><div class="empty-sub">Run your first query to see it here.</div></div>', unsafe_allow_html=True)
    else:
        for i, item in enumerate(st.session_state.chat_history[::-1]):
            with st.expander(f"📄  {item['topic']}  —  {item.get('timestamp','')}", expanded=(i==0)):
                res_card("📋", "Report", item["report"], report=True)
                res_card("🔍", "Feedback", item["feedback"])


# ════════════════════════════════════════
# AI AGENTS
# ════════════════════════════════════════
elif nav == "agents":
    agents = [
        ("🔍","Search Agent","Web Research","Queries the internet for recent, relevant information using Tavily search API.","ACTIVE"),
        ("🌐","Reader Agent","Content Scraper","Picks the most relevant URL and scrapes detailed content from the webpage.","ACTIVE"),
        ("✍️","Writer Chain","Report Composer","Synthesizes search + scraped content into a structured research report.","ACTIVE"),
        ("🎯","Critic Agent","Quality Reviewer","Reviews the report for accuracy and depth, providing structured feedback.","ACTIVE"),
    ]
    c1, c2 = st.columns(2)
    for i,(icon,name,role,desc,status) in enumerate(agents):
        col = c1 if i%2==0 else c2
        with col:
            st.markdown(f"""
            <div class="rc" style="margin-bottom:12px;">
                <div class="rc-head">
                    <div class="rc-icon">{icon}</div>
                    <div>
                        <div class="rc-title">{name}</div>
                        <div style="font-size:.6rem;color:rgba(0,255,136,.5);letter-spacing:.1em;text-transform:uppercase;margin-top:1px;">● {status}</div>
                    </div>
                </div>
                <div style="font-size:.65rem;letter-spacing:.1em;text-transform:uppercase;color:rgba(0,180,255,.38);margin-bottom:6px;">{role}</div>
                <div class="rc-body" style="font-size:.78rem;">{desc}</div>
            </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════
# SETTINGS
# ════════════════════════════════════════
elif nav == "settings":
    st.markdown("""<div class="rc" style="margin-bottom:14px;">
        <div class="rc-head"><div class="rc-icon">⚙</div><div class="rc-title">System Configuration</div></div>
        <div class="rc-body">Configure API keys and model preferences in your <code>.env</code> file.</div>
    </div>""", unsafe_allow_html=True)
    for k,v in [("MISTRAL_API_KEY","Set in .env"),("TAVILY_API_KEY","Set in .env"),
                ("Model","mistral-large-latest"),("Search Depth","Advanced"),("Max Tokens","4096")]:
        st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;
            padding:10px 0;border-bottom:1px solid rgba(0,180,255,.06);">
            <span style="font-size:.8rem;color:rgba(200,216,240,.45);">{k}</span>
            <span style="font-family:'Share Tech Mono',monospace;font-size:.75rem;color:rgba(0,180,255,.55);">{v}</span>
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════
# MEMORY
# ════════════════════════════════════════
elif nav == "memory":
    count = len(st.session_state.chat_history)
    st.markdown(f"""<div class="rc" style="margin-bottom:14px;">
        <div class="rc-head"><div class="rc-icon">🧠</div><div class="rc-title">Memory Store</div></div>
        <div style="display:flex;gap:24px;margin-top:4px;">
            <div><div style="font-family:'Share Tech Mono',monospace;font-size:1.3rem;color:#00b4ff;">{count}</div>
                 <div style="font-size:.6rem;color:rgba(255,255,255,.28);letter-spacing:.1em;text-transform:uppercase;">Sessions</div></div>
            <div><div style="font-family:'Share Tech Mono',monospace;font-size:1.3rem;color:#00ff88;">Active</div>
                 <div style="font-size:.6rem;color:rgba(255,255,255,.28);letter-spacing:.1em;text-transform:uppercase;">Status</div></div>
        </div>
    </div>""", unsafe_allow_html=True)
    for item in st.session_state.chat_history[::-1]:
        st.markdown(f"""<div style="padding:8px 12px;border-left:2px solid rgba(0,180,255,.2);
            margin-bottom:6px;font-size:.76rem;color:rgba(200,216,240,.4);">
            📄 {item['topic']} <span style="color:rgba(0,180,255,.28);float:right;">{item.get('timestamp','')}</span>
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════
# SAVED
# ════════════════════════════════════════
elif nav == "saved":
    st.markdown('<div class="empty-state"><div class="empty-icon">💾</div><div class="empty-title">Saved Research</div><div class="empty-sub">Save functionality coming soon.</div></div>', unsafe_allow_html=True)
