import streamlit as st
from utils.data import get_pendientes, get_procesos
from utils.email_notif import (
    notif_deadlines_proximos,
    notif_procesos_estancados,
    notif_resumen_semanal,
    EMAIL_CONFIG,
)

def render(usuario: str):
    st.markdown('<div class="section-header">📧 Notificaciones</div>', unsafe_allow_html=True)

    # ── Config status ────────────────────────────────────────────────────────
    pa_url = EMAIL_CONFIG.get("power_automate_url", "")
    is_configured = pa_url and pa_url != "PEGA_TU_URL_AQUI"

    if not is_configured:
        st.markdown("""
        <div class="alert-box alert-warn">
        <b>⚠️ Power Automate no configurado.</b> Crea el flujo y pega la URL en 
        <code>utils/email_notif.py</code>. Sin passwords ni MFA — instrucciones abajo 👇
        </div>
        """, unsafe_allow_html=True)

        with st.expander("📖 Cómo crear el flujo en Power Automate (5 min)"):
            st.markdown("""
            **Paso 1 — Crear el flujo:**
            1. Ve a [make.powerautomate.com](https://make.powerautomate.com)
            2. **Crear** → **Flujo de nube instantáneo**
            3. Nómbralo "People Supply - Envío de correos"
            4. Trigger: **"Cuando se recibe una solicitud HTTP"**

            **Paso 2 — Configurar el trigger (pega este JSON):**
            ```json
            {
              "type": "object",
              "properties": {
                "subject":    { "type": "string" },
                "body":       { "type": "string" },
                "recipients": { "type": "string" }
              }
            }
            ```

            **Paso 3 — Agregar acción de correo:**
            1. ➕ Nueva acción → busca **"Enviar un correo electrónico (V2)"** de Office 365
            2. Configura así:
               - **Para:** `triggerBody()?['recipients']`
               - **Asunto:** `triggerBody()?['subject']`
               - **Cuerpo:** `triggerBody()?['body']`
               - Activa la opción **"Es HTML"** ✅

            **Paso 4 — Guardar y copiar la URL:**
            1. Guarda el flujo
            2. Haz click en el trigger → aparece la **URL HTTP POST**
            3. Cópiala y pégala en `utils/email_notif.py`:
            ```python
            "power_automate_url": "https://prod-XX.westus.logic.azure.com/..."
            ```

            ✅ Sin passwords, sin MFA, funciona con tu cuenta Heineken normal.
            """)
    else:
        st.markdown(f"""
        <div class="alert-box alert-ok">
        ✅ Power Automate configurado — correos listos para enviar
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Acciones manuales ────────────────────────────────────────────────────
    st.markdown('<div class="section-header" style="font-size:1rem;">🚀 Enviar ahora</div>', unsafe_allow_html=True)

    pendientes = get_pendientes()
    procesos   = get_procesos()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="label">Deadlines próximos</div>
            <div style="color:#888;font-size:0.82rem;margin-top:0.4rem;">
                Avisa sobre pendientes venciendo en 48h
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📨 Enviar alerta deadlines", disabled=not is_configured):
            with st.spinner("Enviando..."):
                ok, msg = notif_deadlines_proximos(pendientes, EMAIL_CONFIG)
            if ok:
                st.success(f"✅ {msg}")
            else:
                st.error(f"Error: {msg}")

    with col2:
        dias = st.number_input("Días límite", min_value=7, max_value=90, value=30, step=5)
        st.markdown("""
        <div class="metric-card">
            <div class="label">Procesos estancados</div>
            <div style="color:#888;font-size:0.82rem;margin-top:0.4rem;">
                Avisa sobre procesos sin cerrar
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📨 Enviar alerta procesos", disabled=not is_configured):
            with st.spinner("Enviando..."):
                ok, msg = notif_procesos_estancados(procesos, EMAIL_CONFIG, dias_limite=dias)
            if ok:
                st.success(f"✅ {msg}")
            else:
                st.error(f"Error: {msg}")

    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="label">Resumen semanal</div>
            <div style="color:#888;font-size:0.82rem;margin-top:0.4rem;">
                Resumen completo a ambas
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📨 Enviar resumen semanal", disabled=not is_configured):
            with st.spinner("Enviando..."):
                ok, msg = notif_resumen_semanal(pendientes, procesos, EMAIL_CONFIG)
            if ok:
                st.success(f"✅ {msg}")
            else:
                st.error(f"Error: {msg}")

    # ── Deploy tip ────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🌐 Cómo deployar en Streamlit Cloud (gratis)"):
        st.markdown("""
        **Para que la app esté disponible siempre, sin abrir nada en tu laptop:**

        1. **Sube el código a GitHub** (repositorio privado)
        2. Ve a [share.streamlit.io](https://share.streamlit.io)
        3. Conecta tu cuenta de GitHub
        4. Selecciona el repo → `app.py` como entry point
        5. En **Secrets** agrega:
        ```toml
        [email]
        sender = "tu@correo.com"
        password = "app_password_aqui"
        ```
        6. Deploy → te da una URL que puedes abrir desde cualquier lugar

        **Para las notificaciones automáticas (ej. todos los lunes):**
        Puedes usar [cron-job.org](https://cron-job.org) gratis — hace un ping a tu app
        que dispara el resumen semanal sin que tengas que hacer nada.
        """)

    with st.expander("🔒 Cómo hacer la app más segura"):
        st.markdown("""
        Opciones ordenadas de más simple a más robusto:

        - **Password en Streamlit Cloud**: en Settings → Sharing → "Only specific people"
        - **Contraseñas en Secrets**: mueve las contraseñas del código a st.secrets
        - **Google Auth**: con la librería `streamlit-google-auth` si tienen Google Workspace
        - **Microsoft SSO**: con `msal` si quieren login con cuenta corporativa
        """)
