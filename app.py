import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime, timedelta
import unicodedata
from fpdf import FPDF
from PIL import Image
import os
import requests
import base64
from io import BytesIO
import pytz

# --- CONFIGURAÇÃO PARA ÍCONE E APP INSTALÁVEL (PWA) ---
st.markdown("""
    <head>
        <link rel="manifest" href="https://raw.githubusercontent.com/alexcostasilva2810-create/Rancho-Zion/main/manifest.json?v=100">
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <link rel="icon" type="image/png" href="./logo_pwa.png">
        <link rel="apple-touch-icon" href="./logo_pwa.png">
    </head>
    """, unsafe_allow_html=True)
# -----------------------------------------------------

# =================================================================
# BLOCO 1: CONFIGURAÇÕES, CONSTANTES E ESTADOS
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

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

# =================================================================
# BLOCO 3: FUNÇÃO DO MANUAL DO USUÁRIO
# =================================================================
def gerar_manual_pdf_zion():
    pdf = FPDF()
    pdf.add_page()
    def f(t): return unicodedata.normalize('NFKD', str(t)).encode('latin-1', 'ignore').decode('latin-1')
    pdf.set_font("Arial", "B", 25); pdf.set_text_color(0, 51, 153)
    pdf.cell(0, 20, f("MANUAL DO USUÁRIO - SISTEMA ZION"), ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f("1. ACESSO VIA QR CODE E SEGURANÇA"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 7, f("O acesso ao sistema Zion e realizado exclusivamente via leitura de QR CODE..."))
    pdf.ln(20)
    pdf.set_font("Arial", "I", 9); pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, f(f"Manual gerado em: {datetime.now().strftime('%d/%m/%Y')}"), align="C")
    return pdf.output(dest='S').encode('latin-1')

# =================================================================
# BLOCO 4: TELA HOME
# =================================================================
if st.session_state.pagina == "home":
    img_base64 = get_base64_of_bin_file('zion_final.jpg')
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: #0e1117;
            background-image: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)), url("data:image/jpg;base64,{img_base64}");
            background-size: contain; background-repeat: no-repeat; background-position: center top; background-attachment: fixed;
        }}
        .main-container {{ display: flex; flex-direction: column; align-items: center; justify-content: flex-end; height: 85vh; padding-bottom: 50px; }}
        div.stButton > button {{ width: 280px !important; height: 60px !important; background-color: #FF8C00 !important; color: white !important; border-radius: 12px !important; font-weight: bold !important; font-size: 22px !important; }}
        </style>
        """, unsafe_allow_html=True)
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 400px;'></div>", unsafe_allow_html=True)
    if st.button("🚀 ACESSAR SISTEMA"): 
        st.session_state.pagina = "login"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# =================================================================
# BLOCO 5: TELA LOGIN
# =================================================================
elif st.session_state.pagina == "login":
    st.markdown("""<style>.stApp { background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url("https://images.unsplash.com/photo-1574689049868-e94ed5301745?q=80&w=1920"); background-size: cover; }</style>""", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>🔐 Acesso Restrito</h1>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        navio_sel = st.selectbox("Selecione sua Embarcação", list(USUARIOS.keys()))
        senha_dig = st.text_input("Senha de Acesso", type="password")
        if st.button("🚀 ENTRAR"):
            dados = USUARIOS.get(navio_sel)
            if dados and senha_dig == dados["senha"]:
                st.session_state.cozinheiro = dados["nome"]; st.session_state.navio = navio_sel; st.session_state.pagina = "menu"; st.rerun()
            else: st.error("❌ Senha incorreta!")
        if st.button("⬅️ VOLTAR AO INÍCIO"):
            st.session_state.pagina = "home"; st.rerun()

# =================================================================
# BLOCO 6: MENU PRINCIPAL (CORREÇÃO DA LINHA 283)
# =================================================================
elif st.session_state.pagina == "menu":
    aplicar_estilo_azul()
    st.title(f"🚢 Painel - {st.session_state.navio}")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 TABELA DE RANCHO", use_container_width=True): 
            st.session_state.pagina = "lista"; st.rerun()
        if st.button("📜 VER HISTÓRICO", use_container_width=True): 
            st.session_state.pagina = "historico"; st.rerun()
    with col2:
        if st.button("👨‍✈️ DECLARAÇÃO", use_container_width=True): 
            st.session_state.pagina = "tripulacao"; st.rerun()
            
    # CORREÇÃO DA INDENTAÇÃO AQUI (LINHA 283)
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("📖 BAIXAR MANUAL DO SISTEMA"):
        pdf_bytes = gerar_manual_pdf_zion()
        st.download_button(label="📥 Clique aqui para salvar o Manual", data=pdf_bytes, file_name="Manual_ZION.pdf", mime="application/pdf")

    st.markdown("---")
    if st.button("⬅️ LOGOUT (SAIR)"):
        st.session_state.pagina = "home"; st.rerun()

# =================================================================
# BLOCO 7: TELA DE LISTA / RANCHO
# =================================================================
elif st.session_state.pagina == "lista":
    import io
    st.title("📋 Conferência de Estoque")
    if st.button("🔄 ATUALIZAR TABELA"):
        st.session_state.df_lista = carregar_dados_do_notion(); st.rerun()
    
    df_editado = st.data_editor(st.session_state.df_lista, hide_index=True, use_container_width=True)
    
    if st.button("⬅️ MENU PRINCIPAL"):
        st.session_state.pagina = "menu"; st.rerun()

# =================================================================
# BLOCO 8: TELA DE DECLARAÇÃO
# =================================================================
elif st.session_state.pagina == "tripulacao":
    st.markdown("<h1 style='text-align: center;'>⚓ Declaração de Reabastecimento</h1>", unsafe_allow_html=True)
    with st.form("form_dec"):
        origem = st.text_input("Porto de Origem", value="Porto Velho")
        destino = st.text_input("Porto de Destino", value="Novo remanso")
        st.write("Assinatura Digital:")
        canvas_result = st_canvas(stroke_width=3, height=120, key="canvas_dec")
        if st.form_submit_button("💾 SALVAR E GERAR PDF"):
            st.success("PDF Gerado!")
            
    if st.button("⬅️ MENU"):
        st.session_state.pagina = "menu"; st.rerun()

# =================================================================
# BLOCO 9: HISTÓRICO
# =================================================================
elif st.session_state.pagina == "historico":
    st.title("🗄️ Histórico de Documentos")
    if st.button("⬅️ MENU PRINCIPAL"):
        st.session_state.pagina = "menu"; st.rerun()
