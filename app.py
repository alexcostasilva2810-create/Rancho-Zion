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
# BLOCO 1: CONFIGURAÇÕES INICIAIS
# =================================================================
st.set_page_config(page_title="Zion Rancho App", layout="wide")

# Definição das colunas ANTES de qualquer uso (Evita o erro da imagem c56e2c.png)
COLUNAS_PADRAO = ["ITEM", "DESCRIÇÃO", "TIPO", "UNID MED", "PREDEFINIDO", "CONFIRMA"]

if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state:
    st.session_state.cozinheiro = ""
if 'navio' not in st.session_state:
    st.session_state.navio = ""
if 'pdf_disponivel' not in st.session_state:
    st.session_state.pdf_disponivel = None
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
# BLOCO 3: ESTILO PADRÃO (AZUL) PARA AS OUTRAS TELAS
# =================================================================
def aplicar_estilo_azul():
    st.markdown("""
        <style>
        .stApp { background-color: #4169E1 !important; background-image: none !important; }
        h1, h2, h3, p, label { color: white !important; }
        div.stButton > button { background-color: #FF8C00 !important; color: black !important; font-weight: 900 !important; border-radius: 10px !important; }
        </style>
        """, unsafe_allow_html=True)

# =================================================================
# BLOCO 4: NAVEGAÇÃO E TELAS
# =================================================================

if st.session_state.pagina == "home":
    aplicar_estilo_azul()
    st.markdown("<h1 style='text-align: center;'>Zion Tecnologia</h1>", unsafe_allow_html=True)
    if os.path.exists("ZION.jpg"): st.image("ZION.jpg", use_container_width=True)
    if st.button("🚀 ACESSAR SISTEMA"):
        st.session_state.pagina = "login"
        st.rerun()

elif st.session_state.pagina == "login":
    aplicar_estilo_azul()
    st.title("🔐 Login")
    navio_sel = st.selectbox("Navio", list(USUARIOS.keys()))
    senha_dig = st.text_input("Senha", type="password")
    if st.button("ENTRAR"):
        dados = USUARIOS.get(navio_sel)
        if dados and senha_dig == dados["senha"]:
            st.session_state.cozinheiro = dados["nome"]; st.session_state.navio = navio_sel
            st.session_state.pagina = "menu"; st.rerun()
        else: st.error("❌ Senha incorreta!")

elif st.session_state.pagina == "menu":
    aplicar_estilo_azul()
    st.title(f"🚢 Painel - {st.session_state.navio}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 TABELA DE RANCHO"): st.session_state.pagina = "lista"; st.rerun()
    with col2:
        if st.button("👨‍✈️ DECLARAÇÃO"): st.session_state.pagina = "tripulacao"; st.rerun()
    if st.button("⬅️ SAIR"): st.session_state.pagina = "home"; st.rerun()

# --- BLOCO 6: TELA DE LISTA (COM FUNDO DE ESTOQUE E DOWNLOAD AUTOMÁTICO) ---
elif st.session_state.pagina == "lista":
    # CSS Exclusivo para esta tela: Fundo de estoque e botões nítidos
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                        url("https://images.unsplash.com/photo-1583258292688-d0213dc5a3a8?q=80&w=1920");
            background-size: cover;
            background-position: center;
        }
        /* Torna os botões nítidos e sem fundo branco genérico */
        div.stButton > button {
            background-color: #FF8C00 !important;
            color: white !important;
            border: 2px solid #FF8C00 !important;
            font-weight: bold !important;
            text-shadow: 1px 1px 2px black;
        }
        /* Estilo da Tabela para não sumir no fundo */
        .stDataFrame {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid #FF8C00;
        }
        h1, h2, h3, p, label { color: white !important; text-shadow: 2px 2px 4px black; }
        </style>
        """, unsafe_allow_html=True)
    
    st.title("📋 Conferência de Estoque")
    
    if st.button("🔄 ATUALIZAR DADOS DO NOTION"):
        with st.spinner("Sincronizando..."):
            st.session_state.df_lista = carregar_dados_do_notion()
            st.rerun()

    # Editor de dados
    df_editado = st.data_editor(
        st.session_state.df_lista,
        column_config={
            "ITEM": st.column_config.NumberColumn("CÓD.", disabled=True),
            "CONFIRMA": st.column_config.NumberColumn("SUA QTD", min_value=0),
        },
        hide_index=True, 
        use_container_width=True, 
        key="editor_estoque_final"
    )

    st.markdown("---")
    c1, c2 = st.columns(2)
    
    with c1:
        # Gerar o PDF internamente primeiro
        try:
            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, f"Checklist de Rancho - {st.session_state.navio}", ln=True, align="C")
            pdf.ln(5)
            
            # Cabeçalho da Tabela no PDF
            pdf.set_font("Arial", "B", 9)
            pdf.set_fill_color(220, 220, 220)
            larguras = [15, 70, 30, 25, 30, 80, 25]
            titulos = ["CÓD", "ITEM", "TIPO", "UNID", "PREDEF", "DESCRIÇÃO", "CONF."]
            for i, t in enumerate(titulos):
                pdf.cell(larguras[i], 10, t, 1, 0, "C", True)
            pdf.ln()

            # Conteúdo
            pdf.set_font("Arial", "", 8)
            for _, row in df_editado.iterrows():
                pdf.cell(larguras[0], 8, str(row.get("ITEM", "")), 1, 0, "C")
                pdf.cell(larguras[1], 8, str(row.get("ITEM", "")), 1)
                pdf.cell(larguras[2], 8, str(row.get("TIPO", "")), 1)
                pdf.cell(larguras[3], 8, str(row.get("UNID MED", "")), 1, 0, "C")
                pdf.cell(larguras[4], 8, str(row.get("PREDEFINIDO", "0")), 1, 0, "C")
                pdf.cell(larguras[5], 8, str(row.get("DESCRIÇÃO", "")), 1)
                pdf.cell(larguras[6], 8, str(row.get("CONFIRMA", "0")), 1, 1, "C")

            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            
            # BOTÃO DE DOWNLOAD (Única forma do navegador disparar o arquivo)
            st.download_button(
                label="📥 BAIXAR PDF AGORA",
                data=pdf_bytes,
                file_name=f"Rancho_{st.session_state.navio}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Erro ao preparar PDF: {e}")

    with c2:
        if st.button("⬅️ VOLTAR AO MENU"):
            st.session_state.pagina = "menu"
            st.rerun()
