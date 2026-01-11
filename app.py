import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- 1. CONFIGURAÇÕES DE CONEXÃO (IDs DAS TABELAS) ---
# ID da Tabela onde ficam os ITENS DE ESTOQUE (Rancho)
ID_RANCHO_ESTOQUE = "8bc3303498114065969562723652697b" 

# ID da sua nova Tabela de HISTÓRICO DE PEDIDOS
ID_HISTORICO_NOTION = "2e5025de7b79803187a4d8b865179440"

# Token de Integração do Notion
headers = {
    "Authorization": "Bearer " + st.secrets["notion_token"],
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# --- 2. INICIALIZAÇÃO DO SISTEMA ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "login"

# --- BLOCO 1: TELA DE LOGIN ---
if st.session_state.pagina == "login":
    st.markdown("<h1 style='text-align: center; color: white;'>🚢 Zion Rancho - Login</h1>", unsafe_allow_html=True)
    # (Seu código de login aqui... ao validar, mude para st.session_state.pagina = "menu")

# --- BLOCO 2: MENU PRINCIPAL (PAINEL) ---
elif st.session_state.pagina == "menu":
    st.markdown(f"<h1 style='color: white;'>🚢 Painel - {st.session_state.navio}</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 TABELA DE RANCHO", use_container_width=True):
            st.session_state.pagina = "conferencia"
            st.rerun()
        
        if st.button("📜 VER HISTÓRICO", use_container_width=True):
            st.session_state.pagina = "historico"
            st.rerun()

    with col2:
        if st.button("👨‍🍳 DECLARAÇÃO", use_container_width=True):
            st.session_state.pagina = "declaracao"
            st.rerun()

    st.markdown("---")
    if st.button("⬅️ SAIR", use_container_width=True):
        st.session_state.pagina = "login"
        st.rerun()

# --- BLOCO 6: TELA DE CONFERÊNCIA (ESTOQUE) ---
elif st.session_state.pagina == "conferencia":
    st.title(f"📦 Estoque: {st.session_state.navio}")
    
    # Busca os dados usando o ID_RANCHO_ESTOQUE definido no topo
    if 'df_estoque' not in st.session_state or st.session_state.df_estoque.empty:
        try:
            url_query = f"https://api.notion.com/v1/databases/{ID_RANCHO_ESTOQUE}/query"
            res = requests.post(url_query, headers=headers)
            # (Sua lógica de conversão de JSON para DataFrame aqui)
        except Exception as e:
            st.error(f"Erro ao carregar banco de rancho: {e}")

    # Exibição da Tabela
    if 'df_estoque' in st.session_state:
        df_edit = st.session_state.df_estoque[st.session_state.df_estoque['NAVIO'] == st.session_state.navio].copy()
        st.data_editor(df_edit, hide_index=True, use_container_width=True, key="editor_rancho")
        
        if st.button("⬅️ VOLTAR AO MENU"):
            st.session_state.pagina = "menu"; st.rerun()

# --- BLOCO 8: MÓDULO DE HISTÓRICO (INDIVIDUALIZADO) ---
elif st.session_state.pagina == "historico":
    st.markdown("<h1 style='text-align: center; color: white;'>📜 Histórico de Pedidos</h1>", unsafe_allow_html=True)
    
    try:
        url_hist = f"https://api.notion.com/v1/databases/{ID_HISTORICO_NOTION}/query"
        
        # Filtro: Admin vê tudo, Cozinheiro vê apenas seu navio
        if st.session_state.cozinheiro.lower() == "admin":
            query = {"sorts": [{"property": "Data Pedido", "direction": "descending"}]}
        else:
            query = {
                "filter": {"property": "Navio", "rich_text": {"equals": st.session_state.navio}},
                "sorts": [{"property": "Data Pedido", "direction": "descending"}]
            }

        res_hist = requests.post(url_hist, headers=headers, json=query)
        
        if res_hist.status_code == 200:
            results = res_hist.json().get("results", [])
            dados_lista = []
            for r in results:
                p = r["properties"]
                dados_lista.append({
                    "Data": p["Data Pedido"]["date"]["start"] if p["Data Pedido"]["date"] else "-",
                    "Cozinheiro": p["Cozinheiro"]["title"][0]["text"]["content"] if p["Cozinheiro"]["title"] else "N/A",
                    "Navio": p["Navio"]["rich_text"][0]["text"]["content"] if p["Navio"]["rich_text"] else "N/A",
                    "Validade": p["Validade"]["date"]["start"] if p["Validade"]["date"] else "-",
                })
            st.dataframe(pd.DataFrame(dados_lista), use_container_width=True, hide_index=True)
        else:
            st.error("Erro ao conectar com o Histórico no Notion.")
            
    except Exception as e:
        st.error(f"Falha técnica: {e}")

    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"; st.rerun()
