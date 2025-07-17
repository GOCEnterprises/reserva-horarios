import streamlit as st
from datetime import datetime, timedelta
import sqlite3
import os

# Caminho do banco SQLite na pasta da rede OneDrive da empresa
DB_PATH = r"C:\Users\r958351\OneDrive - voestalpine\CONTROLES\reserva\reservas.db"

# Função para criar a conexão e garantir que a tabela existe
def criar_tabela():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula TEXT,
            nome TEXT,
            departamento TEXT,
            email TEXT,
            horario TEXT,
            data TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Função para salvar reserva no banco SQLite
def salvar_reserva(matricula, nome, departamento, email, horario, data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reservas (matricula, nome, departamento, email, horario, data)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (matricula, nome, departamento, email, horario, data))
    conn.commit()
    conn.close()

# Função para carregar todas as reservas
def carregar_reservas():
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT matricula, nome, departamento, email, horario, data FROM reservas')
    linhas = cursor.fetchall()
    conn.close()
    # Converte para lista de dicts para facilitar uso
    reservas = []
    for linha in linhas:
        reservas.append({
            "Matricula": linha[0],
            "Nome": linha[1],
            "Departamento": linha[2],
            "Email": linha[3],
            "Horario": linha[4],
            "Data": linha[5]
        })
    return reservas

# Função para verificar se já existe reserva da matrícula na data
def verificar_reserva_existente(matricula, data):
    reservas = carregar_reservas()
    for reserva in reservas:
        if reserva['Matricula'] == matricula and reserva['Data'] == data:
            return True
    return False

# Conta reservas por horário e data
def contar_reservas(horario, data):
    reservas = carregar_reservas()
    return sum(1 for r in reservas if r['Horario'] == horario and r['Data'] == data)

# Gera lista de horários entre 10:00 e 13:30, a cada 30 min
def gerar_horarios():
    horarios = []
    hora = datetime.strptime("10:00", "%H:%M")
    fim = datetime.strptime("13:30", "%H:%M")
    while hora <= fim:
        horarios.append(hora.strftime("%H:%M"))
        hora += timedelta(minutes=30)
    return horarios

# Gera dias úteis da semana da data escolhida (segunda a sexta)
def dias_uteis_semana(date):
    inicio = date - timedelta(days=date.weekday())
    dias = [inicio + timedelta(days=i) for i in range(5)]
    return dias

# Formatação das vagas com cor e emoji
def formatar_vagas_cor(vagas, horario):
    if vagas > 50:
        cor = "green"
        emoji = "🟢"
    elif 11 <= vagas <= 50:
        cor = "orange"
        emoji = "🟡"
    else:
        cor = "red"
        emoji = "🔴"
    return f"<span style='color:{cor}'>{emoji} {horario} — {vagas} vagas restantes</span>"

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

# Criar a tabela ao iniciar
criar_tabela()

# Mostrar vagas disponíveis
st.subheader("Vagas disponíveis:")

if semana_toda:
    dias_semana = dias_uteis_semana(data_escolhida)
    for dia in dias_semana:
        st.markdown(f"**{dia.strftime('%A (%d/%m/%Y)')}**")
        for h in horarios:
            vagas = 100 - contar_reservas(h, dia.strftime("%Y-%m-%d"))
            st.markdown(formatar_vagas_cor(vagas, h), unsafe_allow_html=True)
else:
    st.markdown(f"**{data_escolhida.strftime('%A (%d/%m/%Y)')}**")
    for h in horarios:
        vagas = 100 - contar_reservas(h, data_escolhida.strftime("%Y-%m-%d"))
        st.markdown(formatar_vagas_cor(vagas, h), unsafe_allow_html=True)

# Seleção do horário
horario_escolhido = st.selectbox("Escolha um horário para reserva", horarios)

# Botão de reserva
if st.button("Reservar"):
    if not all([matricula, nome, departamento, email]):
        st.error("Por favor, preencha todos os campos antes de reservar.")
    else:
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
                    salvar_reserva(matricula, nome, departamento, email, horario_escolhido, data_str)
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
                salvar_reserva(matricula, nome, departamento, email, horario_escolhido, data_str)
                st.success(f"Reserva confirmada para {nome} às {horario_escolhido} no dia {data_str}.")
