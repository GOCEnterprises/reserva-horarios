import streamlit as st
import pandas as pd
import os

# Caminho para o arquivo CSV
csv_path = os.path.join("C:/Users/r958351/OneDrive - voestalpine/CONTROLES/reserva", "reservas.csv")

# Título do painel
st.title("📊 Painel de Reservas - Chefia")

# Verifica se o arquivo existe
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)

    # Converte a coluna "Data" para apenas a data (sem hora)
    df["Data"] = pd.to_datetime(df["Data"]).dt.date

    # Filtro por data
    data_filtro = st.date_input("Filtrar por data (opcional)")

    if data_filtro:
        df_filtrado = df[df["Data"] == data_filtro]
        if not df_filtrado.empty:
            st.subheader(f"📅 Reservas para {data_filtro.strftime('%d/%m/%Y')}")
            st.dataframe(df_filtrado)
        else:
            st.warning("⚠️ Nenhuma reserva para a data selecionada.")
    else:
        st.subheader("📋 Todas as Reservas")
        st.dataframe(df)

    # Botão para download do CSV filtrado
    if not df.empty:
        csv_export = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Baixar todas as reservas em CSV",
            data=csv_export,
            file_name="reservas_completas.csv",
            mime="text/csv"
        )

else:
    st.warning("⚠️ Nenhuma reserva encontrada ainda!")

