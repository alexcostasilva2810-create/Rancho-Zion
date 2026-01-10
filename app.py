import streamlit as st
import requests
import pandas as pd
import os

# ==========================================
# BLOCO 1: CONFIGURAÇÕES E BANCO DE DADOS
# ==========================================
# Chaves de acesso (Puxando do Streamlit Secrets)
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
DATABASE_ID = st.secrets["DATABASE_ID"]

# Lista de Navios e Senhas (Defina aqui o que entregar aos cozinheiros)
USUARIOS = {
    "AROEIRA": "ALLAN", "NAVIO 02": "zion02", "NAVIO 03": "zion03",
    "IPE": "ELZA", "NAVIO 05": "zion05", "NAVIO 06": "zion06",
    "NAVIO 07": "zion07", "NAVIO 08": "zion08", "NAVio 09": "zion09",
    "NAVIO 10": "zion10", "NAVIO 11": "zion11", "NAVIO 12": "zion12",
    "NAVIO 13": "zion13"
}

# Configuração da Página
st.set_page_config(page_title="Zion Rancho", layout="centered")

# Estilo CSS (Fundo Azul, Botões Brancos, Texto Preto nos Botões)
st.markdown("""
    <style>
    .stApp { background-color: #4169E1; color: white; text-align: center; }
    h1, h2, h3, p, label { color: white !important; }
    
    /* ESTILO DOS BOTÕES: Texto Preto, Fundo Branco */
    .stButton>button { 
        background-color: #FFFFFF !important; 
        color: #000000 !important; 
        font-size: 18px !important;
        font-weight: bold !important; 
        border-radius: 12px; 
        height: 3.5em;
        width: 100%;
        border: 2px solid #000000;
        margin-bottom: 10px;
    }
    
    /* Inputs de texto pretos para leitura */
    input { color: black !important; }
    div[data-baseweb="select"] > div { color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# Controle de Navegação
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'usuario_ativo' not in st.session_state:
    st.session_state.usuario_ativo = ""

# ==========================================
# BLOCO 2: #--- TELA INICIAL ---#
# ==========================================
if st.session_state.pagina == "home":
    st.title("Bem-vindo ao Zion Rancho App!")
    st.write("Seu controle de estoque inteligente com IA.")
    
    # Exibe sua logo se o arquivo existir
    if os.path.exists("APPRANCHO.png"):
        st.image("APPRANCHO.png", width=400)
    
    if st.button("INICIAR ACESSO"):
        st.session_state.pagina = "login"
        st.rerun()

# ==========================================
# BLOCO 3: TELA DE LOGIN (ACESSO DO COZINHEIRO)
# ==========================================

elif st.session_state.pagina == "login":
    # CSS específico para letras pretas nos botões e fundo de cozinha
    st.markdown("""
        <style>
        /* Fundo com imagem de cozinha e máscara azul */
        .stApp {
            background: linear-gradient(rgba(65, 105, 225, 0.8), rgba(65, 105, 225, 0.8)), 
            url("https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&w=1350&q=80");
            background-size: cover;
        }

        /* FORÇAR LETRA PRETA NOS BOTÕES */
        div.stButton > button {
            background-color: #FFFFFF !important;
            color: #000000 !important; /* PRETO ABSOLUTO */
            font-weight: bold !important;
            border: 2px solid #000000 !important;
        }

        /* Garante que o texto continue preto ao passar o mouse */
        div.stButton > button:hover {
            color: #000000 !important;
            border: 2px solid #000000 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
    st.title("🔐 Acesso do Cozinheiro")
    
    # Seleção de Navio e Senha
    navio = st.selectbox("Selecione o seu Navio", [""] + list(USUARIOS.keys()))
    senha = st.text_input("Senha de Acesso", type="password")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Botão ENTRAR com ícone
    if st.button("🛒 ENTRAR"):
        if navio in USUARIOS and USUARIOS[navio] == senha:
            st.session_state.usuario_ativo = navio
            st.session_state.pagina = "menu"
            st.rerun()
        else:
            st.error("Navio ou Senha incorretos!")
            
    # Botão VOLTAR com ícone
    if st.button("⬅️ VOLTAR"):
        st.session_state.pagina = "home"
        st.rerun()
# ==========================================
# BLOCO 4: #--- SUBSTELA (MENU PRINCIPAL) ---#
# ==========================================
elif st.session_state.pagina == "menu":
    # Saudação Personalizada
    st.markdown(f"## Seja Bem-vindo, {st.session_state.usuario_ativo}!")
    st.write("Selecione o módulo desejado:")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🛒 LISTA DE RANCHO"):
            st.session_state.pagina = "lista_rancho"
            st.rerun()
            
    with col2:
        if st.button("👨‍✈️ TRIPULAÇÃO"):
            st.session_state.pagina = "tripulacao"
            st.rerun()

    st.markdown("---")
    if st.button("SAIR DO SISTEMA"):
        st.session_state.pagina = "home"
        st.rerun()

# ==========================================
# BLOCO 5: ÁREAS DE CONTEÚDO (RANCHO / TRIPULAÇÃO)
# ==========================================
elif st.session_state.pagina == "lista_rancho":
    st.title("🛒 Lista de Rancho")
    st.info(f"Responsável Logado: {st.session_state.usuario_ativo}")
    
    # Aqui chamaremos a função de puxar dados do Notion no próximo passo
    st.warning("Carregando banco de dados do Notion...")
    
    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"
        st.rerun()

elif st.session_state.pagina == "tripulacao":
    st.title("👨‍✈️ Gestão de Tripulação")
    st.write(f"Módulo acessado por: {st.session_state.usuario_ativo}")
    
    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"
        st.rerun()
