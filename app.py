import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime, timedelta
import unicodedata
from fpdf import FPDF
from PIL import Image
import os

# =================================================================
# ESTILO PROFISSIONAL (PLANO DE FUNDO BANCO DE DADOS)
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
# TELA DE DECLARAÇÃO (RESTAURAÇÃO TOTAL DO CONTEÚDO)
# =================================================================
if st.session_state.pagina == "tripulacao":
    aplicar_estilo_tecnologico()
    
    # Cabeçalho com Logo
    h1, h2 = st.columns([1, 8])
    with h1: 
        if os.path.exists("ZION.jpg"): st.image("ZION.jpg", width=70)
    with h2: 
        st.markdown("<h2>⚓ Declaração de Reabastecimento</h2>", unsafe_allow_html=True)

    st.markdown("---")
    
    # Informações Restauradas
    col1, col2 = st.columns(2)
    with col1:
        responsavel = st.text_input("Responsável pelo Registro", value=st.session_state.cozinheiro, disabled=True)
        data_ultimo = st.date_input("Data do Último Rancho", format="DD/MM/YYYY")
        origem = st.text_input("Origem", value="Porto Velho")
    
    with col2:
        data_pedido = st.date_input("Data do Pedido", value=datetime.now(), format="DD/MM/YYYY")
        escolta = st.selectbox("A embarcação possui Escolta?", ["NÃO", "SIM"])
        destino = st.text_input("Destino", value="Novo remanso")

    # Lógica de Dias (12 com Escolta / 15 sem Escolta)
    dias = 12 if escolta == "SIM" else 15
    vencimento = data_pedido + timedelta(days=dias)
    
    # Quadro de Aviso Dinâmico
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
        height=150, update_streamlit=True, key="canvas_final_v1"
    )

    # Campo de Considerações (Abaixo da Assinatura)
    consideracoes = st.text_area("CONSIDERAÇÕES:", placeholder="Ex: Foi acrescentado 10 água no rancho pelo fato da baixa do rio...")

    # Botões de Ação
    st.markdown("---")
    b1, b2 = st.columns(2)
    
    with b1:
        if st.button("📄 GERAR PDF DA DECLARAÇÃO"):
            if canvas_result.image_data is not None:
                pdf = FPDF(); pdf.add_page()
                if os.path.exists("ZION.jpg"): pdf.image("ZION.jpg", 90, 10, 25)
                
                pdf.set_font("Arial", "B", 14); pdf.set_y(40)
                pdf.cell(0, 10, preparar("DECLARACAO DE REABASTECIMENTO"), ln=True, align="C")
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, preparar(f"Embarcacao: {st.session_state.navio}"), ln=True, align="C")
                
                # Texto Oficial da Carta Restaurado
                pdf.set_font("Arial", "", 11); pdf.ln(10)
                texto_corpo = (
                    f"Pelo presente, certifico que a lotacao de tripulantes a bordo do empurrador e de 14 tripulantes. "
                    f"A provisao de rancho a ser reabastecida destina-se a cobrir as necessidades nutricionais da "
                    f"tripulacao por um periodo de {dias} dias nauticos a partir de {data_pedido.strftime('%d/%m/%Y')}. "
                    f"Este suprimento e planejado para a viagem corrente."
                )
                pdf.multi_cell(0, 8, preparar(texto_corpo))
                
                pdf.ln(5); pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 8, preparar(f"Origem: {origem} | Destino: {destino}"), ln=True)
                pdf.cell(0, 8, preparar(f"Ultimo Rancho: {data_ultimo.strftime('%d/%m/%Y')}"), ln=True)
                
                # Considerações no PDF
                if consideracoes:
                    pdf.ln(5); pdf.set_font("Arial", "B", 11)
                    pdf.cell(0, 8, "CONSIDERACOES:", ln=True)
                    pdf.set_font("Arial", "", 11)
                    pdf.multi_cell(0, 7, preparar(consideracoes))

                # Assinatura e Rodapé
                img_path = "assinatura_temp.png"
                Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA').save(img_path)
                pdf.image(img_path, x=75, y=pdf.get_y() + 5, w=50)
                pdf.set_y(pdf.get_y() + 25)
                pdf.line(60, pdf.get_y(), 150, pdf.get_y())
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 8, preparar(f"Responsavel: {st.session_state.cozinheiro}"), ln=True, align="C")
                
                st.download_button("📥 BAIXAR DECLARAÇÃO", pdf.output(dest='S').encode('latin-1'), 
                                 f"Declaracao_{st.session_state.navio}.pdf", "application/pdf")
                st.success("✅ PDF Restaurado com sucesso!")
            else:
                st.warning("Assine o documento antes de gerar.")

    with b2:
        if st.button("⬅️ VOLTAR AO MENU"):
            st.session_state.pagina = "menu"; st.rerun()
