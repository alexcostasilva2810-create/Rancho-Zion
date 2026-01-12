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

def preparar_celula(conteudo):
    texto = str(conteudo) if conteudo is not None else ""
    return unicodedata.normalize('NFKD', texto).encode('latin-1', 'ignore').decode('latin-1')

# =================================================================
# BLOCO 2: TELAS
# =================================================================

# --- HOME ---
if st.session_state.pagina == "home":
    st.markdown("<style>.stApp { background-color: #FF8C00; }</style>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: black;'>Zion Tecnologia</h1>", unsafe_allow_html=True)
    if os.path.exists("ZION.jpg"): st.image("ZION.jpg", use_container_width=True)
    if st.button("🚀 ACESSAR SISTEMA", key="btn_h"): st.session_state.pagina = "login"; st.rerun()

# --- LOGIN (FUNDO LARANJA / LETRA PRETA) ---
elif st.session_state.pagina == "login":
    st.markdown("""<style>
        .stApp { background-color: #FF8C00; }
        h1, label, p { color: black !important; font-weight: bold; }
        input { color: black !important; }
    </style>""", unsafe_allow_html=True)
    st.title("🔐 Login")
    n_sel = st.selectbox("Selecione o Navio", list(USUARIOS.keys()), key="l1")
    s_dig = st.text_input("Senha", type="password", key="l2")
    if st.button("ENTRAR", key="btn_l"):
        if s_dig == USUARIOS[n_sel]["senha"]:
            st.session_state.cozinheiro = USUARIOS[n_sel]["nome"]
            st.session_state.navio = n_sel
            st.session_state.pagina = "menu"; st.rerun()
        else: st.error("❌ Senha incorreta")

# --- MENU (SEMPRE LARANJA) ---
elif st.session_state.pagina == "menu":
    st.markdown("<style>.stApp { background-color: #FF8C00; } button { background-color: white !important; color: black !important; }</style>", unsafe_allow_html=True)
    st.title(f"🚢 Painel - {st.session_state.navio}")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📋 TABELA DE RANCHO", use_container_width=True, key="m1"): st.session_state.pagina = "lista"; st.rerun()
        if st.button("📜 VER HISTÓRICO", use_container_width=True, key="m2"): st.session_state.pagina = "historico"; st.rerun()
    with c2:
        if st.button("👨‍✈️ DECLARAÇÃO", use_container_width=True, key="m3"): st.session_state.pagina = "tripulacao"; st.rerun()
        if st.session_state.navio == "ADMIN":
            if st.button("👑 PAINEL ADM", use_container_width=True, key="m4"): st.session_state.pagina = "admin"; st.rerun()
    if st.button("⬅️ SAIR", key="m5"): st.session_state.pagina = "home"; st.rerun()

# --- TABELA DE RANCHO (TÍTULO VERDE / FUNDO ESTOQUE) ---
elif st.session_state.pagina == "lista":
    st.markdown("""<style>
        .stApp { background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("https://images.unsplash.com/photo-1583258292688-d0213dc5a3a8?q=80&w=1920"); background-size: cover; }
        h1 { color: #00FF00 !important; font-weight: bold; text-shadow: 2px 2px 4px #000; }
        label { color: white !important; }
    </style>""", unsafe_allow_html=True)
    st.title("📋 Conferência de Estoque")
    
    if st.button("🔄 ATUALIZAR NOTION", key="upd"):
        url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
        headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Notion-Version": "2022-06-28"}
        res = requests.post(url, headers=headers)
        if res.status_code == 200:
            dados = []
            for p in res.json().get("results", []):
                prop = p.get("properties", {})
                dados.append({
                    "ITEM": prop.get("ITEM", {}).get("title", [{}])[0].get("plain_text", ""),
                    "DESCRIÇÃO": prop.get("DESCRIÇÃO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "TIPO": prop.get("TIPO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "UNID MED": prop.get("UNID MED", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "PREDEFINIDO": prop.get("PREDEFINIDO", {}).get("number", 0),
                    "CONFIRMA": 0
                })
            st.session_state.df_lista = pd.DataFrame(dados)
            st.rerun()

    if not st.session_state.df_lista.empty:
        df_ed = st.data_editor(st.session_state.df_lista, hide_index=True, use_container_width=True, key="ed_r")
        if st.button("📥 SALVAR E GERAR PDF DO RANCHO", key="pdf_r"):
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Checklist de Rancho", ln=True, align="C")
            st.download_button("Baixar PDF", pdf.output(dest='S').encode('latin-1'), "rancho.pdf")

    if st.button("⬅️ VOLTAR", key="v_r"): st.session_state.pagina = "menu"; st.rerun()

# --- DECLARAÇÃO (PAISAGEM NAVIO / CAMPOS PRETOS) ---
elif st.session_state.pagina == "tripulacao":
    st.markdown("""<style>
        .stApp { background: linear-gradient(rgba(255,255,255,0.4), rgba(255,255,255,0.4)), url("https://images.unsplash.com/photo-1498084393753-b411b2d26b34?q=80&w=1920"); background-size: cover; }
        h1, label, p { color: black !important; font-weight: bold; }
        .stTextInput input, .stTextArea textarea, .stNumberInput input { color: black !important; background-color: white !important; }
    </style>""", unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center;'>⚓ Declaração de Reabastecimento</h1>", unsafe_allow_html=True)
    
    escolta = st.radio("O navio está com escolta?", ["NÃO", "SIM"], horizontal=True, key="rad_e")
    dias = 12 if escolta == "SIM" else 15
    dt_prev = st.date_input("Data prevista para receber:", datetime.now(), key="d_p")
    dt_val = dt_prev + timedelta(days=dias)
    st.warning(f"Atenção: Rancho durará até {dt_val.strftime('%d/%m/%Y')}")

    with st.form("f_dec"):
        c1, c2 = st.columns(2)
        with c1:
            st.number_input("Tripulantes:", min_value=1, value=16, key="lot")
            st.text_input("Porto Origem:", value="Porto Velho", key="orig")
        with c2:
            st.date_input("Data do último rancho:", datetime.now(), key="dt_u")
            st.text_input("Porto Destino:", value="Novo Remanso", key="dest")
        
        st.text_area("Necessidades Extras:", key="ext")
        st.write("Assinatura Digital:")
        canvas = st_canvas(stroke_width=3, stroke_color="#000", background_color="#FFF", height=100, key="canv")
        
        if st.form_submit_button("💾 SALVAR E GERAR PDF"):
            h = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
            body = {"parent": {"database_id": ID_HISTORICO_NOTION}, "properties": {
                "Cozinheiro": {"title": [{"text": {"content": st.session_state.cozinheiro}}]},
                "Navio": {"rich_text": [{"text": {"content": st.session_state.navio}}]},
                "Data Pedido": {"date": {"start": dt_prev.strftime("%Y-%m-%d")}},
                "Validade": {"date": {"start": dt_val.strftime("%Y-%m-%d")}}
            }}
            requests.post("https://api.notion.com/v1/pages", headers=h, json=body)
            st.success("✅ Documento Salvo no Histórico!")

    if st.button("⬅️ VOLTAR", key="v_t"): st.session_state.pagina = "menu"; st.rerun()

# --- HISTÓRICO (AGORA ATIVO) ---
elif st.session_state.pagina == "historico":
    st.markdown("<style>.stApp { background-color: #FF8C00; }</style>", unsafe_allow_html=True)
    st.title(f"📜 Histórico - {st.session_state.navio}")
    
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Notion-Version": "2022-06-28"}
    res = requests.post(f"https://api.notion.com/v1/databases/{ID_HISTORICO_NOTION}/query", headers=headers)
    if res.status_code == 200:
        dados_h = []
        for r in res.json().get("results", []):
            p = r["properties"]
            navio_reg = p["Navio"]["rich_text"][0]["text"]["content"] if p["Navio"]["rich_text"] else ""
            if navio_reg == st.session_state.navio or st.session_state.navio == "ADMIN":
                dados_h.append({
                    "Data": p["Data Pedido"]["date"]["start"] if p["Data Pedido"]["date"] else "",
                    "Cozinheiro": p["Cozinheiro"]["title"][0]["text"]["content"] if p["Cozinheiro"]["title"] else "",
                    "Validade": p["Validade"]["date"]["start"] if p["Validade"]["date"] else ""
                })
        st.dataframe(pd.DataFrame(dados_h), use_container_width=True)
    
    if st.button("⬅️ VOLTAR", key="v_h"): st.session_state.pagina = "menu"; st.rerun()
