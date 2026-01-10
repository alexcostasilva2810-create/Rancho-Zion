import streamlit as st
import pandas as pd
import requests
import os
from fpdf import FPDF

# ==========================================
# 1. CONFIGURAÇÕES E BANCO DE USUÁRIOS
# ==========================================
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state:
    st.session_state.cozinheiro = ""

USUARIOS = {
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "NAVIO 02": {"nome": "Carlos", "senha": "456"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"}
}

# ==========================================
# 2. ESTILO CSS (BOTÕES LARANJA / TEXTO PRETO)
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #4169E1 !important; }
    h1, h2, h3, p, label { color: white !important; }

    /* BOTÃO LARANJA COM LETRA PRETA */
    div.stButton > button {
        background-color: #FF8C00 !important;
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 18px !important;
        border-radius: 10px !important;
        border: 2px solid #000000 !important;
        width: 100%;
        height: 3.5em;
    }
    div.stButton > button:hover { color: #000000 !important; background-color: #FFA500 !important; }
    
    /* Inputs e Tabela */
    input { color: black !important; }
    .stDataEditor { background-color: white !important; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO AUXILIAR: BUSCA NOTION ---
def buscar_dados_notion():
    # Nota: Certifique-se de ter NOTION_TOKEN e DATABASE_ID nos Secrets
    try:
        url = f"https://api.notion.com/v1/databases/{st.secrets['DATABASE_ID']}/query"
        headers = {
            "Authorization": f"Bearer {st.secrets['NOTION_TOKEN']}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            itens = []
            for row in data["results"]:
                props = row["properties"]
                itens.append({
                    "CÓDIGO": props.get("CÓDIGO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "PROTEÍNA": props.get("PROTEÍNA", {}).get("title", [{}])[0].get("plain_text", "Sem Nome"),
                    "TIPO": props.get("TIPO", {}).get("select", {}).get("name", ""),
                    "UNID.": props.get("UNIDADE DE MEDIDA", {}).get("select", {}).get("name", ""),
                    "PREDEFINIDO": props.get("PREDEFINIDO", {}).get("number", 0),
                    "ESTOQUE": props.get("ESTOQUE", {}).get("number", 0),
                })
            return pd.DataFrame(itens)
    except:
        return pd.DataFrame() # Retorna vazio se não configurar secrets ainda

# ==========================================
# 3. #--- TELA INICIAL ---#
# ==========================================
if st.session_state.pagina == "home":
    st.title("Bem-vindo ao Zion Rancho App!")
    if os.path.exists("APPRANCHO.png"):
        st.image("APPRANCHO.png", width=400)
    
    if st.button("INICIAR ACESSO", key="btn_inicio"):
        st.session_state.pagina = "login"
        st.rerun()

# ==========================================
# 4. #--- TELA DE LOGIN ---#
# ==========================================
elif st.session_state.pagina == "login":
    st.title("🔐 Acesso do Cozinheiro")
    navio_sel = st.selectbox("Selecione o seu Navio", [""] + list(USUARIOS.keys()))
    senha_sel = st.text_input("Senha de Acesso", type="password")
    
    if st.button("🛒 ENTRAR", key="btn_entrar"):
        if navio_sel in USUARIOS and USUARIOS[navio_sel]["senha"] == senha_sel:
            st.session_state.cozinheiro = USUARIOS[navio_sel]["nome"]
            st.session_state.pagina = "menu"
            st.rerun()
        else:
            st.error("Dados incorretos!")
            
    if st.button("⬅️ VOLTAR", key="btn_voltar_login"):
        st.session_state.pagina = "home"
        st.rerun()

# ==========================================
# 5. #--- SUBSTELA (MENU PRINCIPAL) ---#
# ==========================================
elif st.session_state.pagina == "menu":
    st.markdown(f"## Seja Bem-vindo, {st.session_state.cozinheiro}!")
    st.write("Escolha o módulo desejado:")
    
    col1, col2 = st.columns(2)
    with col1:
        # AQUI É O GATILHO PARA A TABELA
        if st.button("🛒 LISTA DE RANCHO", key="btn_ir_lista"):
            st.session_state.pagina = "lista"
            st.rerun()
            
    with col2:
        if st.button("👨‍✈️ TRIPULAÇÃO", key="btn_ir_trip"):
            st.session_state.pagina = "tripulacao"
            st.rerun()

    if st.button("SAIR", key="btn_sair"):
        st.session_state.pagina = "home"
        st.rerun()

# ==========================================
# 6. #--- TELA DA TABELA (LISTA DE RANCHO) ---#
# ==========================================
elif st.session_state.pagina == "lista":
    st.title("🛒 Tabela de Rancho")
    st.write(f"Responsável: **{st.session_state.cozinheiro}**")

    df_itens = buscar_dados_notion()

    if df_itens is not None and not df_itens.empty:
        # Criamos a coluna CONFIRMA (editável) e RESPONSÁVEL (travada)
        df_itens["CONFIRMA"] = 0 
        df_itens["RESPONSÁVEL"] = st.session_state.cozinheiro

        # EDITOR DA TABELA
        df_editavel = st.data_editor(
            df_itens,
            column_config={
                "PREDEFINIDO": st.column_config.NumberColumn("PREDEFINIDO", help="Definido pela Nutri", disabled=True),
                "CONFIRMA": st.column_config.NumberColumn("CONFIRMA (Qtd)", help="Digite a quantidade necessária", min_value=0),
                "RESPONSÁVEL": st.column_config.TextColumn("RESPONSÁVEL", disabled=True),
            },
            disabled=["CÓDIGO", "PROTEÍNA", "TIPO", "UNID.", "PREDEFINIDO", "ESTOQUE", "RESPONSÁVEL"],
            hide_index=True,
            use_container_width=True
        )

        st.markdown("---")
        
        if st.button("💾 SALVAR E GERAR PDF", key="btn_final"):
            st.success("Lista processada com sucesso!")
            # Aqui você pode chamar a função do PDF que criamos anteriormente
    
    else:
        st.warning("Aguardando conexão com a base de dados do Notion...")

    if st.button("⬅️ VOLTAR AO MENU", key="btn_voltar_menu"):
        st.session_state.pagina = "menu"
        st.rerun()

# ==========================================
# 7. TELA TRIPULAÇÃO
# ==========================================
elif st.session_state.pagina == "tripulacao":
    st.title("👨‍✈️ Tripulação")
    st.write("Módulo em desenvolvimento.")
    if st.button("⬅️ VOLTAR", key="btn_v_trip"):
        st.session_state.pagina = "menu"
        st.rerun()
