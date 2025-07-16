import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

CAMINHO_PLANILHA = r"C:\Users\r958351\OneDrive - voestalpine\CONTROLES\reserva\Controle de Vagas Refeitorio1.xlsx"
HORARIOS = ['10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30']
VAGAS_POR_HORARIO = 100

st.title("📅 Formulário de Reserva de Horário")

matricula = st.text_input("Matrícula")
nome = st.text_input("Nome")
departamento = st.text_input("Departamento")
email = st.text_input("Email")
opcao_semana = st.checkbox("Reservar a semana toda no mesmo horário?")

# Gerar datas disponíveis a partir de amanhã (dias úteis)
def dias_uteis_a_partir_de_amanha(qtd=5):
    hoje = datetime.now().date()
    datas = []
    dia = hoje + timedelta(days=1)
    while len(datas) < qtd:
        if dia.weekday() < 5:
            datas.append(dia)
        dia += timedelta(days=1)
    return datas

dias = dias_uteis_a_partir_de_amanha()

if opcao_semana:
    data_selecionada = dias  # todas as datas úteis
else:
    data_unica = st.date_input("Escolha o dia da reserva", dias[0], min_value=dias[0], max_value=dias[-1])
    data_selecionada = [data_unica]

horario = st.radio("Horário", HORARIOS)
botao = st.button("Reservar")

def ler_reservas():
    if os.path.exists(CAMINHO_PLANILHA):
        return pd.read_excel(CAMINHO_PLANILHA)
    return pd.DataFrame(columns=["Matrícula", "Nome", "Departamento", "Email", "Horário", "Data"])

def salvar_reservas(df):
    df.to_excel(CAMINHO_PLANILHA, index=False)

def contar_reservas_por_horario(data):
    df = ler_reservas()
    contagem = df[df['Data'] == pd.to_datetime(data)].groupby("Horário").size().to_dict()
    return contagem

def ja_tem_reserva(matricula, data):
    df = ler_reservas()
    return not df[(df["Matrícula"] == matricula) & (df["Data"] == pd.to_datetime(data))].empty

if botao:
    if not all([matricula, nome, departamento, email]):
        st.warning("⚠️ Por favor, preencha todos os campos antes de reservar.")
    else:
        df_existente = ler_reservas()
        novas_reservas = []
        ja_reservados = []

        for data in data_selecionada:
            reservas_no_dia = contar_reservas_por_horario(data).get(horario, 0)

            if reservas_no_dia >= VAGAS_POR_HORARIO:
                ja_reservados.append(str(data))
                continue

            if ja_tem_reserva(matricula, data):
                ja_reservados.append(str(data))
                continue

            novas_reservas.append({
                "Matrícula": matricula,
                "Nome": nome,
                "Departamento": departamento,
                "Email": email,
                "Horário": horario,
                "Data": data
            })

        if novas_reservas:
            df_atualizado = pd.concat([df_existente, pd.DataFrame(novas_reservas)], ignore_index=True)
            salvar_reservas(df_atualizado)
            datas_confirmadas = ", ".join([str(r["Data"]) for r in novas_reservas])
            st.success(f"✅ Reservas confirmadas para os dias: {datas_confirmadas} no horário {horario}.")
        if ja_reservados:
            dias_negados = ", ".join(ja_reservados)
            st.warning(f"⚠️ Você já tinha reserva ou o horário está lotado nos dias: {dias_negados}. Estes não foram reservados novamente.")
