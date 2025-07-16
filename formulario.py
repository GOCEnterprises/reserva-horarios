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

# Verifica se já tem reserva pra uma data
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

# Conta quantas reservas existem para um horário numa data
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

# Gera lista de horários
def gerar_horarios():
    horarios = []
    hora = datetime.strptime("10:00", "%H:%M")
    fim = datetime.strptime("13:30", "%H:%M")
    while hora <= fim:
        horarios.append(hora.strftime("%H:%M"))
        hora += timedelta(minutes=30)
    return horarios

# Gera dias úteis da semana do dia selecionado
def dias_uteis_semana(date):
    inicio = date - timedelta(days=date.weekday())  # Segunda
    dias = [inicio + timedelta(days=i) for i in range(5)]  # Segunda a sexta
    return dias

# ----------- INTERFACE -----------
st.set_page_config(page_title="Formulário de Reserva", layout="centered")
st.markdown("<h2 style='text-align: center; color: #444;'>Formulário de Reserva de Horário</h2>", unsafe_allow_html=True)

# Campos do formulário
matricula = st.text_input("Matrícula")
nome = st.text_input("Nome")
departamento = st.text_input("Departamento")
email = st.text_input("Email")
horarios = gerar_horarios()
horario_escolhido = st.selectbox("Escolha um horário", horarios)

# Data mínima é amanhã
amanha = datetime.today().date() + timedelta(days=1)
data_escolhida = st.date_input("Escolha a data da reserva", min_value=amanha)

semana_toda = st.checkbox("Reservar a semana inteira (segunda a sexta), no mesmo horário")

# Botão
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
                    continue  # pula se estiver lotado
                else:
                    with open(ARQUIVO_CSV, mode='a', newline='', encoding='utf-8') as arquivo:
                        writer = csv.writer(arquivo)
                        writer.writerow([matricula, nome, departamento, email, horario_escolhido, data_str])
                        reservas_feitas.append(data_str)

            if reservas_feitas:
                st.success(f"Reservas confirmadas para os dias: {', '.join(reservas_feitas)} no horário {horario_escolhido}.")
            if reservas_existentes:
                st.warning(f"Você já tinha reserva nos dias: {', '.join(reservas_existentes)}. Estes não foram reservados novamente.")

            if not reservas_feitas and not reservas_existentes:
                st.warning("Nenhuma reserva foi feita. Verifique se os horários estão lotados.")
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
