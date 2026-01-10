import streamlit as st
import os

# ==========================================
# 1. CONFIGURAÇÕES E BANCO DE DADOS DE USUÁRIOS
# ==========================================
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state:
    st.session_state.cozinheiro = ""

# Dicionário: "LOGIN": {"nome": "NOME DO COZINHEIRO", "senha": "SENHA"}
USUARIOS = {
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "NAVIO 02": {"nome": "Carlos", "senha": "456"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "ZION 04": {"nome": "Ricardo", "senha": "101"}
}

# ==========================================
# 2. ESTILO CSS (FUNDOS E BOTÕES)
# ==========================================
st.markdown("""
    <style>
    /* Fundo Azul Royal */
    .stApp { background-color: #4169E1 !important; }
    
    /* Textos em Branco */
    h1, h2, h3, p, label { color: white !important; }

    /* BOTÃO LARANJA COM LETRA PRETA (FORÇADO) */
    div.stButton > button {
        background-color: #FF8C00 !important;
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 18px !important;
        border-radius: 10px !important;
        border: 2px solid #000000 !important;
        width: 100%;
        height: 3.5em;
    }
    
    /* Garante que o texto continue preto ao passar o mouse ou clicar */
    div.stButton > button:hover, div.stButton > button:active, div.stButton > button:focus {
        color: #000000 !important;
        background-color: #FFA500 !important;
    }

    /* Estilo para campos de texto e selectbox */
    input { color: black !important; }
    div[data-baseweb="select"] > div { color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. #--- TELA INICIAL ---#
# ==========================================
if st.session_state.pagina == "home":
    st.title("Bem-vindo ao Zion Rancho App!")
    st.write("Seu controle de estoque inteligente com IA.")
    
    if os.path.exists("APPRANCHO.png"):
        st.image("APPRANCHO.png", width=400)
    
    if st.button("INICIAR ACESSO", key="btn_inicio"):
        st.session_state.pagina = "login"
        st.rerun()

# ==========================================
# 4. #--- TELA DE LOGIN (SUBSTELA ACESSO) ---#
# ==========================================
elif st.session_state.pagina == "login":
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
    
    navio_sel = st.selectbox("Selecione o seu Navio", [""] + list(USUARIOS.keys()))
    senha_sel = st.text_input("Senha de Acesso", type="password")
    
    if st.button("🛒 ENTRAR", key="btn_entrar"):
        if navio_sel in USUARIOS and USUARIOS[navio_sel]["senha"] == senha_sel:
            # Salva o nome do cozinheiro para a saudação
            st.session_state.cozinheiro = USUARIOS[navio_sel]["nome"]
            st.session_state.pagina = "menu"
            st.rerun()
        else:
            st.error("Dados incorretos!")
            
    if st.button("⬅️ VOLTAR", key="btn_voltar_login"):
        st.session_state.pagina = "home"
        st.rerun()

# ==========================================
# 5. #--- SUBSTELA (MENU PRINCIPAL) ---#
# ==========================================
elif st.session_state.pagina == "menu":
    # Saudação com nome do Cozinheiro
    st.markdown(f"## Seja Bem-vindo, {st.session_state.cozinheiro}!")
    st.write("Escolha o que deseja fazer:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛒 LISTA DE RANCHO", key="btn_rancho"):
            st.session_state.pagina = "lista"
            st.rerun()
    with col2:
        if st.button("👨‍✈️ TRIPULAÇÃO", key="btn_tripulacao"):
            st.session_state.pagina = "tripulacao"
            st.rerun()

    st.markdown("---")
    if st.button("SAIR DO SISTEMA", key="btn_sair_final"):
        st.session_state.pagina = "home"
        st.rerun()

# ==========================================
# 6. TELAS DE CONTEÚDO (LISTA E TRIPULAÇÃO)
# ==========================================
elif st.session_state.pagina == "lista":
    st.title("🛒 Lista de Rancho")
    st.info(f"Cozinheiro Responsável: {st.session_state.cozinheiro}")
    
    # Próximo passo: Integração com Notion aqui
    st.write("Sua lista de compras aparecerá aqui em breve.")
    
    if st.button("⬅️ VOLTAR AO MENU", key="btn_voltar_lista"):
        st.session_state.pagina = "menu"
        st.rerun()

elif st.session_state.pagina == "tripulacao":
    st.title("👨‍✈️ Tripulação")
    st.write("Módulo de gestão de tripulantes.")
    
    if st.button("⬅️ VOLTAR AO MENU", key="btn_voltar_trip"):
        st.session_state.pagina = "menu"
        st.rerun()
