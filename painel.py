import streamlit as st
import pandas as pd
import sqlite3
import os

CAMINHO_BANCO = r"C:\Users\r958351\OneDrive - voestalpine\CONTROLES\reserva\reservas.db"

st.title("📊 Painel de Reservas - Chefia")

if not os.path.exists(CAMINHO_BANCO):
    st.warning("⚠️ Nenhuma reserva encontrada ainda!")
else:
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        df = pd.read_sql_query("SELECT * FROM reservas", conexao)
        conexao.close()

        df["data"] = pd.to_datetime(df["data"]).dt.date

        # Comentei o filtro para testar a exibição direta
        # data_filtro = st.date_input("📅 Filtrar por data (opcional)", value=None)

        # if data_filtro:
        #     df = df[df["data"] == data_filtro]

        if df.empty:
            st.warning("⚠️ Nenhuma reserva para a data selecionada.")
        else:
            st.write("🔍 Reservas encontradas:")
            st.dataframe(df)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Baixar CSV", data=csv, file_name="resumo_reservas.csv", mime='text/csv')

    except Exception as e:
        st.error(f"Erro ao acessar o banco de dados: {e}")
