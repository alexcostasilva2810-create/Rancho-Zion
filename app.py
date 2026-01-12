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
# BLOCO 1: CONFIGURAÇÕES E IDs
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
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "NAVIO 03": {"nome": "Carlos", "senha": "456"},
    "ADMIN": {"nome": "Administrador", "senha": "zion"}
}

# =================================================================
# BLOCO 2: FUNÇÕES AUXILIARES
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
            return df
    except: return st.session_state.df_lista

def aplicar_estilo_azul():
    st.markdown("<style>.stApp { background-color: #4169E1 !important; } h1,h2,h3,p,label { color: white !important; } div.stButton > button { background-color: #FF8C00 !important; color: black !important; font-weight: 900; border-radius: 10px; }</style>", unsafe_allow_html=True)

# =================================================================
# BLOCO 4: NAVEGAÇÃO
# =================================================================

if st.session_state.pagina == "home":
    aplicar_estilo_azul()
    st.markdown("<h1 style='text-align: center;'>Zion Tecnologia</h1>", unsafe_allow_html=True)
    if os.path.exists("ZION.jpg"): st.image("ZION.jpg", width=300)
    if st.button("🚀 ACESSAR SISTEMA"): st.session_state.pagina = "login"; st.rerun()

elif st.session_state.pagina == "login":
    aplicar_estilo_azul(); st.title("🔐 Login")
    navio_sel = st.selectbox("Selecione o Usuário/Navio", list(USUARIOS.keys()))
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
        if st.button("📋 TABELA DE RANCHO", use_container_width=True): st.session_state.pagina = "lista"; st.rerun()
        if st.button("📜 SEU HISTÓRICO", use_container_width=True): st.session_state.pagina = "historico"; st.rerun()
    with col2:
        if st.button("👨‍✈️ NOVA DECLARAÇÃO", use_container_width=True): st.session_state.pagina = "tripulacao"; st.rerun()
        if st.session_state.navio == "ADMIN":
            if st.button("👑 PAINEL ADM (VER TUDO)", use_container_width=True): st.session_state.pagina = "admin"; st.rerun()
    if st.button("⬅️ SAIR"): st.session_state.pagina = "home"; st.rerun()

# --- BLOCO 6: TELA DE LISTA (CONFERÊNCIA) ---
elif st.session_state.pagina == "lista":
    st.title("📋 Conferência de Estoque")
    if st.button("🔄 ATUALIZAR DADOS DO NOTION"):
        st.session_state.df_lista = carregar_dados_do_notion()
        st.rerun()
    df_editado = st.data_editor(st.session_state.df_lista, hide_index=True, use_container_width=True)
    if st.button("⬅️ VOLTAR"): st.session_state.pagina = "menu"; st.rerun()

# --- BLOCO 7: TELA DE DECLARAÇÃO (GRAVAÇÃO NO NOTION) ---
elif st.session_state.pagina == "tripulacao":
    st.title("⚓ Declaração de Reabastecimento")
    escolta = st.radio("O navio está com escolta?", ["NÃO", "SIM"], horizontal=True)
    dias_duracao = 12 if escolta == "SIM" else 15
    data_recebimento = st.date_input("Data prevista:", datetime.now())
    data_validade = data_recebimento + timedelta(days=dias_duracao)

    with st.form("form_declaracao"):
        lotacao = st.number_input("Tripulantes:", min_value=1, value=16)
        origem = st.text_input("Porto Origem", value="Porto Velho")
        destino = st.text_input("Porto Destino", value="Novo Remanso")
        canvas_result = st_canvas(stroke_width=3, stroke_color="#000", background_color="#EEE", height=100, key="canvas")
        
        enviar = st.form_submit_button("💾 SALVAR E GERAR PDF")
        
        if enviar:
            # 1. ENVIAR PARA O NOTION (HISTÓRICO)
            headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
            payload = {
                "parent": {"database_id": ID_HISTORICO_NOTION},
                "properties": {
                    "Cozinheiro": {"title": [{"text": {"content": st.session_state.cozinheiro}}]},
                    "Navio": {"rich_text": [{"text": {"content": st.session_state.navio}}]},
                    "Data Pedido": {"date": {"start": data_recebimento.strftime("%Y-%m-%d")}},
                    "Validade": {"date": {"start": data_validade.strftime("%Y-%m-%d")}}
                }
            }
            res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
            if res.status_code == 200:
                st.success("✅ Pedido Registrado no Histórico!")
                st.balloons()
            else:
                st.error("Erro ao gravar no Notion.")

    if st.button("⬅️ VOLTAR"): st.session_state.pagina = "menu"; st.rerun()

# --- BLOCO 8: TELA DE HISTÓRICO (USUÁRIO) ---
elif st.session_state.pagina == "historico":
    aplicar_estilo_azul(); st.title("📜 Seu Histórico")
    url_h = f"https://api.notion.com/v1/databases/{ID_HISTORICO_NOTION}/query"
    headers_h = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    payload = {"filter": {"property": "Navio", "rich_text": {"equals": st.session_state.navio}}}
    res = requests.post(url_h, headers=headers_h, json=payload)
    if res.status_code == 200:
        results = res.json().get("results", [])
        dados_h = []
        for r in results:
            p = r["properties"]
            dados_h.append({
                "Data": p["Data Pedido"]["date"]["start"] if p["Data Pedido"]["date"] else "N/A",
                "Responsável": p["Cozinheiro"]["title"][0]["text"]["content"] if p["Cozinheiro"]["title"] else "N/A",
                "Validade": p["Validade"]["date"]["start"] if p["Validade"]["date"] else "N/A"
            })
        st.dataframe(pd.DataFrame(dados_h), use_container_width=True)
    if st.button("⬅️ VOLTAR"): st.session_state.pagina = "menu"; st.rerun()

# --- BLOCO 9: PAINEL ADMINISTRADOR (VISÃO GERAL) ---
elif st.session_state.pagina == "admin":
    aplicar_estilo_azul(); st.title("👑 Painel Administrativo")
    st.subheader("Todas as Solicitações")
    
    url_adm = f"https://api.notion.com/v1/databases/{ID_HISTORICO_NOTION}/query"
    headers_adm = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    
    res_adm = requests.post(url_adm, headers=headers_adm)
    if res_adm.status_code == 200:
        results = res_adm.json().get("results", [])
        dados_adm = []
        for r in results:
            p = r["properties"]
            dados_adm.append({
                "USUÁRIO": p["Cozinheiro"]["title"][0]["text"]["content"] if p["Cozinheiro"]["title"] else "N/A",
                "NAVIO": p["Navio"]["rich_text"][0]["text"]["content"] if p["Navio"]["rich_text"] else "N/A",
                "LISTA DE RANCHO": "✅ REGISTRADO",
                "DECLARAÇÃO": "📄 PDF DISPONÍVEL",
                "DATA ÚLTIMO RANCHO": p["Data Pedido"]["date"]["start"] if p["Data Pedido"]["date"] else "N/A"
            })
        st.dataframe(pd.DataFrame(dados_adm), use_container_width=True, hide_index=True)
    
    if st.button("⬅️ VOLTAR"): st.session_state.pagina = "menu"; st.rerun()
