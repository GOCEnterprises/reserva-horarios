import streamlit as st
import pandas as pd
import os
from datetime import datetime

ARQUIVO_CSV = "reservas.csv"

st.set_page_config(page_title="Painel da Chefia", layout="wide")
st.title("Painel da Chefia - Reservas ADM")

# Verifica se o arquivo existe
if not os.path.exists(ARQUIVO_CSV):
    st.error("Nenhuma reserva encontrada ainda!")
else:
    # Lê o CSV
    df = pd.read_csv(ARQUIVO_CSV)

    # Converte a coluna de data para datetime
    df['Data'] = pd.to_datetime(df['Data'], format="%Y-%m-%d")

    # Filtros
    st.sidebar.header("Filtros")

    data_inicio = st.sidebar.date_input("Data inicial", value=df["Data"].min().date())
    data_fim = st.sidebar.date_input("Data final", value=df["Data"].max().date())

    # Aplica os filtros
    df_filtrado = df[(df["Data"] >= pd.to_datetime(data_inicio)) & (df["Data"] <= pd.to_datetime(data_fim))]

    if df_filtrado.empty:
        st.warning("Nenhuma reserva encontrada nesse período.")
    else:
        st.subheader("Reservas encontradas")

        # Mostra a tabela
        st.dataframe(df_filtrado.sort_values(by=["Data", "Horario"]))

        # Contagem por horário
        st.subheader("Total de reservas por horário")
        grafico = df_filtrado.groupby("Horario").size().reset_index(name="Total de Reservas")
        st.bar_chart(data=grafico, x="Horario", y="Total de Reservas")

        # Exportar
        st.subheader("Exportar reservas")
        csv_exportado = df_filtrado.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar CSV filtrado", data=csv_exportado, file_name="reservas_filtradas.csv", mime="text/csv")
