import streamlit as st
import pandas as pd
import requests
import os
from fpdf import FPDF

# =================================================================
# BLOCO 1: CONFIGURAÇÕES DE ESTADO E ESTRUTURA
# =================================================================
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state:
    st.session_state.cozinheiro = ""
if 'navio' not in st.session_state:
    st.session_state.navio = ""

# Colunas padrão do Notion
COLUNAS_PADRAO = ["CODIGO", "PROTEINA", "TIPO", "UNIDADE DE MEDIDA", "ESTOQUE", "DESCRIÇÃO", "CONFIRMA"]

if 'df_lista' not in st.session_state:
    st.session_state.df_lista = pd.DataFrame(columns=COLUNAS_PADRAO)

# Credenciais de acesso
USUARIOS = {
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "NAVIO 03": {"nome": "Carlos", "senha": "456"}
}

# =================================================================
# BLOCO 2: FUNÇÃO DE INTEGRAÇÃO COM NOTION
# =================================================================
def carregar_dados_do_notion():
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
        return st.session_state.df_lista
    except:
        return st.session_state.df_lista

# =================================================================
# BLOCO 3: ESTILO VISUAL (PADRÃO ZION)
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
# BLOCO 4: TELA INICIAL (RESTAURADA ORIGINAL)
# =================================================================
if st.session_state.pagina == "home":
    st.title("Zion Rancho App")
    st.write("Seu controle de estoque inteligente com IA.")
    
    if os.path.exists("APPRANCHO.png"):
        st.image("APPRANCHO.png", width=400)
    
    if st.button("INICIAR ACESSO", key="btn_home"):
        st.session_state.pagina = "login"
        st.rerun()

# =================================================================
# BLOCO 5: LOGIN COM VALIDAÇÃO E MENSAGENS (RESTAURADO)
# =================================================================
elif st.session_state.pagina == "login":
    st.title("🔐 Acesso Restrito")
    
    navio_selecionado = st.selectbox("Selecione a Embarcação", [""] + list(USUARIOS.keys()))
    senha_digitada = st.text_input("Digite a Senha de Acesso", type="password")
    
    if st.button("🛒 ENTRAR NO SISTEMA"):
        if navio_selecionado in USUARIOS:
            if USUARIOS[navio_selecionado]["senha"] == senha_digitada:
                st.session_state.cozinheiro = USUARIOS[navio_selecionado]["nome"]
                st.session_state.navio = navio_selecionado
                st.success(f"✅ Bem-vindo, {st.session_state.cozinheiro}! Acesso autorizado.")
                st.session_state.pagina = "menu"
                st.rerun()
            else:
                st.error("❌ Senha incorreta! Tente novamente.")
        else:
            st.warning("⚠️ Selecione uma embarcação válida.")

# =================================================================
# BLOCO 6: SUBTELA (MENU PRINCIPAL)
# =================================================================
elif st.session_state.pagina == "menu":
    st.markdown(f"## Olá, {st.session_state.cozinheiro}!")
    st.write(f"Gestão da Unidade: **{st.session_state.navio}**")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛒 LISTA DE RANCHO"):
            st.session_state.pagina = "lista"
            st.rerun()
    with col2:
        if st.button("👨‍✈️ TRIPULAÇÃO"):
            st.session_state.pagina = "tripulacao"
            st.rerun()
    
    if st.button("SAIR DO SISTEMA"):
        st.session_state.pagina = "home"
        st.rerun()

# =================================================================
# BLOCO 7: TELA DE LISTA (TABELA E PDF)
# =================================================================
elif st.session_state.pagina == "lista":
    st.title(f"📋 Rancho - {st.session_state.navio}")

    if st.button("🔄 ATUALIZAR DADOS DO NOTION"):
        with st.spinner("Sincronizando com a base de dados..."):
            st.session_state.df_lista = carregar_dados_do_notion()
            st.rerun()

    # Tabela sempre visível
    df_editado = st.data_editor(
        st.session_state.df_lista,
        column_config={
            "CONFIRMA": st.column_config.NumberColumn("SUA QTD", min_value=0),
            "ESTOQUE": st.column_config.NumberColumn("ESTOQUE", disabled=True),
        },
        hide_index=True,
        use_container_width=True
    )

    st.markdown("---")
    c1, c2 = st.columns(2)
    
    with c1:
        if st.button("📄 GERAR PDF"):
            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, f"Checklist de Rancho - {st.session_state.cozinheiro}", ln=True, align="C")
            
            # Cabeçalho
            pdf.set_font("Arial", "B", 8)
            pdf.set_fill_color(200, 200, 200)
            larguras = [20, 45, 25, 20, 20, 85, 25]
            for i, titulo in enumerate(COLUNAS_PADRAO):
                pdf.cell(larguras[i], 10, titulo[:10], 1, 0, "C", True)
            pdf.ln()

            # Linhas
            pdf.set_font("Arial", "", 8)
            for _, row in df_editado.iterrows():
                for i, col in enumerate(COLUNAS_PADRAO):
                    pdf.cell(larguras[i], 8, str(row.get(col, "")), 1)
                pdf.ln()

            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            st.download_button("📥 BAIXAR PDF", data=pdf_bytes, file_name=f"Rancho_{st.session_state.navio}.pdf")

    with c2:
        if st.button("⬅️ VOLTAR AO MENU"):
            st.session_state.pagina = "menu"
            st.rerun()

# =================================================================
# BLOCO 8: TELA DE TRIPULAÇÃO
# =================================================================
elif st.session_state.pagina == "tripulacao":
    st.title("👨‍✈️ Gestão de Tripulação")
    st.info("Formulário de tripulação em desenvolvimento.")
    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"
        st.rerun()
