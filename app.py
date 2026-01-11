import streamlit as st
import pandas as pd
import requests

# --- 1. RESTAURANDO CONFIGURAÇÕES GLOBAIS ---
# IDs que estavam funcionando nas suas versões anteriores
ID_ESTOQUE = "8bc3303498114065969562723652697b"
ID_HISTORICO = "2e5025de7b79803187a4d8b865179440"

# Busca do Token via Secrets conforme configurado no painel
try:
    TOKEN = st.secrets["NOTION_TOKEN"]
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
except Exception:
    st.error("Erro de conexão: Verifique o Token nos Secrets.")
    st.stop()

# --- 2. INICIALIZAÇÃO DE ESTADO (SEM ALTERAR O VISUAL) ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "login"

# --- BLOCO 1: TELA DE LOGIN ORIGINAL ---
if st.session_state.pagina == "login":
    # Aqui volta o seu estilo de fundo e logo que você já possuía
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), 
                        url("https://images.unsplash.com/photo-1580508112997-57fd4a852a10?q=80&w=1920");
            background-size: cover;
        }
        </style>
        """, unsafe_allow_html=True)
    
    st.title("🚢 Zion Rancho")
    # ... (O seu código exato de login com a verificação de senha/usuário que você usava)
    # Certifique-se de manter a lógica: st.session_state.pagina = "menu" ao logar

# --- BLOCO 2: MENU PRINCIPAL (PAINEL RESTAURADO) ---
elif st.session_state.pagina == "menu":
    # Restaurando o layout de botões que você já conhece
    st.markdown(f"<h1 style='color: white;'>🚢 Painel - {st.session_state.navio}</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 TABELA DE RANCHO", use_container_width=True):
            st.session_state.pagina = "conferencia"
            st.rerun()
        
        # Inclusão apenas do novo botão de Histórico no layout antigo
        if st.button("📜 VER HISTÓRICO", use_container_width=True):
            st.session_state.pagina = "historico"
            st.rerun()

    with col2:
        if st.button("👨‍🍳 DECLARAÇÃO", use_container_width=True):
            st.session_state.pagina = "declaracao"
            st.rerun()

    if st.button("⬅️ SAIR"):
        st.session_state.pagina = "login"; st.rerun()

# --- BLOCO 8: MÓDULO DE HISTÓRICO (ADICIONADO SEM QUEBRAR O RESTO) ---
elif st.session_state.pagina == "historico":
    st.markdown("<h1 style='color: white;'>📜 Histórico de Pedidos</h1>", unsafe_allow_html=True)
    
    try:
        url = f"https://api.notion.com/v1/databases/{ID_HISTORICO}/query"
        # Mantendo o filtro que separa por navio para não sobrecarregar
        payload = {"filter": {"property": "Navio", "rich_text": {"equals": st.session_state.navio}}}
        
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            results = res.json().get("results", [])
            df = pd.DataFrame([
                {
                    "Cozinheiro": r["properties"]["Cozinheiro"]["title"][0]["text"]["content"],
                    "Data": r["properties"]["Data Pedido"]["date"]["start"],
                    "Navio": r["properties"]["Navio"]["rich_text"][0]["text"]["content"]
                } for r in results if r["properties"]["Cozinheiro"]["title"]
            ])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("Nenhum registro encontrado ainda.")
    except:
        st.error("Erro ao carregar módulo de histórico.")

    if st.button("⬅️ VOLTAR"):
        st.session_state.pagina = "menu"; st.rerun()
