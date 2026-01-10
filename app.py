import streamlit as st
import requests
import pandas as pd
import os

# --- 1. DEFINIÇÃO DE USUÁRIOS E SENHAS ---
# EDITE AQUI: "NOME DO NAVIO": "SENHA"
USUARIOS = {
    "AROEIRA": "ALLAN",
    "ANGICO": "ELZA",
    "NAVIO 03": "zion03",
    "NAVIO 04": "zion04",
    "NAVIO 05": "zion05",
    "NAVIO 06": "zion06",
    "NAVIO 07": "zion07",
    "NAVIO 08": "zion08",
    "NAVIO 09": "zion09",
    "NAVIO 10": "zion10",
    "NAVIO 11": "zion11",
    "NAVIO 12": "zion12",
    "NAVIO 13": "zion13"
}

# --- 2. CONFIGURAÇÕES E ESTILO ---
st.set_page_config(page_title="Zion Rancho", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #4169E1; color: white; text-align: center; }
    h1, h2, h3, p, label { color: white !important; }
    
    /* BOTÕES MAIS VISÍVEIS */
    .stButton>button { 
        background-color: #FFFFFF !important; 
        color: #00008B !important; /* Azul Escuro para leitura fácil */
        font-size: 20px !important;
        font-weight: bold !important; 
        border-radius: 10px; 
        height: 3em;
        width: 100%;
        border: 2px solid #000000;
    }
    /* Deixar o texto dos campos de entrada visíveis */
    .stTextInput>div>div>input { color: black !important; }
    .stSelectbox>div>div>div { color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"

# TELA 1: CAPA
if st.session_state.pagina == "home":
    st.title("Bem-vindo ao Zion Rancho App!")
    if os.path.exists("APPRANCHO.png"):
        st.image("APPRANCHO.png", width=400)
    
    if st.button("INICIAR ACESSO"):
        st.session_state.pagina = "login"
        st.rerun()

# TELA 2: LOGIN (ONDE APARECEM ENTRAR E VOLTAR)
elif st.session_state.pagina == "login":
    st.title("🔐 Acesso do Cozinheiro")
    
    navio = st.selectbox("Selecione o seu Navio", [""] + list(USUARIOS.keys()))
    senha = st.text_input("Digite a Senha", type="password")
    
    st.markdown("---")
    
    # Botão de Entrar
    if st.button("ENTRAR AGORA"):
        if navio in USUARIOS and USUARIOS[navio] == senha:
            st.session_state.usuario_ativo = navio
            st.session_state.pagina = "menu"
            st.rerun()
        else:
            st.error("Dados incorretos!")
            
    # Botão de Voltar
    if st.button("VOLTAR PARA O INÍCIO"):
        st.session_state.pagina = "home"
        st.rerun()

# TELA 3: MENU COM ÍCONES
elif st.session_state.pagina == "menu":
    st.title(f"⚓ Navio: {st.session_state.usuario_ativo}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛒 LISTA DE RANCHO"):
            st.session_state.pagina = "lista"
            st.rerun()
    with col2:
        if st.button("👨‍✈️ TRIPULAÇÃO"):
            st.info("Módulo em breve")

    if st.button("SAIR"):
        st.session_state.pagina = "home"
        st.rerun()
