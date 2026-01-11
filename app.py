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

if 'pagina' not in st.session_state: st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state: st.session_state.cozinheiro = ""
if 'navio' not in st.session_state: st.session_state.navio = ""

# =================================================================
# BLOCO 2: ESTILO PROFISSIONAL
# =================================================================
def aplicar_estilo_tecnologico():
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(0, 20, 50, 0.88), rgba(0, 20, 50, 0.88)), 
            url('https://images.unsplash.com/photo-1544383333-546e16fd3a51?q=80&w=1920');
            background-size: cover; background-position: center;
        }
        h1, h2, h3, p, label { color: white !important; }
        .stButton > button {
            border: 2px solid #00D4FF !important; background: rgba(0, 212, 255, 0.1) !important;
            color: white !important; font-weight: bold; border-radius: 10px;
        }
        .stButton > button:hover { background: #00D4FF !important; color: black !important; }
        .mensagem-validade { 
            background-color: rgba(255, 140, 0, 0.2); 
            padding: 15px; border-radius: 10px; border-left: 5px solid #FF8C00;
            color: white; font-weight: bold; font-size: 1.1rem;
        }
        </style>
    """, unsafe_allow_html=True)

def preparar(t): return unicodedata.normalize('NFKD', str(t)).encode('latin-1', 'ignore').decode('latin-1')

# =================================================================
# BLOCO 3: NAVEGAÇÃO
# =================================================================

if st.session_state.pagina == "home":
    st.markdown("<h1 style='text-align: center;'>Zion Tecnologia</h1>", unsafe_allow_html=True)
    if os.path.exists("ZION.jpg"): st.image("ZION.jpg", use_container_width=True)
    if st.button("🚀 ACESSAR SISTEMA", use_container_width=True): st.session_state.pagina = "login"; st.rerun()

elif st.session_state.pagina == "login":
    st.title("🔐 Login")
    navio_sel = st.selectbox("Embarcação", ["NAVIO 01", "AROEIRA", "NAVIO 03"])
    nome_user = st.text_input("Seu Nome")
    if st.button("ENTRAR"):
        if nome_user:
            st.session_state.cozinheiro = nome_user
            st.session_state.navio = navio_sel
            st.session_state.pagina = "menu"; st.rerun()
        else: st.warning("Por favor, digite seu nome.")

elif st.session_state.pagina == "menu":
    aplicar_estilo_tecnologico()
    h1, h2 = st.columns([1, 6])
    with h1: 
        if os.path.exists("ZION.jpg"): st.image("ZION.jpg", width=80)
    with h2: st.markdown(f"<h1>Painel - {st.session_state.navio}</h1>", unsafe_allow_html=True)
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📋 TABELA DE RANCHO", use_container_width=True): st.session_state.pagina = "lista"; st.rerun()
        if st.button("📜 VER HISTÓRICO", use_container_width=True): st.session_state.pagina = "historico"; st.rerun()
    with c2:
        if st.button("👨‍✈️ DECLARAÇÃO", use_container_width=True): st.session_state.pagina = "tripulacao"; st.rerun()
        if st.button("⬅️ SAIR", use_container_width=True): st.session_state.pagina = "home"; st.rerun()

# --- BLOCO 7: TELA DE DECLARAÇÃO (RESTAURAÇÃO TOTAL) ---
elif st.session_state.pagina == "tripulacao":
    aplicar_estilo_tecnologico()
    
    h1, h2 = st.columns([1, 8])
    with h1: 
        if os.path.exists("ZION.jpg"): st.image("ZION.jpg", width=80)
    with h2: st.markdown(f"<h2>⚓ Declaração de Reabastecimento</h2>", unsafe_allow_html=True)

    st.markdown("---")
    
    with st.container():
        col1, col2 = st.columns(2)
        # Campo já vem preenchido com o usuário logado
        responsavel = col1.text_input("Responsável pelo Registro", value=st.session_state.cozinheiro, disabled=True)
        data_atual = col2.date_input("Data do Pedido", value=datetime.now())

        col3, col4 = st.columns(2)
        ultimo_rancho = col3.date_input("Data do Último Rancho")
        escolta = col4.selectbox("A embarcação possui Escolta?", ["NÃO", "SIM"])

        # LÓGICA DE DURAÇÃO (12 ou 15 DIAS)
        dias_validade = 12 if escolta == "SIM" else 15
        data_validade = data_atual + timedelta(days=dias_validade)
        
        # Mensagem Dinâmica Restaurada
        st.markdown(f"""
            <div class="mensagem-validade">
                📢 Devido à presença de escolta: {escolta}<br>
                A duração estimada do rancho é de {dias_validade} dias.<br>
                Validade prevista até: {data_validade.strftime('%d/%m/%Y')}
            </div>
        """, unsafe_allow_html=True)

    st.markdown("### ✍️ Assinatura do Comandante/Encarregado")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0.3)", stroke_width=3,
        stroke_color="#000000", background_color="#FFFFFF",
        height=150, update_streamlit=True, key="canvas_final"
    )

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📄 GERAR PDF DA DECLARAÇÃO", use_container_width=True):
            if canvas_result.image_data is not None:
                pdf = FPDF(); pdf.add_page()
                if os.path.exists("ZION.jpg"): pdf.image("ZION.jpg", 90, 10, 30)
                pdf.set_font("Arial", "B", 16); pdf.set_y(45)
                pdf.cell(0, 10, preparar("DECLARAÇÃO DE REABASTECIMENTO"), ln=True, align="C")
                
                pdf.set_font("Arial", "", 11); pdf.ln(10)
                pdf.cell(0, 8, preparar(f"Embarcação: {st.session_state.navio}"), ln=True)
                pdf.cell(0, 8, preparar(f"Responsável: {st.session_state.cozinheiro}"), ln=True)
                pdf.cell(0, 8, preparar(f"Último Rancho: {ultimo_rancho.strftime('%d/%m/%Y')}"), ln=True)
                pdf.cell(0, 8, preparar(f"Escolta: {escolta}"), ln=True)
                pdf.cell(0, 8, preparar(f"Duração Prevista: {dias_validade} dias (Até {data_validade.strftime('%d/%m/%Y')})"), ln=True)
                
                # Salvar assinatura
                img_sig = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                img_sig.save("sig_dec.png")
                pdf.image("sig_dec.png", x=75, y=pdf.get_y() + 10, w=60)
                
                st.download_button("📥 BAIXAR DECLARAÇÃO", data=pdf.output(dest='S').encode('latin-1'), file_name=f"Declaracao_{st.session_state.navio}.pdf", mime="application/pdf", use_container_width=True)
                st.success("✅ Declaração gerada! Envie o PDF ao comprador.")
            else: st.warning("Por favor, assine o documento.")

    with col_btn2:
        if st.button("⬅️ VOLTAR AO MENU", use_container_width=True): 
            st.session_state.pagina = "menu"; st.rerun()

# --- BLOCO 6: LISTA (RESUMO) ---
elif st.session_state.pagina == "lista":
    if st.button("⬅️ VOLTAR AO MENU"): st.session_state.pagina = "menu"; st.rerun()
