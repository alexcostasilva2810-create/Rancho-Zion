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
# BLOCO 6: TELA DA TABELA (LISTA DE RANCHO) - SALVAR E GERAR PDF
# =================================================================
elif st.session_state.pagina == "lista":
    st.markdown("## 📋 Tabela de Rancho")
    st.write(f"Responsável Logado: **{st.session_state.cozinheiro}**")

    # 1. BASE DE DADOS COM TODAS AS COLUNAS (CÓDIGO, PROTEÍNA, TIPO, UNIDADE, ESTOQUE, DESCRIÇÃO, CONFIRMA)
    if 'df_lista' not in st.session_state:
        dados_fixos = {
            "CÓDIGO": ["PR01", "PR02", "PR03", "PR04"],
            "PROTEÍNA": ["Alcatra", "Sobrecoxa Frango", "Filé de Merluza", "Ovos Brancos"],
            "TIPO": ["Carne", "Aves", "Peixe", "Perecíveis"],
            "UNID. MEDIDA": ["KG", "KG", "KG", "DZ"],
            "PREDEFINIDO": [20.0, 35.0, 15.0, 50.0], 
            "ESTOQUE": [5.0, 2.0, 10.0, 12.0],
            "DESCRIÇÃO": ["Peça inteira", "Bandeja 1kg", "Filé congelado", "Cartela c/ 30"],
            "CONFIRMA": [0.0, 0.0, 0.0, 0.0]
        }
        st.session_state.df_lista = pd.DataFrame(dados_fixos)

    # 2. TABELA INTERATIVA (APENAS 'CONFIRMA' É EDITÁVEL)
    df_final = st.data_editor(
        st.session_state.df_lista,
        column_config={
            "CÓDIGO": st.column_config.TextColumn("CÓDIGO", disabled=True),
            "PROTEÍNA": st.column_config.TextColumn("PROTEÍNA", disabled=True),
            "TIPO": st.column_config.TextColumn("TIPO", disabled=True),
            "UNID. MEDIDA": st.column_config.TextColumn("UNID. MEDIDA", disabled=True),
            "PREDEFINIDO": st.column_config.NumberColumn("PREDEFINIDO", disabled=True),
            "ESTOQUE": st.column_config.NumberColumn("ESTOQUE", disabled=True),
            "DESCRIÇÃO": st.column_config.TextColumn("DESCRIÇÃO", disabled=True),
            "CONFIRMA": st.column_config.NumberColumn("CONFIRMA (Qtd)", min_value=0.0, format="%.2f"),
        },
        hide_index=True,
        use_container_width=True,
        key="editor_rancho_v5"
    )

    st.markdown("---")
    
    col_acao, col_voltar = st.columns(2)
    
    with col_acao:
        # BOTÃO ÚNICO: SALVAR E PROCESSAR PDF
        if st.button("💾 SALVAR E GERAR PDF", key="btn_salvar_pdf"):
            try:
                # Criar o PDF em modo PAISAGEM (L) para caber as 8 colunas
                pdf = FPDF(orientation='L', unit='mm', format='A4')
                pdf.add_page()
                
                # Título e Informações de Cabeçalho
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "ZION TECNOLOGIA - RELATÓRIO DE RANCHO", ln=True, align="C")
                pdf.set_font("Arial", "", 11)
                pdf.cell(0, 8, f"Responsável: {st.session_state.cozinheiro}", ln=True, align="C")
                pdf.ln(5)

                # CABEÇALHO DA TABELA NO PDF (Cores e Títulos)
                pdf.set_font("Arial", "B", 8)
                pdf.set_fill_color(255, 140, 0) # Laranja Zion
                pdf.set_text_color(0, 0, 0)     # Texto Preto
                
                larguras = [20, 45, 25, 20, 25, 25, 75, 25] # Total 260mm
                colunas = ["CÓDIGO", "PROTEÍNA", "TIPO", "UNID.", "PREDEF.", "ESTOQUE", "DESCRIÇÃO", "CONFIRMA"]
                
                for i in range(len(colunas)):
                    pdf.cell(larguras[i], 10, colunas[i], 1, 0, "C", True)
                pdf.ln()

                # LINHAS DA TABELA (DESENHANDO CADA PRODUTO)
                pdf.set_font("Arial", "", 8)
                pdf.set_text_color(0, 0, 0)
                
                for _, row in df_final.iterrows():
                    pdf.cell(larguras[0], 8, str(row["CÓDIGO"]), 1, 0, "C")
                    pdf.cell(larguras[1], 8, str(row["PROTEÍNA"]), 1)
                    pdf.cell(larguras[2], 8, str(row["TIPO"]), 1, 0, "C")
                    pdf.cell(larguras[3], 8, str(row["UNID. MEDIDA"]), 1, 0, "C")
                    pdf.cell(larguras[4], 8, str(row["PREDEFINIDO"]), 1, 0, "C")
                    pdf.cell(larguras[5], 8, str(row["ESTOQUE"]), 1, 0, "C")
                    pdf.cell(larguras[6], 8, str(row["DESCRIÇÃO"]), 1)
                    
                    # Destacar a quantidade confirmada em Negrito
                    pdf.set_font("Arial", "B", 8)
                    pdf.cell(larguras[7], 8, str(row["CONFIRMA"]), 1, 1, "C")
                    pdf.set_font("Arial", "", 8)

                # Transformar em Bytes para Download
                pdf_bytes = pdf.output(dest='S').encode('latin-1')
                
                st.success("✅ Dados salvos e PDF gerado!")
                
                # Exibe o botão de download real logo abaixo após o processamento
                st.download_button(
                    label="📥 CLIQUE AQUI PARA BAIXAR O ARQUIVO",
                    data=pdf_bytes,
                    file_name=f"Relatorio_Rancho_{st.session_state.cozinheiro}.pdf",
                    mime="application/pdf",
                    key="download_final"
                )
                
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

    with col_voltar:
        if st.button("⬅️ VOLTAR AO MENU", key="btn_voltar"):
            st.session_state.pagina = "menu"
            st.rerun()
