import streamlit as st
from datetime import datetime, timedelta
import csv
import os
from collections import defaultdict

st.set_page_config(page_title="Formulário de Reserva", layout="centered")

st.markdown(
    "<h2 style='text-align: center; color: #3F5971;'>Formulário de Reserva de Horário</h2>",
    unsafe_allow_html=True
)
st.markdown("---")

# Data da reserva (sempre amanhã)
data_reserva = (datetime.now() + timedelta(days=1)).date().isoformat()

# Capacidade por horário
capacidade_maxima = 100

# Criar lista de horários (10:00 até 13:30 de 30 em 30 minutos)
horarios = []
hora_inicial = datetime.strptime("10:00", "%H:%M")
for i in range(8):
    horario_str = (hora_inicial + timedelta(minutes=30 * i)).strftime("%H:%M")
    horarios.append(horario_str)

# Contar quantas reservas existem por horário
contagem_reservas = defaultdict(int)
arquivo = "reservas.csv"
if os.path.isfile(arquivo):
    with open(arquivo, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for linha in reader:
            if len(linha) < 6:
                continue  # Pula linhas incompletas
            _, _, _, _, horario, data = linha
            if data == data_reserva:
                contagem_reservas[horario] += 1

# Gerar opções disponíveis
opcoes_dropdown = []
for horario in horarios:
    vagas_restantes = capacidade_maxima - contagem_reservas[horario]
    if vagas_restantes > 0:
        label = f"{horario} (vagas restantes: {vagas_restantes})"
        opcoes_dropdown.append((label, horario))

if not opcoes_dropdown:
    st.warning("Todos os horários para amanhã já foram reservados. 😞")
else:
    with st.form("form_reserva"):
        st.markdown("### Preencha os dados abaixo:")

        matricula = st.text_input("Matrícula")
        nome = st.text_input("Nome completo")
        departamento = st.text_input("Departamento")
        email = st.text_input("E-mail corporativo")

        horario_selecionado_label = st.selectbox(
            "Escolha um horário disponível", [op[0] for op in opcoes_dropdown]
        )

        reservado = st.form_submit_button("Reservar horário")

        if reservado:
            if not matricula.strip() or not nome.strip() or not departamento.strip() or not email.strip():
                st.error("Por favor, preencha todos os campos antes de reservar.")
            else:
                horario_selecionado = dict(opcoes_dropdown)[horario_selecionado_label]

                nova_linha = [matricula, nome, departamento, email, horario_selecionado, data_reserva]
                reserva_duplicada = False

                if os.path.isfile(arquivo):
                    with open(arquivo, mode='r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        next(reader)
                        for linha in reader:
                            if len(linha) < 6:
                                continue
                            mat_lida, _, _, _, _, data_lida = linha
                            if mat_lida == matricula and data_lida == data_reserva:
                                reserva_duplicada = True
                                break

                if reserva_duplicada:
                    st.error(f"Você já tem uma reserva para o dia {data_reserva}.")
                else:
                    with open(arquivo, mode='a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        if not os.path.getsize(arquivo):
                            writer.writerow(["Matrícula", "Nome", "Departamento", "Email", "Horário", "Data"])
                        writer.writerow(nova_linha)

                    st.success(f"Reserva confirmada para {nome} às {horario_selecionado} no dia {data_reserva}.")
