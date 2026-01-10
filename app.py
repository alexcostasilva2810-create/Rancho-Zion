import streamlit as st
import requests
import pandas as pd

# --- CONFIGURAÇÕES ---
# O Streamlit vai ler as chaves que você colocou nos 'Secrets'
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
DATABASE_ID = st.secrets["DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def buscar_dados():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    try:
        response = requests.post(url, headers=headers)
        data = response.json()
        
        itens = []
        for row in data.get("results", []):
            p = row["properties"]
            
            # Função auxiliar para ler texto de forma segura
            def get_text(prop_name):
                prop = p.get(prop_name, {})
                # Tenta ler como título ou como texto rico
                if prop.get("title"):
                    return prop["title"][0]["text"]["content"]
                if prop.get("rich_text"):
                    return prop["rich_text"][0]["text"]["content"]
                return ""

            # Função auxiliar para ler números
            def get_num(prop_name):
                return p.get(prop_name, {}).get("number", 0)

            itens.append({
                "CÓDIGO": get_text("CÓDIGO"),
                "PROTEÍNA": get_text("PROTEÍNA"),
                "UNIDADE": get_text("UNIDADE DE MEDIDA"),
                "ESTOQUE": get_num("ESTOQUE")
            })
        return pd.DataFrame(itens)
    except Exception as e:
        st.error(f"Erro técnico: {e}")
        return pd.DataFrame()

# --- INTERFACE ---
st.set_page_config(page_title="Zion Rancho", layout="wide")
st.title("🛒 Estoque Zion Rancho")

with st.spinner("Carregando dados do Notion..."):
    df = buscar_dados()

if not df.empty:
    # Mostra a tabela organizada
    st.write("### Itens no Sistema")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("Nenhum dado encontrado. Verifique se os nomes das colunas no Notion são: CÓDIGO, PROTEÍNA, UNIDADE DE MEDIDA e ESTOQUE.")

if st.button("🔄 Atualizar"):
    st.rerun()
