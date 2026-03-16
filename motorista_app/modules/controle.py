import streamlit as st
import pandas as pd
from datetime import datetime
from database import conectar

ADMIN_CPFS = ["10808560646"]

def tela_controle():

    conn, cursor = conectar()

    st.divider()

    # =========================
    # RESUMO
    # =========================

    if st.session_state.cpf in ADMIN_CPFS:
        df_resumo = pd.read_sql_query(
            "SELECT * FROM corridas",
            conn
        )
    else:
        df_resumo = pd.read_sql_query(
            "SELECT * FROM corridas WHERE cpf=?",
            conn,
            params=(st.session_state.cpf,)
        )

    if not df_resumo.empty:

        df_resumo["data"] = pd.to_datetime(df_resumo["data"])

        valor_total = df_resumo["valor"].sum()
        taxa_total = df_resumo["taxa"].sum()
        lucro_total = df_resumo["lucro"].sum()

        df_resumo["dia_semana"] = df_resumo["data"].dt.day_name()

        mapa_dias = {
            "Monday":"Segunda-feira",
            "Tuesday":"Terça-feira",
            "Wednesday":"Quarta-feira",
            "Thursday":"Quinta-feira",
            "Friday":"Sexta-feira",
            "Saturday":"Sábado",
            "Sunday":"Domingo"
        }

        melhor_dia = (
            df_resumo.groupby("dia_semana")["lucro"]
            .sum()
            .sort_values(ascending=False)
            .index[0]
        )

        melhor_dia = mapa_dias[melhor_dia]

        df_resumo["mes"] = df_resumo["data"].dt.month

        mapa_meses = {
            1:"Janeiro",
            2:"Fevereiro",
            3:"Março",
            4:"Abril",
            5:"Maio",
            6:"Junho",
            7:"Julho",
            8:"Agosto",
            9:"Setembro",
            10:"Outubro",
            11:"Novembro",
            12:"Dezembro"
        }

        melhor_mes_num = (
            df_resumo.groupby("mes")["lucro"]
            .sum()
            .sort_values(ascending=False)
            .index[0]
        )

        melhor_mes = mapa_meses[melhor_mes_num]

        col1,col2,col3,col4,col5 = st.columns(5)

        col1.metric("💰 Valor Bruto", f"R$ {valor_total:,.2f}")
        col2.metric("📉 Taxa Total App", f"R$ {taxa_total:,.2f}")
        col3.metric("💵 Lucro Líquido", f"R$ {lucro_total:,.2f}")
        col4.metric("📅 Melhor Dia", melhor_dia)
        col5.metric("🏆 Melhor Mês", melhor_mes)

    st.divider()

    # =========================
    # SESSION STATE
    # =========================

    if "edit_id" not in st.session_state:
        st.session_state.edit_id = None

    if "load_data" not in st.session_state:
        st.session_state.load_data = None

    if "motorista" not in st.session_state:
        st.session_state.motorista = ""

    if "km" not in st.session_state:
        st.session_state.km = None

    if "corridas" not in st.session_state:
        st.session_state.corridas = None

    if "valor" not in st.session_state:
        st.session_state.valor = None

    if "despesas_extras" not in st.session_state:
        st.session_state.despesas_extras = None

    if "gasolina" not in st.session_state:
        st.session_state.gasolina = None

    if "tipo_pagamento" not in st.session_state:
        st.session_state.tipo_pagamento = "Semanal"

    if "data_corrida" not in st.session_state:
        st.session_state.data_corrida = datetime.now()

    # =========================
    # CARREGAR REGISTRO
    # =========================

    if st.session_state.load_data:

        data = st.session_state.load_data

        st.session_state.edit_id = data["id"]
        st.session_state.motorista = data["motorista"]
        st.session_state.km = data["km"]
        st.session_state.corridas = data["corridas"]
        st.session_state.valor = data["valor"]
        st.session_state.despesas_extras = data["despesas_extras"]
        st.session_state.gasolina = data["gasolina"]
        st.session_state.tipo_pagamento = data["tipo_pagamento"]
        st.session_state.data_corrida = pd.to_datetime(data["data"])

        st.session_state.load_data = None

    # =========================
    # LIMPAR FORM
    # =========================

    def limpar_form():
        for key in list(st.session_state.keys()):
            if key not in ["logado","cpf","usuario_nome","trocar_senha"]:
                del st.session_state[key]
        st.rerun()

    # =========================
    # CAMPOS
    # =========================

    #motorista = st.text_input("Motorista", key="motorista")
    motorista = st.text_input(
        "Motorista",
        value=st.session_state.usuario_nome,
        disabled=True
    )

    data_corrida = st.date_input(
        "📅 Data da corrida",
        key="data_corrida"
    )

    tipo_pagamento = st.selectbox(
        "Tipo de cobrança do app",
        ["Semanal","Corrida"],
        key="tipo_pagamento"
    )

    col1,col2,col3 = st.columns(3)

    with col1:
        km = st.number_input("KM", min_value=0.0, key="km")

    with col2:
        corridas = st.number_input("Corridas", min_value=0, key="corridas")

    with col3:
        valor = st.number_input("Valor ganho", min_value=0.0, key="valor")

    col1,col2 = st.columns(2)

    with col1:
        despesas_extras = st.number_input("Despesas Extras", min_value=0.0, key="despesas_extras")

    with col2:
        gasolina = st.number_input("Gasolina", min_value=0.0, key="gasolina")

    # correção para campos vazios
    km = km or 0
    corridas = corridas or 0
    valor = valor or 0
    gasolina = gasolina or 0
    despesas_extras = despesas_extras or 0

    #valor_km = valor/km if km and km>0 else 0
    valor_km = (valor/km) if km and valor and km > 0 else 0

    if tipo_pagamento == "Semanal":
        taxa = 15 + (corridas * 0.95) + (valor * 0.05)
    else:
        taxa = (corridas * 2) + (valor * 0.05)

    lucro = valor - gasolina - despesas_extras - taxa

    col1,col2,col3 = st.columns(3)

    col1.metric("💰 Valor/KM", f"R$ {valor_km:.2f}")
    col2.metric("📉 Taxa App", f"R$ {taxa:.2f}")
    col3.metric("📈 Lucro", f"R$ {lucro:.2f}")

    st.divider()

    # =========================
    # BOTÕES
    # =========================

    col1,col2,col3,col4 = st.columns(4)

    with col1:
        if st.button("💾 Salvar"):

            cursor.execute("""
                INSERT INTO corridas
                (cpf,motorista,data,tipo_pagamento,km,corridas,valor,gasolina,despesas_extras,valor_km,taxa,lucro)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """,(
            st.session_state.cpf,
            motorista,
            str(data_corrida),
            tipo_pagamento,
            km,
            corridas,
            valor,
            gasolina,
            despesas_extras,
            valor_km,
            taxa,
            lucro
            ))

            conn.commit()
            st.success("Registro salvo")
            limpar_form()

    with col2:
        if st.button("✏️ Alterar") and st.session_state.edit_id:

            cursor.execute("""
            UPDATE corridas
            SET motorista=?,data=?,tipo_pagamento=?,km=?,corridas=?,valor=?,gasolina=?,despesas_extras=?,valor_km=?,taxa=?,lucro=?
            WHERE id=?
            """,(
            motorista,
            str(data_corrida),
            tipo_pagamento,
            km,
            corridas,
            valor,
            gasolina,
            despesas_extras,
            valor_km,
            taxa,
            lucro,
            st.session_state.edit_id
            ))

            conn.commit()
            st.success("Registro alterado")
            limpar_form()

    with col3:
        if st.button("🗑️ Excluir") and st.session_state.edit_id:

            cursor.execute(
                "DELETE FROM corridas WHERE id=?",
                (st.session_state.edit_id,)
            )

            conn.commit()
            st.warning("Registro excluído")
            limpar_form()

    with col4:
        if st.button("🔄 Limpar"):
            limpar_form()

    st.divider()

    # =========================
    # HISTÓRICO
    # =========================

    st.subheader("📊 Histórico")

    if st.session_state.cpf in ADMIN_CPFS:
        df = pd.read_sql_query(
            "SELECT * FROM corridas ORDER BY data DESC",
            conn
        )
    else:
        df = pd.read_sql_query(
            "SELECT * FROM corridas WHERE cpf=? ORDER BY data DESC",
            conn,
            params=(st.session_state.cpf,)
        )

    if not df.empty:

        for i,row in df.iterrows():

            col1,col2,col3,col4,col5,col6,col7,col8,col9,col10, col11 = st.columns(11)

            col1.write(row["id"])
            col2.write(row["motorista"])
            col3.write(row["data"])
            col4.write(row["tipo_pagamento"])
            col5.write(row["km"])
            col6.write(row["corridas"])
            col7.write(row["valor"])
            col8.write(row["gasolina"])
            col9.write(row["despesas_extras"])
            col10.write(row["lucro"])

            if col11.button("Editar", key=f"edit_{row['id']}"):

                st.session_state.load_data = row.to_dict()
                st.rerun()