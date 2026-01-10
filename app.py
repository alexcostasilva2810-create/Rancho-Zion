import streamlit as st
import pandas as pd
import requests
import os
from fpdf import FPDF

# =================================================================
# BLOCO 1: CONFIGURAÇÕES, ESTADOS E ESTILO (CSS)
# =================================================================
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state:
    st.session_state.cozinheiro = ""

# Dicionário de acesso
USUARIOS = {
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "NAVIO 03": {"nome": "Carlos", "senha": "456"}
}

# Aplicação de Estilos
st.markdown("""
    <style>
    /* Fundo Azul para o App */
    .stApp { background-color: #4169E1 !important; }
    h1, h2, h3, p, label { color: white !important; }

    /* BOTÃO LARANJA COM LETRA PRETA (PADRÃO ZION) */
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
    
    /* Ajuste de inputs para texto preto */
    input { color: black !important; }
    div[data-baseweb="select"] > div { color: black !important; }
    </style>
    """, unsafe_allow_html=True)


# =================================================================
# BLOCO 2: TELA INICIAL
# =================================================================
if st.session_state.pagina == "home":
    st.title("Bem-vindo ao Zion Rancho App!")
    st.write("Seu controle de estoque inteligente com IA.")
    
    if os.path.exists("APPRANCHO.png"):
        st.image("APPRANCHO.png", width=400)
    
    if st.button("INICIAR ACESSO", key="btn_home"):
        st.session_state.pagina = "login"
        st.rerun()


# =================================================================
# BLOCO 3: TELA DE LOGIN (ACESSO DO COZINHEIRO)
# =================================================================
elif st.session_state.pagina == "login":
    # Fundo leve de cozinha apenas nesta tela
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
    
    navio_sel = st.selectbox("Selecione o seu Navio", [""] + list(USUARIOS.keys()), key="sel_login")
    senha_sel = st.text_input("Senha de Acesso", type="password", key="pwd_login")
    
    if st.button("🛒 ENTRAR", key="btn_entrar"):
        if navio_sel in USUARIOS and USUARIOS[navio_sel]["senha"] == senha_sel:
            st.session_state.cozinheiro = USUARIOS[navio_sel]["nome"]
            st.session_state.pagina = "menu"
            st.rerun()
        else:
            st.error("Credenciais inválidas.")

    if st.button("⬅️ VOLTAR", key="btn_voltar_home"):
        st.session_state.pagina = "home"
        st.rerun()


# =================================================================
# BLOCO 4: SUBSTELA (MENU PRINCIPAL)
# =================================================================
elif st.session_state.pagina == "menu":
    st.markdown(f"## Seja Bem-vindo, {st.session_state.cozinheiro}!")
    st.write("Escolha o que deseja fazer:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛒 LISTA DE RANCHO", key="btn_menu_rancho"):
            st.session_state.pagina = "lista"
            st.rerun()
    with col2:
        if st.button("👨‍✈️ TRIPULAÇÃO", key="btn_menu_trip"):
            st.session_state.pagina = "tripulacao"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("SAIR DO SISTEMA", key="btn_logout"):
        st.session_state.pagina = "home"
        st.rerun()


# =================================================================
# BLOCO 5: TELA DA TABELA (LISTA DE RANCHO) E PDF
# =================================================================
elif st.session_state.pagina == "lista":
    st.title("📋 Tabela de Rancho")
    st.write(f"Responsável Logado: **{st.session_state.cozinheiro}**")

    # Dados Simulados (Integrar com sua função buscar_dados_notion)
    dados = {
        "CÓDIGO": ["PR01", "PR02", "PR03"],
        "PROTEÍNA": ["Alcatra", "Sobrecoxa Frango", "Filé de Merluza"],
        "UNID.": ["KG", "KG", "KG"],
        "PREDEFINIDO": [20.0, 35.0, 15.0],
        "CONFIRMA": [0.0, 0.0, 0.0]
    }
    df = pd.DataFrame(dados)

    # Editor de Tabela
    df_editado = st.data_editor(
        df,
        column_config={
            "PREDEFINIDO": st.column_config.NumberColumn("PREDEFINIDO (Nutri)", disabled=True),
            "CONFIRMA": st.column_config.NumberColumn("CONFIRMA (Sua Qtd)", min_value=0),
        },
        hide_index=True,
        use_container_width=True,
        key="editor_lista"
    )

    st.markdown("---")
    
    col_pdf, col_back = st.columns(2)
    with col_pdf:
        # Função interna de PDF rápida
        if st.button("📄 GERAR PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(190, 10, f"Checklist de Rancho - Cozinheiro: {st.session_state.cozinheiro}", ln=True, align="C")
            pdf.ln(5)
            # Gerar bytes e disponibilizar download
            pdf_out = pdf.output(dest='S').encode('latin-1')
            st.download_button("Clique aqui para baixar", data=pdf_out, file_name="rancho_zion.pdf")

    with col_back:
        if st.button("⬅️ VOLTAR AO MENU", key="btn_voltar_menu"):
            st.session_state.pagina = "menu"
            st.rerun()


# =================================================================
# BLOCO 6: TELA DA TABELA (LISTA DE RANCHO) - DADOS REAIS DO NOTION
# =================================================================
elif st.session_state.pagina == "lista":
    nome_navio = st.session_state.get('navio', 'NAVIO').upper()
    st.markdown(f"## 📋 Tabela de Rancho - {nome_navio}")
    
    # 1. PUXAR DADOS (Aqui usamos os dados que você acabou de inserir no Notion)
    # Se a função query_notion ainda não estiver integrada, os dados não aparecerão.
    df_notion = st.session_state.get('df_lista', pd.DataFrame())

    if df_notion.empty:
        st.warning("⚠️ O sistema ainda não carregou os dados do Notion. Clique em 'Sincronizar' ou verifique a conexão.")
        if st.button("⬅️ VOLTAR"):
            st.session_state.pagina = "menu"
            st.rerun()
    else:
        # 2. EXIBIÇÃO NA TELA (Configurada para as colunas do seu Notion)
        df_usuario = st.data_editor(
            df_notion,
            column_config={
                "CODIGO": st.column_config.TextColumn("CÓD.", disabled=True),
                "PROTEINA": st.column_config.TextColumn("ITEM", disabled=True),
                "TIPO": st.column_config.TextColumn(disabled=True),
                "UNIDADE DE MEDIDA": st.column_config.TextColumn("UNID.", disabled=True),
                "ESTOQUE": st.column_config.NumberColumn(disabled=True),
                "DESCRIÇÃO": st.column_config.TextColumn(disabled=True),
                "CONFIRMA": st.column_config.NumberColumn("SUA QTD", min_value=0.0),
            },
            hide_index=True,
            use_container_width=True,
            key="editor_real_com_dados"
        )

        # 3. GERAÇÃO DO PDF COM OS DADOS DO NOTION
        if st.button("💾 GERAR PDF COM LISTA DO NOTION"):
            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()
            
            # Cabeçalho
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, f"LISTA DE RANCHO - {nome_navio}", ln=True, align="C")
            pdf.ln(5)

            # Cabeçalho da Tabela
            pdf.set_font("Arial", "B", 8)
            pdf.set_fill_color(240, 240, 240)
            
            # Larguras para as colunas reais do seu Notion
            w = [20, 50, 30, 20, 20, 80, 25] 
            titulos = ["COD", "PROTEINA", "TIPO", "UNID", "ESTQ", "DESCRICAO", "CONF."]
            
            for i in range(len(titulos)):
                pdf.cell(w[i], 10, titulos[i], 1, 0, "C", True)
            pdf.ln()

            # Preenchimento das Linhas (Agora pegando do Notion)
            pdf.set_font("Arial", "", 8)
            for _, row in df_usuario.iterrows():
                pdf.cell(w[0], 8, str(row.get("CODIGO", "")), 1)
                pdf.cell(w[1], 8, str(row.get("PROTEINA", "")), 1)
                pdf.cell(w[2], 8, str(row.get("TIPO", "")), 1)
                pdf.cell(w[3], 8, str(row.get("UNIDADE DE MEDIDA", "")), 1)
                pdf.cell(w[4], 8, str(row.get("ESTOQUE", "0")), 1, 0, "C")
                pdf.cell(w[5], 8, str(row.get("DESCRIÇÃO", "")), 1)
                pdf.cell(w[6], 8, str(row.get("CONFIRMA", "0")), 1, 1, "C")

            pdf_output = pdf.output(dest='S').encode('latin-1')
            st.download_button("📥 BAIXAR PDF COMPLETO", data=pdf_output, file_name="Rancho_Zion.pdf")
