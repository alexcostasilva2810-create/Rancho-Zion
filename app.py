import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime, timedelta
import unicodedata
from fpdf import FPDF
from PIL import Image
import os
import requests
import io
import base64
import pytz

# =================================================================
# BLOCO 1: CONFIGURAÇÕES, CONSTANTES E ESTADO
# =================================================================
st.set_page_config(page_title="Zion Rancho App", layout="wide")

COLUNAS_PADRAO = ["ITEM", "DESCRIÇÃO", "TIPO", "UNID MED", "PREDEFINIDO", "CONFIRMA"]
NOTION_TOKEN = "ntn_jZ6353375938j9kJFqKWjD0N4ONt1rwP515tsIMwxtucHa"
DATABASE_ID = "2e3025de7b79803abe0efde74f87a2e1" 
ID_HISTORICO_NOTION = "2e5025de7b79803187a4d8b865179440"

if 'pagina' not in st.session_state: st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state: st.session_state.cozinheiro = ""
if 'navio' not in st.session_state: st.session_state.navio = ""
if 'df_lista' not in st.session_state: st.session_state.df_lista = pd.DataFrame(columns=COLUNAS_PADRAO)

USUARIOS = {
    "JATOBA": {"nome": "CZA AUGUSTO", "senha": "5881"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "ADMINISTRADOR": {"nome": "ALEX", "senha": "2463"}
}

# =================================================================
# BLOCO 2: FUNÇÕES DE SUPORTE E CONEXÕES (API)
# =================================================================
def carregar_dados_do_notion():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            results = response.json().get("results", [])
            dados = []
            for page in results:
                p = page.get("properties", {})
                dados.append({
                    "ITEM": p.get("ITEM", {}).get("title", [{}])[0].get("plain_text", ""),
                    "DESCRIÇÃO": p.get("DESCRIÇÃO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "TIPO": p.get("TIPO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "UNID MED": p.get("UNID MED", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "PREDEFINIDO": p.get("PREDEFINIDO", {}).get("number", 0),
                    "CONFIRMA": 0
                })
            df = pd.DataFrame(dados)
            df['ITEM'] = pd.to_numeric(df['ITEM'], errors='coerce')
            return df.sort_values(by='ITEM').reset_index(drop=True)
        return st.session_state.df_lista
    except: return st.session_state.df_lista

def aplicar_estilo_azul():
    st.markdown("<style>.stApp { background-color: #4169E1 !important; } h1,h2,h3,p,label { color: white !important; } div.stButton > button { background-color: #FF8C00 !important; color: black !important; font-weight: 900; border-radius: 10px; }</style>", unsafe_allow_html=True)

# =================================================================
# BLOCO 3: TELA HOME (DESIGN OFFSHORE E LOGO ZION2)
# =================================================================
if st.session_state.pagina == "home":
    st.markdown("""
        <style>
        .stApp {
            background: radial-gradient(circle, #0e1117 0%, #000000 100%);
            background-image: url("https://www.transparenttextures.com/patterns/carbon-fibre.png");
        }
        @keyframes pulse-shimmer {
            0% { box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.4); transform: scale(1); }
            50% { box-shadow: 0 0 20px 5px rgba(255, 165, 0, 0.6); transform: scale(1.02); }
            100% { box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.4); transform: scale(1); }
        }
        .main-container { display: flex; flex-direction: column; align-items: center; justify-content: center; }
        
        div.stButton > button {
            background: linear-gradient(145deg, #d1d1d1, #f0f0f0) !important;
            color: #1a365d !important;
            font-weight: 800 !important;
            border-radius: 60px 60px 15px 15px !important;
            height: 70px !important; width: 280px !important;
            animation: pulse-shimmer 3s infinite !important;
            transition: all 0.4s ease-in-out !important;
        }
        div.stButton > button:hover {
            transform: translateY(-5px) scale(1.05) !important;
            box-shadow: 0 10px 30px rgba(255, 69, 0, 0.8) !important;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    try:
        st.image("zion2.jpg", use_container_width=True) # Sua nova imagem offshore
    except:
        st.markdown("<h1 style='color:white; text-align:center;'>ZION TECNOLOGIA</h1>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✨ INICIAR"):
        st.session_state.pagina = "login"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# =================================================================
# BLOCO 4: TELA DE LOGIN (ACESSO RESTRITO)
# =================================================================
elif st.session_state.pagina == "login":
    st.markdown("<h1 style='text-align: center; color: white;'>🔐 Acesso Restrito</h1>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        navio_sel = st.selectbox("Selecione sua Embarcação", list(USUARIOS.keys()))
        senha_dig = st.text_input("Senha de Acesso", type="password")
        if st.button("🚀 ENTRAR", use_container_width=True):
            dados = USUARIOS.get(navio_sel)
            if dados and senha_dig == dados["senha"]:
                st.session_state.cozinheiro = dados["nome"]
                st.session_state.navio = navio_sel
                st.session_state.pagina = "menu"
                st.rerun()
            else: st.error("❌ Senha incorreta!")
        if st.button("⬅️ VOLTAR", use_container_width=True):
            st.session_state.pagina = "home"; st.rerun()

# =================================================================
# BLOCO 5: MENU PRINCIPAL
# =================================================================
elif st.session_state.pagina == "menu":
    aplicar_estilo_azul()
    st.title(f"🚢 Painel - {st.session_state.navio}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 TABELA DE RANCHO", use_container_width=True): st.session_state.pagina = "lista"; st.rerun()
        if st.button("📜 VER HISTÓRICO", use_container_width=True): st.session_state.pagina = "historico"; st.rerun()
    with col2:
        if st.button("👨‍✈️ DECLARAÇÃO", use_container_width=True): st.session_state.pagina = "tripulacao"; st.rerun()
    if st.button("⬅️ LOGOUT"): st.session_state.pagina = "home"; st.rerun()

# =================================================================
# BLOCO 6: LISTA DE RANCHO (CONFERÊNCIA)
# =================================================================
elif st.session_state.pagina == "lista":
    st.title("📋 Conferência de Estoque")
    if st.button("🔄 ATUALIZAR TABELA"):
        st.session_state.df_lista = carregar_dados_do_notion()
        st.rerun()
    
    df_editado = st.data_editor(st.session_state.df_lista, hide_index=True, use_container_width=True)
    
    if st.button("⬅️ MENU"): st.session_state.pagina = "menu"; st.rerun()

# =================================================================
# BLOCO 7: TELA DE DECLARAÇÃO (TRIPULAÇÃO E ASSINATURA)
# =================================================================
elif st.session_state.pagina == "tripulacao":
    st.title("⚓ Declaração de Reabastecimento")
    
    with st.form("form_declaracao"):
        c1, c2 = st.columns(2)
        with c1:
            origem = st.text_input("Porto de Origem", value="Manaus")
            data_recebimento = st.date_input("Data prevista para o novo rancho:")
        with c2:
            destino = st.text_input("Porto de Destino", value="Belem")
            qtde_trip = st.number_input("Qtde Tripulante:", min_value=1, value=9)
        
        canvas_result = st_canvas(stroke_width=3, stroke_color="#000000", background_color="#FFFFFF", height=120, key="assinatura")
        
        if st.form_submit_button("💾 SALVAR E ENVIAR"):
            # Lógica de salvar no Notion e PDF aqui (conforme seu original)
            st.success("Dados salvos com sucesso!")

# =================================================================
# BLOCO 8: HISTÓRICO (NOTION)
# =================================================================
elif st.session_state.pagina == "historico":
    st.title("🗄️ Histórico de Documentos")
    if st.button("⬅️ MENU"): st.session_state.pagina = "menu"; st.rerun()
    # Filtros e busca no Notion aqui (conforme seu original)
