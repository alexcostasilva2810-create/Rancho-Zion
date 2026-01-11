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

# =================================================================
# BLOCO 2: ESTILO PROFISSIONAL (BANCO DE DADOS)
# =================================================================
def aplicar_estilo_tecnologico():
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(0, 20, 50, 0.85), rgba(0, 20, 50, 0.85)), 
            url('https://images.unsplash.com/photo-1544383333-546e16fd3a51?q=80&w=1920');
            background-size: cover; background-position: center;
        }
        h1, h2, h3, p, label { color: white !important; font-weight: bold; }
        .stButton > button {
            border: 2px solid #00D4FF !important; background: rgba(0, 212, 255, 0.1) !important;
            color: white !important; height: 50px; font-size: 16px !important; border-radius: 10px;
        }
        .stButton > button:hover { background: #00D4FF !important; color: black !important; }
        input { background-color: rgba(255,255,255,0.1) !important; color: white !important; }
        </style>
    """, unsafe_allow_html=True)

def preparar(t): return unicodedata.normalize('NFKD', str(t)).encode('latin-1', 'ignore').decode('latin-1')

# =================================================================
# BLOCO 3: NAVEGAÇÃO
# =================================================================

if st.session_state.pagina == "home":
    st.markdown("<h1 style='text-align: center; color: white;'>Zion Tecnologia</h1>", unsafe_allow_html=True)
    if os.path.exists("ZION.jpg"): st.image("ZION.jpg", use_container_width=True)
    if st.button("🚀 ACESSAR SISTEMA", use_container_width=True): st.session_state.pagina = "login"; st.rerun()

elif st.session_state.pagina == "login":
    st.title("🔐 Login")
    navio_sel = st.selectbox("Selecione a Embarcação", ["NAVIO 01", "AROEIRA", "NAVIO 03"])
    if st.button("ENTRAR"):
        st.session_state.navio = navio_sel
        st.session_state.pagina = "menu"; st.rerun()

elif st.session_state.pagina == "menu":
    aplicar_estilo_tecnologico()
    head_col1, head_col2 = st.columns([1, 6])
    with head_col1:
        if os.path.exists("ZION.jpg"): st.image("ZION.jpg", width=80)
    with head_col2:
        st.markdown(f"<h1>Painel - {st.session_state.navio}</h1>", unsafe_allow_html=True)
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📋 TABELA DE RANCHO", use_container_width=True): st.session_state.pagina = "lista"; st.rerun()
        if st.button("📜 VER HISTÓRICO", use_container_width=True): st.session_state.pagina = "historico"; st.rerun()
    with c2:
        if st.button("👨‍✈️ DECLARAÇÃO", use_container_width=True): st.session_state.pagina = "tripulacao"; st.rerun()
        if st.button("⬅️ SAIR", use_container_width=True): st.session_state.pagina = "home"; st.rerun()

# --- BLOCO 7: TELA DE DECLARAÇÃO (RESTAURADA COM ESCOLTA E ÚLTIMO RANCHO) ---
elif st.session_state.pagina == "tripulacao":
    aplicar_estilo_tecnologico()
    
    # Cabeçalho Profissional
    h1, h2 = st.columns([1, 8])
    with h1: 
        if os.path.exists("ZION.jpg"): st.image("ZION.jpg", width=70)
    with h2:
        st.markdown(f"<h2>⚓ Declaração de Reabastecimento - {st.session_state.navio}</h2>", unsafe_allow_html=True)

    with st.form("form_declaracao"):
        st.markdown("### 📝 Informações de Logística")
        col1, col2, col3 = st.columns(3)
        comandante = col1.text_input("Comandante Responsável")
        data_ultimo = col2.date_input("Data do Último Rancho")
        tem_escolta = col3.selectbox("Possui Escolta?", ["NÃO", "SIM"])

        col4, col5, col6 = st.columns(3)
        tripulantes = col4.number_input("Qtd de Tripulantes", min_value=1)
        autonomia = col5.number_input("Dias de Autonomia", min_value=1)
        local = col6.text_input("Local de Operação", value="Belém/PA")

        st.markdown("### ✍️ Assinatura Digital")
        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0.3)",
            stroke_width=3, stroke_color="#000000",
            background_color="#FFFFFF",
            height=150, update_streamlit=True, key="canvas_dec"
        )
        
        btn_gerar = st.form_submit_state = st.form_submit_button("💾 GERAR DECLARAÇÃO E SALVAR")

    if btn_gerar:
        if comandante and canvas_result.image_data is not None:
            try:
                pdf = FPDF(); pdf.add_page()
                if os.path.exists("ZION.jpg"): pdf.image("ZION.jpg", 90, 10, 30)
                pdf.set_font("Arial", "B", 16); pdf.set_y(45)
                pdf.cell(0, 10, preparar("DECLARAÇÃO DE REABASTECIMENTO"), ln=True, align="C")
                
                pdf.set_font("Arial", "", 11); pdf.ln(10)
                pdf.multi_cell(0, 8, preparar(f"Embarcação: {st.session_state.navio}"))
                pdf.multi_cell(0, 8, preparar(f"Comandante: {comandante}"))
                pdf.multi_cell(0, 8, preparar(f"Último Rancho: {data_ultimo.strftime('%d/%m/%Y')}"))
                pdf.multi_cell(0, 8, preparar(f"Possui Escolta: {tem_escolta}"))
                pdf.multi_cell(0, 8, preparar(f"Tripulantes: {tripulantes} | Autonomia: {autonomia} dias"))
                
                pdf.ln(15)
                pdf.set_font("Arial", "I", 10)
                texto_legal = f"Eu, {comandante}, declaro para os devidos fins que as informações acima são verídicas e que o reabastecimento é necessário para a continuidade das operações em {local}."
                pdf.multi_cell(0, 7, preparar(texto_legal))

                # Assinatura
                img_sig = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                img_sig.save("temp_sig.png")
                pdf.image("temp_sig.png", x=75, y=pdf.get_y() + 10, w=60)
                
                pdf_bytes = pdf.output(dest='S').encode('latin-1')
                st.download_button("📥 BAIXAR DECLARAÇÃO PDF", pdf_bytes, f"Declaracao_{st.session_state.navio}.pdf", "application/pdf", use_container_width=True)
                st.success("✅ Declaração gerada com sucesso! Envie o arquivo ao setor responsável.")
            except Exception as e: st.error(f"Erro ao gerar: {e}")
        else:
            st.warning("⚠️ Preencha o nome do Comandante e faça a assinatura.")

    if st.button("⬅️ VOLTAR AO MENU", use_container_width=True): 
        st.session_state.pagina = "menu"; st.rerun()

# --- BLOCO 6: CONFERÊNCIA DE ESTOQUE ---
elif st.session_state.pagina == "lista":
    st.markdown("<style>.stApp { background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url('https://images.unsplash.com/photo-1583258292688-d0213dc5a3a8?q=80&w=1920'); background-size: cover; }</style>", unsafe_allow_html=True)
    st.title("📋 Conferência de Estoque")
    if st.button("⬅️ VOLTAR AO MENU"): st.session_state.pagina = "menu"; st.rerun()

# --- BLOCO 8: TELA DE HISTÓRICO ---
elif st.session_state.pagina == "historico":
    aplicar_estilo_tecnologico(); st.title("📜 Histórico")
    if st.button("⬅️ VOLTAR AO MENU"): st.session_state.pagina = "menu"; st.rerun()
