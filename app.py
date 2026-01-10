import streamlit as st
import os

# 1. Configuração da Página
st.set_page_config(page_title="Zion Rancho", layout="centered")

# 2. Estilo Azul Royal
st.markdown("""
    <style>
    .stApp {
        background-color: #4169E1;
        color: white;
        text-align: center;
    }
    h1, p { color: white !important; }
    .stButton>button {
        background-color: white;
        color: #4169E1;
        font-weight: bold;
        border-radius: 10px;
        height: 3em;
        width: 50%;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Conteúdo da Tela Inicial
st.title("Bem-vindo ao Zion Rancho!")
st.write("Seu controle de estoque inteligente com IA.")

# Tentativa de carregar a imagem sem quebrar o app
nome_da_imagem = "APPRANCHO.png"

if os.path.exists(nome_da_imagem):
    st.image(nome_da_imagem, width=400)
else:
    st.error(f"Arquivo '{nome_da_imagem}' não encontrado no GitHub. Verifique o nome!")

# --- BLOCO DE CONTROLE DE ACESSO (LOGS E USUÁRIOS) ---

# Lista dos 13 Navios (Ajuste os nomes conforme sua frota)
NAVIO_SENHAS = {
    "Navio 01": "zion01",
    "Navio 02": "zion02",
    "Navio 03": "zion03",
    "Navio 04": "zion04",
    "Navio 05": "zion05",
    "Navio 06": "zion06",
    "Navio 07": "zion07",
    "Navio 08": "zion08",
    "Navio 09": "zion09",
    "Navio 10": "zion10",
    "Navio 11": "zion11",
    "Navio 12": "zion12",
    "Navio 13": "zion13"
}

def tela_login():
    st.markdown("### 🔐 Acesso Restrito aos Cozinheiros")
    
    with st.form("login_form"):
        navio_selecionado = st.selectbox("Selecione seu Navio", list(NAVIO_SENHAS.keys()))
        senha = st.text_input("Senha do Navio", type="password")
        botao_entrar = st.form_submit_button("ENTRAR NO SISTEMA")
        
        if botao_entrar:
            if NAVIO_SENHAS.get(navio_selecionado) == senha:
                st.session_state.logado = True
                st.session_state.usuario_atual = navio_selecionado # Guarda quem acessou
                st.success(f"Bem-vindo, Cozinheiro do {navio_selecionado}!")
                st.rerun()
            else:
                st.error("Senha incorreta. Tente novamente.")

# --- INTEGRAÇÃO COM A TABELA (EXEMPLO DE ENVIO) ---
def atualizar_estoque_notion(item_id, novo_valor):
    # Esta função enviará o 'usuario_atual' para a coluna 'RESPONSÁVEL' do Notion
    url = f"https://api.notion.com/v1/pages/{item_id}"
    dados_atualizados = {
        "properties": {
            "ESTOQUE": {"number": novo_valor},
            "RESPONSÁVEL": {
                "rich_text": [{"text": {"content": st.session_state.usuario_atual}}]
            }
        }
    }
    requests.patch(url, headers=headers, json=dados_atualizados)

# 4. Botão de entrada
if st.button("ACESSAR SISTEMA"):
    st.success("Conectando ao banco de dados...")
    # Aqui depois colocaremos a troca para a tabela
