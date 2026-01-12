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
# BLOCO 1: CONFIGURAÇÕES, IDs E ESTADOS
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
    "JACARANDA": {"nome": "GABRIEL MORANGO", "senha": "4599"}
}

# =================================================================
# BLOCO 2: FUNÇÕES DE ESTILO E CONEXÃO
# =================================================================
def aplicar_estilo_azul():
    st.markdown("<style>.stApp { background-color: #4169E1 !important; } h1,h2,h3,p,label { color: white !important; } div.stButton > button { background-color: #FF8C00 !important; color: black !important; font-weight: 900; border-radius: 10px; }</style>", unsafe_allow_html=True)

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
            return pd.DataFrame(dados)
    except: return pd.DataFrame()

# =================================================================
# BLOCO 3: TELA HOME (INICIAL)
# =================================================================
if st.session_state.pagina == "home":
    aplicar_estilo_azul()
    st.markdown("<h1 style='text-align: center;'>Zion Tecnologia</h1>", unsafe_allow_html=True)
    if os.path.exists("ZION.jpg"):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2: st.image("ZION.jpg", width=250)
    if st.button("🚀 ACESSAR SISTEMA", use_container_width=True):
        st.session_state.pagina = "login"; st.rerun()

# =================================================================
# BLOCO 4: TELA DE LOGIN
# =================================================================
elif st.session_state.pagina == "login":
    aplicar_estilo_azul()
    st.title("🔐 Login")
    navio_sel = st.selectbox("Selecione sua Embarcação", list(USUARIOS.keys()))
    senha_dig = st.text_input("Senha de Acesso", type="password")
    if st.button("ENTRAR", use_container_width=True):
        dados = USUARIOS.get(navio_sel)
        if dados and senha_dig == dados["senha"]:
            st.session_state.cozinheiro = dados["nome"]
            st.session_state.navio = navio_sel
            st.session_state.pagina = "menu"; st.rerun()
        else: st.error("❌ Senha incorreta!")

# =================================================================
# BLOCO 5: MENU PRINCIPAL
# =================================================================
elif st.session_state.pagina == "menu":
    aplicar_estilo_azul()
    st.title(f"🚢 {st.session_state.navio}")
    st.subheader(f"Responsável: {st.session_state.cozinheiro}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 TABELA DE RANCHO", use_container_width=True): st.session_state.pagina = "lista"; st.rerun()
        if st.button("📜 VER HISTÓRICO", use_container_width=True): st.session_state.pagina = "historico"; st.rerun()
    with col2:
        if st.button("👨‍✈️ DECLARAÇÃO", use_container_width=True): st.session_state.pagina = "tripulacao"; st.rerun()
    if st.button("⬅️ SAIR"): st.session_state.pagina = "home"; st.rerun()

# =================================================================
# BLOCO 6: CONFERÊNCIA DE ESTOQUE (LISTA)
# =================================================================
elif st.session_state.pagina == "lista":
    st.title("📋 Conferência de Estoque")
    if st.button("🔄 CARREGAR ITENS DO NOTION"):
        st.session_state.df_lista = carregar_dados_do_notion()
        st.rerun()
    
    if not st.session_state.df_lista.empty:
        df_editado = st.data_editor(st.session_state.df_lista, hide_index=True, use_container_width=True)
    
    if st.button("⬅️ VOLTAR"): st.session_state.pagina = "menu"; st.rerun()

# =================================================================
# BLOCO 7: DECLARAÇÃO E SALVAMENTO (HISTÓRICO)
# =================================================================
elif st.session_state.pagina == "tripulacao":
    st.markdown("<h2 style='text-align: center;'>⚓ Declaração de Rancho</h2>", unsafe_allow_html=True)
    
    escolta = st.radio("Escolta?", ["NÃO", "SIM"], horizontal=True, key="esc_k")
    dias = 12 if escolta == "SIM" else 15
    data_rec = st.date_input("Data Prevista:", datetime.now(), key="dt_k")
    data_val = data_rec + timedelta(days=dias)
    
    st.info(f"Validade estimada: {data_val.strftime('%d/%m/%Y')}")

    with st.form("form_declaracao"):
        lot = st.number_input("Tripulantes:", min_value=1, value=16)
        orig = st.text_input("Porto Origem:", value="Porto Velho")
        dest = st.text_input("Porto Destino:", value="Novo Remanso")
        canvas_res = st_canvas(stroke_width=3, height=120, key="canv_k")
        
        if st.form_submit_button("💾 SALVAR REGISTRO"):
            # ENVIO PARA O NOTION
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
            res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
            if res.status_code == 200: st.success("✅ Histórico Gravado!"); st.balloons()
            else: st.error("Erro ao gravar no Notion.")

    if st.button("⬅️ VOLTAR"): st.session_state.pagina = "menu"; st.rerun()

# =================================================================
# BLOCO 8: VISUALIZAÇÃO DO HISTÓRICO
# =================================================================
elif st.session_state.pagina == "historico":
    st.title("📜 Registros de Viagens")
    url_h = f"https://api.notion.com/v1/databases/{ID_HISTORICO_NOTION}/query"
    headers_h = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    payload = {"filter": {"property": "Navio", "rich_text": {"equals": st.session_state.navio}}}
    
    res = requests.post(url_h, headers=headers_h, json=payload)
    if res.status_code == 200:
        results = res.json().get("results", [])
        lista_h = []
        for r in results:
            p = r["properties"]
            lista_h.append({
                "Data": p["Data Pedido"]["date"]["start"] if p["Data Pedido"]["date"] else "",
                "Cozinheiro": p["Cozinheiro"]["title"][0]["text"]["content"] if p["Cozinheiro"]["title"] else "",
                "Validade": p["Validade"]["date"]["start"] if p["Validade"]["date"] else ""
            })
        st.table(pd.DataFrame(lista_h))
    
    if st.button("⬅️ VOLTAR"): st.session_state.pagina = "menu"; st.rerun()
