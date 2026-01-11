import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime, timedelta
import unicodedata
from fpdf import FPDF
from PIL import Image
import os
import requests

# =================================================================
# BLOCO 1: CONFIGURAÇÕES INICIAIS
# =================================================================
st.set_page_config(page_title="Zion Rancho App", layout="wide")

COLUNAS_PADRAO = ["ITEM", "DESCRIÇÃO", "TIPO", "UNID MED", "PREDEFINIDO", "CONFIRMA"]

# IDs E TOKEN FIXOS (Para evitar tela branca por falta de Secrets)
NOTION_TOKEN = "ntn_jZ6353375938j9kJFqKWjD0N4ONt1rwP515tsIMwxtucHa"
DATABASE_ID = "2e3025de7b79803abe0efde74f87a2e1" # Tabela de Estoque
ID_HISTORICO_NOTION = "2e5025de7b79803187a4d8b865179440" # Sua nova tabela de histórico

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
# BLOCO 2: CONEXÃO COM NOTION (ESTOQUE)
# =================================================================
def carregar_dados_do_notion():
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
# BLOCO 3: ESTILO PADRÃO (AZUL)
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

# --- MENU PRINCIPAL ATUALIZADO (ADICIONADO O BOTÃO HISTÓRICO) ---
elif st.session_state.pagina == "menu":
    aplicar_estilo_azul()
    st.title(f"🚢 Painel - {st.session_state.navio}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 TABELA DE RANCHO"): st.session_state.pagina = "lista"; st.rerun()
        # BOTÃO NOVO
        if st.button("📜 VER HISTÓRICO"): st.session_state.pagina = "historico"; st.rerun()
    with col2:
        if st.button("👨‍✈️ DECLARAÇÃO"): st.session_state.pagina = "tripulacao"; st.rerun()
    
    if st.button("⬅️ SAIR"): st.session_state.pagina = "home"; st.rerun()

# --- BLOCO 6: CONFERÊNCIA DE ESTOQUE ---
elif st.session_state.pagina == "lista":
    st.markdown("""<style>.stApp { background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url("https://images.unsplash.com/photo-1583258292688-d0213dc5a3a8?q=80&w=1920"); background-size: cover; }</style>""", unsafe_allow_html=True)
    st.title("📋 Conferência de Estoque")
    if st.button("🔄 ATUALIZAR DADOS DO NOTION"):
        st.session_state.df_lista = carregar_dados_do_notion()
        st.rerun()
    df_editado = st.data_editor(st.session_state.df_lista, column_config={"ITEM": st.column_config.NumberColumn("CÓD.", disabled=True), "CONFIRMA": st.column_config.NumberColumn("SUA QTD", min_value=0)}, hide_index=True, use_container_width=True, key="editor_estoque_final")
    if st.button("⬅️ VOLTAR AO MENU"): st.session_state.pagina = "menu"; st.rerun()

# --- BLOCO 8: A BENDITA TELA DE HISTÓRICO (PROTEGIDA) ---
elif st.session_state.pagina == "historico":
    aplicar_estilo_azul()
    st.title("📜 Histórico de Registros")
    st.write(f"Filtrando dados para: **{st.session_state.navio}**")
    
    try:
        url_hist = f"https://api.notion.com/v1/databases/{ID_HISTORICO_NOTION}/query"
        headers_h = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
        
        # Filtro para ver apenas o navio logado
        payload = {"filter": {"property": "Navio", "rich_text": {"equals": st.session_state.navio}}}
        res = requests.post(url_hist, headers=headers_h, json=payload)
        
        if res.status_code == 200:
            results = res.json().get("results", [])
            if results:
                dados_h = []
                for r in results:
                    p = r["properties"]
                    dados_h.append({
                        "Data": p["Data Pedido"]["date"]["start"] if p["Data Pedido"]["date"] else "-",
                        "Responsável": p["Cozinheiro"]["title"][0]["text"]["content"] if p["Cozinheiro"]["title"] else "N/A",
                        "Validade": p["Validade"]["date"]["start"] if p["Validade"]["date"] else "-",
                        "Escolta": p["Escolta"]["select"]["name"] if p["Escolta"]["select"] else "NÃO"
                    })
                st.dataframe(pd.DataFrame(dados_h), use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum pedido registrado para este navio.")
        else:
            st.error(f"Erro ao acessar o histórico no Notion (Status: {res.status_code})")
    except Exception as e:
        st.error(f"Falha ao carregar histórico: {e}")

    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"; st.rerun()

# --- BLOCO 7: TELA DE DECLARAÇÃO / TRIPULAÇÃO ---
elif st.session_state.pagina == "tripulacao":
    st.markdown("""<style>.stApp { background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url("https://images.unsplash.com/photo-1500514960902-e64e75c44c83?q=80&w=1920"); background-size: cover; }</style>""", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>⚓ Declaração de Reabastecimento</h1>", unsafe_allow_html=True)
    
    escolta = st.radio("O navio está com escolta?", ["NÃO", "SIM"], horizontal=True)
    dias_duracao = 12 if escolta == "SIM" else 15
    data_recebimento = st.date_input("Data prevista:", datetime.now())
    data_validade = data_recebimento + timedelta(days=dias_duracao)
    st.info(f"Validade até: {data_validade.strftime('%d/%m/%Y')}")

    if st.button("⬅️ VOLTAR AO MENU"): st.session_state.pagina = "menu"; st.rerun()
