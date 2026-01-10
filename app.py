import streamlit as st
import pandas as pd
import requests
import os
from fpdf import FPDF

# =================================================================
# BLOCO 1: CONFIGURAÇÕES, ESTADOS E ESTRUTURA PADRÃO
# =================================================================
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state:
    st.session_state.cozinheiro = ""

# Colunas padrão baseadas no seu banco de dados Notion
COLUNAS_PADRAO = ["CODIGO", "PROTEINA", "TIPO", "UNIDADE DE MEDIDA", "ESTOQUE", "DESCRIÇÃO", "CONFIRMA"]

if 'df_lista' not in st.session_state:
    # Garante que a tabela apareça mesmo se o Notion não carregar
    st.session_state.df_lista = pd.DataFrame(columns=COLUNAS_PADRAO)

# =================================================================
# BLOCO 2: FUNÇÃO DE INTEGRAÇÃO COM NOTION (TOKEN E ID INSERIDOS)
# =================================================================
def carregar_dados_do_notion():
    """Busca os dados reais inseridos no Notion"""
    # Seus códigos de acesso
    NOTION_TOKEN = "ntn_jZ6353375938j9kJFqKWjD0N4ONt1rwP515tsIMwxtucHa"
    DATABASE_ID = "2e3025de7b79803abe0efde74f87a2e1"
    
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            results = response.json().get("results", [])
            dados_notion = []
            for page in results:
                p = page.get("properties", {})
                # Mapeamento exato das colunas do seu Notion
                dados_notion.append({
                    "CODIGO": p.get("CODIGO", {}).get("title", [{}])[0].get("plain_text", ""),
                    "PROTEINA": p.get("PROTEINA", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "TIPO": p.get("TIPO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "UNIDADE DE MEDIDA": p.get("UNIDADE DE MEDIDA", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "ESTOQUE": p.get("ESTOQUE", {}).get("number", 0),
                    "DESCRIÇÃO": p.get("DESCRIÇÃO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "CONFIRMA": 0.0
                })
            return pd.DataFrame(dados_notion)
        else:
            st.error(f"Erro de conexão: {response.status_code}")
            return st.session_state.df_lista
    except Exception as e:
        st.error(f"Falha ao carregar dados: {e}")
        return st.session_state.df_lista

# =================================================================
# BLOCO 3: ESTILO VISUAL (CSS)
# =================================================================
st.markdown("""
    <style>
    .stApp { background-color: #4169E1 !important; }
    h1, h2, h3, p, label { color: white !important; }
    div.stButton > button {
        background-color: #FF8C00 !important;
        color: #000000 !important;
        font-weight: 900 !important;
        border-radius: 10px !important;
        border: 2px solid #000000 !important;
        width: 100%;
        height: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# BLOCO 4: TELAS INICIAIS (HOME E LOGIN)
# =================================================================
if st.session_state.pagina == "home":
    st.title("Bem-vindo ao Zion Rancho App!")
    if st.button("INICIAR ACESSO"):
        st.session_state.pagina = "login"
        st.rerun()

elif st.session_state.pagina == "login":
    st.title("🔐 Acesso do Cozinheiro")
    navio = st.selectbox("Selecione o seu Navio", ["AROEIRA", "NAVIO 01", "NAVIO 03"])
    if st.button("🛒 ENTRAR"):
        st.session_state.cozinheiro = "Marcos"
        st.session_state.navio = navio
        st.session_state.pagina = "menu"
        st.rerun()

# =================================================================
# BLOCO 5: MENU PRINCIPAL (SUBTELA COM TRIPULAÇÃO E RANCHO)
# =================================================================
elif st.session_state.pagina == "menu":
    st.markdown(f"## Seja Bem-vindo, {st.session_state.cozinheiro}!")
    st.write(f"Gestão atual: **{st.session_state.navio}**")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛒 LISTA DE RANCHO"):
            st.session_state.pagina = "lista"
            st.rerun()
    with col2:
        if st.button("👨‍✈️ TRIPULAÇÃO"):
            st.session_state.pagina = "tripulacao"
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("SAIR DO SISTEMA"):
        st.session_state.pagina = "home"
        st.rerun()

# =================================================================
# BLOCO 6: TELA DE LISTA (CORRIGIDA E INTEGRADA)
# =================================================================
elif st.session_state.pagina == "lista":
    st.title(f"📋 Tabela de Rancho - {st.session_state.get('navio', '')}")

    # Botão de Sincronização Real
    if st.button("🔄 ATUALIZAR DADOS DO NOTION"):
        with st.spinner("Conectando ao Notion..."):
            st.session_state.df_lista = carregar_dados_do_notion()
            st.rerun()

    # Tabela sempre visível
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
            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, f"Checklist de Rancho - Cozinheiro: {st.session_state.cozinheiro}", ln=True, align="C")
            
            # Cabeçalho da Tabela no PDF
            pdf.set_font("Arial", "B", 8)
            pdf.set_fill_color(220, 220, 220)
            larguras = [20, 50, 25, 20, 20, 85, 25]
            titulos_pdf = ["COD", "PROTEINA", "TIPO", "UNID", "ESTOQUE", "DESCRICAO", "CONF."]
            
            for i, titulo in enumerate(titulos_pdf):
                pdf.cell(larguras[i], 10, titulo, 1, 0, "C", True)
            pdf.ln()

            # Preenchimento do PDF
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

    with c2:
        if st.button("⬅️ VOLTAR AO MENU"):
            st.session_state.pagina = "menu" # Volta para o Bloco 5
            st.rerun()

# =================================================================
# BLOCO 7: TELA DE TRIPULAÇÃO
# =================================================================
elif st.session_state.pagina == "tripulacao":
    st.title("👨‍✈️ Gestão de Tripulação")
    st.write("Insira os dados da tripulação abaixo:")
    # Espaço para futuros inputs de tripulação
    st.text_input("Nome do Tripulante")
    st.selectbox("Função", ["Comandante", "Cozinheiro", "Marinheiro"])
    
    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"
        st.rerun()
