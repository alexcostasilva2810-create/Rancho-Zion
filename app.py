import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime, timedelta
import unicodedata
from fpdf import FPDF
from PIL import Image
import os
import requests

# =================================================================
# BLOCO 1: CONFIGURAÇÕES INICIAIS
# =================================================================
st.set_page_config(page_title="Zion Rancho App", layout="wide")

COLUNAS_PADRAO = ["ITEM", "DESCRIÇÃO", "TIPO", "UNID MED", "PREDEFINIDO", "CONFIRMA"]

# IDs E TOKEN FIXOS (Segurança contra tela branca)
NOTION_TOKEN = "ntn_jZ6353375938j9kJFqKWjD0N4ONt1rwP515tsIMwxtucHa"
DATABASE_ID = "2e3025de7b79803abe0efde74f87a2e1" 
ID_HISTORICO_NOTION = "2e5025de7b79803187a4d8b865179440"

if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state:
    st.session_state.cozinheiro = ""
if 'navio' not in st.session_state:
    st.session_state.navio = ""
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

def aplicar_estilo_azul():
    st.markdown("<style>.stApp { background-color: #4169E1 !important; } h1,h2,h3,p,label { color: white !important; } div.stButton > button { background-color: #FF8C00 !important; color: black !important; font-weight: 900; border-radius: 10px; }</style>", unsafe_allow_html=True)

# =================================================================
# BLOCO 4: NAVEGAÇÃO
# =================================================================

if st.session_state.pagina == "home":
    aplicar_estilo_azul()
    st.markdown("<h1 style='text-align: center;'>Zion Tecnologia</h1>", unsafe_allow_html=True)
    if os.path.exists("ZION.jpg"): st.image("ZION.jpg", use_container_width=True)
    if st.button("🚀 ACESSAR SISTEMA"):
        st.session_state.pagina = "login"; st.rerun()

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
        if st.button("📋 TABELA DE RANCHO", use_container_width=True): st.session_state.pagina = "lista"; st.rerun()
        if st.button("📜 VER HISTÓRICO", use_container_width=True): st.session_state.pagina = "historico"; st.rerun()
    with col2:
        if st.button("👨‍✈️ DECLARAÇÃO", use_container_width=True): st.session_state.pagina = "tripulacao"; st.rerun()
    if st.button("⬅️ SAIR"): st.session_state.pagina = "home"; st.rerun()

# --- BLOCO 6: TELA DE LISTA COM PDF RESTAURADO ---
elif st.session_state.pagina == "lista":
    st.markdown("<style>.stApp { background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url('https://images.unsplash.com/photo-1583258292688-d0213dc5a3a8?q=80&w=1920'); background-size: cover; }</style>", unsafe_allow_html=True)
    st.title("📋 Conferência de Estoque")
    
    if st.button("🔄 ATUALIZAR DADOS DO NOTION"):
        st.session_state.df_lista = carregar_dados_do_notion()
        st.rerun()

    df_editado = st.data_editor(st.session_state.df_lista, column_config={"ITEM": st.column_config.NumberColumn("CÓD.", disabled=True), "CONFIRMA": st.column_config.NumberColumn("SUA QTD", min_value=0)}, hide_index=True, use_container_width=True, key="editor_estoque_v3")

    st.markdown("---")
    col_pdf, col_voltar = st.columns(2)
    
    with col_pdf:
        def preparar_celula(conteudo):
            return unicodedata.normalize('NFKD', str(conteudo)).encode('latin-1', 'ignore').decode('latin-1')

        try:
            class PDF(FPDF):
                def footer(self):
                    self.set_y(-15); self.set_font('Arial', 'I', 8)
                    agora = datetime.now() - timedelta(hours=3)
                    self.cell(0, 10, f'Gerado em: {agora.strftime("%d/%m/%Y %H:%M:%S")} - Pagina ' + str(self.page_no()), 0, 0, 'C')

            pdf = PDF(orientation='P', unit='mm', format='A4')
            pdf.add_page()
            if os.path.exists("ZION.jpg"): pdf.image("ZION.jpg", 95, 8, 20)
            pdf.set_font("Arial", "B", 14); pdf.set_y(30)
            pdf.cell(0, 10, preparar_celula(f"Checklist de Rancho: {st.session_state.navio}"), ln=True, align="C")
            pdf.set_font("Arial", "", 11); pdf.cell(0, 8, preparar_celula(f"Responsavel: {st.session_state.cozinheiro}"), ln=True, align="C")
            pdf.ln(5)
            
            pdf.set_font("Arial", "B", 8); pdf.set_fill_color(220, 220, 220)
            larguras = [10, 80, 25, 15, 20, 15]
            titulos = ["COD", "ITEM / DESCRICAO", "TIPO", "UNID", "PREDEF", "CONF."]
            for i, t in enumerate(titulos): pdf.cell(larguras[i], 10, t, 1, 0, "C", True)
            pdf.ln()
            pdf.set_font("Arial", "", 7)
            for _, row in df_editado.iterrows():
                pdf.cell(larguras[0], 8, preparar_celula(row["ITEM"]), 1, 0, "C")
                pdf.cell(larguras[1], 8, preparar_celula(f"{row['ITEM']} - {row['DESCRIÇÃO']}"), 1)
                pdf.cell(larguras[2], 8, preparar_celula(row["TIPO"]), 1)
                pdf.cell(larguras[3], 8, preparar_celula(row["UNID MED"]), 1, 0, "C")
                pdf.cell(larguras[4], 8, preparar_celula(row["PREDEFINIDO"]), 1, 0, "C")
                pdf.cell(larguras[5], 8, preparar_celula(row["CONFIRMA"]), 1, 1, "C")

            st.download_button(label="📥 BAIXAR PDF DO ESTOQUE", data=pdf.output(dest='S').encode('latin-1'), file_name=f"Rancho_{st.session_state.navio}.pdf", mime="application/pdf", use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao preparar PDF: {e}")

    with col_voltar:
        if st.button("⬅️ VOLTAR AO MENU", use_container_width=True): st.session_state.pagina = "menu"; st.rerun()

# --- BLOCO 8: TELA DE HISTÓRICO ---
elif st.session_state.pagina == "historico":
    aplicar_estilo_azul()
    st.title("📜 Histórico de Registros")
    try:
        url_h = f"https://api.notion.com/v1/databases/{ID_HISTORICO_NOTION}/query"
        headers_h = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
        payload = {"filter": {"property": "Navio", "rich_text": {"equals": st.session_state.navio}}}
        res = requests.post(url_h, headers=headers_h, json=payload)
        if res.status_code == 200:
            results = res.json().get("results", [])
            dados_h = [{"Data": r["properties"]["Data Pedido"]["date"]["start"], "Responsável": r["properties"]["Cozinheiro"]["title"][0]["text"]["content"], "Validade": r["properties"]["Validade"]["date"]["start"]} for r in results if r["properties"]["Cozinheiro"]["title"]]
            st.dataframe(pd.DataFrame(dados_h), use_container_width=True, hide_index=True)
        else: st.warning("Sem registros encontrados.")
    except: st.error("Erro ao carregar histórico.")
    if st.button("⬅️ VOLTAR AO MENU"): st.session_state.pagina = "menu"; st.rerun()

# --- BLOCO 7: TELA DE DECLARAÇÃO ---
elif st.session_state.pagina == "tripulacao":
    aplicar_estilo_azul(); st.title("⚓ Declaração de Reabastecimento")
    if st.button("⬅️ VOLTAR AO MENU"): st.session_state.pagina = "menu"; st.rerun()
