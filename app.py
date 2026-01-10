import streamlit as st
import pandas as pd
import requests
import os
from fpdf import FPDF

# =================================================================
# BLOCO 1: CONFIGURAÇÕES DE ESTADO E SEGURANÇA
# =================================================================
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state:
    st.session_state.cozinheiro = ""
if 'navio' not in st.session_state:
    st.session_state.navio = ""

# Colunas atualizadas conforme sua nova base do Notion
COLUNAS_PADRAO = ["ITEM", "DESCRIÇÃO", "TIPO", "UNID MED", "PREDEFINIDO", "CONFIRMA"]

if 'df_lista' not in st.session_state:
    st.session_state.df_lista = pd.DataFrame(columns=COLUNAS_PADRAO)

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
                    "ITEM": p.get("ITEM", {}).get("title", [{}])[0].get("plain_text", ""),
                    "DESCRIÇÃO": p.get("DESCRIÇÃO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "TIPO": p.get("TIPO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "UNID MED": p.get("UNID MED", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "PREDEFINIDO": p.get("PREDEFINIDO", {}).get("number", 0),
                    "CONFIRMA": 0
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
        color: black !important;
        font-weight: 900 !important;
        border-radius: 10px !important;
        height: 3.5em;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# BLOCO 4: TELA INICIAL
# =================================================================
if st.session_state.pagina == "home":
    st.title("Zion Rancho App")
    st.write("Seu controle de estoque inteligente com IA.")
    if os.path.exists("APPRANCHO.png"):
        st.image("APPRANCHO.png", width=400)
    if st.button("INICIAR ACESSO"):
        st.session_state.pagina = "login"
        st.rerun()

# =================================================================
# BLOCO 5: LOGIN E SUBTELA
# =================================================================
elif st.session_state.pagina == "login":
    st.title("🔐 Login")
    navio = st.selectbox("Embarcação", [""] + list(USUARIOS.keys()))
    senha = st.text_input("Senha", type="password")
    if st.button("ENTRAR"):
        if navio in USUARIOS and USUARIOS[navio]["senha"] == senha:
            st.session_state.cozinheiro = USUARIOS[navio]["nome"]
            st.session_state.navio = navio
            st.success(f"✅ Bem-vindo, {st.session_state.cozinheiro}!")
            st.session_state.pagina = "menu"
            st.rerun()
        else:
            st.error("❌ Credenciais inválidas.")

elif st.session_state.pagina == "menu":
    st.title(f"Olá, {st.session_state.cozinheiro}!")
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
# BLOCO 6: TELA DE LISTA (CORREÇÃO DE PDF INCLUÍDA)
# =================================================================
elif st.session_state.pagina == "lista":
    st.title(f"📋 Rancho - {st.session_state.navio}")
    st.write(f"**Responsável:** {st.session_state.cozinheiro}")

    if st.button("🔄 ATUALIZAR DADOS DO NOTION"):
        st.session_state.df_lista = carregar_dados_do_notion()
        st.rerun()

    # TRAVA DE COLUNAS: Apenas 'CONFIRMA' é editável
    df_editado = st.data_editor(
        st.session_state.df_lista,
        column_config={
            "ITEM": st.column_config.TextColumn("ITEM", disabled=True),
            "DESCRIÇÃO": st.column_config.TextColumn("DESCRIÇÃO", disabled=True),
            "TIPO": st.column_config.TextColumn("TIPO", disabled=True),
            "UNID MED": st.column_config.TextColumn("UNID.", disabled=True),
            "PREDEFINIDO": st.column_config.NumberColumn("PREDEF.", disabled=True),
            "CONFIRMA": st.column_config.NumberColumn("CONFIRMA (Sua Qtd)", min_value=0),
        },
        hide_index=True,
        use_container_width=True
    )

    st.markdown("---")
    c1, c2 = st.columns(2)
    
    with c1:
        if st.button("📄 GERAR PDF"):
            # Função interna para limpar acentos e evitar o erro Unicode
            def normalizar(texto):
                import unicodedata
                return "".join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn')

            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, normalizar(f"Checklist de Rancho - Responsavel: {st.session_state.cozinheiro}"), ln=True, align="C")
            
            pdf.set_font("Arial", "B", 8)
            pdf.set_fill_color(200, 200, 200)
            larguras = [15, 80, 30, 20, 25, 25]
            titulos = ["ITEM", "DESCRICAO", "TIPO", "UNID", "PREDEF", "CONF"]
            
            for i, titulo in enumerate(titulos):
                pdf.cell(larguras[i], 10, titulo, 1, 0, "C", True)
            pdf.ln()

            pdf.set_font("Arial", "", 8)
            for _, row in df_editado.iterrows():
                pdf.cell(larguras[0], 8, normalizar(row["ITEM"]), 1)
                pdf.cell(larguras[1], 8, normalizar(row["DESCRIÇÃO"]), 1)
                pdf.cell(larguras[2], 8, normalizar(row["TIPO"]), 1)
                pdf.cell(larguras[3], 8, normalizar(row["UNID MED"]), 1)
                pdf.cell(larguras[4], 8, str(row["PREDEFINIDO"]), 1)
                pdf.cell(larguras[5], 8, str(row["CONFIRMA"]), 1)
                pdf.ln()

            # Gera o PDF sem o erro de codificação
            pdf_output = pdf.output(dest='S')
            st.download_button("📥 BAIXAR PDF", data=pdf_output, file_name=f"Rancho_{st.session_state.navio}.pdf", mime="application/pdf")

    with c2:
        if st.button("⬅️ VOLTAR AO MENU"):
            st.session_state.pagina = "menu"
            st.rerun()

# =================================================================
# BLOCO 7: TELA DE TRIPULAÇÃO
# =================================================================
elif st.session_state.pagina == "tripulacao":
    st.title("👨‍✈️ Gestão de Tripulação")
    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"
        st.rerun()
