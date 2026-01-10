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
# BLOCO 6: TELA DA TABELA (LISTA DE RANCHO) + GERADOR DE PDF REAL
# =================================================================
elif st.session_state.pagina == "lista":
    st.markdown("## 📋 Tabela de Rancho")
    st.write(f"Responsável Logado: **{st.session_state.cozinheiro}**")

    # 1. DADOS (Simulado - Substitua pela busca do Notion se necessário)
    if 'df_lista' not in st.session_state:
        dados = {
            "CÓDIGO": ["PR01", "PR02", "PR03"],
            "PROTEÍNA": ["Alcatra", "Sobrecoxa Frango", "Filé de Merluza"],
            "TIPO": ["Carne", "Aves", "Peixe"],
            "UNID. MEDIDA": ["KG", "KG", "KG"],
            "PREDEFINIDO": [20.0, 35.0, 15.0], 
            "ESTOQUE": [5.0, 2.0, 10.0],
            "DESCRIÇÃO": ["Peça inteira", "Bandeja 1kg", "Filé congelado"],
            "CONFIRMA": [0.0, 0.0, 0.0]
        }
        st.session_state.df_lista = pd.DataFrame(dados)

    # 2. TABELA INTERATIVA (Apenas 'CONFIRMA' é editável)
    df_editado = st.data_editor(
        st.session_state.df_lista,
        column_config={
            "CONFIRMA": st.column_config.NumberColumn("CONFIRMA (Qtd)", min_value=0.0, format="%.2f"),
            "PREDEFINIDO": st.column_config.NumberColumn("PREDEFINIDO", disabled=True),
        },
        disabled=["CÓDIGO", "PROTEÍNA", "TIPO", "UNID. MEDIDA", "PREDEFINIDO", "ESTOQUE", "DESCRIÇÃO"],
        hide_index=True,
        use_container_width=True,
        key="editor_rancho_final"
    )

    st.markdown("---")
    
    # 3. BOTÕES DE AÇÃO
    col_pdf, col_back = st.columns(2)
    
    with col_pdf:
        if st.button("📄 GERAR PDF COMPLETO", key="btn_pdf_lista"):
            try:
                pdf = FPDF(orientation='L', unit='mm', format='A4') # 'L' para modo Paisagem (cabe mais colunas)
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                
                # Título
                pdf.cell(0, 10, f"Zion Tecnologia - Checklist de Rancho", ln=True, align="C")
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 10, f"Responsavel: {st.session_state.cozinheiro}", ln=True, align="C")
                pdf.ln(5)

                # Cabeçalho da Tabela no PDF
                pdf.set_font("Arial", "B", 8)
                pdf.set_fill_color(255, 140, 0) # Laranja Zion
                pdf.cell(20, 10, "CODIGO", 1, 0, "C", True)
                pdf.cell(45, 10, "PROTEINA", 1, 0, "C", True)
                pdf.cell(20, 10, "TIPO", 1, 0, "C", True)
                pdf.cell(20, 10, "UNID.", 1, 0, "C", True)
                pdf.cell(25, 10, "PREDEF.", 1, 0, "C", True)
                pdf.cell(25, 10, "ESTOQUE", 1, 0, "C", True)
                pdf.cell(40, 10, "DESCRICAO", 1, 0, "C", True)
                pdf.cell(25, 10, "CONFIRMA", 1, 1, "C", True)

                # Linhas da Tabela (Onde o PDF era preenchido)
                pdf.set_font("Arial", "", 8)
                for i in range(len(df_editado)):
                    pdf.cell(20, 8, str(df_editado.iloc[i]["CÓDIGO"]), 1)
                    pdf.cell(45, 8, str(df_editado.iloc[i]["PROTEÍNA"]), 1)
                    pdf.cell(20, 8, str(df_editado.iloc[i]["TIPO"]), 1)
                    pdf.cell(20, 8, str(df_editado.iloc[i]["UNID. MEDIDA"]), 1, 0, "C")
                    pdf.cell(25, 8, str(df_editado.iloc[i]["PREDEFINIDO"]), 1, 0, "C")
                    pdf.cell(25, 8, str(df_editado.iloc[i]["ESTOQUE"]), 1, 0, "C")
                    pdf.cell(40, 8, str(df_editado.iloc[i]["DESCRIÇÃO"]), 1)
                    pdf.cell(25, 8, str(df_editado.iloc[i]["CONFIRMA"]), 1, 1, "C")

                # Preparar Download
                pdf_output = pdf.output(dest='S').encode('latin-1')
                st.download_button(
                    label="📥 BAIXAR RELATORIO PDF",
                    data=pdf_output,
                    file_name=f"Relatorio_Rancho_{st.session_state.cozinheiro}.pdf",
                    mime="application/pdf"
                )
                st.success("PDF gerado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}")

    with col_back:
        if st.button("⬅️ VOLTAR AO MENU", key="btn_voltar_menu_lista"):
            st.session_state.pagina = "menu"
            st.rerun()
