import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- 1. CONFIGURAÇÕES TÉCNICAS (IDs DAS TABELAS) ---
# Tabelas que você criou no Notion
ID_RANCHO_ESTOQUE = "8bc3303498114065969562723652697b" 
ID_HISTORICO_NOTION = "2e5025de7b79803187a4d8b865179440"

# PROTEÇÃO DE TOKEN: Tenta ler o token; se falhar, mostra aviso amigável
try:
    NOTION_TOKEN = st.secrets["notion_token"]
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
except Exception:
    st.error("🚨 ERRO DE CONFIGURAÇÃO: O Token do Notion não foi encontrado nos 'Secrets'.")
    st.stop()

# --- 2. CONTROLE DE NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "login"

# --- BLOCO 1: LOGIN (Simplificado para o exemplo) ---
if st.session_state.pagina == "login":
    st.title("🚢 Zion Rancho - Login")
    user = st.text_input("Usuário")
    navio = st.selectbox("Selecione o Navio", ["AROEIRA", "IMERYS", "PAMA"])
    if st.button("ENTRAR"):
        st.session_state.cozinheiro = user
        st.session_state.navio = navio
        st.session_state.pagina = "menu"
        st.rerun()

# --- BLOCO 2: MENU PRINCIPAL ---
elif st.session_state.pagina == "menu":
    st.markdown(f"## 🚢 Painel: {st.session_state.navio}")
    st.info(f"Bem-vindo, {st.session_state.cozinheiro}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 TABELA DE RANCHO", use_container_width=True):
            st.session_state.pagina = "conferencia"
            st.rerun()
        
        # O botão que faltava no seu painel
        if st.button("📜 VER HISTÓRICO", use_container_width=True):
            st.session_state.pagina = "historico"
            st.rerun()

    with col2:
        if st.button("👨‍🍳 DECLARAÇÃO", use_container_width=True):
            st.session_state.pagina = "declaracao"
            st.rerun()
    
    st.divider()
    if st.button("⬅️ SAIR"):
        st.session_state.pagina = "login"; st.rerun()

# --- BLOCO 6: CONFERÊNCIA DE ESTOQUE ---
elif st.session_state.pagina == "conferencia":
    st.title(f"📦 Conferência - {st.session_state.navio}")
    # Aqui entra sua lógica de carregar o estoque do Notion...
    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"; st.rerun()

# --- BLOCO 8: MÓDULO DE HISTÓRICO (O QUE ESTAVA DANDO ERRO) ---
elif st.session_state.pagina == "historico":
    st.markdown("### 📜 Histórico de Pedidos Zion")
    
    try:
        url_hist = f"https://api.notion.com/v1/databases/{ID_HISTORICO_NOTION}/query"
        
        # Filtro: Se for admin vê tudo, se for cozinheiro vê só o seu navio
        if st.session_state.cozinheiro.lower() == "admin":
            query = {"sorts": [{"property": "Data Pedido", "direction": "descending"}]}
        else:
            query = {
                "filter": {"property": "Navio", "rich_text": {"equals": st.session_state.navio}},
                "sorts": [{"property": "Data Pedido", "direction": "descending"}]
            }

        res = requests.post(url_hist, headers=headers, json=query)
        
        if res.status_code == 200:
            results = res.json().get("results", [])
            dados_final = []
            for r in results:
                p = r["properties"]
                dados_final.append({
                    "Data": p["Data Pedido"]["date"]["start"] if p["Data Pedido"]["date"] else "-",
                    "Cozinheiro": p["Cozinheiro"]["title"][0]["text"]["content"] if p["Cozinheiro"]["title"] else "N/A",
                    "Navio": p["Navio"]["rich_text"][0]["text"]["content"] if p["Navio"]["rich_text"] else "N/A",
                    "Validade": p["Validade"]["date"]["start"] if p["Validade"]["date"] else "-"
                })
            
            if dados_final:
                st.dataframe(pd.DataFrame(dados_final), use_container_width=True, hide_index=True)
            else:
                st.warning("Nenhum pedido registrado para este navio.")
        else:
            st.error(f"Erro na API do Notion: {res.status_code}")

    except Exception as e:
        st.error(f"Falha ao carregar histórico: {e}")

    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"; st.rerun()
