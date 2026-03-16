import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
from database import conectar

ADMIN_CPFS = ["10808560646"]

def tela_analise():

    conn, cursor = conectar()

    st.subheader("📈 Análises")

    # =========================
    # BUSCAR DADOS
    # =========================
    if st.session_state.cpf in ADMIN_CPFS:
        df = pd.read_sql_query("SELECT * FROM corridas", conn)
    else:
        df = pd.read_sql_query(
            "SELECT * FROM corridas WHERE cpf=?",
            conn,
            params=(st.session_state.cpf,)
        )

    if df.empty:
        st.info("Sem dados ainda")
        return

    # =========================
    # PREPARAR DADOS
    # =========================
    df["data"] = pd.to_datetime(df["data"])
    df["dia_semana"] = df["data"].dt.day_name()
    df["mes"] = df["data"].dt.month
    df["ano"] = df["data"].dt.year

    mapa_dias = {
        "Monday": "Segunda-feira",
        "Tuesday": "Terça-feira",
        "Wednesday": "Quarta-feira",
        "Thursday": "Quinta-feira",
        "Friday": "Sexta-feira",
        "Saturday": "Sábado",
        "Sunday": "Domingo",
    }

    mapa_meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    # =========================
    # ANÁLISE GERAL
    # =========================
    lucro_total = df["lucro"].sum()
    total_corridas = df["corridas"].sum()
    lucro_medio_corrida = lucro_total / total_corridas if total_corridas else 0

    melhor_dia = mapa_dias[
        df.groupby("dia_semana")["lucro"].sum().idxmax()
    ]
    melhor_mes = mapa_meses[
        df.groupby("mes")["lucro"].sum().idxmax()
    ]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Maior lucro", f"R$ {lucro_total:,.2f}")
    col2.metric("🚗 Lucro Médio/Corrida", f"R$ {lucro_medio_corrida:.2f}")
    col3.metric("📅 Melhor Dia", melhor_dia)
    col4.metric("🏆 Melhor Mês", melhor_mes)

    st.divider()

    # =========================
    # ANÁLISE MÊS ATUAL
    # =========================
    hoje = datetime.now()
    df_mes = df[df["data"].dt.month == hoje.month]

    lucro_total_mes = df_mes["lucro"].sum()
    total_corridas_mes = df_mes["corridas"].sum()
    lucro_medio_corrida_mes = lucro_total_mes / total_corridas_mes if total_corridas_mes else 0

    melhor_dia_mes = mapa_dias[
        df_mes.groupby("dia_semana")["lucro"].sum().idxmax()
    ] if not df_mes.empty else "-"

    melhor_mes_atual = mapa_meses[hoje.month]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Lucro Total", f"R$ {lucro_total_mes:,.2f}")
    col2.metric("🚗 Lucro Médio/Corrida", f"R$ {lucro_medio_corrida_mes:.2f}")
    col3.metric("📅 Melhor Dia", melhor_dia_mes)
    col4.metric("🏆 Mês Atual", melhor_mes_atual)

    st.divider()

    # =========================
    # ANÁLISE SEMANA ATUAL
    # =========================
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    # CORREÇÃO: remover HTML escape e usar >= corretamente
    df_semana = df[df["data"].dt.date >= inicio_semana.date()]

    lucro_total_semana = df_semana["lucro"].sum()
    total_corridas_semana = df_semana["corridas"].sum()
    lucro_medio_corrida_semana = lucro_total_semana / total_corridas_semana if total_corridas_semana else 0

    melhor_dia_semana = mapa_dias[
        df_semana.groupby("dia_semana")["lucro"].sum().idxmax()
    ] if not df_semana.empty else "-"

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Lucro Total", f"R$ {lucro_total_semana:,.2f}")
    col2.metric("🚗 Lucro Médio/Corrida", f"R$ {lucro_medio_corrida_semana:.2f}")
    col3.metric("📅 Melhor Dia", melhor_dia_semana)

    st.divider()

    # =========================
    # GRÁFICOS
    # =========================
    st.subheader("📊 Ganhos vs Lucro")

    # ---------- Função auxiliar: barras separadas + labels + ajustes ----------
    def bar_chart_with_labels_grouped_sorted(data, x_cat, fold_cols, x_title, y_title="Valor (R$)"):
        """
        Gráfico de barras agrupadas (valor vs lucro) com:
        - Barras separadas (xOffset por Tipo)
        - Label de dados "R$"
        - Eixo X legível (sem truncar nomes)
        - Ordenação decrescente por 'valor' (usa campo 'ordem' no DataFrame)
        """
        base = (
            alt.Chart(data)
            .transform_fold(fold_cols, as_=["Tipo", "Valor"])
            .transform_calculate(Label='\"R$ \" + format(datum.Valor, ",.2f")')
        )

        bars = base.mark_bar().encode(
            x=alt.X(
                f"{x_cat}:N",
                title=x_title,
                # Ordena pelo campo de apoio 'ordem' (desc)
                sort=alt.SortField(field="ordem", order="descending"),
                axis=alt.Axis(
                    labelAngle=0,       # se precisar, troque para -20
                    labelLimit=260,
                    labelOverlap=False
                )
            ),
            xOffset=alt.X("Tipo:N"),  # barras lado a lado por tipo
            y=alt.Y("Valor:Q", title=y_title),
            color=alt.Color(
                "Tipo:N",
                title="",
                scale=alt.Scale(domain=["valor", "lucro"], range=["#eb0b0b", "#10db10"])  # vermelho/verde
            ),
            tooltip=[
                alt.Tooltip(f"{x_cat}:N", title=x_title),
                alt.Tooltip("Tipo:N", title="Tipo"),
                alt.Tooltip("Valor:Q", title="Valor", format=",.2f")
            ]
        )

        labels = base.mark_text(
            align="center", baseline="bottom", dy=-4, fontSize=12, color="black"
        ).encode(
            x=alt.X(
                f"{x_cat}:N",
                sort=alt.SortField(field="ordem", order="descending")
            ),
            xOffset=alt.X("Tipo:N"),
            y=alt.Y("Valor:Q"),
            text=alt.Text("Label:N")
        )

        return (bars + labels).properties(
            height=360,
            padding={"top": 36, "right": 8, "bottom": 18, "left": 8}
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=12
        ).configure_view(
            stroke=None
        )

    # -------------------------
    # Ganhos por Dia da Semana — ORDENADO por maior 'valor'
    # -------------------------
    ordem_dias_en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df_dia = (
        df.groupby("dia_semana")[["valor", "lucro"]]
          .sum()
          .reindex(ordem_dias_en)              # mantém todas as categorias
          .rename(index=mapa_dias)
          .reset_index()
          .rename(columns={"index": "Dia", "dia_semana": "Dia"})
    )
    df_dia["ordem"] = df_dia["valor"]  # campo para ordenar por valor
    chart_dia = bar_chart_with_labels_grouped_sorted(
        df_dia, x_cat="Dia", fold_cols=["valor", "lucro"], x_title="Dia da Semana"
    )
    st.altair_chart(chart_dia, use_container_width=True)  # <-- 1º gráfico

    # ---------------
    # Ganhos por Mês — ORDENADO por maior 'valor'
    # ---------------
    df_mes_chart = (
        df.groupby("mes")[["valor", "lucro"]]
          .sum()
          .reset_index()
    )
    df_mes_chart["Mês"] = df_mes_chart["mes"].map(mapa_meses)
    df_mes_chart = df_mes_chart.drop(columns=["mes"])
    df_mes_chart["ordem"] = df_mes_chart["valor"]
    chart_mes = bar_chart_with_labels_grouped_sorted(
        df_mes_chart, x_cat="Mês", fold_cols=["valor", "lucro"], x_title="Mês"
    )
    st.altair_chart(chart_mes, use_container_width=True)  # <-- 2º gráfico

    # ----------------
    # Ganhos por Ano — ORDENADO por maior 'valor'
    # ----------------
    df_ano_chart = (
        df.groupby("ano")[["valor", "lucro"]]
          .sum()
          .reset_index()
          .rename(columns={"ano": "Ano"})
    )
    df_ano_chart["ordem"] = df_ano_chart["valor"]
    chart_ano = bar_chart_with_labels_grouped_sorted(
        df_ano_chart, x_cat="Ano", fold_cols=["valor", "lucro"], x_title="Ano"
    )
    st.altair_chart(chart_ano, use_container_width=True)  # <-- 3º gráfico (embaixo)
