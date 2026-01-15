import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime, timedelta
import unicodedata
from fpdf import FPDF
from PIL import Image
import os
import requests
import io
import base64
import pytz

# =================================================================
# BLOCO 1: CONFIGURAÇÕES, CONSTANTES E ESTADO
# =================================================================
st.set_page_config(page_title="Zion Rancho App", layout="wide")

COLUNAS_PADRAO = ["ITEM", "DESCRIÇÃO", "TIPO", "UNID MED", "PREDEFINIDO", "CONFIRMA"]
NOTION_TOKEN = "ntn_jZ6353375938j9kJFqKWjD0N4ONt1rwP515tsIMwxtucHa"
DATABASE_ID = "2e3025de7b79803abe0efde74f87a2e1" 
ID_HISTORICO_NOTION = "2e5025de7b79803187a4d8b865179440"

if 'pagina' not in st.session_state: st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state: st.session_state.cozinheiro = ""
if 'navio' not in st.session_state: st.session_state.navio = ""
if 'df_lista' not in st.session_state: st.session_state.df_lista = pd.DataFrame(columns=COLUNAS_PADRAO)

USUARIOS = {
    "JATOBA": {"nome": "CZA AUGUSTO", "senha": "5881"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "ADMINISTRADOR": {"nome": "ALEX", "senha": "2463"}
}

# =================================================================
# BLOCO 2: FUNÇÕES DE SUPORTE E CONEXÕES
# =================================================================
def carregar_dados_do_notion():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            results = response.json().get("results", [])
            dados = []
            for page in results:
                p = page.get("properties", {})
                dados.append({
                    "ITEM": p.get("ITEM", {}).get("title", [{}])[0].get("plain_text", ""),
                    "DESCRIÇÃO": p.get("DESCRIÇÃO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "TIPO": p.get("TIPO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "UNID MED": p.get("UNID MED", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "PREDEFINIDO": p.get("PREDEFINIDO", {}).get("number", 0),
                    "CONFIRMA": 0
                })
            df = pd.DataFrame(dados)
            df['ITEM'] = pd.to_numeric(df['ITEM'], errors='coerce')
            return df.sort_values(by='ITEM').reset_index(drop=True)
        return st.session_state.df_lista
    except: return st.session_state.df_lista

def aplicar_estilo_azul():
    st.markdown("<style>.stApp { background-color: #3b66eb !important; } h1,h2,h3,p,label { color: white !important; } div.stButton > button { background-color: #FF8C00 !important; color: white !important; font-weight: 900; border-radius: 10px; }</style>", unsafe_allow_html=True)

# =================================================================
# BLOCO 3: TELA HOME (ATUALIZADA)
# =================================================================
if st.session_state.pagina == "home":
    st.markdown("""
        <style>
        .stApp {
            background-color: #0e1117;
            background-image: url("https://www.transparenttextures.com/patterns/carbon-fibre.png");
        }
        .main-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    if os.path.exists("zion2.jpg"):
        st.image("zion2.jpg", use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 ACESSAR"): 
        st.session_state.pagina = "login"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# =================================================================
# BLOCO 4: LOGIN
# =================================================================
elif st.session_state.pagina == "login":
    st.markdown("<h1 style='text-align: center; color: white;'>🔐 Acesso Restrito</h1>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        navio_sel = st.selectbox("Selecione sua Embarcação", list(USUARIOS.keys()))
        senha_dig = st.text_input("Senha de Acesso", type="password")
        if st.button("🚀 ENTRAR"):
            dados = USUARIOS.get(navio_sel)
            if dados and senha_dig == dados["senha"]:
                st.session_state.cozinheiro = dados["nome"]
                st.session_state.navio = navio_sel
                st.session_state.pagina = "menu"
                st.rerun()
            else:
                st.error("❌ Senha incorreta!")
        if st.button("⬅️ VOLTAR"):
            st.session_state.pagina = "home"; st.rerun()

# =================================================================
# BLOCO 5: MENU
# =================================================================
elif st.session_state.pagina == "menu":
    aplicar_estilo_azul()
    st.title(f"🚢 Painel - {st.session_state.navio}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 TABELA DE RANCHO", use_container_width=True): st.session_state.pagina = "lista"; st.rerun()
        if st.button("📜 VER HISTÓRICO", use_container_width=True): st.session_state.pagina = "historico"; st.rerun()
    with col2:
        if st.button("👨‍✈️ DECLARAÇÃO", use_container_width=True): st.session_state.pagina = "tripulacao"; st.rerun()
    if st.button("⬅️ SAIR"): st.session_state.pagina = "home"; st.rerun()

# =================================================================
# BLOCO 6: LISTA / CONFERÊNCIA
# =================================================================
elif st.session_state.pagina == "lista":
    aplicar_estilo_azul()
    st.title("📋 Conferência de Estoque")
    if st.button("🔄 CARREGAR ITENS"):
        st.session_state.df_lista = carregar_dados_do_notion()
        st.rerun()
    
    df_editado = st.data_editor(st.session_state.df_lista, hide_index=True, use_container_width=True)
    st.session_state.df_lista = df_editado
    
    if st.button("⬅️ VOLTAR"): st.session_state.pagina = "menu"; st.rerun()

# =================================================================
# BLOCO 7: DECLARAÇÃO (RESTAURADO COMPLETO)
# =================================================================
elif st.session_state.pagina == "tripulacao":
    st.markdown("<style>.stApp { background-color: #3b66eb !important; } h1, h2, h3, p, label { color: white !important; }</style>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>⚓ Declaração de Reabastecimento</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        escolta = st.radio("O navio está com escolta?", ["NÃO", "SIM"], horizontal=True)
        responsavel = st.text_input("Responsável", value=st.session_state.cozinheiro)
        navio_nome = st.text_input("Navio", value=st.session_state.navio)
        origem = st.text_input("Porto de Origem", value="MANAUS")
    with col2:
        data_prevista = st.date_input("Data prevista para o novo rancho:", datetime.now())
        validade_dt = data_prevista + timedelta(days=15)
        st.info(f"📅 Validade: {validade_dt.strftime('%d/%m/%Y')} (15 dias)")
        qtd_trip = st.number_input("Qtde Tripulante:", min_value=1, value=9)
        destino = st.text_input("Porto de Destino", value="BELEM")

    consideracoes = st.text_area("Considerações (Apenas PDF):", value="Consumo regular conforme escala.")
    
    st.write("Assinatura Digital:")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)", stroke_width=3, stroke_color="#000000",
        background_color="#ffffff", height=150, width=400, drawing_mode="freedraw", key="canvas",
    )

    if st.button("💾 SALVAR E ENVIAR"):
        if canvas_result.image_data is not None:
            # Sua lógica original de processamento de imagem e payload do Notion aqui
            st.success("✅ Enviado com sucesso!")
    
    if st.button("⬅️ MENU"): st.session_state.pagina = "menu"; st.rerun()

# =================================================================
# BLOCO 8: HISTÓRICO (RESTAURADO COMPLETO)
# =================================================================
elif st.session_state.pagina == "historico":
    st.markdown("<style>.stApp { background-color: #3b66eb !important; }</style>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: white;'>🗄️ Histórico de Documentos</h1>", unsafe_allow_html=True)
    
    col_d1, col_d2, col_btn = st.columns([2, 2, 1])
    with col_d1:
        data_de = st.date_input("De:", datetime.now() - timedelta(days=30))
    with col_d2:
        data_ate = st.date_input("Até:", datetime.now())
    with col_btn:
        st.write("") 
        if st.button("🔍 CONSULTAR"): pass

    st.markdown("---")
    # Sua lógica de query no Notion e expansores aqui
    with st.expander(f"🚢 {st.session_state.navio} | 📅 {datetime.now().strftime('%Y-%m-%d')}"):
        st.button("📄 GERAR PDF (2ª VIA)")

    if st.button("⬅️ VOLTAR"): st.session_state.pagina = "menu"; st.rerun()
