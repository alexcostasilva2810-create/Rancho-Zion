import streamlit as st
import pandas as pd
import requests

# --- CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="Zion Rancho", layout="wide")

# --- 1. CONEXÃO SEGURA COM SECRETS ---
try:
    # Busca os dados salvos na aba Secrets
    TOKEN = st.secrets["NOTION_TOKEN"]
    ID_ESTOQUE = st.secrets["DATABASE_ID"]
    ID_HIST_NOTION = st.secrets["ID_HISTORICO"] # ID da tabela 2e5025de...
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
except Exception as e:
    st.error(f"🚨 Erro nos Secrets: {e}. Verifique a aba de configurações.")
    st.stop()

# --- 2. INICIALIZAÇÃO DE VARIÁVEIS ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "login"
if 'navio' not in st.session_state:
    st.session_state.navio = "NÃO SELECIONADO"
if 'cozinheiro' not in st.session_state:
    st.session_state.cozinheiro = "Usuário"

# --- 3. LOGICA DE NAVEGAÇÃO ---

# TELA DE LOGIN
if st.session_state.pagina == "login":
    st.title("🚢 Zion Rancho - Login")
    user = st.text_input("Nome do Cozinheiro")
    navio_sel = st.selectbox("Selecione a Embarcação", ["AROEIRA", "IMERYS", "PAMA"])
    
    if st.button("ACESSAR PAINEL"):
        if user:
            st.session_state.cozinheiro = user
            st.session_state.navio = navio_sel
            st.session_state.pagina = "menu"
            st.rerun()
        else:
            st.warning("Por favor, digite seu nome.")

# TELA DO MENU PRINCIPAL (PAINEL)
elif st.session_state.pagina == "menu":
    st.markdown(f"# 🚢 Painel - {st.session_state.navio}")
    st.write(f"Bem-vindo, **{st.session_state.cozinheiro}**")
    
    col1, col2 = st.columns(2)
    with col1:
        # Botão que leva à lista de rancho
        if st.button("📋 TABELA DE RANCHO", use_container_width=True):
            st.session_state.pagina = "conferencia"
            st.rerun()
        
        # Novo botão para o Histórico
        if st.button("📜 VER HISTÓRICO", use_container_width=True):
            st.session_state.pagina = "historico"
            st.rerun()
            
    with col2:
        if st.button("👨‍🍳 DECLARAÇÃO", use_container_width=True):
            st.session_state.pagina = "declaracao"
            st.rerun()

    st.divider()
    if st.button("⬅️ SAIR"):
        st.session_state.pagina = "login"
        st.rerun()

# TELA DE HISTÓRICO (BLOQUEIA TELA BRANCA)
elif st.session_state.pagina == "historico":
    st.title("📜 Histórico de Pedidos")
    st.info(f"Filtrando por: {st.session_state.navio}")
    
    try:
        url = f"https://api.notion.com/v1/databases/{ID_HIST_NOTION}/query"
        # Filtro por navio conforme a tabela
        payload = {
            "filter": {"property": "Navio", "rich_text": {"equals": st.session_state.navio}},
            "sorts": [{"property": "Data Pedido", "direction": "descending"}]
        }
        
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if res.status_code == 200:
            results = res.json().get("results", [])
            if results:
                dados = []
                for r in results:
                    p = r["properties"]
                    dados.append({
                        "Data": p["Data Pedido"]["date"]["start"] if p["Data Pedido"]["date"] else "-",
                        "Cozinheiro": p["Cozinheiro"]["title"][0]["text"]["content"] if p["Cozinheiro"]["title"] else "N/A",
                        "Validade": p["Validade"]["date"]["start"] if p["Validade"]["date"] else "-",
                        "Escolta": p["Escolta"]["select"]["name"] if p["Escolta"]["select"] else "NÃO"
                    })
                st.dataframe(pd.DataFrame(dados), use_container_width=True, hide_index=True)
            else:
                st.write("ℹ️ Nenhum registro encontrado para este navio.")
        else:
            st.error(f"Erro na API do Notion: {res.status_code}")
            
    except Exception as e:
        st.error("Sincronizando com o banco de dados... Por favor, aguarde.")

    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"
        st.rerun()

# TELA DE CONFERÊNCIA (EXEMPLO)
elif st.session_state.pagina == "conferencia":
    st.title(f"📋 Lista de Rancho: {st.session_state.navio}")
    st.write("Carregando itens do estoque...")
    if st.button("⬅️ VOLTAR"):
        st.session_state.pagina = "menu"; st.rerun()
