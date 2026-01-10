import streamlit as st
import requests
import pandas as pd
from io import BytesIO

# --- CONFIGURAÇÕES ---
# O Streamlit lê as chaves que você colocou nos 'Secrets'
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
DATABASE_ID = st.secrets["DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

# --- FUNÇÕES AUXILIARES DE LEITURA DO NOTION ---
def get_text(p_dict, prop_name):
    prop = p_dict.get(prop_name, {})
    if prop.get("title") and prop["title"]:
        return prop["title"][0]["text"]["content"]
    if prop.get("rich_text") and prop["rich_text"]:
        return prop["rich_text"][0]["text"]["content"]
    return ""

def get_num(p_dict, prop_name):
    return p_dict.get(prop_name, {}).get("number", 0)

# --- FUNÇÃO PRINCIPAL DE BUSCA DE DADOS ---
@st.cache_data(ttl=600) # Cache para não consultar o Notion toda hora
def buscar_dados():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status() # Lança um erro para status 4xx/5xx
        data = response.json()
        
        itens = []
        for row in data.get("results", []):
            p = row["properties"]
            itens.append({
                "CÓDIGO": get_text(p, "CÓDIGO"),
                "PROTEÍNA": get_text(p, "PROTEÍNA"),
                "TIPO": p.get("TIPO", {}).get("select", {}).get("name", ""),
                "UNIDADE DE MEDIDA": get_text(p, "UNIDADE DE MEDIDA"),
                "ESTOQUE": get_num(p, "ESTOQUE")
            })
        return pd.DataFrame(itens)
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão com o Notion: {e}. Verifique sua conexão e as credenciais.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao processar dados do Notion: {e}. Verifique os nomes das colunas.")
        return pd.DataFrame()

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Zion Rancho App", layout="centered", initial_sidebar_state="collapsed")

# Estilo CSS para a tela azul royal
st.markdown("""
<style>
.stApp {
    background-color: #4169E1; /* Azul Royal */
    text-align: center;
    padding-top: 50px;
}
.title-container {
    color: white;
    font-size: 3em;
    margin-bottom: 20px;
}
.slogan {
    color: white;
    font-size: 1.2em;
    margin-bottom: 40px;
}
.stButton>button {
    background-color: #364F6B; /* Azul mais escuro para o botão */
    color: white;
    padding: 10px 20px;
    border-radius: 8px;
    border: none;
    font-size: 1.1em;
    cursor: pointer;
}
.stButton>button:hover {
    background-color: #2F4050; /* Um pouco mais escuro no hover */
}
</style>
""", unsafe_allow_html=True)

# Lógica de controle de página (Home ou App)
if 'page' not in st.session_state:
    st.session_state.page = 'home'

if st.session_state.page == 'home':
    # Tela inicial
    st.markdown('<div class="title-container">Bem-vindo ao Zion Rancho App!</div>', unsafe_allow_html=True)
    st.markdown('<div class="slogan">Seu controle de estoque inteligente com IA.</div>', unsafe_allow_html=True)
    
    # Imagem do robô humanizado
    # CERTIFIQUE-SE QUE ESTE É O NOME EXATO DO ARQUIVO DE IMAGEM
    st.image("NOME_DA_SUA_IMAGEM.png", width=300) 
    
    if st.button("Iniciar Aplicativo"):
        st.session_state.page = 'app'
        st.rerun()

elif st.session_state.page == 'app':
    # Tela principal do aplicativo (onde estava antes)
    st.title("🛒 Estoque Zion Rancho")

    with st.spinner("Carregando dados do Notion..."):
        df = buscar_dados()

    if not df.empty:
        st.write("### Itens no Sistema")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Nenhum dado encontrado ou erro de conexão. Verifique suas credenciais e os nomes das colunas no Notion.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Atualizar Lista"):
            st.rerun()
    with col2:
        if st.button("⬅️ Voltar para o Início"):
            st.session_state.page = 'home'
            st.rerun()
