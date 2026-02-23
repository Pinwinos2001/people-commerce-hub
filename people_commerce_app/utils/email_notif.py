import requests
from datetime import datetime, date, timedelta
import pandas as pd

# ── Config — solo pegar la URL de Power Automate, sin passwords ──────────────
#
# CÓMO OBTENER LA URL:
#   1. Power Automate → Crear → Flujo de nube instantáneo
#   2. Trigger: "Cuando se recibe una solicitud HTTP"
#   3. Pega este JSON en "Esquema JSON del cuerpo de la solicitud":
#      {
#        "type": "object",
#        "properties": {
#          "subject":    { "type": "string" },
#          "body":       { "type": "string" },
#          "recipients": { "type": "string" }
#        }
#      }
#   4. Agrega acción: "Enviar un correo electrónico (V2)" de Office 365 Outlook
#      - Para:    triggerBody()?['recipients']
#      - Asunto:  triggerBody()?['subject']
#      - Cuerpo:  triggerBody()?['body']  (activa "Es HTML")
#   5. Guarda el flujo → copia la URL que aparece en el trigger
#   6. Pégala abajo en POWER_AUTOMATE_URL

EMAIL_CONFIG = {
    "power_automate_url": "https://default66e853deece344dd9d66ee6bdf4159.d4.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/c7a4dd30e4844065a3b6fe0362f14ae3/triggers/manual/paths/invoke?api-version=1",  # ← la única config necesaria
    "recipients": {
        "HRBP Intern": "sissy.ospina@heineken.com",  # ← cambiar al correo real
        "Business Partner": "Claudia.Bacigalupo@heineken.com",   # ← cambiar al correo real
    }
}

def _send_email(to_emails: list, subject: str, html_body: str, config: dict) -> tuple[bool, str]:
    """Abre Outlook con el correo pre-redactado."""
    import urllib.parse
    body_plain = html_body.replace("<br>", "\n").replace("</div>", "\n")
    import re
    body_clean = re.sub(r'<[^>]+>', '', body_plain)
    
    mailto = f"mailto:{';'.join(to_emails)}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body_clean)}"
    
    import streamlit as st
    st.markdown(f'<a href="{mailto}" target="_blank"><button style="background:#c8f04a;color:#0f0f13;padding:0.5rem 1.5rem;border:none;border-radius:6px;font-weight:700;cursor:pointer;">📨 Abrir en Outlook</button></a>', unsafe_allow_html=True)
    return True, "Correo listo — click en el botón para enviarlo"

def _html_template(title: str, items: list[dict], color: str = "#c8f04a") -> str:
    rows = ""
    for item in items:
        rows += f"""
        <tr style="border-bottom:1px solid #2a2a35;">
            <td style="padding:10px 16px; color:#f0f0f0;">{item.get('nombre','')}</td>
            <td style="padding:10px 16px; color:#aaa;">{item.get('detalle','')}</td>
            <td style="padding:10px 16px;">
                <span style="background:rgba(200,240,74,0.1);color:{color};padding:3px 10px;
                border-radius:999px;font-size:12px;">{item.get('badge','')}</span>
            </td>
        </tr>"""

    return f"""
    <!DOCTYPE html><html><body style="background:#0f0f13;margin:0;padding:32px;font-family:'Segoe UI',sans-serif;">
    <div style="max-width:600px;margin:0 auto;background:#18181f;border-radius:16px;overflow:hidden;
                border:1px solid #2a2a35;">
        <div style="background:linear-gradient(135deg,#22222c,#1a1a24);padding:28px 32px;
                    border-bottom:1px solid #2a2a35;">
            <div style="font-size:22px;font-weight:800;color:{color};letter-spacing:-0.02em;">
                🏢 People Supply Hub
            </div>
            <div style="color:#888;font-size:13px;margin-top:4px;">{title}</div>
        </div>
        <div style="padding:24px 32px;">
            <table style="width:100%;border-collapse:collapse;">
                <thead>
                    <tr style="background:#22222c;">
                        <th style="padding:10px 16px;text-align:left;color:#888;font-size:11px;
                            text-transform:uppercase;letter-spacing:0.1em;">Item</th>
                        <th style="padding:10px 16px;text-align:left;color:#888;font-size:11px;
                            text-transform:uppercase;letter-spacing:0.1em;">Detalle</th>
                        <th style="padding:10px 16px;text-align:left;color:#888;font-size:11px;
                            text-transform:uppercase;letter-spacing:0.1em;">Estado</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        <div style="padding:16px 32px;background:#12121a;color:#555;font-size:11px;">
            Generado automáticamente — {datetime.now().strftime('%d/%m/%Y %H:%M')}
        </div>
    </div>
    </body></html>"""

# ── Notificaciones específicas ────────────────────────────────────────────────

def notif_deadlines_proximos(pendientes_df: pd.DataFrame, config: dict) -> tuple[bool, str]:
    """Avisa sobre pendientes con deadline en los próximos 2 días."""
    hoy = date.today()
    proximos = pendientes_df[
        (pd.to_datetime(pendientes_df["deadline"]).dt.date <= hoy + timedelta(days=2)) &
        (pendientes_df["status"] != "Listo")
    ]
    if proximos.empty:
        return True, "Sin deadlines próximos"

    items = []
    for _, row in proximos.iterrows():
        dl = pd.to_datetime(row["deadline"]).date()
        dias = (dl - hoy).days
        badge = "HOY" if dias == 0 else ("MAÑANA" if dias == 1 else f"En {dias}d")
        items.append({"nombre": row["tema"], "detalle": row["accion"][:60], "badge": badge})

    html = _html_template("⚠️ Pendientes con deadline próximo", items, "#ffb84d")
    emails = list(config["recipients"].values())
    return _send_email(emails, "⚠️ People Supply — Deadlines próximos", html, config)

def notif_procesos_estancados(procesos_df: pd.DataFrame, config: dict, dias_limite: int = 30) -> tuple[bool, str]:
    """Avisa sobre procesos abiertos con más de N días sin cerrar."""
    hoy = pd.Timestamp.today()
    abiertos = procesos_df[procesos_df["status"] != "Cerrado"].copy()
    abiertos["dias"] = (hoy - pd.to_datetime(abiertos["inicio_reclutamiento"])).dt.days
    estancados = abiertos[abiertos["dias"] > dias_limite]
    if estancados.empty:
        return True, "Sin procesos estancados"

    items = []
    for _, row in estancados.iterrows():
        items.append({
            "nombre": row["posicion"],
            "detalle": f'{row["area"]} — {row["responsable"]}',
            "badge": f'{int(row["dias"])} días',
        })

    html = _html_template("🔴 Procesos R&S sin cerrar", items, "#ff5c5c")
    emails = list(config["recipients"].values())
    return _send_email(emails, "🔴 People Supply — Procesos estancados", html, config)

def notif_resumen_semanal(pendientes_df: pd.DataFrame, procesos_df: pd.DataFrame, config: dict) -> tuple[bool, str]:
    """Resumen semanal completo."""
    pend_abiertos = len(pendientes_df[pendientes_df["status"] != "Listo"])
    proc_activos  = len(procesos_df[procesos_df["status"] != "Cerrado"])
    proc_cerrados_mes = len(procesos_df[
        (procesos_df["status"] == "Cerrado") &
        (pd.to_datetime(procesos_df["fecha_ingreso_real"]).dt.month == datetime.now().month)
    ])

    items = [
        {"nombre": "Pendientes abiertos",     "detalle": "Total entre ambas",        "badge": str(pend_abiertos)},
        {"nombre": "Procesos R&S activos",     "detalle": "Sin cerrar",               "badge": str(proc_activos)},
        {"nombre": "Ingresos este mes",        "detalle": "Procesos cerrados",        "badge": str(proc_cerrados_mes)},
    ]
    html = _html_template("📋 Resumen semanal — People Supply", items, "#c8f04a")
    emails = list(config["recipients"].values())
    return _send_email(emails, "📋 People Supply — Resumen semanal", html, config)

def notif_nuevo_pendiente(tema: str, asignado_a: str, deadline: str, config: dict) -> tuple[bool, str]:
    """Avisa cuando se asigna un nuevo pendiente."""
    to_email = config["recipients"].get(asignado_a)
    if not to_email:
        return False, f"No se encontró email para {asignado_a}"
    items = [{"nombre": tema, "detalle": f"Deadline: {deadline}", "badge": "NUEVO"}]
    html = _html_template(f"📌 Nuevo pendiente asignado a {asignado_a}", items, "#c8f04a")
    return _send_email([to_email], f"📌 Nuevo pendiente: {tema}", html, config)
