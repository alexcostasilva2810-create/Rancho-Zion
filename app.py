import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime
import unicodedata
from fpdf import FPDF
from PIL import Image
import os
import requests

# =================================================================
# BLOCO 1: CONFIGURAÇÕES E ESTADO DA SESSÃO
# =================================================================
st.set_page_config(page_title="Zion Rancho App", layout="wide")

if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state:
    st.session_state.cozinheiro = ""
if 'navio' not in st.session_state:
    st.session_state.navio = ""
if 'pdf_disponivel' not in st.session_state:
    st.session_state.pdf_disponivel = None

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
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    
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
            df = pd.DataFrame(dados_notion)
            df['ITEM'] = pd.to_numeric(df['ITEM'], errors='coerce')
            return df.sort_values(by='ITEM').reset_index(drop=True)
        return st.session_state.df_lista
    except:
        return st.session_state.df_lista

# =================================================================
# BLOCO 3: ESTILO VISUAL
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
# BLOCO 4: LÓGICA DE TELAS
# =================================================================

# --- TELA HOME ---
if st.session_state.pagina == "home":
    st.markdown("<h1 style='text-align: center;'>Aplicativo Zion Rancho</h1>", unsafe_allow_html=True)
    if os.path.exists("ZION.jpg"): st.image("ZION.jpg", use_container_width=True)
    elif os.path.exists("APPRANCHO.png"): st.image("APPRANCHO.png", use_container_width=True)

    if st.button("🚀 INICIAR ACESSO"):
        st.session_state.pagina = "login"
        st.rerun()

# --- TELA LOGIN ---
elif st.session_state.pagina == "login":
    st.title("🔐 Acesso do Cozinheiro")
    navio_sel = st.selectbox("Selecione o seu Navio", list(USUARIOS.keys()))
    senha_dig = st.text_input("Digite a Senha", type="password")
    
    if st.button("🛒 ENTRAR NO MENU"):
        dados = USUARIOS.get(navio_sel)
        if dados and senha_dig == dados["senha"]:
            st.session_state.cozinheiro = dados["nome"]
            st.session_state.navio = navio_sel
            st.session_state.pagina = "menu"
            st.rerun()
        else:
            st.error("❌ Senha incorreta!")

# --- TELA MENU (O SUBMENU QUE FALTAVA) ---
elif st.session_state.pagina == "menu":
    st.title(f"🚢 Painel - {st.session_state.navio}")
    st.write(f"Bem-vindo, **{st.session_state.cozinheiro}**")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 TABELA DE RANCHO (NOTION)"):
            st.session_state.pagina = "lista"
            st.rerun()
    with col2:
        if st.button("👨‍✈️ DECLARAÇÃO / TRIPULAÇÃO"):
            st.session_state.pagina = "tripulacao"
            st.rerun()
    
    st.markdown("---")
    if st.button("⬅️ SAIR"):
        st.session_state.pagina = "home"
        st.rerun()

# --- TELA LISTA (NOTION) ---
elif st.session_state.pagina == "lista":
    st.title(f"📋 Tabela de Rancho - {st.session_state.navio}")
    
    if st.button("🔄 ATUALIZAR DADOS DO NOTION"):
        with st.spinner("Sincronizando..."):
            st.session_state.df_lista = carregar_dados_do_notion()
            st.rerun()

    df_editado = st.data_editor(
        st.session_state.df_lista,
        column_config={
            "ITEM": st.column_config.NumberColumn("CÓD.", disabled=True),
            "CONFIRMA": st.column_config.NumberColumn("SUA QTD", min_value=0),
        },
        hide_index=True, use_container_width=True
    )

    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"
        st.rerun()

# --- TELA TRIPULAÇÃO (DECLARAÇÃO) ---
elif st.session_state.pagina == "tripulacao":
    st.title("👨‍✈️ Declaração de Reabastecimento")
    
    def obter_localizacao_simples():
        try:
            response = requests.get('https://ipapi.co/json/', timeout=3)
            dados = response.json()
            return f"{dados.get('city', 'Cidade')}/{dados.get('region', 'Estado')}"
        except: return "Localização não identificada"

    with st.form("form_tripulacao"):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Responsável", value=st.session_state.cozinheiro, disabled=True)
            st.text_input("Empurrador", value=st.session_state.navio, disabled=True)
            st.text_input("Data do Último Rancho", value=datetime.now().strftime("%d/%m/%Y"))
        with col2:
            st.text_input("Data de Início", value=datetime.now().strftime("%d/%m/%Y"))
            origem = st.text_input("Origem", placeholder="Ex: Belém/PA")
            destino = st.text_input("Destino", placeholder="Ex: Santarém/PA")

        consideracoes = st.text_area("Observações:", height=80)
        canvas_result = st_canvas(stroke_width=3, stroke_color="#000", background_color="#eee", height=110, drawing_mode="freedraw", key="canvas")
        
        btn_gerar = st.form_submit_button("💾 GERAR DOCUMENTO")

    if btn_gerar:
        if not origem or not destino or canvas_result.image_data is None:
            st.error("⚠️ Preencha tudo e assine!")
        else:
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, f"DECLARACAO DE RANCHO - {st.session_state.navio}", 0, 1, "C")
                
                # Assinatura
                img_data = canvas_result.image_data.astype('uint8')
                Image.fromarray(img_data, 'RGBA').save("assinatura_temp.png")
                pdf.image("assinatura_temp.png", x=75, y=150, w=55)
                
                st.session_state.pdf_disponivel = pdf.output(dest='S').encode('latin-1')
                st.success("✅ Gerado!")
            except Exception as e: st.error(f"Erro: {e}")

    if st.session_state.pdf_disponivel:
        st.download_button("📥 BAIXAR PDF", data=st.session_state.pdf_disponivel, file_name="Declaracao.pdf", mime="application/pdf")

    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"
        st.rerun()
