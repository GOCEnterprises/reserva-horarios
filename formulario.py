import streamlit as st
import csv
import os
from datetime import datetime, timedelta

ARQUIVO_CSV = "reservas.csv"

# Função para garantir que o arquivo exista
def criar_arquivo_se_nao_existir():
    if not os.path.exists(ARQUIVO_CSV):
        with open(ARQUIVO_CSV, mode='w', newline='', encoding='utf-8') as arquivo:
            writer = csv.writer(arquivo)
            writer.writerow(["Matricula", "Nome", "Departamento", "Email", "Horario", "Data"])

def verificar_reserva_existente(matricula, data):
    if not os.path.exists(ARQUIVO_CSV):
        return False
    with open(ARQUIVO_CSV, mode='r', encoding='utf-8') as arquivo:
        reader = csv.reader(arquivo)
        next(reader)
        for linha in reader:
            mat_lida, _, _, _, _, data_lida = linha
            if mat_lida == matricula and data_lida == data:
                return True
    return False

def contar_reservas(horario, data):
    if not os.path.exists(ARQUIVO_CSV):
        return 0
    count = 0
    with open(ARQUIVO_CSV, mode='r', encoding='utf-8') as arquivo:
        reader = csv.reader(arquivo)
        next(reader)
        for linha in reader:
            _, _, _, _, horario_lido, data_lida = linha
            if horario_lido == horario and data_lida == data:
                count += 1
    return count

def gerar_horarios():
    horarios = []
    hora = datetime.strptime("10:00", "%H:%M")
    fim = datetime.strptime("13:30", "%H:%M")
    while hora <= fim:
        horarios.append(hora.strftime("%H:%M"))
        hora += timedelta(minutes=30)
    return horarios

def dias_uteis_semana(date):
    inicio = date - timedelta(days=date.weekday())
    dias = [inicio + timedelta(days=i) for i in range(5)]
    return dias

# ========== INTERFACE ==========

st.set_page_config(page_title="Formulário de Reserva", layout="centered")
st.markdown("<h2 style='text-align: center; color: #444;'>Formulário de Reserva de Horário</h2>", unsafe_allow_html=True)

matricula = st.text_input("Matrícula")
nome = st.text_input("Nome")
departamento = st.text_input("Departamento")
email = st.text_input("Email")

horarios = gerar_horarios()

amanha = datetime.today().date() + timedelta(days=1)
data_escolhida = st.date_input("Escolha a data da reserva", min_value=amanha)

semana_toda = st.checkbox("Reservar a semana inteira (segunda a sexta), no mesmo horário")

# === Mostrar VAGAS DISPONÍVEIS ===
st.subheader("Vagas disponíveis:")

if semana_toda:
    dias_semana = dias_uteis_semana(data_escolhida)
    for dia in dias_semana:
        st.markdown(f"**{dia.strftime('%A (%d/%m/%Y)')}**")
        for h in horarios:
            vagas = 100 - contar_reservas(h, dia.strftime("%Y-%m-%d"))
            st.write(f"🕒 {h} — {vagas} vagas restantes")
else:
    st.markdown(f"**{data_escolhida.strftime('%A (%d/%m/%Y)')}**")
    for h in horarios:
        vagas = 100 - contar_reservas(h, data_escolhida.strftime("%Y-%m-%d"))
        st.write(f"🕒 {h} — {vagas} vagas restantes")

# === SELEÇÃO DO HORÁRIO ===
horario_escolhido = st.selectbox("Escolha um horário para reserva", horarios)

# === BOTÃO DE RESERVA ===
if st.button("Reservar"):
    if not all([matricula, nome, departamento, email]):
        st.error("Por favor, preencha todos os campos antes de reservar.")
    else:
        criar_arquivo_se_nao_existir()

        if semana_toda:
            dias = dias_uteis_semana(data_escolhida)
            reservas_feitas = []
            reservas_existentes = []

            for dia in dias:
                data_str = dia.strftime("%Y-%m-%d")
                if verificar_reserva_existente(matricula, data_str):
                    reservas_existentes.append(data_str)
                elif contar_reservas(horario_escolhido, data_str) >= 100:
                    continue
                else:
                    with open(ARQUIVO_CSV, mode='a', newline='', encoding='utf-8') as arquivo:
                        writer = csv.writer(arquivo)
                        writer.writerow([matricula, nome, departamento, email, horario_escolhido, data_str])
                        reservas_feitas.append(data_str)

            if reservas_feitas:
                st.success(f"Reservas confirmadas para os dias: {', '.join(reservas_feitas)} no horário {horario_escolhido}.")
            if reservas_existentes:
                st.warning(f"Você já tinha reserva nos dias: {', '.join(reservas_existentes)}.")
            if not reservas_feitas and not reservas_existentes:
                st.warning("Nenhuma reserva foi feita. Todos os horários estavam lotados ou você já tinha reserva.")
        else:
            data_str = data_escolhida.strftime("%Y-%m-%d")
            if verificar_reserva_existente(matricula, data_str):
                st.warning(f"Você já tem uma reserva para o dia {data_str}.")
            elif contar_reservas(horario_escolhido, data_str) >= 100:
                st.warning(f"O horário {horario_escolhido} do dia {data_str} já está lotado.")
            else:
                with open(ARQUIVO_CSV, mode='a', newline='', encoding='utf-8') as arquivo:
                    writer = csv.writer(arquivo)
                    writer.writerow([matricula, nome, departamento, email, horario_escolhido, data_str])
                st.success(f"Reserva confirmada para {nome} às {horario_escolhido} no dia {data_str}.")
