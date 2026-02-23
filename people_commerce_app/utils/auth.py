# Contraseñas — cámbialas antes de deployar
USERS = {
    "HRBP Intern": "hrbp2024",
    "Business Partner": "commerce2024",
}

def check_login(usuario: str, password: str) -> bool:
    if usuario == "Selecciona...":
        return False
    return USERS.get(usuario) == password

def get_current_user():
    import streamlit as st
    return st.session_state.get("usuario", "")
