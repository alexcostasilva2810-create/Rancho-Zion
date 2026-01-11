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
    "NAVIO 03": {"nome": "Carlos", "senha": "456"}
}

# =================================================================
# BLOCO 2: ESTILOS E UTILITÁRIOS
# =================================================================
def aplicar_estilo_tecnologico():
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(0, 20, 50, 0.85), rgba(0, 20, 50, 0.85)), 
            url('https://images.unsplash.com/photo-1544383333-546e16fd3a51?q=80&w=1920');
            background-size: cover; background-position: center;
        }
        h1, h2, h3, p, label { color: white !important; }
        .stButton > button {
            border: 2px solid #00D4FF !important; background: rgba(0, 212, 255, 0.1) !important;
            color: white !important; height: 60px; font-size: 18px !important; border-radius: 10px;
        }
        .stButton > button:hover { background: #00D4FF !important; color: black !important; }
        </style>
    """, unsafe_allow_html=True)

def preparar(t): return unicodedata.normalize('NFKD', str(t)).encode('latin-1', 'ignore').decode('latin-1')

# =================================================================
# BLOCO 4: NAVEGAÇÃO
# =================================================================

if st.session_state.pagina == "home":
    st.markdown("<style>.stApp { background-color: #4169E1; }</style>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: white;'>Zion Tecnologia</h1>", unsafe_allow_html=True)
    if os.path.exists("ZION.jpg"): st.image("ZION.jpg", use_container_width=True)
    if st.button("🚀 ACESSAR SISTEMA"): st.session_state.pagina = "login"; st.rerun()

elif st.session_state.pagina == "login":
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
    aplicar_estilo_tecnologico()
    head_col1, head_col2 = st.columns([1, 6])
    with head_col1:
        if os.path.exists("ZION.jpg"): st.image("ZION.jpg", width=80)
    with head_col2:
        st.markdown(f"<h1 style='color: #00D4FF !important;'>Painel - {st.session_state.navio}</h1>", unsafe_allow_html=True)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 TABELA DE RANCHO", use_container_width=True): st.session_state.pagina = "lista"; st.rerun()
        if st.button("📜 VER HISTÓRICO", use_container_width=True): st.session_state.pagina = "historico"; st.rerun()
    with col2:
        if st.button("👨‍✈️ DECLARAÇÃO", use_container_width=True): st.session_state.pagina = "tripulacao"; st.rerun()
        if st.button("⬅️ SAIR DO SISTEMA", use_container_width=True): st.session_state.pagina = "home"; st.rerun()

# --- BLOCO 6: CONFERÊNCIA DE ESTOQUE ---
elif st.session_state.pagina == "lista":
    st.markdown("<style>.stApp { background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url('https://images.unsplash.com/photo-1583258292688-d0213dc5a3a8?q=80&w=1920'); background-size: cover; }</style>", unsafe_allow_html=True)
    st.title("📋 Conferência de Estoque")
    
    df_editado = st.data_editor(st.session_state.df_lista, column_config={"ITEM": st.column_config.NumberColumn("CÓD.", disabled=True), "CONFIRMA": st.column_config.NumberColumn("SUA QTD", min_value=0)}, hide_index=True, use_container_width=True)

    col_pdf, col_voltar = st.columns(2)
    with col_pdf:
        if st.button("💾 GERAR E SALVAR RELATÓRIO"):
            pdf = FPDF(); pdf.add_page()
            if os.path.exists("ZION.jpg"): pdf.image("ZION.jpg", 95, 8, 20)
            pdf.set_font("Arial", "B", 14); pdf.set_y(30)
            pdf.cell(0, 10, preparar(f"Checklist de Rancho: {st.session_state.navio}"), ln=True, align="C")
            # ... (lógica de tabela simplificada para brevidade)
            st.download_button(label="📥 BAIXAR PDF", data=pdf.output(dest='S').encode('latin-1'), file_name="Rancho.pdf", mime="application/pdf", use_container_width=True)
            st.success("✅ Sua solicitação está gerada! Envie o PDF para o comprador.")
    with col_voltar:
        if st.button("⬅️ VOLTAR AO MENU", use_container_width=True): st.session_state.pagina = "menu"; st.rerun()

# --- BLOCO 7: TELA DE DECLARAÇÃO (RESTAURADA E LINDA) ---
elif st.session_state.pagina == "tripulacao":
    aplicar_estilo_tecnologico()
    head_col1, head_col2 = st.columns([1, 6])
    with head_col1:
        if os.path.exists("ZION.jpg"): st.image("ZION.jpg", width=80)
    with head_col2:
        st.markdown(f"<h1 style='color: #00D4FF !important;'>⚓ Declaração de Reabastecimento</h1>", unsafe_allow_html=True)

    with st.container():
        st.markdown("### 📝 Dados da Embarcação")
        c1, c2 = st.columns(2)
        cmd = c1.text_input("Comandante Responsável")
        coz = c2.text_input("Cozinheiro Responsável", value=st.session_state.cozinheiro)
        
        c3, c4 = st.columns(2)
        qtd_trip = c3.number_input("Quantidade de Tripulantes", min_value=1, step=1)
        dias = c4.number_input("Dias de Autonomia", min_value=1, step=1)

    st.markdown("### ✍️ Assinatura Digital")
    canvas_result = st_canvas(fill_color="rgba(255, 255, 255, 0.3)", stroke_width=3, stroke_color="#000000", background_color="#FFFFFF", height=150, update_streamlit=True, key="canvas")

    col_gerar, col_voltar = st.columns(2)
    with col_gerar:
        if st.button("📄 GERAR DECLARAÇÃO PDF", use_container_width=True):
            if canvas_result.image_data is not None:
                pdf = FPDF(); pdf.add_page()
                if os.path.exists("ZION.jpg"): pdf.image("ZION.jpg", 90, 10, 30)
                pdf.set_font("Arial", "B", 16); pdf.set_y(50)
                pdf.cell(0, 10, preparar("DECLARAÇÃO DE REABASTECIMENTO"), ln=True, align="C")
                pdf.ln(10); pdf.set_font("Arial", "", 12)
                texto = f"Eu, {cmd}, Comandante da embarcação {st.session_state.navio}, declaro que recebemos o rancho conferido por {coz} para atender {qtd_trip} tripulantes por {dias} dias."
                pdf.multi_cell(0, 10, preparar(texto))
                # Salvar assinatura
                img_sig = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                img_sig.save("sig.png")
                pdf.image("sig.png", x=75, y=100, w=60)
                pdf.line(60, 130, 150, 130)
                pdf.text(85, 135, preparar("Assinatura do Responsável"))
                
                st.download_button("📥 BAIXAR DECLARAÇÃO", data=pdf.output(dest='S').encode('latin-1'), file_name="Declaracao.pdf", mime="application/pdf", use_container_width=True)
                st.success("✅ Declaração gerada com sucesso!")
            else: st.warning("Por favor, assine antes de gerar o PDF.")

    with col_voltar:
        if st.button("⬅️ VOLTAR AO MENU", use_container_width=True): st.session_state.pagina = "menu"; st.rerun()

# --- BLOCO 8: TELA DE HISTÓRICO ---
elif st.session_state.pagina == "historico":
    aplicar_estilo_tecnologico(); st.title("📜 Histórico")
    if st.button("⬅️ VOLTAR AO MENU"): st.session_state.pagina = "menu"; st.rerun()
