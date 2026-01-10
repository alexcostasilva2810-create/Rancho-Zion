import streamlit as st
import pandas as pd
import requests
import os
from fpdf import FPDF

# =================================================================
# BLOCO 1: CONFIGURAÇÕES DE ESTADO, SEGURANÇA E TABELA PADRÃO
# =================================================================
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state:
    st.session_state.cozinheiro = ""
if 'navio' not in st.session_state:
    st.session_state.navio = ""

# Estrutura baseada na sua nova alimentação do Notion
COLUNAS_PADRAO = ["ITEM", "DESCRIÇÃO", "TIPO", "UNID MED", "PREDEFINIDO", "CONFIRMA"]

if 'df_lista' not in st.session_state:
    st.session_state.df_lista = pd.DataFrame(columns=COLUNAS_PADRAO)

# Credenciais de acesso
USUARIOS = {
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "NAVIO 03": {"nome": "Carlos", "senha": "456"}
}

# =================================================================
# BLOCO 2: FUNÇÃO DE INTEGRAÇÃO COM NOTION (CONEXÃO REAL)
# =================================================================
def carregar_dados_do_notion():
    """Busca os dados reais inseridos no Notion"""
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
                # Mapeamento para as colunas exatas da sua imagem
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
# BLOCO 3: ESTILIZAÇÃO VISUAL (AZUL ZION)
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
        border: 2px solid #000000 !important;
        width: 100%;
        height: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# BLOCO 4: TELA INICIAL (LOGO E BOAS-VINDAS)
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
# BLOCO 5: LOGIN E SUBTELA (MENU PRINCIPAL)
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
    st.write(f"Unidade: **{st.session_state.navio}**")
    
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
# BLOCO 6: TELA DE LISTA (TRAVADA PARA EDIÇÃO)
# =================================================================
elif st.session_state.pagina == "lista":
    st.title(f"📋 Rancho - {st.session_state.navio}")
    st.write(f"**Responsável Logado:** {st.session_state.cozinheiro}")

    if st.button("🔄 ATUALIZAR DADOS DO NOTION"):
        st.session_state.df_lista = carregar_dados_do_notion()
        st.rerun()

    # TRAVA: Apenas 'CONFIRMA' pode ser editado
    df_editado = st.data_editor(
        st.session_state.df_lista,
        column_config={
            "ITEM": st.column_config.TextColumn("ITEM", disabled=True),
            "DESCRIÇÃO": st.column_config.TextColumn("DESCRIÇÃO", disabled=True),
            "TIPO": st.column_config.TextColumn("TIPO", disabled=True),
            "UNID MED": st.column_config.TextColumn("UNID.", disabled=True),
            "PREDEFINIDO": st.column_config.NumberColumn("ESTOQUE", disabled=True),
            "CONFIRMA": st.column_config.NumberColumn("CONFIRMA (Sua Qtd)", min_value=0),
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
            # Nome dinâmico no PDF
            pdf.cell(0, 10, f"Checklist de Rancho - Responsável: {st.session_state.cozinheiro}", ln=True, align="C")
            
            pdf.set_font("Arial", "B", 8)
            pdf.set_fill_color(200, 200, 200)
            larguras = [15, 85, 30, 20, 25, 25]
            for i, titulo in enumerate(COLUNAS_PADRAO):
                pdf.cell(larguras[i], 10, titulo, 1, 0, "C", True)
            pdf.ln()

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
# BLOCO 7: TELA DE TRIPULAÇÃO
# =================================================================
elif st.session_state.pagina == "tripulacao":
    st.title("👨‍✈️ Preencher Dados da Tripulação")
    st.info("Formulário de tripulação disponível para preenchimento.")
    
    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"
        st.rerun()
