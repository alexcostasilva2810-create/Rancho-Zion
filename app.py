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

NOTION_TOKEN = "ntn_jZ6353375938j9kJFqKWjD0N4ONt1rwP515tsIMwxtucHa"
DATABASE_ID = "2e3025de7b79803abe0efde74f87a2e1" 
ID_HISTORICO_NOTION = "2e5025de7b79803187a4d8b865179440"

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
# BLOCO 2: FUNÇÕES TÉCNICAS
# =================================================================
def aplicar_estilo_azul():
    st.markdown("<style>.stApp { background-color: #4169E1 !important; } h1,h2,h3,p,label { color: white !important; } div.stButton > button { background-color: #FF8C00 !important; color: black !important; font-weight: 900; border-radius: 10px; }</style>", unsafe_allow_html=True)

def carregar_dados_do_notion():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Notion-Version": "2022-06-28"}
    res = requests.post(url, headers=headers)
    if res.status_code == 200:
        results = res.json().get("results", [])
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
        return pd.DataFrame(dados)
    return pd.DataFrame()

# =================================================================
# NAVEGAÇÃO
# =================================================================

if st.session_state.pagina == "home":
    aplicar_estilo_azul()
    st.markdown("<h1 style='text-align: center;'>Zion Tecnologia</h1>", unsafe_allow_html=True)
    if os.path.exists("ZION.jpg"):
        col1, col2, col3 = st.columns([1,1,1])
        with col2: st.image("ZION.jpg", width=300)
    if st.button("🚀 ACESSAR SISTEMA", key="btn_home"): st.session_state.pagina = "login"; st.rerun()

elif st.session_state.pagina == "login":
    aplicar_estilo_azul(); st.title("🔐 Login")
    navio_sel = st.selectbox("Navio", list(USUARIOS.keys()), key="sel_navio")
    senha_dig = st.text_input("Senha", type="password", key="input_senha")
    if st.button("ENTRAR", key="btn_login"):
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
        if st.button("📋 TABELA DE RANCHO", use_container_width=True, key="m1"): st.session_state.pagina = "lista"; st.rerun()
        if st.button("📜 VER HISTÓRICO", use_container_width=True, key="m2"): st.session_state.pagina = "historico"; st.rerun()
    with col2:
        if st.button("👨‍✈️ DECLARAÇÃO", use_container_width=True, key="m3"): st.session_state.pagina = "tripulacao"; st.rerun()
        if st.session_state.navio == "ADMIN":
            if st.button("👑 PAINEL ADM", use_container_width=True, key="m4"): st.session_state.pagina = "admin"; st.rerun()
    if st.button("⬅️ SAIR", key="m5"): st.session_state.pagina = "home"; st.rerun()

# --- TELA DE LISTA (ESTOQUE) ---
elif st.session_state.pagina == "lista":
    st.markdown("""<style>.stApp { background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("https://images.unsplash.com/photo-1583258292688-d0213dc5a3a8?q=80&w=1920"); background-size: cover; }</style>""", unsafe_allow_html=True)
    st.title("📋 Conferência de Estoque")
    if st.button("🔄 ATUALIZAR DADOS", key="upd_notion"):
        st.session_state.df_lista = carregar_dados_do_notion()
        st.rerun()
    
    if not st.session_state.df_lista.empty:
        st.data_editor(st.session_state.df_lista, hide_index=True, use_container_width=True, key="editor_estoque")
    
    if st.button("⬅️ VOLTAR", key="v1"): st.session_state.pagina = "menu"; st.rerun()

# --- TELA DE DECLARAÇÃO (RESTAURADA) ---
elif st.session_state.pagina == "tripulacao":
    st.markdown("""<style>.stApp { background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("https://images.unsplash.com/photo-1500514960902-e64e75c44c83?q=80&w=1920"); background-size: cover; }</style>""", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>⚓ Declaração de Reabastecimento</h1>", unsafe_allow_html=True)
    
    escolta = st.radio("O navio está com escolta?", ["NÃO", "SIM"], horizontal=True, key="radio_esc")
    dias = 12 if escolta == "SIM" else 15
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        data_rec = st.date_input("Data prevista para receber:", datetime.now(), key="dt_rec")
        data_val = data_rec + timedelta(days=dias)
    with col_d2:
        st.success(f"Validade estimada: {data_val.strftime('%d/%m/%Y')}")

    with st.form("form_dec"):
        c1, c2 = st.columns(2)
        with c1:
            lot = st.number_input("Tripulantes:", min_value=1, value=16, key="f1")
            orig = st.text_input("Porto Origem:", value="Porto Velho", key="f2")
        with c2:
            dt_ult = st.date_input("Data do último rancho:", datetime.now(), key="f3")
            dest = st.text_input("Porto Destino:", value="Novo Remanso", key="f4")
        
        extras = st.text_area("Necessidades Extras:", value="Ex: Água mineral, vassouras...", key="f5")
        canvas_res = st_canvas(stroke_width=3, stroke_color="#000", background_color="#FFF", height=120, key="f6")
        
        if st.form_submit_button("💾 SALVAR E GRAVAR HISTÓRICO"):
            headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
            payload = {
                "parent": {"database_id": ID_HISTORICO_NOTION},
                "properties": {
                    "Cozinheiro": {"title": [{"text": {"content": st.session_state.cozinheiro}}]},
                    "Navio": {"rich_text": [{"text": {"content": st.session_state.navio}}]},
                    "Data Pedido": {"date": {"start": data_rec.strftime("%Y-%m-%d")}},
                    "Validade": {"date": {"start": data_val.strftime("%Y-%m-%d")}}
                }
            }
            requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
            st.success("✅ Histórico Gravado com Sucesso!"); st.balloons()

    if st.button("⬅️ VOLTAR", key="v2"): st.session_state.pagina = "menu"; st.rerun()

# --- PAINEL ADM (COLUNAS PEDIDAS) ---
elif st.session_state.pagina == "admin":
    aplicar_estilo_azul()
    st.title("👑 Painel do Administrador")
    url = f"https://api.notion.com/v1/databases/{ID_HISTORICO_NOTION}/query"
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Notion-Version": "2022-06-28"}
    res = requests.post(url, headers=headers)
    if res.status_code == 200:
        results = res.json().get("results", [])
        dados_adm = []
        for r in results:
            p = r["properties"]
            dados_adm.append({
                "USUÁRIO": p["Cozinheiro"]["title"][0]["text"]["content"] if p["Cozinheiro"]["title"] else "",
                "NAVIO": p["Navio"]["rich_text"][0]["text"]["content"] if p["Navio"]["rich_text"] else "",
                "ANEXO LISTA": "📎 Ver PDF",
                "ANEXO DECLARAÇÃO": "📄 Ver PDF",
                "DATA ÚLTIMO RANCHO": p["Data Pedido"]["date"]["start"] if p["Data Pedido"]["date"] else ""
            })
        st.table(pd.DataFrame(dados_adm))
    
    if st.button("⬅️ VOLTAR", key="v3"): st.session_state.pagina = "menu"; st.rerun()
