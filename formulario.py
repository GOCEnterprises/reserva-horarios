import streamlit as st
import csv
import os
from datetime import datetime, timedelta

# Caminho completo do arquivo no OneDrive
ARQUIVO_CSV = r"C:\Users\r958351\OneDrive - voestalpine\CONTROLES\reserva\reservas.csv"

# Cria o arquivo se ele não existir
if not os.path.exists(ARQUIVO_CSV):
    with open(ARQUIVO_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Matrícula", "Nome", "Departamento", "Email", "Horário", "Data"])

st.title("Reserva de Horário")

matricula = st.text_input("Matrícula")
nome = st.text_input("Nome")
departamento = st.text_input("Departamento")
email = st.text_input("Email")

# Selecionar um único dia ou semana inteira
modo_semana = st.checkbox("Reservar a semana toda (mesmo horário todos os dias úteis)")

# Gera horários de 10:00 às 13:30 (de 30 em 30 min)
horarios = [f"{h:02d}:{m:02d}" for h in range(10, 14) for m in (0, 30)]
horario_escolhido = st.selectbox("Escolha o horário", horarios)

# Gera a(s) data(s)
hoje = datetime.now().date()
amanha = hoje + timedelta(days=1)

# Verifica se o usuário escolheu reservar a semana toda
if modo_semana:
    datas_selecionadas = [
        amanha + timedelta(days=i) for i in range(7)
        if (amanha + timedelta(days=i)).weekday() < 5  # Só dias úteis
    ]
else:
    data_unica = st.date_input("Escolha a data", amanha, min_value=amanha)
    datas_selecionadas = [data_unica]

def carregar_reservas():
    if not os.path.exists(ARQUIVO_CSV):
        return []
    with open(ARQUIVO_CSV, mode='r', encoding='utf-8') as f:
        return list(csv.reader(f))[1:]

def salvar_reserva(matricula, nome, depto, email, horario, data):
    with open(ARQUIVO_CSV, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([matricula, nome, depto, email, horario, data])

def contar_reservas(data, horario):
    reservas = carregar_reservas()
    return sum(1 for r in reservas if r[4] == horario and r[5] == str(data))

if st.button("Reservar"):
    if not all([matricula, nome, departamento, email]):
        st.warning("Por favor, preencha todos os campos antes de reservar.")
    else:
        reservas = carregar_reservas()
        datas_confirmadas = []
        datas_recusadas = []

        for data in datas_selecionadas:
            ja_reservou = any(r[0] == matricula and r[5] == str(data) for r in reservas)
            if ja_reservou:
                datas_recusadas.append(data)
            elif contar_reservas(data, horario_escolhido) >= 100:
                datas_recusadas.append(data)
            else:
                salvar_reserva(matricula, nome, departamento, email, horario_escolhido, data)
                datas_confirmadas.append(data)

        if datas_confirmadas:
            st.success(f"Reservas confirmadas para os dias: {', '.join(str(d) for d in datas_confirmadas)} no horário {horario_escolhido}.")
        if datas_recusadas:
            st.error(f"Você já tinha reserva ou o horário estava cheio nos dias: {', '.join(str(d) for d in datas_recusadas)}.")
