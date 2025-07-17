import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import date

CAMINHO_DB = r"C:\Users\r958351\OneDrive - voestalpine\CONTROLES\reserva\reservas.db"

st.set_page_config(page_title="Painel de Reservas - Chefia", layout="centered")
st.title("📊 Painel de Reservas - Chefia")

if not os.path.exists(CAMINHO_DB):
    st.warning("⚠️ Nenhuma reserva encontrada ainda!")
else:
    conn = sqlite3.connect(CAMINHO_DB)
    df = pd.read_sql_query("SELECT * FROM reservas", conn)
    conn.close()

    if df.empty:
        st.warning("⚠️ Nenhuma reserva encontrada no banco de dados.")
    else:
        df["Data"] = pd.to_datetime(df["data"]).dt.date
        df = df.drop(columns=["id"])  # opcional: remove o ID

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
