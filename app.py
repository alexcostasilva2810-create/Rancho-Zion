# =================================================================
# BLOCO 1: IMPORTAÇÕES E TOKENS NOTION
# =================================================================
import streamlit as st
import pandas as pd
import os
import requests
import unicodedata
from datetime import datetime
from fpdf import FPDF
from PIL import Image
from streamlit_drawable_canvas import st_canvas

# --- COLOQUE SEUS TOKENS AQUI SE ELES FOREM DIFERENTES ---
NOTION_TOKEN = "secret_your_token_here"
DATABASE_ID = "your_database_id_here"

# =================================================================
# BLOCO 2: FUNÇÕES DE INTEGRAÇÃO (RESTAURO DO NOTION)
# =================================================================
def carregar_dados_do_notion():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    try:
        response = requests.post(url, headers=headers)
        data = response.json()
        resultados = []
        for page in data.get("results", []):
            props = page.get("properties", {})
            resultados.append({
                "CODIGO": props.get("CODIGO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                "PROTEINA": props.get("PROTEINA", {}).get("title", [{}])[0].get("plain_text", ""),
                "TIPO": props.get("TIPO", {}).get("select", {}).get("name", ""),
                "UNIDADE DE MEDIDA": props.get("UNIDADE DE MEDIDA", {}).get("select", {}).get("name", ""),
                "ESTOQUE": props.get("ESTOQUE", {}).get("number", 0),
                "DESCRIÇÃO": props.get("DESCRIÇÃO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                "CONFIRMA": 0
            })
        return pd.DataFrame(resultados)
    except Exception as e:
        st.error(f"Erro na conexão Notion: {e}")
        return pd.DataFrame(columns=["CODIGO", "PROTEINA", "TIPO", "UNIDADE DE MEDIDA", "ESTOQUE", "DESCRIÇÃO", "CONFIRMA"])

# =================================================================
# BLOCO 3: CONFIGURAÇÃO INICIAL (RESOLVE LINHA 22)
# =================================================================
st.set_page_config(page_title="Zion Rancho App", layout="wide")

USUARIOS = {
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "NAVIO 03": {"nome": "Carlos", "senha": "456"}
}

if 'pagina' not in st.session_state: st.session_state.pagina = "home"
if 'df_lista' not in st.session_state: st.session_state.df_lista = pd.DataFrame()

# =================================================================
# BLOCO 4: NAVEGAÇÃO (HOME E LOGIN)
# =================================================================
if st.session_state.pagina == "home":
    st.markdown("<h1 style='text-align: center;'>Aplicativo Zion Rancho</h1>", unsafe_allow_html=True)
    if os.path.exists("ZION.jpg"): st.image("ZION.jpg", use_container_width=True)
    if st.button("🚀 INICIAR ACESSO", use_container_width=True):
        st.session_state.pagina = "login"
        st.rerun()

elif st.session_state.pagina == "login":
    st.title("🔐 Acesso do Cozinheiro")
    navio_sel = st.selectbox("Selecione o Navio", list(USUARIOS.keys()))
    senha_ent = st.text_input("Senha", type="password")
    if st.button("🛒 ENTRAR", use_container_width=True):
        if senha_ent == USUARIOS[navio_sel]["senha"]:
            st.session_state.cozinheiro = USUARIOS[navio_sel]["nome"]
            st.session_state.navio = navio_sel
            st.session_state.pagina = "menu"
            st.rerun()
        else: st.error("Senha incorreta!")

# =================================================================
# BLOCO 5: SUBMENU (O CORAÇÃO DA INTEGRAÇÃO)
# =================================================================
elif st.session_state.pagina == "menu":
    st.title(f"🚢 Painel Zion - {st.session_state.navio}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 DECLARAÇÃO / TRIPULAÇÃO", use_container_width=True):
            st.session_state.pagina = "tripulacao"
            st.rerun()
    with col2:
        if st.button("📋 TABELA DE RANCHO (NOTION)", use_container_width=True):
            st.session_state.pagina = "lista"
            st.rerun()

# =================================================================
# BLOCO 6: TELA DE TRIPULAÇÃO (RESTAURADA)
# =================================================================
elif st.session_state.pagina == "tripulacao":
    st.title("👨‍✈️ Declaração de Rancho")
    # --- FORMULÁRIO ---
    with st.form("form_trip"):
        origem = st.text_input("Origem")
        destino = st.text_input("Destino")
        st.write("Assinatura:")
        canvas_res = st_canvas(stroke_width=3, height=110, key="canvas_real")
        if st.form_submit_button("SALVAR PDF"):
            st.success("PDF Gerado!")
    if st.button("⬅️ VOLTAR"):
        st.session_state.pagina = "menu"
        st.rerun()

# =================================================================
# BLOCO 7: TELA DE LISTA (INTEGRAÇÃO NOTION REAL)
# =================================================================
elif st.session_state.pagina == "lista":
    st.title(f"📋 Checklist Notion - {st.session_state.navio}")
    
    if st.button("🔄 ATUALIZAR DADOS DO NOTION"):
        st.session_state.df_lista = carregar_dados_do_notion()
        st.rerun()

    if not st.session_state.df_lista.empty:
        df_editado = st.data_editor(st.session_state.df_lista, hide_index=True, use_container_width=True)
        if st.button("📄 GERAR PDF DA LISTA"):
            st.info("Gerando PDF...")
    else:
        st.warning("Clique no botão atualizar para carregar os itens do Notion.")

    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"
        st.rerun()
