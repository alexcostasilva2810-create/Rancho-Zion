import streamlit as st
import requests
import pandas as pd

# --- CONFIGURAÇÕES DE SEGURANÇA ---
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
DATABASE_ID = st.secrets["DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

# --- FUNÇÃO PARA BUSCAR DADOS ---
def buscar_dados():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    try:
        response = requests.post(url, headers=headers)
        data = response.json()
        itens = []
        for row in data.get("results", []):
            p = row["properties"]
            
            # Captura segura dos dados baseada na sua tabela real
            nome_item = ""
            if "PROTEINA" in p and p["PROTEINA"]["rich_text"]:
                nome_item = p["PROTEINA"]["rich_text"][0]["text"]["content"]
            elif "Nome" in p and p["Nome"]["title"]:
                nome_item = p["Nome"]["title"][0]["text"]["content"]

            itens.append({
                "CÓDIGO": p["CODIGO"]["title"][0]["text"]["content"] if "CODIGO" in p and p["CODIGO"]["title"] else "N/A",
                "ITEM": nome_item,
                "ESTOQUE": p["ESTOQUE"]["number"] if "ESTOQUE" in p else 0,
                "UNID MED": p["UNID MED"]["rich_text"][0]["text"]["content"] if "UNID MED" in p and p["UNID MED"]["rich_text"] else ""
            })
        return pd.DataFrame(itens)
    except Exception as e:
        return pd.DataFrame()

# --- INTERFACE VISUAL ---
st.set_page_config(page_title="Zion Rancho", layout="centered")

# Estilo Azul Royal
st.markdown("""
    <style>
    .stApp { background-color: #4169E1; color: white; text-align: center; }
    h1 { color: white !important; }
    .stButton>button { background-color: #ffffff; color: #4169E1; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    # TELA INICIAL
    st.title("Bem-vindo ao Zion Rancho App!")
    st.write("Seu controle de estoque inteligente com IA.")
    
    # USANDO O NOME CORRETO DO SEU ARQUIVO
    st.image("robo_humanizado.jpg", width=400)
    
    if st.button("ACESSAR SISTEMA"):
        st.session_state.logado = True
        st.rerun()
else:
    # TELA DO SISTEMA
    st.title("🛒 Estoque Zion Rancho")
    df = buscar_dados()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.error("Erro ao carregar dados. Verifique a conexão com o Notion.")
        
    if st.button("SAIR"):
        st.session_state.logado = False
        st.rerun()
