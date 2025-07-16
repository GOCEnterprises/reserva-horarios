import streamlit as st
import pandas as pd
import os

CAMINHO_PLANILHA = r"C:\Users\r958351\OneDrive - voestalpine\CONTROLES\reserva\Controle de Vagas Refeitorio1.xlsx"

st.title("📊 Painel de Reservas - Chefia")

if not os.path.exists(CAMINHO_PLANILHA):
    st.warning("⚠️ Nenhuma reserva encontrada ainda!")
else:
    df = pd.read_excel(CAMINHO_PLANILHA)
    df["Data"] = pd.to_datetime(df["Data"]).dt.date

    data_filtro = st.date_input("📅 Filtrar por data (opcional)", value=None)

    if data_filtro:
        df = df[df["Data"] == data_filtro]

    if df.empty:
        st.warning("⚠️ Nenhuma reserva para a data selecionada.")
    else:
        st.write("🔍 Reservas encontradas:")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Baixar CSV", data=csv, file_name="resumo_reservas.csv", mime='text/csv')
