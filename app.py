import streamlit as st
import pandas as pd
import requests
import os
from fpdf import FPDF

# =================================================================
# BLOCO 1: CONFIGURAÇÕES E ESTADOS
# =================================================================
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state:
    st.session_state.cozinheiro = ""
if 'df_lista' not in st.session_state:
    # Criamos um DataFrame inicial vazio com as colunas corretas para a tabela nunca sumir
    st.session_state.df_lista = pd.DataFrame(columns=["CODIGO", "PROTEINA", "TIPO", "UNIDADE DE MEDIDA", "ESTOQUE", "DESCRIÇÃO", "CONFIRMA"])

USUARIOS = {
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "NAVIO 03": {"nome": "Carlos", "senha": "456"}
}

# Função Real de Conexão (Substitua os tokens abaixo)
def buscar_dados_notion():
    NOTION_TOKEN = "SEU_INTERNAL_INTEGRATION_TOKEN"
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
            lista = []
            for p in dados:
                props = p.get("properties", {})
                lista.append({
                    "CODIGO": props.get("CODIGO", {}).get("title", [{}])[0].get("plain_text", ""),
                    "PROTEINA": props.get("PROTEINA", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "TIPO": props.get("TIPO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "UNIDADE DE MEDIDA": props.get("UNIDADE DE MEDIDA", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "ESTOQUE": props.get("ESTOQUE", {}).get("number", 0),
                    "DESCRIÇÃO": props.get("DESCRIÇÃO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "CONFIRMA": 0.0
                })
            return pd.DataFrame(lista)
        return st.session_state.df_lista # Retorna a estrutura vazia se falhar
    except:
        return st.session_state.df_lista

# Estilos CSS
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
# BLOCO DE NAVEGAÇÃO (HOME / LOGIN / MENU)
# =================================================================
if st.session_state.pagina == "home":
    st.title("Zion Rancho App")
    if st.button("INICIAR ACESSO"):
        st.session_state.pagina = "login"
        st.rerun()

elif st.session_state.pagina == "login":
    st.title("🔐 Login")
    navio_sel = st.selectbox("Navio", [""] + list(USUARIOS.keys()))
    senha_sel = st.text_input("Senha", type="password")
    if st.button("🛒 ENTRAR"):
        if navio_sel in USUARIOS and USUARIOS[navio_sel]["senha"] == senha_sel:
            st.session_state.cozinheiro = USUARIOS[navio_sel]["nome"]
            st.session_state.navio = navio_sel
            st.session_state.pagina = "menu"
            st.rerun()

elif st.session_state.pagina == "menu":
    st.markdown(f"## Bem-vindo, {st.session_state.cozinheiro}!")
    if st.button("🛒 LISTA DE RANCHO"):
        st.session_state.pagina = "lista"
        st.rerun()

# =================================================================
# TELA DE LISTA (CORRIGIDA: TABELA E BOTÕES SEMPRE VISÍVEIS)
# =================================================================
elif st.session_state.pagina == "lista":
    st.title(f"📋 Tabela de Rancho - {st.session_state.get('navio', '')}")
    
    # Botão de Sincronização
    if st.button("🔄 ATUALIZAR DADOS DO NOTION"):
        with st.spinner("Buscando dados reais..."):
            st.session_state.df_lista = buscar_dados_notion()
            st.rerun()

    # A tabela é exibida aqui. Mesmo vazia, as colunas aparecem.
    df_editado = st.data_editor(
        st.session_state.df_lista,
        column_config={
            "CODIGO": st.column_config.TextColumn("CÓD.", disabled=True),
            "PROTEINA": st.column_config.TextColumn("ITEM", disabled=True),
            "CONFIRMA": st.column_config.NumberColumn("SUA QTD", min_value=0),
        },
        hide_index=True,
        use_container_width=True,
        key="editor_unico"
    )

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📄 GERAR PDF"):
            # O PDF agora usa a estrutura correta de 7 colunas 
            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, f"Checklist de Rancho - {st.session_state.cozinheiro}", ln=True, align="C")
            
            # Cabeçalho da Tabela no PDF
            pdf.set_font("Arial", "B", 8)
            pdf.set_fill_color(200, 200, 200)
            larguras = [20, 45, 30, 20, 20, 70, 25]
            titulos = ["COD", "PROTEINA", "TIPO", "UNID", "ESTOQUE", "DESCRICAO", "CONF."]
            
            for i in range(len(titulos)):
                pdf.cell(larguras[i], 10, titulos[i], 1, 0, "C", True)
            pdf.ln()

            # Se a tabela estiver vazia, gera linhas em branco no PDF 
            pdf.set_font("Arial", "", 8)
            dados_para_pdf = df_editado if not df_editado.empty else pd.DataFrame([[""]*7]*5, columns=titulos)
            
            for _, row in dados_para_pdf.iterrows():
                for i, col in enumerate(df_editado.columns):
                    pdf.cell(larguras[i], 8, str(row.get(col, "")), 1)
                pdf.ln()

            pdf_out = pdf.output(dest='S').encode('latin-1')
            st.download_button("📥 BAIXAR PDF", data=pdf_out, file_name="rancho.pdf")

    with col2:
        if st.button("⬅️ VOLTAR"):
            st.session_state.pagina = "menu"
            st.rerun()
