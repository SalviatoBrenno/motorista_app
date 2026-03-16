import streamlit as st
import pandas as pd
from database import conectar


def formatar_cpf(cpf):
    cpf = str(cpf)

    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf


def tela_admin():

    conn, cursor = conectar()

    st.subheader("👑 Painel Admin")

    usuarios = pd.read_sql_query(
        "SELECT id,nome,cpf,liberado FROM usuarios",
        conn
    )

    st.divider()

    for i, row in usuarios.iterrows():

        col1, col2, col3, col4, col5 = st.columns([2,2,2,1,1])

        col1.write(row["nome"])
        col2.write(formatar_cpf(row["cpf"]))

        status = "🟢 Liberado" if row["liberado"] else "🔴 Bloqueado"
        col3.write(status)

        # -------------------------
        # LIBERAR
        # -------------------------
        if row["liberado"] == 0:

            if col4.button("Liberar", key=f"lib_{row['id']}"):

                cursor.execute(
                    "UPDATE usuarios SET liberado=1 WHERE id=?",
                    (row["id"],)
                )

                conn.commit()
                st.rerun()

        # -------------------------
        # BLOQUEAR
        # -------------------------
        else:

            if col4.button("Bloquear", key=f"bloq_{row['id']}"):

                cursor.execute(
                    "UPDATE usuarios SET liberado=0 WHERE id=?",
                    (row["id"],)
                )

                conn.commit()
                st.rerun()

        # -------------------------
        # EXCLUIR
        # -------------------------

        if col5.button("Excluir", key=f"del_{row['id']}"):

            cursor.execute(
                "DELETE FROM usuarios WHERE id=?",
                (row["id"],)
            )

            conn.commit()
            st.warning("Usuário excluído")
            st.rerun()

        st.divider()