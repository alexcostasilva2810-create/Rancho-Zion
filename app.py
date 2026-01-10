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

# --- 1. ESTILO VISUAL AJUSTADO ---
st.markdown("""
    <style>
    .stApp { background-color: #4169E1; color: white; text-align: center; }
    h1, h2, h3, p, label { color: white !important; }
    
    /* BOTÕES COM TEXTO PRETO E BEM VISÍVEIS */
    .stButton>button { 
        background-color: #FFFFFF !important; 
        color: #000000 !important; /* Texto Preto conforme solicitado */
        font-size: 18px !important;
        font-weight: bold !important; 
        border-radius: 10px; 
        height: 3em;
        width: 100%;
        border: 2px solid #000000;
        margin-top: 10px;
    }

    /* Ajuste para inputs aparecerem com texto legível */
    input { color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LÓGICA DE LOGIN E SAUDAÇÃO ---
if st.session_state.pagina == "login":
    st.title("🔐 Acesso do Cozinheiro")
    
    navio = st.selectbox("Selecione o seu Navio", [""] + list(USUARIOS.keys()))
    senha = st.text_input("Senha de Acesso", type="password")
    
    # Botão de Entrar com ícone de carrinho 🛒
    if st.button("🛒 ENTRAR"):
        if navio in USUARIOS and USUARIOS[navio] == senha:
            st.session_state.usuario_ativo = navio
            st.session_state.logado = True
            st.session_state.pagina = "menu"
            # Mensagem de sucesso personalizada
            st.success(f"Seja Bem-vindo, {navio}!") 
            st.rerun()
        else:
            st.error("Navio ou Senha incorretos!")
            
    # Botão de Voltar
    if st.button("⬅️ VOLTAR"):
        st.session_state.pagina = "home"
        st.rerun()

# --- 3. TELA DE MENU (ONDE APARECE A SAUDAÇÃO) ---
elif st.session_state.pagina == "menu":
    # Saudação personalizada no topo do menu
    st.markdown(f"## Seja Bem-vindo, {st.session_state.usuario_ativo}!")
    st.write("Escolha o módulo que deseja acessar:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🛒 LISTA DE RANCHO"):
            st.session_state.pagina = "lista_rancho"
            st.rerun()
            
    with col2:
        if st.button("👨‍✈️ TRIPULAÇÃO"):
            st.session_state.pagina = "tripulacao"
            st.rerun()

    if st.button("SAIR"):
        st.session_state.logado = False
        st.session_state.pagina = "home"
        st.rerun()
