import streamlit as st
import pandas as pd
import requests

# --- CONFIGURAÇÃO DE SEGURANÇA ---
try:
    # Busca as informações que você acabou de salvar nos Secrets
    TOKEN = st.secrets["NOTION_TOKEN"]
    ID_ESTOQUE = st.secrets["DATABASE_ID"]
    ID_HISTORICO = st.secrets["ID_HISTORICO"]
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
except Exception:
    st.error("🚨 Verifique se salvou o NOTION_TOKEN nos Secrets conforme a imagem.")
    st.stop()

# --- CONTROLE DE PÁGINAS ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "login"

# --- BLOCO MENU PRINCIPAL ---
if st.session_state.pagina == "menu":
    st.title(f"🚢 Painel - {st.session_state.navio}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 TABELA DE RANCHO", use_container_width=True):
            st.session_state.pagina = "conferencia"; st.rerun()
        
        # Botão para o Histórico
        if st.button("📜 VER HISTÓRICO", use_container_width=True):
            st.session_state.pagina = "historico"; st.rerun()
    with col2:
        if st.button("👨‍🍳 DECLARAÇÃO", use_container_width=True):
            st.session_state.pagina = "declaracao"; st.rerun()

# --- BLOCO HISTÓRICO (ESTÁVEL) ---
elif st.session_state.pagina == "historico":
    st.header("📜 Histórico de Pedidos")
    
    try:
        url = f"https://api.notion.com/v1/databases/{ID_HISTORICO}/query"
        # Filtro por navio
        payload = {"filter": {"property": "Navio", "rich_text": {"equals": st.session_state.navio}}}
        
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            results = res.json().get("results", [])
            dados = []
            for r in results:
                p = r["properties"]
                dados.append({
                    "Cozinheiro": p["Cozinheiro"]["title"][0]["text"]["content"] if p["Cozinheiro"]["title"] else "N/A",
                    "Data": p["Data Pedido"]["date"]["start"] if p["Data Pedido"]["date"] else "-",
                    "Navio": p["Navio"]["rich_text"][0]["text"]["content"] if p["Navio"]["rich_text"] else "N/A"
                })
            st.dataframe(pd.DataFrame(dados), use_container_width=True, hide_index=True)
        else:
            st.warning("Aguardando registros...")
    except Exception as e:
        st.error(f"Erro ao carregar: {e}")

    if st.button("⬅️ VOLTAR"):
        st.session_state.pagina = "menu"; st.rerun()
