# =================================================================
# BLOCO 1: IMPORTAÇÕES (ESSENCIAL PARA O PDF E ASSINATURA)
# =================================================================
import streamlit as st
import pandas as pd
import os
import requests
import unicodedata
from datetime import datetime
from fpdf import FPDF
from PIL import Image
from streamlit_drawable_canvas import st_canvas

# =================================================================
# BLOCO 2: CONFIGURAÇÃO DA PÁGINA E ESTILO
# =================================================================
st.set_page_config(page_title="Zion Rancho App", layout="centered")

# =================================================================
# BLOCO 3: VARIÁVEIS DE SESSÃO E BANCO DE DADOS (RESOLVE LINHA 22)
# =================================================================

# Definição das colunas para evitar o NameError
COLUNAS_PADRAO = ["Item", "Quantidade", "Unidade", "Navio", "Cozinheiro", "Data"]

# Dicionário de Usuários e Senhas
USUARIOS = {
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "NAVIO 03": {"nome": "Carlos", "senha": "456"}
}

# Inicialização do estado do sistema
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"

if 'df_lista' not in st.session_state:
    st.session_state.df_lista = pd.DataFrame(columns=COLUNAS_PADRAO)

if 'pdf_disponivel' not in st.session_state:
    st.session_state.pdf_disponivel = None

# =================================================================
# BLOCO 4: TELAS INICIAIS (HOME E LOGIN)
# =================================================================

# TELA HOME
if st.session_state.pagina == "home":
    st.markdown("<h1 style='text-align: center;'>Aplicativo Zion Rancho</h1>", unsafe_allow_html=True)
    
    # Exibe a imagem do robô se existir
    if os.path.exists("ZION.jpg"):
        st.image("ZION.jpg", use_container_width=True)
    elif os.path.exists("APPRANCHO.png"):
        st.image("APPRANCHO.png", use_container_width=True)
    
    if st.button("🚀 INICIAR ACESSO", use_container_width=True):
        st.session_state.pagina = "login"
        st.rerun()

# TELA DE LOGIN (COM SENHA)
elif st.session_state.pagina == "login":
    st.title("🔐 Acesso do Cozinheiro")
    
    navio_sel = st.selectbox("Selecione o seu Navio", list(USUARIOS.keys()))
    senha_ent = st.text_input("Digite a Senha de Acesso", type="password")
    
    if st.button("🛒 ENTRAR NO SISTEMA", use_container_width=True):
        if senha_ent == USUARIOS[navio_sel]["senha"]:
            st.session_state.cozinheiro = USUARIOS[navio_sel]["nome"]
            st.session_state.navio = navio_sel
            st.session_state.pagina = "tripulacao" # Conecta ao Bloco 5
            st.rerun()
        else:
            st.error("❌ Senha incorreta!")

# =================================================================
# BLOCO 5: TELA DE TRIPULAÇÃO E PDF (SUA VERSÃO PROFISSIONAL)
# =================================================================

elif st.session_state.pagina == "tripulacao":
    st.title("👨‍✈️ Declaração de Reabastecimento")
    
    def obter_localizacao_simples():
        try:
            response = requests.get('https://ipapi.co/json/', timeout=3)
            dados = response.json()
            return f"{dados.get('city', 'Cidade')}/{dados.get('region', 'Estado')}"
        except:
            return "Localização não identificada"

    with st.form("form_tripulacao"):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Responsável", value=st.session_state.cozinheiro, disabled=True)
            st.text_input("Empurrador", value=st.session_state.navio, disabled=True)
            data_ult = st.text_input("Data do Último Rancho", value="01/01/2026")
        
        with col2:
            data_ini = st.text_input("Data de Início", value=datetime.now().strftime("%d/%m/%Y"))
            origem = st.text_input("Origem", placeholder="Ex: Belém/PA")
            destino = st.text_input("Destino", placeholder="Ex: Santarém/PA")

        consideracoes = st.text_area("Observações:", height=80)

        st.subheader("✍️ Assinatura")
        canvas_result = st_canvas(
            stroke_width=3, stroke_color="#000000", background_color="#eeeeee",
            height=110, drawing_mode="freedraw", key="canvas_v_ajustada"
        )

        btn_gerar = st.form_submit_button("💾 SALVAR E GERAR DOCUMENTO")

    if btn_gerar:
        if not origem or not destino or canvas_result.image_data is None:
            st.error("⚠️ Preencha todos os campos e assine!")
        else:
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, f"DECLARACAO DE RANCHO - {st.session_state.navio}", 0, 1, "C")
                
                # Salvando assinatura temporária
                img_data = canvas_result.image_data.astype('uint8')
                Image.fromarray(img_data, 'RGBA').save("assinatura_temp.png")
                pdf.image("assinatura_temp.png", x=75, y=150, w=55)
                
                st.session_state.pdf_disponivel = pdf.output(dest='S').encode('latin-1')
                st.success("✅ PDF Gerado!")
            except Exception as e:
                st.error(f"Erro: {e}")

    if st.session_state.pdf_disponivel:
        st.download_button("📥 BAIXAR PDF", data=st.session_state.pdf_disponivel, file_name="Declaracao.pdf", mime="application/pdf")

    if st.button("⬅️ VOLTAR"):
        st.session_state.pagina = "home"
        st.rerun()
