import streamlit as st
import pandas as pd
import requests
import os
from fpdf import FPDF

# =================================================================
# BLOCO 1: CONFIGURAÇÕES, ESTADOS E ESTILO (CSS)
# =================================================================
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state:
    st.session_state.cozinheiro = ""
if 'df_lista' not in st.session_state:
    st.session_state.df_lista = pd.DataFrame()

# Dicionário de acesso
USUARIOS = {
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "NAVIO 03": {"nome": "Carlos", "senha": "456"}
}

# FUNÇÃO DE CONEXÃO COM NOTION
def carregar_dados_notion():
    # SUBSTITUA PELOS SEUS DADOS REAIS
    NOTION_TOKEN = "SEU_TOKEN_AQUI"
    DATABASE_ID = "ID_DA_SUA_DATABASE"
    
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            dados = response.json().get("results", [])
            lista_final = []
            for p in dados:
                props = p.get("properties", {})
                lista_final.append({
                    "CODIGO": props.get("CODIGO", {}).get("title", [{}])[0].get("plain_text", ""),
                    "PROTEINA": props.get("PROTEINA", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "TIPO": props.get("TIPO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "UNIDADE DE MEDIDA": props.get("UNIDADE DE MEDIDA", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "ESTOQUE": props.get("ESTOQUE", {}).get("number", 0),
                    "DESCRIÇÃO": props.get("DESCRIÇÃO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "CONFIRMA": 0.0
                })
            return pd.DataFrame(lista_final)
        else:
            return pd.DataFrame()
    except:
        return pd.DataFrame()

# Estilos CSS
st.markdown("""
    <style>
    .stApp { background-color: #4169E1 !important; }
    h1, h2, h3, p, label { color: white !important; }
    div.stButton > button {
        background-color: #FF8C00 !important;
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 18px !important;
        border-radius: 10px !important;
        border: 2px solid #000000 !important;
        width: 100%;
        height: 3.5em;
    }
    input { color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# BLOCO 2 & 3: TELAS DE HOME E LOGIN
# =================================================================
if st.session_state.pagina == "home":
    st.title("Bem-vindo ao Zion Rancho App!")
    if os.path.exists("APPRANCHO.png"):
        st.image("APPRANCHO.png", width=400)
    if st.button("INICIAR ACESSO"):
        st.session_state.pagina = "login"
        st.rerun()

elif st.session_state.pagina == "login":
    st.title("🔐 Acesso do Cozinheiro")
    navio_sel = st.selectbox("Selecione o seu Navio", [""] + list(USUARIOS.keys()))
    senha_sel = st.text_input("Senha de Acesso", type="password")
    
    if st.button("🛒 ENTRAR"):
        if navio_sel in USUARIOS and USUARIOS[navio_sel]["senha"] == senha_sel:
            st.session_state.cozinheiro = USUARIOS[navio_sel]["nome"]
            st.session_state.navio = navio_sel
            st.session_state.pagina = "menu"
            st.rerun()
        else:
            st.error("Credenciais inválidas.")

# =================================================================
# BLOCO 4: MENU PRINCIPAL
# =================================================================
elif st.session_state.pagina == "menu":
    st.markdown(f"## Seja Bem-vindo, {st.session_state.cozinheiro}!")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛒 LISTA DE RANCHO"):
            st.session_state.pagina = "lista"
            st.rerun()
    with col2:
        if st.button("👨‍✈️ TRIPULAÇÃO"):
            st.session_state.pagina = "tripulacao"
            st.rerun()

# =================================================================
# BLOCO 5: TELA DA LISTA (UNIFICADA E CORRIGIDA)
# =================================================================
elif st.session_state.pagina == "lista":
    nome_navio = st.session_state.get('navio', 'NAVIO').upper()
    st.markdown(f"## 📋 Tabela de Rancho - {nome_navio}")

    # Botão de Sincronização
    if st.button("🔄 ATUALIZAR DADOS DO NOTION"):
        with st.spinner("Conectando ao banco de dados..."):
            st.session_state.df_lista = carregar_dados_notion()
            st.rerun()

    if st.session_state.df_lista.empty:
        st.warning("⚠️ A lista está vazia. Clique no botão 'ATUALIZAR DADOS' acima.")
    else:
        # EDITOR COM TODAS AS COLUNAS DO NOTION
        df_usuario = st.data_editor(
            st.session_state.df_lista,
            column_config={
                "CODIGO": st.column_config.TextColumn("CÓD.", disabled=True),
                "PROTEINA": st.column_config.TextColumn("ITEM", disabled=True),
                "UNIDADE DE MEDIDA": st.column_config.TextColumn("UNID.", disabled=True),
                "ESTOQUE": st.column_config.NumberColumn(disabled=True),
                "CONFIRMA": st.column_config.NumberColumn("SUA QTD", min_value=0.0),
            },
            hide_index=True,
            use_container_width=True,
            key="editor_final"
        )

        st.markdown("---")
        col_pdf, col_voltar = st.columns(2)

        with col_pdf:
            if st.button("📄 GERAR PDF COMPLETO"):
                pdf = FPDF(orientation='L', unit='mm', format='A4')
                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, f"CHECKLIST DE RANCHO - {nome_navio}", ln=True, align="C")
                pdf.set_font("Arial", "", 12)
                pdf.cell(0, 10, f"Cozinheiro: {st.session_state.cozinheiro}", ln=True, align="C")
                pdf.ln(5)

                # Cabeçalho do PDF
                pdf.set_font("Arial", "B", 8)
                pdf.set_fill_color(255, 140, 0)
                # Larguras otimizadas para Paisagem
                w = [20, 50, 30, 20, 20, 85, 25]
                titulos = ["COD", "PROTEINA", "TIPO", "UNID", "ESTQ", "DESCRICAO", "CONF."]
                
                for i in range(len(titulos)):
                    pdf.cell(w[i], 10, titulos[i], 1, 0, "C", True)
                pdf.ln()

                # Linhas do PDF
                pdf.set_font("Arial", "", 8)
                for _, row in df_usuario.iterrows():
                    pdf.cell(w[0], 8, str(row.get("CODIGO","")), 1)
                    pdf.cell(w[1], 8, str(row.get("PROTEINA","")), 1)
                    pdf.cell(w[2], 8, str(row.get("TIPO","")), 1)
                    pdf.cell(w[3], 8, str(row.get("UNIDADE DE MEDIDA","")), 1)
                    pdf.cell(w[4], 8, str(row.get("ESTOQUE","0")), 1, 0, "C")
                    pdf.cell(w[5], 8, str(row.get("DESCRIÇÃO","")), 1)
                    pdf.cell(w[6], 8, str(row.get("CONFIRMA","0")), 1, 1, "C")

                pdf_output = pdf.output(dest='S').encode('latin-1')
                st.download_button("📥 BAIXAR RELATÓRIO", data=pdf_output, file_name=f"Rancho_{nome_navio}.pdf")

        with col_voltar:
            if st.button("⬅️ MENU"):
                st.session_state.pagina = "menu"
                st.rerun()
