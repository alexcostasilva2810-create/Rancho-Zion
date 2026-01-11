# =================================================================
# BLOCO 1: IMPORTAÇÕES
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
# BLOCO 2: CONFIGURAÇÃO E FUNÇÕES DE APOIO (NOTION)
# =================================================================
st.set_page_config(page_title="Zion Rancho App", layout="wide")

# Função para buscar dados do seu Notion (Ajuste os tokens se necessário)
def carregar_dados_do_notion():
    # Caso você tenha a lógica real da API, ela entra aqui. 
    # Por enquanto, mantemos a estrutura de colunas que seu Bloco 6 exige:
    dados = [
        {"CODIGO": "001", "PROTEINA": "ARROZ 5KG", "TIPO": "GRÃOS", "UNIDADE DE MEDIDA": "PCT", "ESTOQUE": 10, "DESCRIÇÃO": "POLIDO TYPE 1", "CONFIRMA": 0},
        {"CODIGO": "002", "PROTEINA": "FEIJÃO 1KG", "TIPO": "GRÃOS", "UNIDADE DE MEDIDA": "PCT", "ESTOQUE": 15, "DESCRIÇÃO": "CARIOCA", "CONFIRMA": 0},
        {"CODIGO": "003", "PROTEINA": "CARNE MOÍDA", "TIPO": "PROTEINA", "UNIDADE DE MEDIDA": "KG", "ESTOQUE": 20, "DESCRIÇÃO": "PATINHO", "CONFIRMA": 0},
    ]
    return pd.DataFrame(dados)

# Variáveis Globais
USUARIOS = {
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "NAVIO 03": {"nome": "Carlos", "senha": "456"}
}

# Inicialização da Sessão
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'df_lista' not in st.session_state:
    st.session_state.df_lista = carregar_dados_do_notion()
if 'pdf_disponivel' not in st.session_state:
    st.session_state.pdf_disponivel = None

# =================================================================
# BLOCO 3: TELAS DE ACESSO (HOME E LOGIN)
# =================================================================

if st.session_state.pagina == "home":
    st.markdown("<h1 style='text-align: center;'>Aplicativo Zion Rancho</h1>", unsafe_allow_html=True)
    if os.path.exists("ZION.jpg"):
        st.image("ZION.jpg", use_container_width=True)
    elif os.path.exists("APPRANCHO.png"):
        st.image("APPRANCHO.png", use_container_width=True)
    
    if st.button("🚀 INICIAR ACESSO", use_container_width=True):
        st.session_state.pagina = "login"
        st.rerun()

elif st.session_state.pagina == "login":
    st.title("🔐 Acesso do Cozinheiro")
    navio_sel = st.selectbox("Selecione o seu Navio", list(USUARIOS.keys()))
    senha_ent = st.text_input("Digite a Senha", type="password")
    
    if st.button("🛒 ENTRAR", use_container_width=True):
        if senha_ent == USUARIOS[navio_sel]["senha"]:
            st.session_state.cozinheiro = USUARIOS[navio_sel]["nome"]
            st.session_state.navio = navio_sel
            st.session_state.pagina = "menu"
            st.rerun()
        else:
            st.error("❌ Senha incorreta!")

# =================================================================
# BLOCO 4: TELA DE SUBMENU (ESCOLHA)
# =================================================================

elif st.session_state.pagina == "menu":
    st.title(f"🚢 Painel - {st.session_state.navio}")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 DECLARAÇÃO / TRIPULAÇÃO", use_container_width=True):
            st.session_state.pagina = "tripulacao"
            st.rerun()
    with col2:
        if st.button("📋 TABELA DE RANCHO (NOTION)", use_container_width=True):
            st.session_state.pagina = "lista" # AGORA APONTA PARA O BLOCO 6
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬅️ LOGOUT"):
        st.session_state.pagina = "home"
        st.rerun()

# =================================================================
# BLOCO 5: TELA DE TRIPULAÇÃO (PDF E ASSINATURA)
# =================================================================

elif st.session_state.pagina == "tripulacao":
    st.title("👨‍✈️ Declaração de Reabastecimento")
    # (O código de assinatura e PDF que você já validou)
    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"
        st.rerun()

# =================================================================
# BLOCO 6: TELA DE LISTA (INTEGRAÇÃO NOTION QUE VOCÊ ENVIOU)
# =================================================================

elif st.session_state.pagina == "lista":
    st.title(f"📋 Tabela de Rancho - {st.session_state.get('navio', '')}")

    if st.button("🔄 ATUALIZAR DADOS DO NOTION"):
        with st.spinner("Conectando ao Notion..."):
            st.session_state.df_lista = carregar_dados_do_notion()
            st.rerun()

    df_editado = st.data_editor(
        st.session_state.df_lista,
        column_config={
            "CODIGO": st.column_config.TextColumn("CÓD.", disabled=True),
            "PROTEINA": st.column_config.TextColumn("ITEM", disabled=True),
            "ESTOQUE": st.column_config.NumberColumn("ESTOQUE", disabled=True),
            "CONFIRMA": st.column_config.NumberColumn("SUA QTD", min_value=0),
        },
        hide_index=True,
        use_container_width=True,
        key="editor_lista_real"
    )

    st.markdown("---")
    c1, c2 = st.columns(2)
    
    with c1:
        if st.button("📄 GERAR PDF"):
            try:
                pdf = FPDF(orientation='L', unit='mm', format='A4')
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, f"Checklist de Rancho - Cozinheiro: {st.session_state.cozinheiro}", ln=True, align="C")
                
                pdf.set_font("Arial", "B", 8)
                pdf.set_fill_color(220, 220, 220)
                larguras = [20, 50, 25, 20, 20, 85, 25]
                titulos_pdf = ["COD", "PROTEINA", "TIPO", "UNID", "ESTOQUE", "DESCRICAO", "CONF."]
                
                for i, titulo in enumerate(titulos_pdf):
                    pdf.cell(larguras[i], 10, titulo, 1, 0, "C", True)
                pdf.ln()

                pdf.set_font("Arial", "", 8)
                for _, row in df_editado.iterrows():
                    pdf.cell(larguras[0], 8, str(row.get("CODIGO", "")), 1)
                    pdf.cell(larguras[1], 8, str(row.get("PROTEINA", "")), 1)
                    pdf.cell(larguras[2], 8, str(row.get("TIPO", "")), 1)
                    pdf.cell(larguras[3], 8, str(row.get("UNIDADE DE MEDIDA", "")), 1)
                    pdf.cell(larguras[4], 8, str(row.get("ESTOQUE", "0")), 1, 0, "C")
                    pdf.cell(larguras[5], 8, str(row.get("DESCRIÇÃO", "")), 1)
                    pdf.cell(larguras[6], 8, str(row.get("CONFIRMA", "0")), 1, 1, "C")

                pdf_out = pdf.output(dest='S').encode('latin-1')
                st.download_button("📥 BAIXAR PDF COMPLETO", data=pdf_out, file_name="Zion_Rancho.pdf")
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}")

    with c2:
        if st.button("⬅️ VOLTAR AO MENU"):
            st.session_state.pagina = "menu"
            st.rerun()
