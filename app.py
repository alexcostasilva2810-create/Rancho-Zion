import streamlit as st
import pandas as pd
import requests
import os
from fpdf import FPDF
import unicodedata

# =================================================================
# BLOCO 1: CONFIGURAÇÕES E SEGURANÇA (TRAVAS)
# =================================================================
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state:
    st.session_state.cozinheiro = ""
if 'navio' not in st.session_state:
    st.session_state.navio = ""

# Colunas conforme sua nova base do Notion
COLUNAS_PADRAO = ["ITEM", "DESCRIÇÃO", "TIPO", "UNID MED", "PREDEFINIDO", "CONFIRMA"]

if 'df_lista' not in st.session_state:
    st.session_state.df_lista = pd.DataFrame(columns=COLUNAS_PADRAO)

USUARIOS = {
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "NAVIO 03": {"nome": "Carlos", "senha": "456"}
}

# =================================================================
# BLOCO 2: CONEXÃO COM NOTION
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
# BLOCO 3: ESTILO VISUAL (AZUL ZION)
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
# BLOCO 4: TELA INICIAL (RESTAURADA)
# =================================================================
if st.session_state.pagina == "home":
    st.markdown("<h1 style='text-align: center;'>Zion Rancho App</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Seu controle de estoque inteligente com IA.</p>", unsafe_allow_html=True)
    if os.path.exists("APPRANCHO.png"):
        st.image("APPRANCHO.png", use_container_width=True)
    if st.button("INICIAR ACESSO"):
        st.session_state.pagina = "login"
        st.rerun()

# =================================================================
# BLOCO 5: LOGIN E SUBTELA
# =================================================================
elif st.session_state.pagina == "login":
    st.title("🔐 Acesso Restrito")
    navio_sel = st.selectbox("Selecione a Embarcação", [""] + list(USUARIOS.keys()))
    senha_digitada = st.text_input("Senha", type="password")
    
    if st.button("ENTRAR"):
        if navio_sel in USUARIOS and USUARIOS[navio_sel]["senha"] == senha_digitada:
            st.session_state.cozinheiro = USUARIOS[navio_sel]["nome"]
            st.session_state.navio = navio_sel
            st.success(f"✅ Bem-vindo, {st.session_state.cozinheiro}!")
            st.session_state.pagina = "menu"
            st.rerun()
        else:
            st.error("❌ Credenciais incorretas.")

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
    if st.button("SAIR"):
        st.session_state.pagina = "home"
        st.rerun()

# =================================================================
# BLOCO 6: TELA DE LISTA (O PULO DO GATO ESTÁ AQUI)
# =================================================================
elif st.session_state.pagina == "lista":
    st.title(f"📋 Rancho - {st.session_state.navio}")
    st.write(f"**Responsável Logado:** {st.session_state.cozinheiro}")

    if st.button("🔄 ATUALIZAR DADOS DO NOTION"):
        st.session_state.df_lista = carregar_dados_do_notion()
        st.rerun()

    # TRAVA: Apenas 'CONFIRMA' editável
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
            # FUNÇÃO DE NORMALIZAÇÃO BLINDADA
            def limpar(texto):
                # Remove acentos e caracteres que o FPDF não gosta
                nfkd_form = unicodedata.normalize('NFKD', str(texto))
                return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            
            # Título sem acentos para evitar erro
            pdf.cell(0, 10, limpar(f"Checklist de Rancho - Responsavel: {st.session_state.cozinheiro}"), ln=True, align="C")
            
            pdf.set_font("Arial", "B", 8)
            pdf.set_fill_color(200, 200, 200)
            larguras = [15, 85, 30, 20, 25, 25]
            titulos = ["ITEM", "DESCRICAO", "TIPO", "UNID", "PREDEF", "CONF"]
            
            for i, t in enumerate(titulos):
                pdf.cell(larguras[i], 10, t, 1, 0, "C", True)
            pdf.ln()

            pdf.set_font("Arial", "", 8)
            for _, row in df_editado.iterrows():
                pdf.cell(larguras[0], 8, limpar(row["ITEM"]), 1)
                pdf.cell(larguras[1], 8, limpar(row["DESCRIÇÃO"]), 1)
                pdf.cell(larguras[2], 8, limpar(row["TIPO"]), 1)
                pdf.cell(larguras[3], 8, limpar(row["UNID MED"]), 1)
                pdf.cell(larguras[4], 8, str(row["PREDEFINIDO"]), 1)
                pdf.cell(larguras[5], 8, str(row["CONFIRMA"]), 1)
                pdf.ln()

            # O PULO DO GATO: encode com 'ignore' mata o erro de vez
            try:
                pdf_output = pdf.output(dest='S').encode('latin-1', 'ignore')
                st.download_button("📥 BAIXAR PDF", data=pdf_output, file_name=f"Rancho_{st.session_state.navio}.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"Erro técnico ao converter PDF: {e}")

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
