import streamlit as st
import requests
import pandas as pd
import os

# --- 1. CONFIGURAÇÕES DE SEGURANÇA E CONEXÃO ---
# O Streamlit lê as chaves que você salvou em 'Advanced Settings'
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
DATABASE_ID = st.secrets["DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

# Banco de dados de usuários (Ajuste as senhas como desejar)
USUARIOS = {
    "NAVIO 01": "zion01", "NAVIO 02": "zion02", "NAVIO 03": "zion03",
    "NAVIO 04": "zion04", "NAVIO 05": "zion05", "NAVIO 06": "zion06",
    "NAVIO 07": "zion07", "NAVIO 08": "zion08", "NAVIO 09": "zion09",
    "NAVIO 10": "zion10", "NAVIO 11": "zion11", "NAVIO 12": "zion12",
    "NAVIO 13": "zion13"
}

# --- 2. ESTILO VISUAL (AZUL ROYAL) ---
st.set_page_config(page_title="Zion Rancho App", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #4169E1; color: white; text-align: center; }
    h1, h2, h3, p { color: white !important; }
    /* Estilo dos botões brancos com texto azul */
    .stButton>button { 
        background-color: #ffffff; 
        color: #4169E1; 
        font-weight: bold; 
        border-radius: 15px; 
        height: 3em;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONTROLE DE ESTADO (SESSÃO) ---
if 'logado' not in st.session_state:
    st.session_state.logado = False
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'usuario_ativo' not in st.session_state:
    st.session_state.usuario_ativo = ""

# --- 4. LÓGICA DE TELAS ---

# TELA 1: CAPA COM LOGO
if st.session_state.pagina == "home":
    st.title("Bem-vindo ao Zion Rancho App!")
    st.write("Seu controle de estoque inteligente com IA.")
    
    if os.path.exists("APPRANCHO.png"):
        st.image("APPRANCHO.png", width=400)
    
    if st.button("INICIAR ACESSO"):
        st.session_state.pagina = "login"
        st.rerun()

# TELA 2: LOGIN POR NAVIO
elif st.session_state.pagina == "login":
    st.title("🔐 Acesso do Cozinheiro")
    
    navio = st.selectbox("Selecione o seu Navio", [""] + list(USUARIOS.keys()))
    senha = st.text_input("Senha de Acesso", type="password")
    
    if st.button("ENTRAR"):
        if navio in USUARIOS and USUARIOS[navio] == senha:
            st.session_state.logado = True
            st.session_state.usuario_ativo = navio
            st.session_state.pagina = "menu"
            st.rerun()
        else:
            st.error("Navio ou Senha incorretos!")
    
    if st.button("⬅ Voltar"):
        st.session_state.pagina = "home"
        st.rerun()

# TELA 3: MENU COM ÍCONES (PÓS-LOGIN)
elif st.session_state.pagina == "menu":
    st.title(f"⚓ Painel do {st.session_state.usuario_ativo}")
    st.write("Escolha o módulo que deseja acessar:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🛒")
        if st.button("LISTA DE RANCHO"):
            st.session_state.pagina = "lista_rancho"
            st.rerun()
            
    with col2:
        st.markdown("### 👨‍✈️")
        if st.button("TRIPULAÇÃO"):
            st.session_state.pagina = "tripulacao"
            st.rerun()
    
    st.markdown("---")
    if st.button("SAIR / LOGOFF"):
        st.session_state.logado = False
        st.session_state.pagina = "home"
        st.rerun()

# TELA 4: LISTA DE RANCHO (INTEGRADA AO NOTION)
elif st.session_state.pagina == "lista_rancho":
    st.title("🛒 Lista de Rancho")
    st.info(f"Responsável: {st.session_state.usuario_ativo}")
    
    st.write("Aqui aparecerá sua tabela do Notion em breve...")
    
    if st.button("⬅ Voltar ao Menu"):
        st.session_state.pagina = "menu"
        st.rerun()

# TELA 5: TRIPULAÇÃO
elif st.session_state.pagina == "tripulacao":
    st.title("👨‍✈️ Gestão de Tripulação")
    st.write("Módulo de cadastro de tripulantes em desenvolvimento.")
    
    if st.button("⬅ Voltar ao Menu"):
        st.session_state.pagina = "menu"
        st.rerun()
