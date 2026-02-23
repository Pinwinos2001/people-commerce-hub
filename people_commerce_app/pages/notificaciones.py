import streamlit as st
from utils.data import get_pendientes, get_procesos
from utils.email_notif import (
    notif_deadlines_proximos,
    notif_procesos_estancados,
    notif_resumen_semanal,
    EMAIL_CONFIG,
)

def render(usuario: str):

    st.markdown('<div class="section-header">Notificaciones</div>', unsafe_allow_html=True)

    # Estado configuración Power Automate
    pa_url = EMAIL_CONFIG.get("power_automate_url", "")
    is_configured = pa_url and pa_url != "PEGA_TU_URL_AQUI"

    if not is_configured:
        st.markdown("""
        <div style="
            background:#fff4e5;
            border-left:5px solid #ffb200;
            padding:14px 18px;
            border-radius:10px;
            margin-bottom:18px;
            font-size:14px;
        ">
        <b>Power Automate no configurado.</b><br>
        Pega la URL del flujo en <code>utils/email_notif.py</code>.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="
            background:#f0faf5;
            border-left:5px solid #008C45;
            padding:14px 18px;
            border-radius:10px;
            margin-bottom:18px;
            font-size:14px;
        ">
        Power Automate configurado — listo para enviar correos
        </div>
        """, unsafe_allow_html=True)

    pendientes = get_pendientes()
    procesos   = get_procesos()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Envío manual")

    col1, col2, col3 = st.columns(3)

    # DEADLINES
    with col1:
        st.markdown(f"""
        <div style="
            background:#ffffff;
            border:1px solid #e6e6e6;
            border-radius:14px;
            padding:18px;
            box-shadow:0 4px 12px rgba(0,0,0,0.05);
            height:160px;
        ">
            <div style="font-weight:700;color:#008C45;">
                Deadlines próximos
            </div>
            <div style="font-size:13px;color:#666;margin-top:6px;">
                Pendientes venciendo en 48 horas
            </div>
            <div style="font-size:22px;font-weight:700;margin-top:10px;">
                {len(pendientes)}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Enviar alerta deadlines", disabled=not is_configured):
            with st.spinner("Enviando..."):
                ok, msg = notif_deadlines_proximos(pendientes, EMAIL_CONFIG)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

    # PROCESOS
    with col2:

        dias = st.number_input("Días límite", min_value=7, max_value=90, value=30, step=5)

        st.markdown(f"""
        <div style="
            background:#ffffff;
            border:1px solid #e6e6e6;
            border-radius:14px;
            padding:18px;
            box-shadow:0 4px 12px rgba(0,0,0,0.05);
            height:160px;
        ">
            <div style="font-weight:700;color:#008C45;">
                Procesos estancados
            </div>
            <div style="font-size:13px;color:#666;margin-top:6px;">
                Procesos con más de {dias} días abiertos
            </div>
            <div style="font-size:22px;font-weight:700;margin-top:10px;">
                {len(procesos)}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Enviar alerta procesos", disabled=not is_configured):
            with st.spinner("Enviando..."):
                ok, msg = notif_procesos_estancados(
                    procesos,
                    EMAIL_CONFIG,
                    dias_limite=dias
                )
            if ok:
                st.success(msg)
            else:
                st.error(msg)

    # RESUMEN
    with col3:
        st.markdown(f"""
        <div style="
            background:#ffffff;
            border:1px solid #e6e6e6;
            border-radius:14px;
            padding:18px;
            box-shadow:0 4px 12px rgba(0,0,0,0.05);
            height:160px;
        ">
            <div style="font-weight:700;color:#008C45;">
                Resumen semanal
            </div>
            <div style="font-size:13px;color:#666;margin-top:6px;">
                Estado consolidado
            </div>
            <div style="font-size:22px;font-weight:700;margin-top:10px;">
                Reporte ejecutivo
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Enviar resumen semanal", disabled=not is_configured):
            with st.spinner("Enviando..."):
                ok, msg = notif_resumen_semanal(pendientes, procesos, EMAIL_CONFIG)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("Configuración y deploy"):
        st.markdown("""
        - Subir repositorio a GitHub  
        - Deploy en Streamlit Cloud  
        - Configurar Power Automate  
        - Automatizar con cron-job si se requiere
        """)

    with st.expander("Seguridad"):
        st.markdown("""
        - Usar st.secrets para credenciales  
        - Limitar acceso en Streamlit Cloud  
        - Implementar SSO corporativo si es necesario
        """)