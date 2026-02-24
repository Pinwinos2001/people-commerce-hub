# 🏢 People Supply Hub

Clave de subpase: 

App web para gestionar pendientes, procesos de selección y headcount de ventas — sin abrir Excel.

## ⚡ Instalación (5 minutos)

### 1. Instala Python (si no lo tienes)
Descarga desde [python.org](https://python.org) → versión 3.10 o superior.

### 2. Descarga los archivos
Descarga la carpeta `people_supply_app` y ponla donde quieras en tu laptop.

### 3. Instala las dependencias
Abre una terminal en la carpeta del proyecto y ejecuta:
```bash
pip install -r requirements.txt
```

### 4. Corre la app
```bash
streamlit run app.py
```
Se abre automáticamente en tu navegador en `http://localhost:8501`

---

## 🔐 Contraseñas por defecto
| Usuario | Contraseña |
|---------|-----------|
| HRBP Intern| hrbp2024 |
| Business Partner | commerce2024   |

**Cámbialas** en `utils/auth.py` antes de compartir.

---

## 📧 Configurar correo (Outlook corporativo)

Edita `utils/email_notif.py`:

```python
EMAIL_CONFIG = {
    "smtp_server": "smtp.office365.com",
    "smtp_port": 587,
    "sender_email": "TU_CORREO@empresa.com",   # ← tu correo
    "sender_password": "TU_APP_PASSWORD",       # ← App Password de Microsoft
    "recipients": {
        "Ariana": "ariana@empresa.com",
        "Jefa":   "jefa@empresa.com",
    }
}
```

Para obtener el App Password:
1. [myaccount.microsoft.com](https://myaccount.microsoft.com) → Seguridad
2. Contraseñas de aplicación → Nueva → "People Supply App"
3. Copia y pega la contraseña

---

## 🌐 Deploy en Streamlit Cloud (para acceder sin abrir la laptop)

1. Sube el código a GitHub (repo privado)
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta GitHub → selecciona el repo → Entry point: `app.py`
4. Deploy → obtienes una URL permanente

---

## 📁 Estructura del proyecto

```
people_supply_app/
├── app.py                  # Entrada principal + login
├── requirements.txt
├── data/                   # CSVs generados automáticamente
│   ├── pendientes.csv
│   ├── procesos.csv
│   ├── headcount.csv
│   └── ceses.csv
├── pages/
│   ├── dashboard.py        # KPIs y alertas
│   ├── pendientes.py       # Gestión de pendientes
│   ├── procesos.py         # Tracker R&S con cierre automático
│   ├── headcount.py        # Headcount ventas + ceses
│   └── notificaciones.py   # Envío de correos
└── utils/
    ├── auth.py             # Login
    ├── data.py             # Lectura/escritura de datos
    └── email_notif.py      # Notificaciones por correo
```

---

## 🔄 ¿Qué hace automáticamente?

- **Al cerrar un proceso R&S**: registra al ingresante en headcount y si hay reemplazo, registra el cese de quien sale
- **Alertas visuales**: en el dashboard ves pendientes vencidos y procesos +30 días sin cerrar
- **Notificaciones por correo**: deadlines próximos, procesos estancados, resumen semanal
- **Import de Excel**: sube tu planilla de ventas y detecta las columnas automáticamente
- **Export a Excel**: descarga todo en un Excel formateado desde el dashboard
