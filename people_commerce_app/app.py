import streamlit as st
import pandas as pd
from utils.auth import check_login
from utils.data import init_data

st.set_page_config(
    page_title="People Commerce Hub",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Minimal Corporate CSS ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg: #F7F8FA;
    --surface: #FFFFFF;
    --accent: #0F5132;
    --accent-soft: #E9F5EF;
    --text: #1F2937;
    --muted: #6B7280;
    --border: #E5E7EB;
    --danger: #DC2626;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp {
    background: var(--bg) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid var(--border) !important;
}

/* Buttons */
.stButton > button {
    background: var(--accent) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.15s ease !important;
}

.stButton > button:hover {
    opacity: 0.9 !important;
}

/* Inputs */
.stTextInput input,
.stSelectbox div[data-baseweb="select"],
.stTextArea textarea {
    background: #FFFFFF !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
}

/* Cards */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.metric-card .label {
    color: var(--muted);
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.metric-card .value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text);
}

.metric-card .sub {
    color: var(--muted);
    font-size: 0.8rem;
}

/* Login */
.login-container {
    max-width: 380px;
    margin: 8rem auto;
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 2.5rem 2rem;
}

.login-title {
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.login-sub {
    color: var(--muted);
    margin-bottom: 2rem;
    font-size: 0.85rem;
}

[data-testid="stSidebarNav"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# ── Init data ─────────────────────────────────────────────────────────
init_data()

# ── Auth gate ─────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-title"><img src="assets/logo_small.svg" width="28" style="vertical-align:middle;margin-right:8px;display:inline-block;"/>People Commerce Hub</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">Hub de gestión interno</div>', unsafe_allow_html=True)

    usuario = st.selectbox("Usuario", ["Selecciona...", "HRBP Intern", "Business Partner"])
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if check_login(usuario, password):
            st.session_state.logged_in = True
            st.session_state.usuario = usuario
            st.rerun()
        else:
            st.error("Credenciales incorrectas.")

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────
usuario = st.session_state.usuario

with st.sidebar:
    st.markdown(f"""
    <div style="padding: 1rem 0 2rem 0;">
        <div style="display:flex; align-items:center; gap:8px;">
            <img src="assets/logo_small.svg" width="28" style="display:inline-block;"/>
            <div style="font-size:1.05rem; font-weight:700;">People Commerce Hub</div>
        </div>
        <div style="color:#6B7280; font-size:0.8rem; margin-top:4px;">Hub interno</div>
        <div style="margin-top:1rem; padding:0.6rem 1rem; background:#F3F4F6; border-radius:6px; font-size:0.85rem;">
            {usuario}
        </div>
    </div>
    """, unsafe_allow_html=True)

    pagina = st.radio("Navegación", [
        "Dashboard",
        "Pendientes",
        "Procesos R&S",
        "Headcount Ventas",
        "Notificaciones",
    ], label_visibility="collapsed")

    st.markdown("---")

    if st.button("Cerrar sesión"):
        st.session_state.logged_in = False
        st.rerun()

# ── Routing ───────────────────────────────────────────────────────────
if pagina == "Dashboard":
    from pages.dashboard import render
    render(usuario)

elif pagina == "Pendientes":
    from pages.pendientes import render
    render(usuario)

elif pagina == "Procesos R&S":
    from pages.procesos import render
    render(usuario)

elif pagina == "Headcount Ventas":
    from pages.headcount import render
    render(usuario)

elif pagina == "Notificaciones":
    from pages.notificaciones import render
    render(usuario)