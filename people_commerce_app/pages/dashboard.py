import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils.data import get_pendientes, get_procesos, get_headcount, get_ceses, export_to_excel


def render(usuario: str):
    st.markdown('<div class="section-header">Dashboard</div>', unsafe_allow_html=True)

    pendientes = get_pendientes()
    procesos   = get_procesos()
    headcount  = get_headcount()
    ceses      = get_ceses()
    hoy        = date.today()
    mes_actual = pd.Timestamp.today().month

    # ── KPIs ─────────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)

    pend_mis     = len(pendientes[(pendientes["responsable"] == usuario) & (pendientes["status"] != "Listo")]) if not pendientes.empty else 0
    pend_total   = len(pendientes[pendientes["status"] != "Listo"]) if not pendientes.empty else 0
    proc_activos = len(procesos[procesos["status"] != "Cerrado"]) if not procesos.empty else 0

    ingresos_mes = 0
    if not headcount.empty and "fecha_ingreso" in headcount.columns:
        ingresos_mes = len(headcount[pd.to_datetime(headcount["fecha_ingreso"], errors="coerce").dt.month == mes_actual])

    ceses_mes = 0
    if not ceses.empty and "fecha_cese" in ceses.columns:
        ceses_mes = len(ceses[pd.to_datetime(ceses["fecha_cese"], errors="coerce").dt.month == mes_actual])

    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="label">Mis pendientes</div>
            <div class="value">{pend_mis}</div>
            <div class="sub">{pend_total} en total</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="label">Procesos activos</div>
            <div class="value">{proc_activos}</div>
            <div class="sub">Reclutamiento abierto</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="label">Ingresos del mes</div>
            <div class="value">{ingresos_mes}</div>
            <div class="sub">Ventas y Supply</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        st.markdown(f"""<div class="metric-card">
            <div class="label">Ceses del mes</div>
            <div class="value">{ceses_mes}</div>
            <div class="sub">Registrados</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Alertas + Mis pendientes ──────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-header" style="font-size:1rem;">Alertas</div>', unsafe_allow_html=True)

        alertas = []

        if not pendientes.empty:
            vencidos = pendientes[
                (pd.to_datetime(pendientes["deadline"], errors="coerce").dt.date < hoy) &
                (pendientes["status"] != "Listo")
            ]
            for _, r in vencidos.iterrows():
                alertas.append(("danger", f"Pendiente vencido: <b>{r['tema']}</b> — {r['responsable']}"))

            proximos = pendientes[
                (pd.to_datetime(pendientes["deadline"], errors="coerce").dt.date.between(hoy, hoy + timedelta(days=2))) &
                (pendientes["status"] != "Listo")
            ]
            for _, r in proximos.iterrows():
                alertas.append(("warn", f"Deadline próximo: <b>{r['tema']}</b> — {r['responsable']}"))

        if not procesos.empty:
            abiertos = procesos[procesos["status"] != "Cerrado"].copy()
            if not abiertos.empty and "inicio_reclutamiento" in abiertos.columns:
                abiertos["dias"] = (pd.Timestamp.today() - pd.to_datetime(abiertos["inicio_reclutamiento"], errors="coerce")).dt.days
                for _, r in abiertos[abiertos["dias"] > 30].iterrows():
                    alertas.append(("warn", f"Proceso >30 días: <b>{r['posicion']}</b> ({int(r['dias'])} días)"))

        if alertas:
            for tipo, msg in alertas[:8]:
                st.markdown(f'<div class="alert-box alert-{tipo}">{msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-box alert-ok">Sin alertas activas</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="section-header" style="font-size:1rem;">Mis pendientes</div>', unsafe_allow_html=True)

        mis = pendientes[
            (pendientes["responsable"] == usuario) & (pendientes["status"] != "Listo")
        ].head(6) if not pendientes.empty else pd.DataFrame()

        if mis.empty:
            st.markdown('<div class="alert-box alert-ok">No tienes pendientes abiertos</div>', unsafe_allow_html=True)
        else:
            for _, r in mis.iterrows():
                prio_color = {"Alta": "badge-red", "Media": "badge-yellow", "Baja": "badge-green"}.get(r.get("prioridad", ""), "badge-purple")
                dl_str = pd.to_datetime(r["deadline"]).strftime("%d/%m") if pd.notna(r.get("deadline")) else "—"
                st.markdown(f"""
                <div style="background:#FFFFFF;border:1px solid #E5E7EB;border-radius:8px;
                            padding:0.8rem 1rem;margin-bottom:0.6rem;display:flex;
                            justify-content:space-between;align-items:center;">
                    <div>
                        <div style="font-size:0.9rem;font-weight:600;color:#1F2937;">{r['tema']}</div>
                        <div style="font-size:0.78rem;color:#6B7280;">{str(r.get('accion',''))[:60]}</div>
                    </div>
                    <div style="text-align:right;">
                        <span class="badge {prio_color}">{r.get('prioridad','')}</span>
                        <div style="font-size:0.75rem;color:#6B7280;margin-top:4px;">{dl_str}</div>
                    </div>
                </div>""", unsafe_allow_html=True)

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header" style="font-size:1rem;">Exportar</div>', unsafe_allow_html=True)

    if st.button("Descargar Excel"):
        buffer = export_to_excel()
        st.download_button(
            label="Guardar archivo",
            data=buffer,
            file_name=f"people_supply_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )