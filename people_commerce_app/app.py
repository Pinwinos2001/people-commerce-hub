import streamlit as st
import pandas as pd
from utils.auth import check_login, get_current_user
from utils.data import init_data

st.set_page_config(
    page_title="People Supply Hub",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg: #0E1117;
    --surface: #1C1F26;
    --surface2: #252830;
    --accent: #008C45;
    --accent-hover: #00a352;
    --text: #FFFFFF;
    --muted: #8B8FA8;
    --danger: #E53E3E;
    --warn: #D69E2E;
    --ok: #008C45;
    --border: #2D3748;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

h1, h2, h3 { 
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
}

.stApp { background: var(--bg) !important; }

section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

.stButton > button {
    background: var(--accent) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.02em !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: var(--accent-hover) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(0,140,69,0.3) !important;
}

.stTextInput > div > div > input,
.stSelectbox > div > div,
.stTextArea textarea,
.stDateInput > div > div > input {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
}

.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: var(--accent); }
.metric-card .label { 
    color: var(--muted); 
    font-size: 0.72rem; 
    text-transform: uppercase; 
    letter-spacing: 0.12em;
    font-weight: 500;
}
.metric-card .value { 
    font-family: 'Inter', sans-serif; 
    font-size: 2.4rem; 
    font-weight: 700; 
    color: var(--accent);
    line-height: 1.1;
    margin: 0.3rem 0;
}
.metric-card .sub { color: var(--muted); font-size: 0.8rem; }

.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    letter-spacing: 0.04em;
}
.badge-green { background: rgba(0,140,69,0.15); color: #00c45a; }
.badge-yellow { background: rgba(214,158,46,0.15); color: #D69E2E; }
.badge-red { background: rgba(229,62,62,0.15); color: #E53E3E; }
.badge-purple { background: rgba(128,90,213,0.15); color: #9F7AEA; }

.section-header {
    font-family: 'Inter', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 1.2rem;
    color: var(--text);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid var(--border);
}

.login-container {
    max-width: 380px;
    margin: 8rem auto;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2.5rem 2rem;
    box-shadow: 0 20px 60px rgba(0,0,0,0.4);
}
.login-title {
    font-family: 'Inter', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 0.3rem;
    letter-spacing: -0.02em;
}
.login-accent {
    color: var(--accent);
}
.login-sub { color: var(--muted); margin-bottom: 2rem; font-size: 0.85rem; }

.alert-box {
    padding: 0.75rem 1rem;
    border-radius: 8px;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
    font-weight: 400;
}
.alert-danger { background: rgba(229,62,62,0.08); border-left: 3px solid var(--danger); color: #fc8181; }
.alert-warn { background: rgba(214,158,46,0.08); border-left: 3px solid var(--warn); color: #f6c05c; }
.alert-ok { background: rgba(0,140,69,0.08); border-left: 3px solid var(--ok); color: #68d391; }

[data-testid="stSidebarNav"] { display: none; }

.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 8px !important;
    padding: 4px !important;
    gap: 2px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 6px !important;
    color: var(--muted) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: #FFFFFF !important;
}

div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
.stDataFrame { border: 1px solid var(--border) !important; }
</style>
""", unsafe_allow_html=True)

# ── Init data store ──────────────────────────────────────────────────────────
init_data()

# ── Auth gate ────────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-title"> People <span class="login-accent">Supply</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">Hub de gestión interno — Heineken Supply & BO</div>', unsafe_allow_html=True)

    usuario = st.selectbox("¿Quién eres?", ["Selecciona...", "Ariana", "Jefa"])
    password = st.text_input("Contraseña", type="password", placeholder="••••••••")

    if st.button("Ingresar →"):
        if check_login(usuario, password):
            st.session_state.logged_in = True
            st.session_state.usuario = usuario
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ── Sidebar nav ──────────────────────────────────────────────────────────────
usuario = st.session_state.usuario

with st.sidebar:
    st.markdown(f"""
    <div style="padding: 1rem 0 2rem 0;">
        <div style="font-family:'Syne',sans-serif; font-size:1.3rem; font-weight:800; color:#c8f04a;">People Supply</div>
        <div style="color:#888; font-size:0.8rem;">Hub de gestión</div>
        <div style="margin-top:1rem; padding:0.6rem 1rem; background:#22222c; border-radius:8px; font-size:0.85rem;">
            👤 {usuario}
        </div>
    </div>
    """, unsafe_allow_html=True)

    pagina = st.radio("Navegación", [
        "📊 Dashboard",
        "✅ Pendientes",
        "🔍 Procesos R&S",
        "👥 Headcount Ventas",
        "📧 Notificaciones",
    ], label_visibility="collapsed")

    st.markdown("---")
    if st.button("Cerrar sesión"):
        st.session_state.logged_in = False
        st.rerun()

# ── Page routing ─────────────────────────────────────────────────────────────
if pagina == "📊 Dashboard":
    from pages.dashboard import render
    render(usuario)
elif pagina == "✅ Pendientes":
    from pages.pendientes import render
    render(usuario)
elif pagina == "🔍 Procesos R&S":
    from pages.procesos import render
    render(usuario)
elif pagina == "👥 Headcount Ventas":
    from pages.headcount import render
    render(usuario)
elif pagina == "📧 Notificaciones":
    from pages.notificaciones import render
    render(usuario)
