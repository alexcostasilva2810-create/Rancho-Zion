import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES GLOBAIS ---
# ID da sua nova tabela de histórico no Notion
ID_HISTORICO_NOTION = "2e5025de7b79803187a4d8b865179440"

# Seus headers da Zion Tecnologia (Mantenha o seu Token aqui)
headers = {
    "Authorization": "Bearer " + st.secrets["notion_token"],
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# --- INICIALIZAÇÃO DO ESTADO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "login"

# --- BLOCO 1: TELA DE LOGIN ---
if st.session_state.pagina == "login":
    st.markdown("<h1 style='text-align: center; color: white;'>🚢 Zion Rancho - Login</h1>", unsafe_allow_html=True)
    # ... (Seu código de login atual aqui)
    # Ao logar com sucesso, defina st.session_state.pagina = "menu"

# --- BLOCO 2: MENU PRINCIPAL (PAINEL) ---
elif st.session_state.pagina == "menu":
    st.markdown(f"<h1 style='color: white;'>🚢 Painel - {st.session_state.navio}</h1>", unsafe_allow_html=True)
    st.write(f"Usuário: **{st.session_state.cozinheiro}**")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 TABELA DE RANCHO", use_container_width=True):
            st.session_state.pagina = "conferencia"
            st.rerun()
        
        # Botão para o novo Módulo de Histórico
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

# --- BLOCO 6: CONFERÊNCIA DE ESTOQUE (VERSÃO LIMPA) ---
elif st.session_state.pagina == "conferencia":
    st.title(f"📦 Estoque: {st.session_state.navio}")
    
    if 'df_estoque' in st.session_state and not st.session_state.df_estoque.empty:
        df_edit = st.session_state.df_estoque[st.session_state.df_estoque['NAVIO'] == st.session_state.navio].copy()
        
        df_conferido = st.data_editor(
            df_edit,
            column_config={
                "CONFIRMA": st.column_config.NumberColumn("Qtd em Estoque", min_value=0),
                "PREDEFINIDO": st.column_config.NumberColumn("Meta", disabled=True),
                "ITEM": None, "NAVIO": None 
            },
            disabled=["DESCRIÇÃO", "TIPO", "UNID MED"],
            hide_index=True, use_container_width=True, key="editor_rancho"
        )

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("💾 GERAR PDF"):
                st.success("PDF Pronto para download!")
        with col_b:
            if st.button("⬅️ VOLTAR"):
                st.session_state.pagina = "menu"; st.rerun()
    else:
        st.error("Erro ao carregar estoque.")

# --- BLOCO 7: DECLARAÇÃO E SALVAMENTO NO NOTION ---
elif st.session_state.pagina == "declaracao":
    st.title("👨‍🍳 Declaração de Rancho")
    
    # ... (Seus campos de data, lotação e escolta aqui)
    # No botão de 'ENVIAR', adicione a função para salvar na tabela de histórico:
    if st.button("Finalizar e Salvar"):
        # Lógica de salvar no Notion aqui usando ID_HISTORICO_NOTION
        st.success("Dados salvos no histórico!")

# --- BLOCO 8: MÓDULO DE HISTÓRICO (INDIVIDUALIZADO) ---
elif st.session_state.pagina == "historico":
    st.markdown("<h1 style='text-align: center; color: white;'>📜 Histórico de Pedidos</h1>", unsafe_allow_html=True)
    
    try:
        url_hist = f"https://api.notion.com/v1/databases/{ID_HISTORICO_NOTION}/query"
        
        # Filtro: Cozinheiro vê apenas seu navio
        # Admin vê todos os registros da frota
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
            dados_lista = []
            for r in results:
                p = r["properties"]
                dados_lista.append({
                    "Data": p["Data Pedido"]["date"]["start"] if p["Data Pedido"]["date"] else "-",
                    "Cozinheiro": p["Cozinheiro"]["title"][0]["text"]["content"] if p["Cozinheiro"]["title"] else "N/A",
                    "Navio": p["Navio"]["rich_text"][0]["text"]["content"] if p["Navio"]["rich_text"] else "N/A",
                    "Validade": p["Validade"]["date"]["start"] if p["Validade"]["date"] else "-",
                    "Lotação": p["Lotação"]["number"] if "Lotação" in p else 0,
                    "Escolta": p["Escolta"]["select"]["name"] if p["Escolta"]["select"] else "NÃO"
                })
            
            df_hist = pd.DataFrame(dados_lista)
            
            # Ferramenta de busca exclusiva do Administrador
            if st.session_state.cozinheiro.lower() == "admin" and not df_hist.empty:
                filtro_coz = st.selectbox("Filtrar por Cozinheiro:", ["TODOS"] + sorted(df_hist["Cozinheiro"].unique().tolist()))
                if filtro_coz != "TODOS":
                    df_hist = df_hist[df_hist["Cozinheiro"] == filtro_coz]

            st.dataframe(df_hist, use_container_width=True, hide_index=True)
        else:
            st.error("Erro ao acessar banco de dados do Notion.")
            
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")

    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"; st.rerun()
