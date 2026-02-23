# Contraseñas — cámbialas antes de deployar
USERS = {
    "Ariana": "supply2024",
    "Jefa":   "jefa2024",
}

def check_login(usuario: str, password: str) -> bool:
    if usuario == "Selecciona...":
        return False
    return USERS.get(usuario) == password

def get_current_user():
    import streamlit as st
    return st.session_state.get("usuario", "")
