import streamlit as st
import os

# ==========================================
# 1. CONFIGURAÇÕES E BANCO DE DADOS DE USUÁRIOS
# ==========================================
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state:
    st.session_state.cozinheiro = ""

# Dicionário: "LOGIN": {"nome": "NOME DO COZINHEIRO", "senha": "SENHA"}
USUARIOS = {
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "NAVIO 02": {"nome": "Carlos", "senha": "456"},
    "AROEIRA": {"nome": "ALLAN", "senha": "789"},
    "ZION 04": {"nome": "Ricardo", "senha": "101"}
}

# ==========================================
# 2. ESTILO CSS (FUNDOS E BOTÕES)
# ==========================================
st.markdown("""
    <style>
    /* Fundo Azul Royal */
    .stApp { background-color: #4169E1 !important; }
    
    /* Textos em Branco */
    h1, h2, h3, p, label { color: white !important; }

    /* BOTÃO LARANJA COM LETRA PRETA (FORÇADO) */
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
    
    /* Garante que o texto continue preto ao passar o mouse ou clicar */
    div.stButton > button:hover, div.stButton > button:active, div.stButton > button:focus {
        color: #000000 !important;
        background-color: #FFA500 !important;
    }

    /* Estilo para campos de texto e selectbox */
    input { color: black !important; }
    div[data-baseweb="select"] > div { color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. #--- TELA INICIAL ---#
# ==========================================
if st.session_state.pagina == "home":
    st.title("Bem-vindo ao Zion Rancho App!")
    st.write("Seu controle de estoque inteligente com IA.")
    
    if os.path.exists("APPRANCHO.png"):
        st.image("APPRANCHO.png", width=400)
    
    if st.button("INICIAR ACESSO", key="btn_inicio"):
        st.session_state.pagina = "login"
        st.rerun()

# ==========================================
# 4. #--- TELA DE LOGIN (SUBSTELA ACESSO) ---#
# ==========================================
elif st.session_state.pagina == "login":
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(65, 105, 225, 0.8), rgba(65, 105, 225, 0.8)), 
            url("https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&w=1350&q=80");
            background-size: cover;
        }
        </style>
        """, unsafe_allow_html=True)
        
    st.title("🔐 Acesso do Cozinheiro")
    
    navio_sel = st.selectbox("Selecione o seu Navio", [""] + list(USUARIOS.keys()))
    senha_sel = st.text_input("Senha de Acesso", type="password")
    
    if st.button("🛒 ENTRAR", key="btn_entrar"):
        if navio_sel in USUARIOS and USUARIOS[navio_sel]["senha"] == senha_sel:
            # Salva o nome do cozinheiro para a saudação
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
    # Saudação com nome do Cozinheiro
    st.markdown(f"## Seja Bem-vindo, {st.session_state.cozinheiro}!")
    st.write("Escolha o que deseja fazer:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛒 LISTA DE RANCHO", key="btn_rancho"):
            st.session_state.pagina = "lista"
            st.rerun()
    with col2:
        if st.button("👨‍✈️ TRIPULAÇÃO", key="btn_tripulacao"):
            st.session_state.pagina = "tripulacao"
            st.rerun()

    st.markdown("---")
    if st.button("SAIR DO SISTEMA", key="btn_sair_final"):
        st.session_state.pagina = "home"
        st.rerun()

# ==========================================
# 6. TELAS DE CONTEÚDO (LISTA E TRIPULAÇÃO)
# ==========================================
elif st.session_state.pagina == "lista":
    st.title("🛒 Lista de Rancho")
    st.info(f"Cozinheiro Responsável: {st.session_state.cozinheiro}")
    
    # Próximo passo: Integração com Notion aqui
    st.write("Sua lista de compras aparecerá aqui em breve.")
    
    if st.button("⬅️ VOLTAR AO MENU", key="btn_voltar_lista"):
        st.session_state.pagina = "menu"
        st.rerun()

elif st.session_state.pagina == "tripulacao":
    st.title("👨‍✈️ Tripulação")
    st.write("Módulo de gestão de tripulantes.")
    
    if st.button("⬅️ VOLTAR AO MENU", key="btn_voltar_trip"):
        st.session_state.pagina = "menu"
        st.rerun()

# ==========================================
# 6. TELA: LISTA DE RANCHO (AJUSTADA)
# ==========================================
elif st.session_state.pagina == "lista":
    st.markdown(f"## 🛒 Lista de Rancho")
    st.markdown(f"**Responsável:** {st.session_state.cozinheiro}")

    # --- FUNÇÃO PARA BUSCAR DADOS (Certifique-se que as colunas existem no Notion) ---
    def buscar_dados_notion():
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
                    "PREDEFINIDO": props.get("PREDEFINIDO", {}).get("number", 0), # Quantidade da Nutricionista
                    "ESTOQUE": props.get("ESTOQUE", {}).get("number", 0),
                    "DESCRIÇÃO": props.get("DESCRIÇÃO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                })
            return pd.DataFrame(itens)
        else:
            return pd.DataFrame()

    with st.spinner("Sincronizando com Notion..."):
        df_itens = buscar_dados_notion()

    if not df_itens.empty:
        # Criamos a coluna CONFIRMA onde o cozinheiro digita a quantidade dele
        # Ela começa zerada ou com o valor do estoque para ele ajustar
        df_itens["CONFIRMA"] = 0 
        df_itens["RESPONSÁVEL"] = st.session_state.cozinheiro

        st.write("Compare os valores da Nutricionista e insira sua necessidade na coluna **CONFIRMA**:")

        # --- EDITOR DE TABELA ---
        df_editavel = st.data_editor(
            df_itens,
            column_config={
                "PREDEFINIDO": st.column_config.NumberColumn("PREDEFINIDO (Nutri)", help="Quantidade definida pela Nutricionista", disabled=True),
                "CONFIRMA": st.column_config.NumberColumn("CONFIRMA (Qtd)", help="Digite aqui a quantidade que você precisa", min_value=0),
                "ESTOQUE": st.column_config.NumberColumn("ESTOQUE ATUAL", disabled=True),
                "RESPONSÁVEL": st.column_config.TextColumn("RESPONSÁVEL", disabled=True),
            },
            disabled=["CÓDIGO", "PROTEÍNA", "TIPO", "UNID.", "PREDEFINIDO", "ESTOQUE", "DESCRIÇÃO", "RESPONSÁVEL"],
            hide_index=True,
            use_container_width=True
        )

        st.markdown("---")
        
        col_pdf, col_notion = st.columns(2)
        
        with col_pdf:
            # Aqui você gera o PDF usando os dados de 'df_editavel'
            if st.button("📄 GERAR PDF DA LISTA"):
                st.info("Gerando documento...")
                # (A lógica do PDF que passamos antes entra aqui)

        with col_notion:
            if st.button("💾 ENVIAR PARA O NOTION"):
                st.success("Lista enviada com sucesso!")

    if st.button("⬅️ VOLTAR AO MENU", key="btn_voltar_lista"):
        st.session_state.pagina = "menu"
        st.rerun()
