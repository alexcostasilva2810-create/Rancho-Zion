# =================================================================
# BLOCO 1: IMPORTAÇÕES COMPLETAS
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
# BLOCO 2: CONFIGURAÇÃO INICIAL E RESOLUÇÃO DA LINHA 22
# =================================================================
st.set_page_config(page_title="Zion Rancho App", layout="centered")

# Definição obrigatória para evitar NameError
COLUNAS_PADRAO = ["Item", "Quantidade", "Unidade", "Navio", "Cozinheiro", "Data"]

# Dicionário de usuários conforme seu banco de dados
USUARIOS = {
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "NAVIO 03": {"nome": "Carlos", "senha": "456"}
}

# Inicialização de variáveis de sessão
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'df_lista' not in st.session_state:
    st.session_state.df_lista = pd.DataFrame(columns=COLUNAS_PADRAO)
if 'pdf_disponivel' not in st.session_state:
    st.session_state.pdf_disponivel = None
if 'navio' not in st.session_state:
    st.session_state.navio = ""
if 'cozinheiro' not in st.session_state:
    st.session_state.cozinheiro = ""

# =================================================================
# BLOCO 3: TELA HOME (COM IMAGEM DO ROBÔ)
# =================================================================
if st.session_state.pagina == "home":
    st.markdown("<h1 style='text-align: center;'>Aplicativo Zion Rancho</h1>", unsafe_allow_html=True)
    
    # Busca a imagem do robô ou a logo antiga
    if os.path.exists("ZION.jpg"):
        st.image("ZION.jpg", use_container_width=True)
    elif os.path.exists("APPRANCHO.png"):
        st.image("APPRANCHO.png", use_container_width=True)
    
    if st.button("🚀 INICIAR ACESSO", use_container_width=True):
        st.session_state.pagina = "login"
        st.rerun()

# =================================================================
# BLOCO 4: TELA DE LOGIN (VALIDAÇÃO POR SENHA)
# =================================================================
elif st.session_state.pagina == "login":
    st.title("🔐 Acesso do Cozinheiro")
    
    navio_sel = st.selectbox("Selecione o seu Navio", list(USUARIOS.keys()))
    senha_ent = st.text_input("Digite a Senha de Acesso", type="password")
    
    if st.button("🛒 ENTRAR NO SISTEMA", use_container_width=True):
        if senha_ent == USUARIOS[navio_sel]["senha"]:
            st.session_state.cozinheiro = USUARIOS[navio_sel]["nome"]
            st.session_state.navio = navio_sel
            st.session_state.pagina = "menu" # Leva ao Submenu
            st.rerun()
        else:
            st.error("❌ Senha incorreta! Tente novamente.")

# =================================================================
# BLOCO 4.5: SUBMENU DE ESCOLHA (A TELA QUE FALTAVA)
# =================================================================
elif st.session_state.pagina == "menu":
    st.title(f"🚢 Painel - {st.session_state.navio}")
    st.subheader(f"Cozinheiro: {st.session_state.cozinheiro}")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 GERAR DECLARAÇÃO\n(PDF COM ASSINATURA)", use_container_width=True):
            st.session_state.pagina = "tripulacao"
            st.rerun()
            
    with col2:
        if st.button("📦 LANÇAR ITENS\n(LISTA DE RANCHO)", use_container_width=True):
            st.session_state.pagina = "lancamento"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬅️ LOGOUT (SAIR)"):
        st.session_state.pagina = "home"
        st.rerun()

# =================================================================
# BLOCO 5: TELA DE DECLARAÇÃO PROFISSIONAL (COM PDF E ASSINATURA)
# =================================================================
elif st.session_state.pagina == "tripulacao":
    st.title("👨‍✈️ Declaração de Reabastecimento")
    
    def obter_localizacao_simples():
        try:
            response = requests.get('https://ipapi.co/json/', timeout=3)
            dados = response.json()
            return f"{dados.get('city', 'Cidade')}/{dados.get('region', 'Estado')}"
        except:
            return "Localização via Satélite"

    with st.form("form_tripulacao", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Responsável", value=st.session_state.cozinheiro, disabled=True)
            st.text_input("Empurrador", value=st.session_state.navio, disabled=True)
            data_ult_br = st.text_input("Data do Último Rancho", value="01/01/2026")
        
        with col2:
            data_hoje_br = datetime.now().strftime("%d/%m/%Y")
            data_input_br = st.text_input("Data de Início", value=data_hoje_br)
            origem = st.text_input("Origem", placeholder="Ex: Belém/PA")
            destino = st.text_input("Destino", placeholder="Ex: Santarém/PA")

        st.markdown("---")
        consideracoes = st.text_area("Observações (Limpeza, água, pessoal extra):", height=80)

        st.subheader("✍️ Assinatura Digital")
        canvas_result = st_canvas(
            stroke_width=3, stroke_color="#000000", background_color="#eeeeee",
            height=110, drawing_mode="freedraw", key="canvas_trip"
        )

        btn_gerar = st.form_submit_button("💾 SALVAR E GERAR PDF", use_container_width=True)

    if btn_gerar:
        if not origem or not destino or canvas_result.image_data is None:
            st.error("⚠️ Preencha Origem, Destino e realize a Assinatura!")
        else:
            local_real = obter_localizacao_simples()
            def blindar(t):
                return unicodedata.normalize('NFKD', str(t)).encode('ascii', 'ignore').decode('ascii')

            try:
                pdf = FPDF()
                pdf.add_page()
                
                # Cabeçalho
                if os.path.exists("APPRANCHO.png"):
                    pdf.image("APPRANCHO.png", 10, 10, 30)
                
                pdf.set_font("Arial", "B", 14)
                pdf.set_xy(45, 20)
                pdf.cell(0, 10, blindar(f"DECLARACAO DE RANCHO - {st.session_state.navio}"), 0, 1, "L")
                
                pdf.ln(20)
                pdf.set_font("Arial", "", 12)
                corpo = (f"A provisao de rancho a ser reabastecida destina-se a cobrir as necessidades "
                         f"nutricionais da tripulacao por um periodo de 15 dias, a partir de {data_input_br}.")
                pdf.multi_cell(0, 8, blindar(corpo))
                
                pdf.ln(5)
                pdf.cell(0, 8, blindar(f"Origem: {origem}"), 0, 1)
                pdf.cell(0, 8, blindar(f"Destino: {destino}"), 0, 1)

                # Assinatura
                img_data = canvas_result.image_data.astype('uint8')
                Image.fromarray(img_data, 'RGBA').save("assinatura_temp.png")
                pdf.image("assinatura_temp.png", x=75, y=pdf.get_y()+10, w=50)
                
                pdf.set_y(-30)
                pdf.set_font("Arial", "I", 8)
                pdf.cell(0, 5, blindar(f"Registro: {datetime.now().strftime('%d/%m/%Y')} | Local: {local_real}"), 0, 0, "C")

                st.session_state.pdf_disponivel = pdf.output(dest='S').encode('latin-1')
                st.success("✅ Documento pronto para download!")
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}")

    if st.session_state.pdf_disponivel:
        st.download_button("📥 BAIXAR DECLARAÇÃO PDF", data=st.session_state.pdf_disponivel, 
                           file_name=f"Declaracao_{st.session_state.navio}.pdf", mime="application/pdf", use_container_width=True)

    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pdf_disponivel = None
        st.session_state.pagina = "menu"
        st.rerun()

# =================================================================
# BLOCO 6: TELA DE LANÇAMENTO DE ITENS (LISTA)
# =================================================================
elif st.session_state.pagina == "lancamento":
    st.title("📦 Lista de Pedidos")
    # (Aqui você pode colocar o código de adicionar itens à tabela df_lista se desejar)
    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"
        st.rerun()
