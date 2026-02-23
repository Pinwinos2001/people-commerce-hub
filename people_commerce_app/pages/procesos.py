import streamlit as st
import pandas as pd
from datetime import date
from utils.data import get_procesos, add_proceso, update_proceso, cerrar_proceso

AREAS = ["Supply", "Logística", "Ventas", "Operaciones", "RRHH", "Otro"]
ETAPAS = ["Requerimiento", "Reclutamiento", "Selección", "Oferta/Documentos", "Contratación", "Cerrado"]
TIPOS_COBERTURA = ["Externa", "Interna"]
TIPOS_CIERRE = ["Contratación", "Movimiento interno", "Cancelado"]
RESPONSABLES = ["HRBP Intern", "Business Partner"]

ETAPA_COLORS = {
    "Requerimiento":       "badge-purple",
    "Reclutamiento":       "badge-yellow",
    "Selección":           "badge-yellow",
    "Oferta/Documentos":   "badge-yellow",
    "Contratación":        "badge-green",
    "Cerrado":             "badge-green",
}

def render(usuario: str):
    st.markdown('<div class="section-header">🔍 Procesos R&S</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 Activos", "✅ Cerrados", "➕ Nuevo proceso"])

    with tab1:
        _render_procesos(activos=True, usuario=usuario)

    with tab2:
        _render_procesos(activos=False, usuario=usuario)

    with tab3:
        _form_nuevo_proceso(usuario)


def _render_procesos(activos: bool, usuario: str):
    df = get_procesos()
    if df.empty:
        st.markdown('<div class="alert-box alert-ok">No hay procesos registrados aún.</div>', unsafe_allow_html=True)
        return

    if activos:
        df = df[df["status"] != "Cerrado"]
    else:
        df = df[df["status"] == "Cerrado"]

    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        filtro_area = st.selectbox("Área", ["Todas"] + AREAS, key=f"fa_{activos}")
    with col2:
        filtro_resp = st.selectbox("Responsable", ["Todos"] + RESPONSABLES, key=f"fr_{activos}")

    if filtro_area != "Todas":
        df = df[df["area"] == filtro_area]
    if filtro_resp != "Todos":
        df = df[df["responsable"] == filtro_resp]

    if df.empty:
        st.info("Sin procesos con esos filtros.")
        return

    # Calcular días en curso
    hoy = pd.Timestamp.today()
    df = df.copy()
    df["dias"] = (hoy - pd.to_datetime(df["inicio_reclutamiento"], errors="coerce")).dt.days.fillna(0).astype(int)

    for _, row in df.iterrows():
        _render_proceso_card(row, activos)


def _render_proceso_card(row, puede_cerrar: bool):
    etapa = row.get("etapa", "")
    badge_class = ETAPA_COLORS.get(etapa, "badge-purple")
    dias = int(row.get("dias", 0))

    # Colores Heineken style
    if dias > 30:
        dias_color = "#E30613"   # rojo
    elif dias > 15:
        dias_color = "#FFB200"   # amarillo
    else:
        dias_color = "#008C45"   # verde

    with st.container():
        st.markdown(f"""
        <div style="
            background:#ffffff;
            border:1px solid #e6e6e6;
            border-left:5px solid #008C45;
            border-radius:16px;
            padding:1.3rem 1.5rem;
            margin-bottom:1rem;
            box-shadow:0 6px 18px rgba(0,0,0,0.05);
            transition:all 0.2s ease;
        ">
            <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:0.6rem;">
                <div>
                    <div style="
                        font-weight:700;
                        font-size:1.05rem;
                        color:#111;
                    ">
                        {row.get('posicion','')}
                    </div>
                    <div style="color:#666;font-size:0.85rem;margin-top:2px;">
                        {row.get('area','')} · {row.get('tipo_cobertura','')}  
                        · Resp: <span style="color:#008C45;font-weight:600;">{row.get('responsable','')}</span>
                    </div>
                </div>

                <div style="text-align:right;">
                    <span class="badge {badge_class}">{etapa}</span>
                    <div style="
                        font-size:0.85rem;
                        color:{dias_color};
                        margin-top:6px;
                        font-weight:700;
                    ">
                        {dias} días en curso
                    </div>
                </div>
            </div>

            <div style="
                font-size:0.8rem;
                color:#555;
                display:flex;
                gap:1.5rem;
                margin-top:0.4rem;
            ">
                <span>👤 Reemplaza: {row.get('reemplaza','—')}</span>
                <span>📋 Jefe: {row.get('jefe_directo','—')}</span>
                {f'<span>🟢 Seleccionado: {row.get("seleccionado","")}</span>' if row.get('seleccionado') and str(row.get('seleccionado')) != 'nan' else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)


def _form_nuevo_proceso(usuario: str):
    st.markdown("### Registrar nuevo proceso")

    with st.form("nuevo_proceso", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            posicion = st.text_input("Posición *", placeholder="Ej: Operador de Producción")
            area = st.selectbox("Área *", AREAS)
            responsable = st.selectbox("Responsable *", RESPONSABLES,
                                       index=RESPONSABLES.index(usuario) if usuario in RESPONSABLES else 0)
            tipo_cobertura = st.selectbox("Tipo de cobertura", TIPOS_COBERTURA)
        with col2:
            jefe_directo = st.text_input("Jefe directo")
            gerente = st.text_input("Gerente")
            reemplaza = st.text_input("Reemplaza a", placeholder="Nombre o 'NUEVO HC'")
            vacantes = st.number_input("Vacantes", min_value=1, value=1)

        col3, col4 = st.columns(2)
        with col3:
            inicio_reclutamiento = st.date_input("Inicio reclutamiento", value=date.today())
            etapa = st.selectbox("Etapa inicial", ETAPAS, index=0)
        with col4:
            fecha_ingreso_plan = st.date_input("Fecha ingreso planificada", value=None)
            comentarios = st.text_area("Comentarios", height=80)

        submitted = st.form_submit_button("Registrar proceso →")
        if submitted:
            if not posicion:
                st.error("La posición es obligatoria.")
            else:
                add_proceso({
                    "año": date.today().year,
                    "posicion": posicion,
                    "area": area,
                    "responsable": responsable,
                    "jefe_directo": jefe_directo,
                    "gerente": gerente,
                    "reemplaza": reemplaza,
                    "tipo_cobertura": tipo_cobertura,
                    "vacantes": vacantes,
                    "etapa": etapa,
                    "inicio_reclutamiento": str(inicio_reclutamiento),
                    "seleccionado": None,
                    "fecha_ingreso_plan": str(fecha_ingreso_plan) if fecha_ingreso_plan else None,
                    "fecha_ingreso_real": None,
                    "tipo_cierre": None,
                    "status": "Activo",
                    "comentarios": comentarios,
                })
                st.success(f"✅ Proceso registrado: {posicion} — {area}")
                st.rerun()
