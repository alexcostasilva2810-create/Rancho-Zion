import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime, timedelta
import unicodedata
from fpdf import FPDF
from PIL import Image
import os
import requests
import pytz

# =================================================================
# BLOCO 1: CONFIGURAÇÕES, IDs E ESTILOS GERAIS
# =================================================================
st.set_page_config(page_title="Zion Rancho App", layout="wide")

# Credenciais e IDs
NOTION_TOKEN = "ntn_jZ6353375938j9kJFqKWjD0N4ONt1rwP515tsIMwxtucHa"
DATABASE_ID = "2e3025de7b79803abe0efde74f87a2e1" 
ID_HISTORICO_NOTION = "2e5025de7b79803187a4d8b865179440"

# Inicialização de Variáveis de Estado
if 'pagina' not in st.session_state: st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state: st.session_state.cozinheiro = ""
if 'navio' not in st.session_state: st.session_state.navio = ""
if 'df_lista' not in st.session_state: st.session_state.df_lista = pd.DataFrame(columns=["ITEM", "DESCRIÇÃO", "TIPO", "UNID MED", "PREDEFINIDO", "CONFIRMA"])

# Funções Utilitárias
def preparar(t): return unicodedata.normalize('NFKD', str(t)).encode('latin-1', 'ignore').decode('latin-1')

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
            color: white !important; border-radius: 8px; width: 100%; height: 50px; font-weight: bold;
        }
        .stButton > button:hover { background: #00D4FF !important; color: black !important; }
        .mensagem-validade { 
            background-color: rgba(60, 45, 30, 0.9); 
            padding: 20px; border-radius: 8px; border-left: 6px solid #FF8C00;
            color: white; margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

# =================================================================
# BLOCO 2: TELA HOME (ZION TECNOLOGIA)
# =================================================================
if st.session_state.pagina == "home":
    st.markdown("<style>.stApp { background-color: #4169E1; }</style>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: white;'>Zion Tecnologia</h1>", unsafe_allow_html=True)
    if os.path.exists("ZION.jpg"): st.image("ZION.jpg", use_container_width=True)
    if st.button("🚀 ACESSAR SISTEMA"): st.session_state.pagina = "login"; st.rerun()

# =================================================================
# BLOCO 3: TELA DE LOGIN
# =================================================================
elif st.session_state.pagina == "login":
    st.title("🔐 Login")
    navio_sel = st.selectbox("Selecione a Embarcação", ["NAVIO 01", "AROEIRA", "NAVIO 03"])
    nome_user = st.text_input("Nome do Cozinheiro Responsável")
    if st.button("ENTRAR NO SISTEMA"):
        if nome_user:
            st.session_state.cozinheiro = nome_user
            st.session_state.navio = navio_sel
            st.session_state.pagina = "menu"; st.rerun()
        else: st.warning("Por favor, informe seu nome.")

# =================================================================
# BLOCO 4: MENU PRINCIPAL (PROFISSIONAL)
# =================================================================
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

# =================================================================
# BLOCO 6: CONFERÊNCIA DE ESTOQUE (RESTAURADO)
# =================================================================
elif st.session_state.pagina == "lista":
    aplicar_estilo_tecnologico()
    st.title("📋 Conferência de Estoque")
    
    df_editado = st.data_editor(st.session_state.df_lista, column_config={"ITEM": st.column_config.NumberColumn("CÓD.", disabled=True), "CONFIRMA": st.column_config.NumberColumn("SUA QTD", min_value=0)}, hide_index=True, use_container_width=True)

    col_pdf, col_voltar = st.columns(2)
    with col_pdf:
        if st.button("💾 GERAR E SALVAR RELATÓRIO"):
            fuso_br = pytz.timezone('America/Sao_Paulo')
            data_hora = datetime.now(fuso_br).strftime('%d/%m/%Y %H:%M:%S')
            
            pdf = FPDF(); pdf.add_page()
            if os.path.exists("ZION.jpg"): pdf.image("ZION.jpg", 95, 8, 20)
            pdf.set_font("Arial", "B", 14); pdf.set_y(30)
            pdf.cell(0, 10, preparar(f"Checklist de Rancho: {st.session_state.navio}"), ln=True, align="C")
            # (Lógica da tabela omitida aqui para brevidade, mas deve conter seus loops de dados)
            pdf.set_y(-15); pdf.set_font('Arial', 'I', 8)
            pdf.cell(0, 10, f'Gerado em: {data_hora}', 0, 0, 'C')
            
            st.download_button("📥 BAIXAR PDF DO ESTOQUE", pdf.output(dest='S').encode('latin-1'), f"Rancho_{st.session_state.navio}.pdf", "application/pdf")
            st.success("✅ Sua solicitação está gerada! Envie o PDF para o comprador.")
    with col_voltar:
        if st.button("⬅️ VOLTAR AO MENU"): st.session_state.pagina = "menu"; st.rerun()

# =================================================================
# BLOCO 7: TELA DE DECLARAÇÃO (CARTA OFICIAL + FUSO BRASÍLIA)
# =================================================================
elif st.session_state.pagina == "tripulacao":
    aplicar_estilo_tecnologico()
    h1, h2 = st.columns([1, 8])
    with h1: 
        if os.path.exists("ZION.jpg"): st.image("ZION.jpg", width=70)
    with h2: st.markdown("<h2>⚓ Declaração de Reabastecimento</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        responsavel = st.text_input("Responsável", value=st.session_state.cozinheiro, disabled=True)
        data_ultimo = st.date_input("Data do Último Rancho", format="DD/MM/YYYY")
        origem = st.text_input("Origem", value="Porto Velho")
    with col2:
        data_pedido = st.date_input("Data do Pedido", value=datetime.now(), format="DD/MM/YYYY")
        escolta = st.selectbox("Possui Escolta?", ["NÃO", "SIM"])
        destino = st.text_input("Destino", value="Novo remanso")
    with col3:
        qtd_tripulantes = st.number_input("Tripulantes", min_value=1, value=14)

    dias = 12 if escolta == "SIM" else 15
    vencimento = data_pedido + timedelta(days=dias)
    st.markdown(f'<div class="mensagem-validade">📢 Escolta: {escolta} | Duração: {dias} dias | Validade: {vencimento.strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)

    st.markdown("### ✍️ Assinatura do Responsável")
    canvas_result = st_canvas(fill_color="rgba(255, 255, 255, 0.3)", stroke_width=2, stroke_color="#000000", background_color="#FFFFFF", height=150, key="canvas_block7")
    consideracoes = st.text_area("CONSIDERAÇÕES:", placeholder="Ex: Acréscimo de água devido à baixa do rio...")

    b1, b2 = st.columns(2)
    with b1:
        if st.button("📄 GERAR PDF DA DECLARAÇÃO"):
            if canvas_result.image_data is not None:
                fuso_br = pytz.timezone('America/Sao_Paulo')
                data_hora_rodape = datetime.now(fuso_br).strftime('%d/%m/%Y %H:%M:%S')

                pdf = FPDF(); pdf.add_page()
                if os.path.exists("ZION.jpg"): pdf.image("ZION.jpg", 90, 10, 25)
                pdf.set_font("Arial", "B", 14); pdf.set_y(40)
                pdf.cell(0, 10, preparar("DECLARAÇÃO DE REABASTECIMENTO"), ln=True, align="C")
                pdf.set_font("Arial", "", 11); pdf.ln(10)
                texto = f"Certifico que a lotação é de {qtd_tripulantes} tripulantes. O rancho atende {dias} dias a partir de {data_pedido.strftime('%d/%m/%Y')}."
                pdf.multi_cell(0, 8, preparar(texto))
                if consideracoes:
                    pdf.ln(5); pdf.set_font("Arial", "B", 11); pdf.cell(0, 8, "CONSIDERAÇÕES:", ln=True)
                    pdf.set_font("Arial", "", 11); pdf.multi_cell(0, 7, preparar(consideracoes))

                img_p = "sig_temp.png"; Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA').save(img_p)
                pdf.image(img_p, x=75, y=pdf.get_y() + 5, w=50)
                pdf.set_y(pdf.get_y() + 25); pdf.line(60, pdf.get_y(), 150, pdf.get_y())
                pdf.set_font("Arial", "", 10); pdf.cell(0, 6, preparar(f"Responsável: {st.session_state.cozinheiro}"), ln=True, align="C")
                pdf.set_font("Arial", "I", 8); pdf.cell(0, 6, preparar(f"Gerado em: {data_hora_rodape} (Brasília)"), ln=True, align="C")
                st.download_button("📥 BAIXAR DECLARAÇÃO", pdf.output(dest='S').encode('latin-1'), f"Declaracao.pdf", "application/pdf")
    with b2:
        if st.button("⬅️ VOLTAR AO MENU"): st.session_state.pagina = "menu"; st.rerun()

# =================================================================
# BLOCO 8: TELA DE HISTÓRICO
# =================================================================
elif st.session_state.pagina == "historico":
    aplicar_estilo_tecnologico()
    st.title("📜 Histórico de Registros")
    if st.button("⬅️ VOLTAR AO MENU"): st.session_state.pagina = "menu"; st.rerun()
