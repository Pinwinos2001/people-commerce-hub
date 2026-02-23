import pandas as pd
import os
from datetime import datetime, date

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

FILES = {
    "pendientes": os.path.join(DATA_DIR, "pendientes.csv"),
    "procesos":   os.path.join(DATA_DIR, "procesos.csv"),
    "headcount":  os.path.join(DATA_DIR, "headcount.csv"),
    "ceses":      os.path.join(DATA_DIR, "ceses.csv"),
}

PENDIENTES_COLS = ["id", "tema", "accion", "responsable", "deadline", "status", "prioridad", "comentarios", "creado_por", "fecha_creacion"]
PROCESOS_COLS   = ["id", "año", "posicion", "area", "responsable", "jefe_directo", "gerente", "reemplaza",
                   "tipo_cobertura", "vacantes", "etapa", "inicio_reclutamiento", "seleccionado",
                   "fecha_ingreso_plan", "fecha_ingreso_real", "tipo_cierre", "status", "comentarios", "fecha_creacion"]
HEADCOUNT_COLS  = ["id", "nombre", "cargo", "area", "fecha_ingreso", "fecha_cese", "tipo_movimiento",
                   "motivo_cese", "reemplazado_por", "activo", "comentarios", "fecha_registro"]
CESES_COLS      = ["id", "nombre", "cargo", "area", "fecha_cese", "motivo", "reemplazado_por", "proceso_id", "fecha_registro"]

def init_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    _init_csv(FILES["pendientes"], PENDIENTES_COLS)
    _init_csv(FILES["procesos"],   PROCESOS_COLS)
    _init_csv(FILES["headcount"],  HEADCOUNT_COLS)
    _init_csv(FILES["ceses"],      CESES_COLS)

def _init_csv(path, cols):
    if not os.path.exists(path):
        pd.DataFrame(columns=cols).to_csv(path, index=False)

# ── PENDIENTES ───────────────────────────────────────────────────────────────

def get_pendientes():
    df = pd.read_csv(FILES["pendientes"])
    if "deadline" in df.columns:
        df["deadline"] = pd.to_datetime(df["deadline"], errors="coerce")
    return df

def add_pendiente(tema, accion, responsable, deadline, status, prioridad, comentarios, creado_por):
    df = get_pendientes()
    new_id = int(df["id"].max() + 1) if len(df) > 0 else 1
    row = {
        "id": new_id, "tema": tema, "accion": accion, "responsable": responsable,
        "deadline": deadline, "status": status, "prioridad": prioridad,
        "comentarios": comentarios, "creado_por": creado_por,
        "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(FILES["pendientes"], index=False)

def update_pendiente(row_id, campo, valor):
    df = get_pendientes()
    df.loc[df["id"] == row_id, campo] = valor
    df.to_csv(FILES["pendientes"], index=False)

def delete_pendiente(row_id):
    df = get_pendientes()
    df = df[df["id"] != row_id]
    df.to_csv(FILES["pendientes"], index=False)

# ── PROCESOS R&S ──────────────────────────────────────────────────────────────

def get_procesos():
    df = pd.read_csv(FILES["procesos"])
    for col in ["inicio_reclutamiento", "fecha_ingreso_plan", "fecha_ingreso_real"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

def add_proceso(data: dict):
    df = get_procesos()
    new_id = int(df["id"].max() + 1) if len(df) > 0 else 1
    data["id"] = new_id
    data["fecha_creacion"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(FILES["procesos"], index=False)
    return new_id

def update_proceso(row_id, updates: dict):
    df = get_procesos()
    for campo, valor in updates.items():
        df.loc[df["id"] == row_id, campo] = valor
    df.to_csv(FILES["procesos"], index=False)

def cerrar_proceso(row_id, seleccionado, fecha_ingreso_real, tipo_cierre, reemplaza=None):
    """Cierra proceso y registra al ingresante/cese automáticamente."""
    df = get_procesos()
    row = df[df["id"] == row_id].iloc[0]

    # Actualizar proceso
    updates = {
        "seleccionado": seleccionado,
        "fecha_ingreso_real": fecha_ingreso_real,
        "tipo_cierre": tipo_cierre,
        "status": "Cerrado",
        "reemplaza": reemplaza or row.get("reemplaza", ""),
    }
    update_proceso(row_id, updates)

    # Registrar ingresante en headcount
    add_headcount({
        "nombre": seleccionado,
        "cargo": row["posicion"],
        "area": row["area"],
        "fecha_ingreso": fecha_ingreso_real,
        "fecha_cese": None,
        "tipo_movimiento": "Ingreso",
        "motivo_cese": None,
        "reemplazado_por": None,
        "activo": True,
        "comentarios": f"Proceso R&S #{row_id}",
    })

    # Si hay reemplazado, registrar cese
    if reemplaza and str(reemplaza).strip() and reemplaza != "NUEVO HC":
        add_cese({
            "nombre": reemplaza,
            "cargo": row["posicion"],
            "area": row["area"],
            "fecha_cese": fecha_ingreso_real,
            "motivo": "Baja (proceso de reemplazo)",
            "reemplazado_por": seleccionado,
            "proceso_id": row_id,
        })
        # Marcar como inactivo en headcount si existe
        hc = get_headcount()
        mask = hc["nombre"].str.lower() == str(reemplaza).lower()
        hc.loc[mask, "activo"] = False
        hc.loc[mask, "fecha_cese"] = fecha_ingreso_real
        hc.to_csv(FILES["headcount"], index=False)

# ── HEADCOUNT ─────────────────────────────────────────────────────────────────

def get_headcount():
    df = pd.read_csv(FILES["headcount"])
    for col in ["fecha_ingreso", "fecha_cese"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

def add_headcount(data: dict):
    df = get_headcount()
    new_id = int(df["id"].max() + 1) if len(df) > 0 else 1
    data["id"] = new_id
    data["fecha_registro"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(FILES["headcount"], index=False)

def get_ceses():
    df = pd.read_csv(FILES["ceses"])
    if "fecha_cese" in df.columns:
        df["fecha_cese"] = pd.to_datetime(df["fecha_cese"], errors="coerce")
    return df

def add_cese(data: dict):
    df = get_ceses()
    new_id = int(df["id"].max() + 1) if len(df) > 0 else 1
    data["id"] = new_id
    data["fecha_registro"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(FILES["ceses"], index=False)

# ── IMPORT EXCEL ──────────────────────────────────────────────────────────────

def import_headcount_excel(uploaded_file):
    """Importa un Excel con columnas libres de headcount de ventas."""
    df = pd.read_excel(uploaded_file)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Mapeo flexible de columnas comunes
    col_map = {
        "nombre": ["nombre", "name", "apellidos_y_nombres", "colaborador"],
        "cargo": ["cargo", "posicion", "position", "puesto"],
        "fecha_ingreso": ["fecha_ingreso", "ingreso", "fecha_de_ingreso", "start_date"],
        "fecha_cese": ["fecha_cese", "cese", "fecha_de_cese", "end_date", "fecha_salida"],
    }

    rename = {}
    for std, options in col_map.items():
        for opt in options:
            if opt in df.columns:
                rename[opt] = std
                break
    df = df.rename(columns=rename)

    hc = get_headcount()
    new_id_start = int(hc["id"].max() + 1) if len(hc) > 0 else 1

    rows = []
    for i, row in df.iterrows():
        nombre = str(row.get("nombre", "")).strip()
        if not nombre or nombre.lower() == "nan":
            continue
        fecha_cese = row.get("fecha_cese")
        activo = pd.isna(fecha_cese) or str(fecha_cese).strip() == ""
        rows.append({
            "id": new_id_start + i,
            "nombre": nombre,
            "cargo": row.get("cargo", "Desarrollador de Ventas"),
            "area": "Ventas",
            "fecha_ingreso": row.get("fecha_ingreso"),
            "fecha_cese": None if activo else fecha_cese,
            "tipo_movimiento": "Ingreso",
            "motivo_cese": row.get("motivo_cese", None),
            "reemplazado_por": None,
            "activo": activo,
            "comentarios": "Importado desde Excel",
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })

    if rows:
        new_df = pd.DataFrame(rows)
        combined = pd.concat([hc, new_df], ignore_index=True)
        combined.to_csv(FILES["headcount"], index=False)

    return len(rows)

# ── EXPORT EXCEL ──────────────────────────────────────────────────────────────

def export_to_excel():
    import io
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment

    wb = Workbook()

    sheets_data = {
        "Pendientes":  get_pendientes(),
        "Procesos R&S": get_procesos(),
        "Headcount":   get_headcount(),
        "Ceses":       get_ceses(),
    }

    first = True
    for name, df in sheets_data.items():
        if first:
            ws = wb.active
            ws.title = name
            first = False
        else:
            ws = wb.create_sheet(name)

        # Header row
        header_fill = PatternFill("solid", start_color="1a1a24", end_color="1a1a24")
        header_font = Font(bold=True, color="C8F04A")
        for col_idx, col_name in enumerate(df.columns, 1):
            cell = ws.cell(row=1, column=col_idx, value=col_name.upper())
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")

        # Data rows
        for row_idx, row in df.iterrows():
            for col_idx, value in enumerate(row, 1):
                cell = ws.cell(row=row_idx + 2, column=col_idx, value=str(value) if pd.notna(value) else "")

        # Auto width
        for col in ws.columns:
            max_len = max((len(str(c.value or "")) for c in col), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer
