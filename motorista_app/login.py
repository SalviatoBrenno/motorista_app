import streamlit as st
from database import conectar

# CPF ADMIN
ADMIN_CPFS = ["10808560646"]

def formatar_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, cpf))

    if len(cpf) <= 3:
        return cpf
    elif len(cpf) <= 6:
        return f"{cpf[:3]}.{cpf[3:]}"
    elif len(cpf) <= 9:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:]}"
    else:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"


def verificar_login():

    conn, cursor = conectar()

    if "logado" not in st.session_state:
        st.session_state.logado = False

    if st.session_state.logado:
        return

    st.title("🔐 Login Motorista")

    tab1, tab2 = st.tabs(["Entrar", "Cadastrar"])

    # =========================
    # LOGIN
    # =========================
    with tab1:

        cpf_login = st.text_input("CPF", key="cpf_login")
        senha_login = st.text_input("Senha", type="password", key="senha_login")

        if cpf_login:
            st.caption(f"CPF: {formatar_cpf(cpf_login)}")

        if st.button("Entrar"):

            cpf_login = ''.join(filter(str.isdigit, cpf_login))

            if not cpf_login or not senha_login:
                st.error("Informe CPF e senha")

            else:

                usuario = cursor.execute(
                    """
                    SELECT nome, liberado, trocar_senha
                    FROM usuarios
                    WHERE cpf=? AND senha=?
                    """,
                    (cpf_login, senha_login)
                ).fetchone()

                if usuario:

                    nome, liberado, trocar_senha = usuario

                    if liberado == 0 and cpf_login not in ADMIN_CPFS:
                        st.error("Usuário aguardando liberação")
                        st.stop()

                    st.session_state.logado = True
                    st.session_state.cpf = cpf_login
                    st.session_state.usuario_nome = nome
                    st.session_state.trocar_senha = trocar_senha

                    st.success("Login realizado")
                    st.rerun()

                else:
                    st.error("CPF ou senha incorretos")

    # =========================
    # CADASTRO
    # =========================
    with tab2:

        nome_cadastro = st.text_input("Nome", key="nome_cadastro")
        cpf_cadastro = st.text_input("CPF", key="cpf_cadastro")

        if cpf_cadastro:
            st.caption(f"CPF: {formatar_cpf(cpf_cadastro)}")

        if st.button("Cadastrar"):

            cpf_cadastro = ''.join(filter(str.isdigit, cpf_cadastro))

            if not nome_cadastro or not cpf_cadastro:
                st.error("Preencha todos os campos")

            elif len(cpf_cadastro) != 11:
                st.error("CPF deve ter 11 números")

            else:

                try:

                    senha_automatica = cpf_cadastro[:6]

                    liberado = 1 if cpf_cadastro in ADMIN_CPFS else 0

                    cursor.execute(
                        """
                        INSERT INTO usuarios (nome,cpf,senha,liberado,trocar_senha)
                        VALUES (?,?,?,?,?)
                        """,
                        (nome_cadastro, cpf_cadastro, senha_automatica, liberado, 1)
                    )

                    conn.commit()

                    st.success(
                        f"""
                        Cadastro realizado!

                        Senha inicial: {senha_automatica}

                        Aguarde liberação do administrador.
                        """
                    )

                except Exception as e:

                    if "UNIQUE" in str(e).upper():
                        st.error("CPF já cadastrado")
                    else:
                        st.error(f"Erro ao cadastrar: {e}")

    st.stop()