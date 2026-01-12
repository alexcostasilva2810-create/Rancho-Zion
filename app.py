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
# BLOCO 2: FUNÇÕES DE ESTILO E PDF
# =================================================================
def aplicar_estilo_base():
    st.markdown("<style>.stApp { background-color: #4169E1; } h1,h2,h3,p,label { color: white; }</style>", unsafe_allow_html=True)

def preparar_celula(conteudo):
    texto = str(conteudo) if conteudo is not None else ""
    return unicodedata.normalize('NFKD', texto).encode('latin-1', 'ignore').decode('latin-1')

# =================================================================
# BLOCO 3: NAVEGAÇÃO
# =================================================================

if st.session_state.pagina == "home":
    aplicar_estilo_base()
    st.markdown("<h1 style='text-align: center;'>Zion Tecnologia</h1>", unsafe_allow_html=True)
    if os.path.exists("ZION.jpg"): st.image("ZION.jpg", use_container_width=True)
    if st.button("🚀 ACESSAR SISTEMA", key="btn_h"): st.session_state.pagina = "login"; st.rerun()

elif st.session_state.pagina == "login":
    aplicar_estilo_base(); st.title("🔐 Login")
    n_sel = st.selectbox("Navio", list(USUARIOS.keys()), key="l1")
    s_dig = st.text_input("Senha", type="password", key="l2")
    if st.button("ENTRAR", key="btn_l"):
        if s_dig == USUARIOS[n_sel]["senha"]:
            st.session_state.cozinheiro = USUARIOS[n_sel]["nome"]
            st.session_state.navio = n_sel
            st.session_state.pagina = "menu"; st.rerun()
        else: st.error("Senha incorreta")

elif st.session_state.pagina == "menu":
    aplicar_estilo_base()
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

# --- TELA: CONFERÊNCIA DE RANCHO ---
elif st.session_state.pagina == "lista":
    st.markdown("""<style>
        .stApp { background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("https://images.unsplash.com/photo-1583258292688-d0213dc5a3a8?q=80&w=1920"); background-size: cover; }
        h1 { color: #00FF00 !important; text-shadow: 2px 2px 4px black; }
        label { color: black !important; font-weight: bold; }
    </style>""", unsafe_allow_html=True)
    
    st.title("📋 Conferência de Estoque")
    
    if st.button("🔄 ATUALIZAR DADOS DO NOTION", key="upd"):
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
        
        if st.button("📥 GERAR PDF DO RANCHO", key="pdf_r"):
            pdf = FPDF(); pdf.add_page()
            pdf.set_font("Arial", "B", 16); pdf.cell(0, 10, "Relatorio de Rancho", ln=True, align="C")
            # Cabeçalho da tabela no PDF
            pdf.set_font("Arial", "B", 10)
            for col in df_ed.columns: pdf.cell(32, 10, col, 1)
            pdf.ln()
            pdf.set_font("Arial", "", 9)
            for _, row in df_ed.iterrows():
                for val in row: pdf.cell(32, 8, preparar_celula(val), 1)
                pdf.ln()
            st.download_button("Clique aqui para Baixar", pdf.output(dest='S').encode('latin-1'), "rancho.pdf", "application/pdf")

    if st.button("⬅️ VOLTAR", key="v_r"): st.session_state.pagina = "menu"; st.rerun()

# --- TELA: DECLARAÇÃO DE REABASTECIMENTO ---
elif st.session_state.pagina == "tripulacao":
    st.markdown("""<style>
        .stApp { background: linear-gradient(rgba(255,255,255,0.8), rgba(255,255,255,0.8)), url("https://images.unsplash.com/photo-1500514960902-e64e75c44c83?q=80&w=1920"); background-size: cover; }
        h1, label, p { color: black !important; }
        .stTextInput input, .stTextArea textarea { color: black !important; border: 1px solid #4169E1 !important; }
    </style>""", unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center;'>⚓ Declaração de Reabastecimento</h1>", unsafe_allow_html=True)
    
    escolta = st.radio("O navio está com escolta?", ["NÃO", "SIM"], horizontal=True, key="rad_e")
    dias = 12 if escolta == "SIM" else 15
    
    col_a, col_b = st.columns(2)
    with col_a:
        dt_prev = st.date_input("Data prevista para receber:", datetime.now(), key="d_p")
    with col_b:
        dt_val = dt_prev + timedelta(days=dias)
        st.markdown(f"<div style='background-color:#d4edda; padding:10px; border-radius:5px; color:#155724; font-weight:bold;'>"
                    f"Advertência: Rancho durará até {dt_val.strftime('%d/%m/%Y')}</div>", unsafe_allow_html=True)

    with st.form("f_dec"):
        c1, c2 = st.columns(2)
        with c1:
            lot = st.number_input("Tripulantes:", min_value=1, value=16, key="lot")
            orig = st.text_input("Porto Origem:", value="Porto Velho", key="orig")
        with c2:
            dt_ult = st.date_input("Data do último rancho:", datetime.now(), key="dt_u")
            dest = st.text_input("Porto Destino:", value="Novo Remanso", key="dest")
        
        extras = st.text_area("Necessidades Extras:", key="ext")
        st.write("Assinatura:")
        canvas = st_canvas(stroke_width=3, stroke_color="#000", background_color="#FFF", height=100, key="canv")
        
        if st.form_submit_button("💾 SALVAR E GERAR PDF"):
            # Grava no Notion Histórico
            h = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
            body = {
                "parent": {"database_id": ID_HISTORICO_NOTION},
                "properties": {
                    "Cozinheiro": {"title": [{"text": {"content": st.session_state.cozinheiro}}]},
                    "Navio": {"rich_text": [{"text": {"content": st.session_state.navio}}]},
                    "Data Pedido": {"date": {"start": dt_prev.strftime("%Y-%m-%d")}},
                    "Validade": {"date": {"start": dt_val.strftime("%Y-%m-%d")}}
                }
            }
            requests.post("https://api.notion.com/v1/pages", headers=h, json=body)
            st.success("Histórico Salvo!"); st.balloons()

    if st.button("⬅️ VOLTAR", key="v_t"): st.session_state.pagina = "menu"; st.rerun()

# --- TELA: HISTÓRICO INDIVIDUAL ---
elif st.session_state.pagina == "historico":
    aplicar_estilo_base()
    st.title(f"📜 Seu Histórico - {st.session_state.navio}")
    
    url = f"https://api.notion.com/v1/databases/{ID_HISTORICO_NOTION}/query"
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Notion-Version": "2022-06-28"}
    query = {"filter": {"property": "Navio", "rich_text": {"equals": st.session_state.navio}}}
    
    res = requests.post(url, headers=headers, json=query)
    if res.status_code == 200:
        dados_h = []
        for r in res.json().get("results", []):
            p = r["properties"]
            dados_h.append({
                "Data Pedido": p["Data Pedido"]["date"]["start"] if p["Data Pedido"]["date"] else "",
                "Cozinheiro": p["Cozinheiro"]["title"][0]["text"]["content"] if p["Cozinheiro"]["title"] else "",
                "Validade": p["Validade"]["date"]["start"] if p["Validade"]["date"] else ""
            })
        if dados_h:
            st.dataframe(pd.DataFrame(dados_h), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum registro encontrado para este navio.")
    
    if st.button("⬅️ VOLTAR", key="v_h"): st.session_state.pagina = "menu"; st.rerun()

# --- PAINEL ADMINISTRADOR ---
elif st.session_state.pagina == "admin":
    aplicar_estilo_base()
    st.title("👑 Painel Administrativo (Visão Geral)")
    # Puxa tudo sem filtro
    url = f"https://api.notion.com/v1/databases/{ID_HISTORICO_NOTION}/query"
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Notion-Version": "2022-06-28"}
    res = requests.post(url, headers=headers)
    if res.status_code == 200:
        results = res.json().get("results", [])
        lista_adm = []
        for r in results:
            p = r["properties"]
            lista_adm.append({
                "USUÁRIO": p["Cozinheiro"]["title"][0]["text"]["content"] if p["Cozinheiro"]["title"] else "",
                "NAVIO": p["Navio"]["rich_text"][0]["text"]["content"] if p["Navio"]["rich_text"] else "",
                "LISTA": "✅", "DECLARAÇÃO": "✅",
                "ÚLTIMO RANCHO": p["Data Pedido"]["date"]["start"] if p["Data Pedido"]["date"] else ""
            })
        st.table(pd.DataFrame(lista_adm))
    
    if st.button("⬅️ VOLTAR", key="v_adm"): st.session_state.pagina = "menu"; st.rerun()
