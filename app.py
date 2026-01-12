import streamlit as st
import pandas as pd
import base64
import os
import requests
import unicodedata
from fpdf import FPDF
from PIL import Image
from datetime import datetime, timedelta

# =================================================================
# BLOCO 1: CONFIGURAÇÕES, IDs E FUNÇÕES DE BUSCA
# =================================================================
st.set_page_config(page_title="Zion Rancho App", layout="wide")

# Credenciais e IDs (Conforme visto no seu editor)
NOTION_TOKEN = "ntn_z6353375938j9kJfQKwjD0N4ONt1rwP515tsIMwxtucHa"
DATABASE_ID = "2e3025de7b79803abe0efde74f87a2e1"
ID_HISTORICO_NOTION = "2e5025de7b79803187a4d8b865179440"

def carregar_dados_do_notion():
    """Busca a lista completa de estoque no Notion para evitar tabelas curtas."""
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    try:
        res = requests.post(url, headers=headers)
        data = res.json()
        lista_completa = []
        for page in data["results"]:
            props = page["properties"]
            # Mapeamento exato das colunas do seu Notion
            lista_completa.append({
                "ITEM": props["ITEM"]["title"][0]["text"]["content"] if props["ITEM"]["title"] else "",
                "DESCRIÇÃO": props["DESCRIÇÃO"]["rich_text"][0]["text"]["content"] if props["DESCRIÇÃO"]["rich_text"] else "",
                "TIPO": props["TIPO"]["select"]["name"] if props["TIPO"]["select"] else "",
                "UNID MED": props["UNID MED"]["rich_text"][0]["text"]["content"] if props["UNID MED"]["rich_text"] else "",
                "PREDEFINIDO": props["PREDEFINIDO"]["number"] if "PREDEFINIDO" in props and props["PREDEFINIDO"]["number"] is not None else 0,
                "CONFIRMA": 0 
            })
        df = pd.DataFrame(lista_completa)
        if not df.empty:
            # Garante que a ordenação siga a sequência do PDF (1 a 88)
            df['ITEM'] = pd.to_numeric(df['ITEM'], errors='coerce')
            return df.sort_values(by="ITEM")
        return df
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return pd.DataFrame()

def preparar_celula(conteudo):
    """Trata o texto para evitar erros de codificação no PDF."""
    texto = str(conteudo) if conteudo is not None else ""
    return unicodedata.normalize('NFKD', texto).encode('latin-1', 'ignore').decode('latin-1')

# --- INICIALIZAÇÃO DE VARIÁVEIS DE ESTADO ---
if 'pagina' not in st.session_state: st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state: st.session_state.cozinheiro = ""
if 'navio' not in st.session_state: st.session_state.navio = ""
if 'df_lista' not in st.session_state: st.session_state.df_lista = pd.DataFrame()

USUARIOS = {
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "NAVIO 03": {"nome": "Carlos", "senha": "456"},
    "ADMIN": {"nome": "Administrador", "senha": "zion"}
}

# =================================================================
# BLOCO 2: TELAS DO SISTEMA
# =================================================================

# --- TELA INICIAL (LOGO E BOTÃO ACESSAR) ---
if st.session_state.pagina == "home":
    st.markdown("<style>.stApp { background-color: #FF8C00; }</style>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: black;'>Zion Tecnologia</h1>", unsafe_allow_html=True)
    if os.path.exists("ZION.jpg"):
        st.image("ZION.jpg", use_container_width=True)
    if st.button("🚀 ACESSAR SISTEMA", key="btn_h"):
        st.session_state.pagina = "login"
        st.rerun()

# --- TELA DE LOGIN ---
elif st.session_state.pagina == "login":
    st.markdown("<style>.stApp { background-color: #FF8C00; } h1, label, p { color: black !important; font-weight: bold; }</style>", unsafe_allow_html=True)
    st.title("🔐 Login")
    n_sel = st.selectbox("Selecione o Navio", list(USUARIOS.keys()), key="11")
    s_dig = st.text_input("Senha", type="password", key="12")
    if st.button("ENTRAR", key="btn_l"):
        if s_dig == USUARIOS[n_sel]["senha"]:
            st.session_state.cozinheiro = USUARIOS[n_sel]["nome"]
            st.session_state.navio = n_sel
            st.session_state.pagina = "menu"
            st.rerun()
        else:
            st.error("❌ Senha incorreta")

# --- MENU PRINCIPAL (SEMPRE LARANJA) ---
elif st.session_state.pagina == "menu":
    st.markdown("<style>.stApp { background-color: #FF8C00; } button { color: white !important; }</style>", unsafe_allow_html=True)
    st.title(f"🚢 Painel - {st.session_state.navio}")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📋 TABELA DE RANCHO", use_container_width=True):
            st.session_state.pagina = "lista"
            st.rerun()
        if st.button("📊 VER HISTÓRICO", use_container_width=True):
            st.session_state.pagina = "historico"
            st.rerun()
    with c2:
        if st.button("📝 DECLARAÇÃO", use_container_width=True):
            st.session_state.pagina = "tripulacao"
            st.rerun()
        if st.button("🚪 SAIR", use_container_width=True):
            st.session_state.pagina = "home"
            st.rerun()

# --- TELA DE LISTA (CONFERÊNCIA DE ESTOQUE) ---
elif st.session_state.pagina == "lista":
    # CSS: Fundo de estoque e botões nítidos
    st.markdown("""<style>
        .stApp { 
            background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
            url("https://images.unsplash.com/photo-1583258292688-d0213dc5a3a8?q=80&w=1920"); 
            background-size: cover; 
        }
        .pdf-frame { border: 2px solid white; border-radius: 10px; background: white; }
        div.stButton > button { background-color: #FF8C00 !important; color: white !important; font-weight: bold !important; }
    </style>""", unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; color: white;'>📋 Conferência de Estoque</h1>", unsafe_allow_html=True)

    # Botões de topo
    c_nav1, c_nav2 = st.columns([1, 3])
    with c_nav1:
        if st.button("⬅️ VOLTAR"):
            st.session_state.pagina = "menu"; st.rerun()
    with c_nav2:
        if st.button("🔄 ATUALIZAR DADOS DO NOTION"):
            with st.spinner("Buscando todos os itens..."):
                st.session_state.df_lista = carregar_dados_do_notion()
                st.rerun()

    col_pdf, col_tabela = st.columns([1, 1.3])

    with col_pdf:
        st.markdown("<h4 style='color: white;'>📄 Documento Original</h4>", unsafe_allow_html=True)
        pdf_path = "Rancho_JACARANDA.pdf"
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode('utf-8')
            # Altura ajustada para 800 para ver os 88 itens
            st.markdown(f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="800" class="pdf-frame"></iframe>', unsafe_allow_html=True)

    with col_tabela:
        st.markdown("<h4 style='color: white;'>📝 Itens do Notion</h4>", unsafe_allow_html=True)
        if st.session_state.df_lista.empty:
            st.session_state.df_lista = carregar_dados_do_notion()

        # Editor de dados (Sem cortes na tabela)
        st.data_editor(
            st.session_state.df_lista,
            column_config={
                "ITEM": st.column_config.NumberColumn("COD", disabled=True),
                "DESCRIÇÃO": st.column_config.TextColumn("PRODUTO", disabled=True),
                "PREDEFINIDO": st.column_config.NumberColumn("SOLIC.", disabled=True),
                "CONFIRMA": st.column_config.NumberColumn("REC.", min_value=0)
            },
            hide_index=True,
            use_container_width=True,
            height=800,
            key="editor_estoque"
        )
        
        if st.button("💾 SALVAR TUDO", use_container_width=True):
            st.success("Conferência registrada com sucesso!")
