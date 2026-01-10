import streamlit as st
import pandas as pd
import requests
import os
from fpdf import FPDF

# 1. ESTADOS DO APP
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state:
    st.session_state.cozinheiro = ""

# Simulando banco de dados (Ajuste conforme sua necessidade)
USUARIOS = {
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"}
}

# 2. ESTILO CSS (BOTÃO LARANJA COM TEXTO PRETO)
st.markdown("""
    <style>
    .stApp { background-color: #4169E1 !important; }
    h1, h2, h3, p, label { color: white !important; }

    /* BOTÃO LARANJA COM TEXTO PRETO - FORÇADO */
    div.stButton > button {
        background-color: #FF8C00 !important;
        color: #000000 !important;
        font-weight: 900 !important;
        border: 2px solid #000000 !important;
        width: 100%;
        height: 3.5em;
    }
    div.stButton > button:hover { color: #000000 !important; background-color: #FFA500 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. LÓGICA DE NAVEGAÇÃO
if st.session_state.pagina == "home":
    st.title("Bem-vindo ao Zion Rancho App!")
    if os.path.exists("APPRANCHO.png"):
        st.image("APPRANCHO.png", width=400)
    if st.button("INICIAR ACESSO", key="btn_home"):
        st.session_state.pagina = "login"
        st.rerun()

elif st.session_state.pagina == "login":
    st.title("🔐 Acesso do Cozinheiro")
    navio = st.selectbox("Selecione o seu Navio", [""] + list(USUARIOS.keys()))
    senha = st.text_input("Senha", type="password")
    
    if st.button("🛒 ENTRAR", key="btn_login_entrar"):
        if navio in USUARIOS and USUARIOS[navio]["senha"] == senha:
            st.session_state.cozinheiro = USUARIOS[navio]["nome"]
            st.session_state.pagina = "menu"
            st.rerun()
        else:
            st.error("Dados incorretos")
    
    if st.button("⬅️ VOLTAR", key="btn_login_voltar"):
        st.session_state.pagina = "home"
        st.rerun()

elif st.session_state.pagina == "menu":
    st.markdown(f"## Seja Bem-vindo, {st.session_state.cozinheiro}!")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛒 LISTA DE RANCHO", key="menu_rancho"):
            st.session_state.pagina = "lista"
            st.rerun()
    with col2:
        if st.button("👨‍✈️ TRIPULAÇÃO", key="menu_trip"):
            st.info("Em breve")

    if st.button("SAIR", key="menu_sair"):
        st.session_state.pagina = "home"
        st.rerun()

elif st.session_state.pagina == "lista":
    st.title("📋 Tabela de Rancho")
    
    # Criando tabela vazia para exemplo (Aqui você usa sua função do Notion)
    dados = {
        "CÓDIGO": ["001", "002"],
        "PROTEÍNA": ["Carne Moída", "Frango"],
        "PREDEFINIDO": [10, 5],
        "CONFIRMA": [0, 0]
    }
    df = pd.DataFrame(dados)

    st.write(f"Responsável: {st.session_state.cozinheiro}")
    
    df_editado = st.data_editor(df, hide_index=True, use_container_width=True)

    if st.button("📄 GERAR PDF", key="btn_pdf"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(40, 10, f"Lista de Rancho - {st.session_state.cozinheiro}")
        # Lógica simplificada de download
        st.download_button("Baixar PDF", data=pdf.output(dest='S').encode('latin-1'), file_name="lista.pdf")

    if st.button("⬅️ VOLTAR", key="btn_lista_voltar"):
        st.session_state.pagina = "menu"
        st.rerun()
