import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime
import unicodedata
from fpdf import FPDF
from PIL import Image
import os
import requests

# =================================================================
# BLOCO 1: CONFIGURAÇÕES INICIAIS
# =================================================================
st.set_page_config(page_title="Zion Rancho App", layout="wide")

# Definição das colunas ANTES de qualquer uso (Evita o erro da imagem c56e2c.png)
COLUNAS_PADRAO = ["ITEM", "DESCRIÇÃO", "TIPO", "UNID MED", "PREDEFINIDO", "CONFIRMA"]

if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state:
    st.session_state.cozinheiro = ""
if 'navio' not in st.session_state:
    st.session_state.navio = ""
if 'pdf_disponivel' not in st.session_state:
    st.session_state.pdf_disponivel = None
if 'df_lista' not in st.session_state:
    st.session_state.df_lista = pd.DataFrame(columns=COLUNAS_PADRAO)

USUARIOS = {
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "NAVIO 03": {"nome": "Carlos", "senha": "456"}
}

# =================================================================
# BLOCO 2: CONEXÃO COM NOTION
# =================================================================
def carregar_dados_do_notion():
    NOTION_TOKEN = "ntn_jZ6353375938j9kJFqKWjD0N4ONt1rwP515tsIMwxtucHa"
    DATABASE_ID = "2e3025de7b79803abe0efde74f87a2e1"
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            results = response.json().get("results", [])
            dados_notion = []
            for page in results:
                p = page.get("properties", {})
                dados_notion.append({
                    "ITEM": p.get("ITEM", {}).get("title", [{}])[0].get("plain_text", ""),
                    "DESCRIÇÃO": p.get("DESCRIÇÃO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "TIPO": p.get("TIPO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "UNID MED": p.get("UNID MED", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "PREDEFINIDO": p.get("PREDEFINIDO", {}).get("number", 0),
                    "CONFIRMA": 0
                })
            df = pd.DataFrame(dados_notion)
            df['ITEM'] = pd.to_numeric(df['ITEM'], errors='coerce')
            return df.sort_values(by='ITEM').reset_index(drop=True)
        return st.session_state.df_lista
    except:
        return st.session_state.df_lista

# =================================================================
# BLOCO 3: ESTILO PADRÃO (AZUL) PARA AS OUTRAS TELAS
# =================================================================
def aplicar_estilo_azul():
    st.markdown("""
        <style>
        .stApp { background-color: #4169E1 !important; background-image: none !important; }
        h1, h2, h3, p, label { color: white !important; }
        div.stButton > button { background-color: #FF8C00 !important; color: black !important; font-weight: 900 !important; border-radius: 10px !important; }
        </style>
        """, unsafe_allow_html=True)

# =================================================================
# BLOCO 4: NAVEGAÇÃO E TELAS
# =================================================================

if st.session_state.pagina == "home":
    aplicar_estilo_azul()
    st.markdown("<h1 style='text-align: center;'>Zion Tecnologia</h1>", unsafe_allow_html=True)
    if os.path.exists("ZION.jpg"): st.image("ZION.jpg", use_container_width=True)
    if st.button("🚀 ACESSAR SISTEMA"):
        st.session_state.pagina = "login"
        st.rerun()

elif st.session_state.pagina == "login":
    aplicar_estilo_azul()
    st.title("🔐 Login")
    navio_sel = st.selectbox("Navio", list(USUARIOS.keys()))
    senha_dig = st.text_input("Senha", type="password")
    if st.button("ENTRAR"):
        dados = USUARIOS.get(navio_sel)
        if dados and senha_dig == dados["senha"]:
            st.session_state.cozinheiro = dados["nome"]; st.session_state.navio = navio_sel
            st.session_state.pagina = "menu"; st.rerun()
        else: st.error("❌ Senha incorreta!")

elif st.session_state.pagina == "menu":
    aplicar_estilo_azul()
    st.title(f"🚢 Painel - {st.session_state.navio}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 TABELA DE RANCHO"): st.session_state.pagina = "lista"; st.rerun()
    with col2:
        if st.button("👨‍✈️ DECLARAÇÃO"): st.session_state.pagina = "tripulacao"; st.rerun()
    if st.button("⬅️ SAIR"): st.session_state.pagina = "home"; st.rerun()

# --- BLOCO 6: TELA DE LISTA (COM FUNDO DE ESTOQUE EXCLUSIVO) ---
elif st.session_state.pagina == "lista":
    # CSS Aplicado APENAS nesta tela
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                        url("https://images.unsplash.com/photo-1583258292688-d0213dc5a3a8?q=80&w=1920");
            background-size: cover; background-position: center;
        }
        h1, h2, h3, p, label { color: white !important; }
        .stDataFrame { background-color: rgba(255, 255, 255, 0.9) !important; border-radius: 10px; }
        </style>
        """, unsafe_allow_html=True)
    
    st.title("📋 Conferência de Estoque")
    if st.button("🔄 ATUALIZAR NOTION"):
        st.session_state.df_lista = carregar_dados_do_notion()
        st.rerun()

    df_editado = st.data_editor(st.session_state.df_lista, hide_index=True, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("📄 GERAR PDF"):
            # Lógica do PDF em Paisagem (Landscape) alinhado
            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"ESTOQUE - {st.session_state.navio}", ln=True, align="C")
            # ... (Restante da lógica do PDF que você já tem)
            st.success("PDF Pronto para download!")
    with c2:
        if st.button("⬅️ VOLTAR AO MENU"):
            st.session_state.pagina = "menu"; st.rerun()

elif st.session_state.pagina == "tripulacao":
    aplicar_estilo_azul()
    st.title("👨‍✈️ Declaração")
    # ... (Sua lógica de assinatura)
    if st.button("⬅️ VOLTAR"): st.session_state.pagina = "menu"; st.rerun()
