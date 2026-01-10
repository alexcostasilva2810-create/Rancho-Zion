import streamlit as st
import requests
import pandas as pd

# --- CONFIGURAÇÕES ---
# 1. Cole aqui o seu Token que começa com ntn_
NOTION_TOKEN = "ntn_jZ6353375938j9kJFqKWjD0N4ONt1rwP515tsIMwxtucHa"

# 2. O ID que pegamos da sua URL
DATABASE_ID = "2e3025de7b79803abe0efde74f87a2e1"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def buscar_dados():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        itens = []
        for row in data["results"]:
            p = row["properties"]
            # Aqui pegamos as colunas exatamente como estão na sua foto
            itens.append({
                "CÓDIGO": p["CÓDIGO"]["title"][0]["text"]["content"] if p["CÓDIGO"]["title"] else "",
                "PROTEÍNA": p["PROTEÍNA"]["rich_text"][0]["text"]["content"] if p["PROTEÍNA"]["rich_text"] else "",
                "TIPO": p["TIPO"]["select"]["name"] if p["TIPO"]["select"] else "",
                "ESTOQUE": p["ESTOQUE"]["number"] if p["ESTOQUE"]["number"] else 0
            })
        return pd.DataFrame(itens)
    return pd.DataFrame()

st.set_page_config(page_title="Zion Rancho", layout="wide")
st.title("🛒 Estoque Zion Rancho")

df = buscar_dados()

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.error("Erro ao carregar dados. Verifique se o Token está correto e se você 'Conectou' a integração na página do Notion.")

if st.button("Atualizar Lista"):
    st.rerun()
