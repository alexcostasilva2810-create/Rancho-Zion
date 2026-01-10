import streamlit as st
import os

# ==========================================
# BLOCO 1: CONFIGURAÇÕES E USUÁRIOS
# ==========================================
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'usuario_ativo' not in st.session_state:
    st.session_state.usuario_ativo = ""

USUARIOS = {
    "AROEIRA": "ALLAN", "NAVIO 02": "zion02", "NAVIO 03": "zion03",
    "NAVIO 04": "zion04", "NAVIO 05": "zion05", "NAVIO 06": "zion06",
    "NAVIO 07": "zion07", "NAVIO 08": "zion08", "NAVIO 09": "zion09",
    "NAVIO 10": "zion10", "NAVIO 11": "zion11", "NAVIO 12": "zion12",
    "NAVIO 13": "zion13"
}

# ==========================================
# BLOCO 2: ESTILO CSS (BOTÃO LARANJA / TEXTO PRETO)
# ==========================================
st.markdown("""
    <style>
    /* 1. Fundo Azul Royal na tela inteira */
    .stApp { 
        background-color: #4169E1 !important; 
    }
    
    /* 2. Todos os textos em Branco */
    h1, h2, h3, p, label { 
        color: #FFFFFF !important; 
    }

    /* 3. BOTÕES LARANJA COM TEXTO PRETO (FORÇADO) */
    div.stButton > button {
        background-color: #FF8C00 !important; /* Laranja */
        color: #000000 !important;           /* Letra Preta */
        font-weight: 900 !important;         /* Negrito forte */
        font-size: 20px !important;
        border-radius: 12px !important;
        border: 2px solid #000000 !important;
        width: 100% !important;
        height: 3.5em !important;
    }

    /* 4. Inputs com texto legível */
    input { color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# BLOCO 3: #--- TELA INICIAL ---#
# ==========================================
if st.session_state.pagina == "home":
    st.title("Bem-vindo ao Zion Rancho App!")
    st.write("Seu controle de estoque inteligente com IA.")
    
    # Logo da Zion
    if os.path.exists("APPRANCHO.png"):
        st.image("APPRANCHO.png", width=400)
    
    if st.button("INICIAR ACESSO"):
        st.session_state.pagina = "login"
        st.rerun()

# ==========================================
# BLOCO 4: #--- SUBSTELA (LOGIN) ---#
# ==========================================
elif st.session_state.pagina == "login":
    # Fundo especial para o login (Cozinha leve ao fundo)
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(65, 105, 225, 0.8), rgba(65, 105, 225, 0.8)), 
            url("https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&w=1350&q=80");
            background-size: cover;
        }
        </style>
        """, unsafe_allow_html=True)
        
    st.title("🔐 Acesso do Cozinheiro")
    
    navio = st.selectbox("Selecione o seu Navio", [""] + list(USUARIOS.keys()))
    senha = st.text_input("Senha de Acesso", type="password")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🛒 ENTRAR"):
        if navio in USUARIOS and USUARIOS[navio] == senha:
            st.session_state.usuario_ativo = navio
            st.session_state.pagina = "menu"
            st.rerun()
        else:
            st.error("Navio ou Senha incorretos!")
            
    if st.button("⬅️ VOLTAR"):
        st.session_state.pagina = "home"
        st.rerun()

# ==========================================
# BLOCO 5: MENU PRINCIPAL (SAUDAÇÃO AO COZINHEIRO)
# ==========================================
elif st.session_state.pagina == "menu":
    # Reforço do CSS para garantir botões Laranja com letras Pretas nesta tela
    st.markdown("""
        <style>
        .stApp { background-color: #4169E1 !important; }
        
        /* BOTÃO LARANJA COM TEXTO PRETO */
        div.stButton > button {
            background-color: #FF8C00 !important; 
            color: #000000 !important; 
            font-weight: 900 !important; 
            font-size: 18px !important;
            border-radius: 12px !important;
            border: 2px solid #000000 !important;
        }
        </style>
        """, unsafe_allow_html=True)

    # Exibe o nome do Responsável (Cozinheiro) em vez do nome do Navio
    # Nota: Certifique-se de que st.session_state.usuario_ativo contenha o nome do cozinheiro
    st.markdown(f"## Seja Bem-vindo, {st.session_state.usuario_ativo}!")
    st.write("Escolha o que deseja fazer:")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Organização dos botões com ícones
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🛒 LISTA DE RANCHO"):
            st.session_state.pagina = "lista_rancho"
            st.rerun()
            
    with col2:
        if st.button("👨‍✈️ TRIPULAÇÃO"):
            st.session_state.pagina = "tripulacao"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Botão de Sair menor
    if st.button("SAIR"):
        st.session_state.pagina = "home"
        st.rerun()
    if st.button("SAIR"):
        st.session_state.pagina = "home"
        st.rerun()
