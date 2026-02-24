import streamlit as st
import pandas as pd
from datetime import date
from utils.data import get_pendientes, add_pendiente, update_pendiente, delete_pendiente
from utils.email_notif import notif_nuevo_pendiente, EMAIL_CONFIG

USUARIOS = ["HRBP Intern", "Business Partner"]
PRIORIDADES = ["Alta", "Media", "Baja"]
ESTADOS = ["Pendiente", "En curso", "Listo"]


def render(usuario: str):
    st.markdown('<div class="section-header">Pendientes</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Ver pendientes", "Nuevo pendiente"])

    with tab1:
        df = get_pendientes()

        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_resp = st.selectbox("Responsable", ["Todos"] + USUARIOS)
        with col2:
            filtro_status = st.selectbox("Estado", ["Todos"] + ESTADOS)
        with col3:
            filtro_prio = st.selectbox("Prioridad", ["Todos"] + PRIORIDADES)

        if df.empty:
            st.markdown(
                '<div class="alert-box alert-ok">No hay pendientes registrados.</div>',
                unsafe_allow_html=True,
            )
        else:
            mask = pd.Series([True] * len(df))
            if filtro_resp != "Todos":
                mask &= df["responsable"] == filtro_resp
            if filtro_status != "Todos":
                mask &= df["status"] == filtro_status
            if filtro_prio != "Todos":
                mask &= df["prioridad"] == filtro_prio

            filtered = df[mask].copy()

            if filtered.empty:
                st.info("No hay pendientes con los filtros seleccionados.")
            else:
                for _, row in filtered.iterrows():
                    _render_pendiente_card(row, usuario)

    with tab2:
        _form_nuevo_pendiente(usuario)


def _render_pendiente_card(row, usuario_actual):
    status_badge = {
        "Pendiente": "badge-red",
        "En curso":  "badge-yellow",
        "Listo":     "badge-green",
    }.get(row.get("status", ""), "badge-purple")

    prio_badge = {
        "Alta":  "badge-red",
        "Media": "badge-yellow",
        "Baja":  "badge-green",
    }.get(row.get("prioridad", ""), "badge-purple")

    dl = pd.to_datetime(row.get("deadline"))
    dl_str = dl.strftime("%d/%m/%Y") if pd.notna(dl) else "—"
    hoy = pd.Timestamp.today()
    vencido = pd.notna(dl) and dl < hoy and row.get("status") != "Listo"
    border_color = "#DC2626" if vencido else "#E5E7EB"

    st.markdown(f"""
    <div style="
        background:#FFFFFF;
        border:1px solid #E5E7EB;
        border-left:4px solid {border_color};
        border-radius:12px;
        padding:1.1rem 1.3rem;
        margin-bottom:1rem;
    ">
        <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:0.4rem;">
            <div style="font-weight:600;font-size:0.95rem;color:#1F2937;">
                {row.get('tema','')}
            </div>
            <div style="display:flex;gap:6px;">
                <span class="badge {prio_badge}">{row.get('prioridad','')}</span>
                <span class="badge {status_badge}">{row.get('status','')}</span>
            </div>
        </div>
        <div style="color:#6B7280;font-size:0.85rem;margin-bottom:0.6rem;">
            {row.get('accion','')}
        </div>
        <div style="display:flex;gap:1.5rem;font-size:0.75rem;color:#6B7280;">
            <span>{row.get('responsable','')}</span>
            <span>{dl_str}{' · Vencido' if vencido else ''}</span>
            <span>{str(row.get('comentarios',''))[:60] if pd.notna(row.get('comentarios')) else ''}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_s, col_d = st.columns([3, 1])
    with col_s:
        nuevo_status = st.selectbox(
            "Cambiar estado", ESTADOS,
            index=ESTADOS.index(row.get("status", "Pendiente")) if row.get("status") in ESTADOS else 0,
            key=f"status_{row['id']}"
        )
        if nuevo_status != row.get("status"):
            update_pendiente(row["id"], "status", nuevo_status)
            st.rerun()
    with col_d:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Eliminar", key=f"del_{row['id']}"):
            delete_pendiente(row["id"])
            st.rerun()


def _form_nuevo_pendiente(usuario_actual):
    st.markdown("### Crear nuevo pendiente")

    with st.form("nuevo_pendiente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tema = st.text_input("Tema *")
            responsable = st.selectbox(
                "Responsable *", USUARIOS,
                index=USUARIOS.index(usuario_actual) if usuario_actual in USUARIOS else 0,
            )
            prioridad = st.selectbox("Prioridad", PRIORIDADES, index=1)
        with col2:
            accion = st.text_area("Acción *", height=100)
            deadline = st.date_input("Deadline", value=None)

        comentarios = st.text_input("Comentarios")
        notificar = st.checkbox("Notificar por correo al responsable", value=True)

        submitted = st.form_submit_button("Crear pendiente")
        if submitted:
            if not tema or not accion:
                st.error("Tema y acción son obligatorios.")
                return

            add_pendiente(
                tema=tema, accion=accion, responsable=responsable,
                deadline=str(deadline) if deadline else None,
                status="Pendiente", prioridad=prioridad,
                comentarios=comentarios, creado_por=usuario_actual,
            )

            if notificar and deadline:
                ok, msg = notif_nuevo_pendiente(tema, responsable, str(deadline), EMAIL_CONFIG)
                if ok:
                    st.success("Pendiente creado y notificación enviada.")
                else:
                    st.success("Pendiente creado.")
                    st.warning(f"No se pudo enviar la notificación: {msg}")
            else:
                st.success("Pendiente creado.")
            st.rerun()
