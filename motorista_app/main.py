import streamlit as st

st.set_page_config(
    page_title="Controle Motorista",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from login import verificar_login
from modules.controle import tela_controle
from modules.analise import tela_analise
from modules.admin import tela_admin
from modules.trocar_senha import tela_trocar_senha

verificar_login()

ADMIN_CPFS = ["10808560646"]

# verificar troca de senha
if st.session_state.get("trocar_senha") == 1:
    tela_trocar_senha()
    st.stop()

st.title("🚗 Controle Motorista")

if st.session_state.cpf in ADMIN_CPFS:

    tab1,tab2,tab3 = st.tabs(["🚗 Controle","📈 Análises","👑 Admin"])

    with tab1:
        tela_controle()

    with tab2:
        tela_analise()

    with tab3:
        tela_admin()

else:

    tab1,tab2 = st.tabs(["🚗 Controle","📈 Análises"])

    with tab1:
        tela_controle()

    with tab2:
        tela_analise()
