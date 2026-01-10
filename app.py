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
# BLOCO 6: TELA DA TABELA (LISTA DE RANCHO) - VERSÃO FINALÍSSIMA
# =================================================================
elif st.session_state.pagina == "lista":
    # 1. PEGAR NOME DO NAVIO DO LOGIN
    unidade_navio = st.session_state.get('navio', 'UNIDADE NÃO IDENTIFICADA').upper()
    
    st.markdown(f"## 📋 Tabela de Rancho - {unidade_navio}")
    st.write(f"Responsável Logado: **{st.session_state.cozinheiro}**")

    # 2. DEFINIR AS 8 COLUNAS EXATAS DO SEU MODELO (CUMARU)
    # Colunas: ID, CODIGO, PROTEINA, TIPO, UNIDADE, ESTOQUE, PREDEF, CONFIRMA
    if 'df_lista' not in st.session_state:
        dados_modelo = {
            "ID": ["1", "2", "3", "4"],
            "CÓDIGO": ["PR01", "PR02", "PR03", "PR04"],
            "PROTEÍNA": ["Carne Moída", "Alcatra", "Pá ou Agulha", "Charque"],
            "TIPO": ["PROTEÍNAS", "PROTEÍNAS", "PROTEÍNAS", "PROTEÍNAS"],
            "UNID. MED": ["kg", "kg", "kg", "kg"],
            "ESTOQUE": [0.0, 0.0, 0.0, 0.0],
            "PREDEFINIDO": [8.0, 10.0, 8.0, 7.0],
            "CONFIRMA": [0.0, 0.0, 0.0, 0.0]
        }
        st.session_state.df_lista = pd.DataFrame(dados_modelo)

    # 3. EXIBIR A TABELA (Travando tudo, exceto a coluna CONFIRMA)
    df_editavel = st.data_editor(
        st.session_state.df_lista,
        column_config={
            "ID": st.column_config.TextColumn(disabled=True),
            "CÓDIGO": st.column_config.TextColumn(disabled=True),
            "PROTEÍNA": st.column_config.TextColumn(disabled=True),
            "TIPO": st.column_config.TextColumn(disabled=True),
            "UNID. MED": st.column_config.TextColumn(disabled=True),
            "ESTOQUE": st.column_config.NumberColumn(disabled=True),
            "PREDEFINIDO": st.column_config.NumberColumn("PREDEF.", disabled=True),
            "CONFIRMA": st.column_config.NumberColumn("CONFIRMA (Qtd)", min_value=0.0),
        },
        hide_index=True,
        use_container_width=True,
        key="editor_final_real"
    )

    st.markdown("---")
    
    col_acao, col_voltar = st.columns(2)
    
    with col_acao:
        # 4. BOTÃO DE SALVAR E GERAR PDF (Lógica para não sair em branco)
        if st.button("💾 SALVAR E GERAR PDF"):
            try:
                # Criar o PDF em modo PAISAGEM (L) para caber as 8 colunas
                pdf = FPDF(orientation='L', unit='mm', format='A4')
                pdf.add_page()
                
                # Título com o nome do Navio
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, f"CHECKLIST DE RANCHO - {unidade_navio}", ln=True, align="C")
                pdf.set_font("Arial", "", 12)
                pdf.cell(0, 10, f"Responsavel: {st.session_state.cozinheiro}", ln=True, align="C")
                pdf.ln(5)

                # Cabeçalho da Tabela no PDF
                pdf.set_font("Arial", "B", 8)
                pdf.set_fill_color(255, 140, 0) # Laranja Zion
                
                # Larguras calculadas para A4 Paisagem (Total ~270mm)
                larguras = [10, 25, 60, 35, 25, 25, 25, 30]
                headers = ["ID", "CODIGO", "PROTEINA", "TIPO", "UNID", "ESTOQUE", "PREDEF", "CONFIRMA"]
                
                for i in range(len(headers)):
                    pdf.cell(larguras[i], 10, headers[i], 1, 0, "C", True)
                pdf.ln()

                # 5. DESENHAR AS LINHAS NO PDF (Pegando os dados da tela)
                pdf.set_font("Arial", "", 8)
                for index, row in df_editavel.iterrows():
                    pdf.cell(larguras[0], 8, str(row["ID"]), 1, 0, "C")
                    pdf.cell(larguras[1], 8, str(row["CÓDIGO"]), 1, 0, "C")
                    pdf.cell(larguras[2], 8, str(row["PROTEÍNA"]), 1)
                    pdf.cell(larguras[3], 8, str(row["TIPO"]), 1, 0, "C")
                    pdf.cell(larguras[4], 8, str(row["UNID. MED"]), 1, 0, "C")
                    pdf.cell(larguras[5], 8, str(row["ESTOQUE"]), 1, 0, "C")
                    pdf.cell(larguras[6], 8, str(row["PREDEFINIDO"]), 1, 0, "C")
                    
                    # Destacar a quantidade confirmada em Negrito
                    pdf.set_font("Arial", "B", 9)
                    pdf.cell(larguras[7], 8, str(row["CONFIRMA"]), 1, 1, "C")
                    pdf.set_font("Arial", "", 8)

                # Gerar saída binária
                pdf_bytes = pdf.output(dest='S').encode('latin-1')
                
                st.success(f"Dados salvos para o {unidade_navio}!")
                st.download_button(
                    label="📥 CLIQUE AQUI PARA BAIXAR O PDF",
                    data=pdf_bytes,
                    file_name=f"Rancho_{unidade_navio}.pdf",
                    mime="application/pdf",
                    key="download_final_pdf"
                )
            except Exception as e:
                st.error(f"Erro ao gerar: {e}")

    with col_voltar:
        if st.button("⬅️ VOLTAR AO MENU"):
            st.session_state.pagina = "menu"
            st.rerun()
