import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils.data import get_pendientes, get_procesos, get_headcount, get_ceses, export_to_excel

def render(usuario: str):
    st.markdown('<div class="section-header">📊 Dashboard</div>', unsafe_allow_html=True)

    pendientes = get_pendientes()
    procesos   = get_procesos()
    headcount  = get_headcount()
    ceses      = get_ceses()
    hoy        = date.today()

    # ── KPI row ──────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)

    pend_mis     = len(pendientes[(pendientes["responsable"] == usuario) & (pendientes["status"] != "Listo")])
    pend_total   = len(pendientes[pendientes["status"] != "Listo"])
    proc_activos = len(procesos[procesos["status"] != "Cerrado"])
    hc_activo    = len(headcount[headcount["activo"] == True]) if "activo" in headcount.columns else 0

    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="label">Mis pendientes</div>
            <div class="value">{pend_mis}</div>
            <div class="sub">{pend_total} total entre ambas</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="value">{proc_activos}</div>
            <div class="label">Procesos R&S activos</div>
            <div class="sub">Sin cerrar aún</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        # Ingresos este mes
        mes_actual = pd.Timestamp.today().month
        ingresos_mes = 0
        if not headcount.empty and "fecha_ingreso" in headcount.columns:
            ingresos_mes = len(headcount[
                pd.to_datetime(headcount["fecha_ingreso"], errors="coerce").dt.month == mes_actual
            ])
        st.markdown(f"""<div class="metric-card">
            <div class="value">{ingresos_mes}</div>
            <div class="label">Ingresos este mes</div>
            <div class="sub">Ventas + Supply</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        ceses_mes = 0
        if not ceses.empty and "fecha_cese" in ceses.columns:
            ceses_mes = len(ceses[
                pd.to_datetime(ceses["fecha_cese"], errors="coerce").dt.month == mes_actual
            ])
        st.markdown(f"""<div class="metric-card">
            <div class="value">{ceses_mes}</div>
            <div class="label">Ceses este mes</div>
            <div class="sub">Registrados</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Alertas ──────────────────────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-header" style="font-size:1rem;">🚨 Alertas</div>', unsafe_allow_html=True)

        alertas = []

        # Pendientes vencidos
        if not pendientes.empty:
            vencidos = pendientes[
                (pd.to_datetime(pendientes["deadline"], errors="coerce").dt.date < hoy) &
                (pendientes["status"] != "Listo")
            ]
            for _, r in vencidos.iterrows():
                alertas.append(("danger", f"Pendiente vencido: <b>{r['tema']}</b> — {r['responsable']}"))

            # Deadlines en 2 días
            proximos = pendientes[
                (pd.to_datetime(pendientes["deadline"], errors="coerce").dt.date.between(hoy, hoy + timedelta(days=2))) &
                (pendientes["status"] != "Listo")
            ]
            for _, r in proximos.iterrows():
                alertas.append(("warn", f"Deadline próximo: <b>{r['tema']}</b> — {r['responsable']}"))

        # Procesos estancados +30d
        if not procesos.empty:
            hoy_ts = pd.Timestamp.today()
            abiertos = procesos[procesos["status"] != "Cerrado"].copy()
            if not abiertos.empty and "inicio_reclutamiento" in abiertos.columns:
                abiertos["dias"] = (hoy_ts - pd.to_datetime(abiertos["inicio_reclutamiento"], errors="coerce")).dt.days
                estancados = abiertos[abiertos["dias"] > 30]
                for _, r in estancados.iterrows():
                    alertas.append(("warn", f"Proceso +30 días: <b>{r['posicion']}</b> ({int(r['dias'])}d)"))

        if alertas:
            for tipo, msg in alertas[:8]:
                st.markdown(f'<div class="alert-box alert-{tipo}">{msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-box alert-ok">✅ Todo en orden — sin alertas activas</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="section-header" style="font-size:1rem;">📋 Mis pendientes recientes</div>', unsafe_allow_html=True)

        mis = pendientes[
            (pendientes["responsable"] == usuario) & (pendientes["status"] != "Listo")
        ].head(6)

        if mis.empty:
            st.markdown('<div class="alert-box alert-ok">🎉 No tienes pendientes abiertos</div>', unsafe_allow_html=True)
        else:
            for _, r in mis.iterrows():
                prioridad_color = {"Alta": "badge-red", "Media": "badge-yellow", "Baja": "badge-green"}.get(r.get("prioridad", ""), "badge-purple")
                dl_str = pd.to_datetime(r["deadline"]).strftime("%d/%m") if pd.notna(r.get("deadline")) else "—"
                st.markdown(f"""
                <div style="background:#18181f;border:1px solid #2a2a35;border-radius:8px;
                            padding:0.8rem 1rem;margin-bottom:0.5rem;display:flex;
                            justify-content:space-between;align-items:center;">
                    <div>
                        <div style="font-size:0.9rem;font-weight:600;">{r['tema']}</div>
                        <div style="font-size:0.78rem;color:#888;">{str(r.get('accion',''))[:55]}</div>
                    </div>
                    <div style="text-align:right;">
                        <span class="badge {prioridad_color}">{r.get('prioridad','')}</span>
                        <div style="font-size:0.75rem;color:#888;margin-top:4px;">📅 {dl_str}</div>
                    </div>
                </div>""", unsafe_allow_html=True)

    # ── Export ───────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header" style="font-size:1rem;">💾 Exportar</div>', unsafe_allow_html=True)
    if st.button("⬇️ Descargar todo en Excel"):
        buffer = export_to_excel()
        st.download_button(
            label="📥 Guardar Excel",
            data=buffer,
            file_name=f"people_supply_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
