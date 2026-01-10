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
# BLOCO 6: TELA DA TABELA (LISTA DE RANCHO) - VERSÃO FINAL REVISADA
# =================================================================
elif st.session_state.pagina == "lista":
    st.markdown("## 📋 Tabela de Rancho")
    st.write(f"Responsável Logado: **{st.session_state.cozinheiro}**")

    # 1. GARANTINDO AS 8 COLUNAS NO SISTEMA
    if 'df_lista' not in st.session_state:
        st.session_state.df_lista = pd.DataFrame({
            "CÓDIGO": ["PR01", "PR02", "PR03"],
            "PROTEÍNA": ["Alcatra", "Sobrecoxa Frango", "Filé de Merluza"],
            "TIPO": ["Carne", "Aves", "Peixe"],
            "UNIDADE DE MEDIDA": ["KG", "KG", "KG"],
            "ESTOQUE": [5.0, 2.0, 10.0],
            "DESCRIÇÃO": ["Peça inteira", "Bandeja 1kg", "Filé congelado"],
            "PREDEFINIDO": [20.0, 35.0, 15.0],
            "CONFIRMA": [0.0, 0.0, 0.0]
        })

    # 2. TABELA COM TODAS AS COLUNAS VISÍVEIS
    df_final = st.data_editor(
        st.session_state.df_lista,
        column_config={
            "CÓDIGO": st.column_config.TextColumn("CÓDIGO", disabled=True),
            "PROTEÍNA": st.column_config.TextColumn("PROTEÍNA", disabled=True),
            "TIPO": st.column_config.TextColumn("TIPO", disabled=True),
            "UNIDADE DE MEDIDA": st.column_config.TextColumn("UNIDADE", disabled=True),
            "ESTOQUE": st.column_config.NumberColumn("ESTOQUE", disabled=True),
            "DESCRIÇÃO": st.column_config.TextColumn("DESCRIÇÃO", disabled=True),
            "PREDEFINIDO": st.column_config.NumberColumn("PREDEFINIDO (Nutri)", disabled=True),
            "CONFIRMA": st.column_config.NumberColumn("CONFIRMA (Sua Qtd)", min_value=0.0, format="%.2f"),
        },
        hide_index=True,
        use_container_width=True,
        key="editor_definitivo"
    )

    st.markdown("---")
    
    col_salvar, col_voltar = st.columns(2)
    
    with col_salvar:
        # 3. GERAÇÃO DO PDF - AGORA LENDO O DF_FINAL DIRETAMENTE
        if st.button("💾 SALVAR E GERAR PDF", key="btn_final_save"):
            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()
            
            # Cabeçalho Zion
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "ZION RANCHO - RELATORIO DE COMPRAS", ln=True, align="C")
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"Responsavel: {st.session_state.cozinheiro}", ln=True, align="C")
            pdf.ln(5)

            # Cabeçalho da Tabela no PDF (8 Colunas)
            pdf.set_font("Arial", "B", 8)
            pdf.set_fill_color(255, 140, 0)
            
            w = [20, 45, 25, 20, 25, 62, 25, 25] # Larguras ajustadas
            cols = ["COD", "PROTEINA", "TIPO", "UNID", "ESTOQUE", "DESCRICAO", "PREDEF", "CONF"]
            
            for i in range(len(cols)):
                pdf.cell(w[i], 10, cols[i], 1, 0, "C", True)
            pdf.ln()

            # Preenchimento garantido
            pdf.set_font("Arial", "", 8)
            for _, row in df_final.iterrows():
                pdf.cell(w[0], 8, str(row["CÓDIGO"]), 1, 0, "C")
                pdf.cell(w[1], 8, str(row["PROTEÍNA"]), 1)
                pdf.cell(w[2], 8, str(row["TIPO"]), 1, 0, "C")
                pdf.cell(w[3], 8, str(row["UNIDADE DE MEDIDA"]), 1, 0, "C")
                pdf.cell(w[4], 8, str(row["ESTOQUE"]), 1, 0, "C")
                pdf.cell(w[5], 8, str(row["DESCRIÇÃO"]), 1)
                pdf.cell(w[6], 8, str(row["PREDEFINIDO"]), 1, 0, "C")
                pdf.set_font("Arial", "B", 8)
                pdf.cell(w[7], 8, str(row["CONFIRMA"]), 1, 1, "C")
                pdf.set_font("Arial", "", 8)

            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            st.success("✅ Salvo com sucesso!")
            st.download_button("📥 BAIXAR RELATORIO", data=pdf_bytes, file_name="rancho.pdf", mime="application/pdf")

    with col_voltar:
        if st.button("⬅️ VOLTAR AO MENU", key="btn_back"):
            st.session_state.pagina = "menu"
            st.rerun()
