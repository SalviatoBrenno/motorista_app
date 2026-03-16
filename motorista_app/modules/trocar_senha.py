import streamlit as st
from database import conectar


def tela_trocar_senha():

    conn, cursor = conectar()

    st.title("🔑 Trocar senha obrigatória")

    nova_senha = st.text_input("Nova senha", type="password")
    confirmar = st.text_input("Confirmar senha", type="password")

    if st.button("Salvar nova senha"):

        if not nova_senha or not confirmar:
            st.error("Preencha os campos")

        elif nova_senha != confirmar:
            st.error("As senhas não conferem")

        else:

            cursor.execute(
                """
                UPDATE usuarios
                SET senha=?, trocar_senha=0
                WHERE cpf=?
                """,
                (nova_senha, st.session_state.cpf)
            )

            conn.commit()

            st.session_state.trocar_senha = 0

            st.success("Senha alterada com sucesso")
            st.rerun()