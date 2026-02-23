import streamlit as st
import pandas as pd
from datetime import date
from utils.data import get_headcount, get_ceses, add_headcount, add_cese, import_headcount_excel

def render(usuario: str):
    st.markdown('<div class="section-header">👥 Headcount — Desarrolladores de Ventas</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["🟢 Activos", "🔴 Ceses", "📤 Importar Excel", "➕ Registrar manual"])

    with tab1:
        _render_activos()

    with tab2:
        _render_ceses()

    with tab3:
        _render_importar()

    with tab4:
        _render_manual(usuario)


def _render_activos():
    hc = get_headcount()

    # Filtrar solo ventas y activos
    if hc.empty:
        st.markdown('<div class="alert-box alert-ok">Aún no hay registros. Importa desde Excel o añade manualmente.</div>', unsafe_allow_html=True)
        return

    activos = hc[hc["activo"] == True] if "activo" in hc.columns else hc
    ventas = activos[activos["area"].str.lower() == "ventas"] if "area" in activos.columns else activos

    # Métricas rápidas
    c1, c2, c3 = st.columns(3)
    mes = pd.Timestamp.today().month
    ingresos_mes = len(ventas[pd.to_datetime(ventas["fecha_ingreso"], errors="coerce").dt.month == mes]) if not ventas.empty else 0
    ceses_df = get_ceses()
    ceses_mes = len(ceses_df[pd.to_datetime(ceses_df["fecha_cese"], errors="coerce").dt.month == mes]) if not ceses_df.empty else 0

    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="label">Headcount activo</div>
            <div class="value">{len(ventas)}</div>
            <div class="sub">Desarrolladores de ventas</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="label">Ingresos este mes</div>
            <div class="value" style="color:#4dffb8;">{ingresos_mes}</div>
            <div class="sub">Nuevos en el equipo</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="label">Ceses este mes</div>
            <div class="value" style="color:#ff5c5c;">{ceses_mes}</div>
            <div class="sub">Bajas registradas</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if ventas.empty:
        st.info("No hay colaboradores activos de ventas.")
        return

    # Tabla
    cols_show = [c for c in ["nombre", "cargo", "fecha_ingreso", "comentarios"] if c in ventas.columns]
    display = ventas[cols_show].copy()
    if "fecha_ingreso" in display.columns:
        display["fecha_ingreso"] = pd.to_datetime(display["fecha_ingreso"], errors="coerce").dt.strftime("%d/%m/%Y")

    display.columns = [c.replace("_", " ").title() for c in display.columns]

    # Botón de cese por persona
    for idx, row in ventas.iterrows():
        nombre = row.get("nombre", "")
        col_n, col_f, col_btn = st.columns([3, 2, 1])
        with col_n:
            fi = pd.to_datetime(row.get("fecha_ingreso"), errors="coerce")
            fi_str = fi.strftime("%d/%m/%Y") if pd.notna(fi) else "—"
            st.markdown(f"""
            <div style="background:#18181f;border:1px solid #2a2a35;border-radius:8px;
                        padding:0.7rem 1rem;margin-bottom:0.4rem;">
                <span style="font-weight:600;">{nombre}</span>
                <span style="color:#888;font-size:0.8rem;margin-left:1rem;">{row.get('cargo','')}  ·  Ingresó: {fi_str}</span>
            </div>
            """, unsafe_allow_html=True)
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔴 Cese", key=f"cese_{idx}"):
                st.session_state[f"form_cese_{idx}"] = True

        if st.session_state.get(f"form_cese_{idx}"):
            with st.form(f"cese_form_{idx}"):
                fecha_cese = st.date_input("Fecha de cese", value=date.today(), key=f"fc_{idx}")
                motivo = st.selectbox("Motivo", ["Renuncia voluntaria", "Término de contrato", "Desempeño", "Otro"], key=f"mot_{idx}")
                reemplazado_por = st.text_input("¿Quién lo reemplaza? (opcional)", key=f"rp_{idx}")
                ok = st.form_submit_button("Confirmar cese")
                if ok:
                    add_cese({
                        "nombre": nombre,
                        "cargo": row.get("cargo", ""),
                        "area": row.get("area", "Ventas"),
                        "fecha_cese": str(fecha_cese),
                        "motivo": motivo,
                        "reemplazado_por": reemplazado_por,
                        "proceso_id": None,
                    })
                    # Marcar inactivo
                    hc2 = get_headcount()
                    hc2.loc[hc2["nombre"].str.lower() == nombre.lower(), "activo"] = False
                    hc2.loc[hc2["nombre"].str.lower() == nombre.lower(), "fecha_cese"] = str(fecha_cese)
                    hc2.to_csv(__import__("utils.data", fromlist=["FILES"]).FILES["headcount"], index=False)
                    st.session_state[f"form_cese_{idx}"] = False
                    st.success(f"✅ Cese de {nombre} registrado.")
                    st.rerun()


def _render_ceses():
    ceses = get_ceses()
    if ceses.empty:
        st.markdown('<div class="alert-box alert-ok">No hay ceses registrados.</div>', unsafe_allow_html=True)
        return

    # Filtro por mes
    meses = ["Todos"] + sorted(
        pd.to_datetime(ceses["fecha_cese"], errors="coerce").dt.strftime("%Y-%m").dropna().unique().tolist(),
        reverse=True
    )
    mes_filtro = st.selectbox("Filtrar por mes", meses)

    df = ceses.copy()
    if mes_filtro != "Todos":
        df = df[pd.to_datetime(df["fecha_cese"], errors="coerce").dt.strftime("%Y-%m") == mes_filtro]

    if df.empty:
        st.info("Sin ceses en ese período.")
        return

    for _, row in df.iterrows():
        fecha = pd.to_datetime(row.get("fecha_cese")).strftime("%d/%m/%Y") if pd.notna(row.get("fecha_cese")) else "—"
        st.markdown(f"""
        <div style="background:#18181f;border:1px solid #2a2a35;border-radius:8px;
                    padding:0.8rem 1rem;margin-bottom:0.5rem;border-left:3px solid #ff5c5c;">
            <div style="display:flex;justify-content:space-between;">
                <div>
                    <span style="font-weight:600;">{row.get('nombre','')}</span>
                    <span style="color:#888;font-size:0.82rem;margin-left:1rem;">{row.get('cargo','')}</span>
                </div>
                <div style="text-align:right;">
                    <span style="color:#ff5c5c;font-size:0.82rem;">{fecha}</span>
                    <div style="color:#888;font-size:0.75rem;">{row.get('motivo','')}</div>
                </div>
            </div>
            {f'<div style="font-size:0.78rem;color:#666;margin-top:4px;">→ Reemplazado por: {row.get("reemplazado_por","")}</div>' if pd.notna(row.get("reemplazado_por")) and row.get("reemplazado_por") else ''}
        </div>
        """, unsafe_allow_html=True)


def _render_importar():
    st.markdown("### Importar headcount desde Excel")
    st.markdown("""
    <div class="alert-box alert-warn">
    Tu Excel puede tener cualquier nombre de columna — el sistema las mapea automáticamente.<br>
    Columnas reconocidas: <b>Nombre, Cargo, Fecha Ingreso, Fecha Cese, Motivo</b> (en cualquier variación).
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("Sube tu Excel de headcount de ventas", type=["xlsx", "xls"])
    if uploaded:
        st.markdown("**Vista previa del archivo:**")
        preview = pd.read_excel(uploaded)
        st.dataframe(preview.head(10), use_container_width=True)
        uploaded.seek(0)

        if st.button("✅ Importar datos"):
            n = import_headcount_excel(uploaded)
            st.success(f"✅ {n} colaboradores importados correctamente.")
            st.rerun()


def _render_manual(usuario: str):
    st.markdown("### Registrar colaborador manualmente")

    with st.form("nuevo_hc", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre completo *")
            cargo = st.text_input("Cargo", value="Desarrollador de Ventas")
            fecha_ingreso = st.date_input("Fecha de ingreso", value=date.today())
        with col2:
            tipo = st.selectbox("Tipo de movimiento", ["Ingreso", "Reingreso"])
            comentarios = st.text_input("Comentarios")

        submitted = st.form_submit_button("Registrar →")
        if submitted:
            if not nombre:
                st.error("El nombre es obligatorio.")
            else:
                add_headcount({
                    "nombre": nombre,
                    "cargo": cargo,
                    "area": "Ventas",
                    "fecha_ingreso": str(fecha_ingreso),
                    "fecha_cese": None,
                    "tipo_movimiento": tipo,
                    "motivo_cese": None,
                    "reemplazado_por": None,
                    "activo": True,
                    "comentarios": comentarios,
                })
                st.success(f"✅ {nombre} registrado en headcount.")
                st.rerun()
