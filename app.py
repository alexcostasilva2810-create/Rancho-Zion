import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime, timedelta
import unicodedata
from fpdf import FPDF
from PIL import Image
import os

# =================================================================
# ESTILO E CONFIGURAÇÃO (PROFISSIONAL - BANCO DE DADOS)
# =================================================================
def aplicar_estilo_tecnologico():
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(0, 20, 50, 0.88), rgba(0, 20, 50, 0.88)), 
            url('https://images.unsplash.com/photo-1544383333-546e16fd3a51?q=80&w=1920');
            background-size: cover; background-position: center;
        }
        h1, h2, h3, p, label { color: white !important; font-family: 'sans-serif'; }
        .stButton > button {
            border: 1px solid #00D4FF !important; background: rgba(0, 212, 255, 0.1) !important;
            color: white !important; border-radius: 5px; width: 100%;
        }
        .mensagem-validade { 
            background-color: rgba(60, 45, 30, 0.9); 
            padding: 20px; border-radius: 8px; border-left: 6px solid #FF8C00;
            color: white; margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

def preparar(t): return unicodedata.normalize('NFKD', str(t)).encode('latin-1', 'ignore').decode('latin-1')

# =================================================================
# TELA DE DECLARAÇÃO (RESTAURAÇÃO COMPLETA)
# =================================================================
if st.session_state.pagina == "tripulacao":
    aplicar_estilo_tecnologico()
    
    # Cabeçalho com Logo Pequena Lateral
    h1, h2 = st.columns([1, 8])
    with h1: 
        if os.path.exists("ZION.jpg"): st.image("ZION.jpg", width=70)
    with h2: 
        st.markdown("<h2 style='display: flex; align-items: center;'>⚓ Declaração de Reabastecimento</h2>", unsafe_allow_html=True)

    st.markdown("---")
    
    # Grid de Informações
    col1, col2 = st.columns(2)
    with col1:
        responsavel = st.text_input("Responsável pelo Registro", value=st.session_state.cozinheiro, disabled=True)
        # Formatação de data em Português para exibição
        data_ultimo = st.date_input("Data do Último Rancho", format="DD/MM/YYYY")
    
    with col2:
        data_pedido = st.date_input("Data do Pedido", value=datetime.now(), format="DD/MM/YYYY")
        escolta = st.selectbox("A embarcação possui Escolta?", ["NÃO", "SIM"])

    # Lógica de Cálculo (12 ou 15 dias)
    dias = 12 if escolta == "SIM" else 15
    vencimento = data_pedido + timedelta(days=dias)
    
    # Quadro de Aviso (Exatamente como na imagem)
    st.markdown(f"""
        <div class="mensagem-validade">
            📢 Devido à presença de escolta: {escolta}<br>
            A duração estimada do rancho é de {dias} dias.<br>
            Validade prevista até: {vencimento.strftime('%d/%m/%Y')}
        </div>
    """, unsafe_allow_html=True)

    # Área de Assinatura
    st.markdown("### ✍️ Assinatura do Responsável")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0.3)", stroke_width=2,
        stroke_color="#000000", background_color="#FFFFFF",
        height=150, update_streamlit=True, key="canvas_v3"
    )

    # Campo de Observação (Restaurado)
    obs = st.text_area("Observações Adicionais", placeholder="Digite aqui observações importantes sobre o pedido...")

    # Botões de Ação
    st.markdown("---")
    b1, b2 = st.columns(2)
    
    with b1:
        if st.button("📄 GERAR PDF DA DECLARAÇÃO"):
            if canvas_result.image_data is not None:
                pdf = FPDF(); pdf.add_page()
                if os.path.exists("ZION.jpg"): pdf.image("ZION.jpg", 90, 10, 30)
                pdf.set_font("Arial", "B", 16); pdf.set_y(45)
                pdf.cell(0, 10, preparar("DECLARAÇÃO DE REABASTECIMENTO"), ln=True, align="C")
                
                pdf.set_font("Arial", "", 12); pdf.ln(10)
                pdf.cell(0, 8, preparar(f"Embarcação: {st.session_state.navio}"), ln=True)
                pdf.cell(0, 8, preparar(f"Responsável: {st.session_state.cozinheiro}"), ln=True)
                pdf.cell(0, 8, preparar(f"Data do Pedido: {data_pedido.strftime('%d/%m/%Y')}"), ln=True)
                pdf.cell(0, 8, preparar(f"Possui Escolta: {escolta}"), ln=True)
                pdf.cell(0, 8, preparar(f"Duração Estimada: {dias} dias"), ln=True)
                pdf.cell(0, 8, preparar(f"Validade Prevista: {vencimento.strftime('%d/%m/%Y')}"), ln=True)
                
                if obs:
                    pdf.ln(5); pdf.set_font("Arial", "B", 11)
                    pdf.cell(0, 8, "Observações:", ln=True)
                    pdf.set_font("Arial", "", 11)
                    pdf.multi_cell(0, 7, preparar(obs))

                # Assinatura no PDF
                img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                img.save("assinatura.png")
                pdf.image("assinatura.png", x=75, y=pdf.get_y() + 10, w=60)
                
                st.download_button("📥 BAIXAR DECLARAÇÃO", pdf.output(dest='S').encode('latin-1'), 
                                 f"Declaracao_{st.session_state.navio}.pdf", "application/pdf")
                st.success("✅ Gerado! Envie ao comprador.")
            else:
                st.warning("Assine antes de gerar.")

    with b2:
        if st.button("⬅️ VOLTAR AO MENU"):
            st.session_state.pagina = "menu"; st.rerun()
