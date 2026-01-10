import streamlit as st
import pandas as pd
from fpdf import FPDF
import io  # Para melhor manipulação de bytes

# =================================================================
# BLOCO 1: CONFIGURAÇÕES, ESTADOS E ESTILO (CSS)
# =================================================================
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state:
    st.session_state.cozinheiro = ""
if 'navio' not in st.session_state:  # ✅ CORRIGIDO: Armazenar navio
    st.session_state.navio = ""

USUARIOS = {
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "NAVIO 03": {"nome": "Carlos", "senha": "456"}
}

# Estilos CSS (mantido igual)
st.markdown("""
    <style>
    .stApp { background-color: #4169E1 !important; }
    h1, h2, h3, p, label { color: white !important; }
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
    div.stButton > button:hover { background-color: #FFA500 !important; }
    input { color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# BLOCO 2: TELA INICIAL (mantido igual)
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
# BLOCO 3: LOGIN (CORRIGIDO - armazena navio)
# =================================================================
elif st.session_state.pagina == "login":
    st.markdown("""
        <style>
        .stApp { background: linear-gradient(rgba(65, 105, 225, 0.8), rgba(65, 105, 225, 0.8)), 
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
            st.session_state.navio = navio_sel  # ✅ SALVA O NAVIO
            st.session_state.pagina = "menu"
            st.rerun()
        else:
            st.error("Credenciais inválidas.")

    if st.button("⬅️ VOLTAR", key="btn_voltar_home"):
        st.session_state.pagina = "home"
        st.rerun()

# =================================================================
# BLOCO 4: MENU (mantido igual)
# =================================================================
elif st.session_state.pagina == "menu":
    st.markdown(f"## Seja Bem-vindo, {st.session_state.cozinheiro}!")
    st.write(f"**Navio:** {st.session_state.navio}")
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

    if st.button("SAIR DO SISTEMA", key="btn_logout"):
        # Limpa todas as sessões
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.pagina = "home"
        st.rerun()

# =================================================================
# BLOCO 5: LISTA DE RANCHO (ÚNICO - VERSÃO FINAL CORRIGIDA)
# =================================================================
elif st.session_state.pagina == "lista":
    unidade_navio = st.session_state.navio.upper()  # ✅ AGORA FUNCIONA
    
    st.markdown(f"## 📋 Tabela de Rancho - {unidade_navio}")
    st.write(f"Responsável Logado: **{st.session_state.cozinheiro}**")

    # Inicializa dados se não existir
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

    # Editor de tabela
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
        if st.button("💾 SALVAR E GERAR PDF"):
            try:
                # ✅ PDF MELHORADO COM UTF-8 E TOTALS
                class PDF(FPDF):
                    def header(self):
                        self.set_font('Arial', 'B', 16)
                        self.cell(0, 10, f"CHECKLIST DE RANCHO - {unidade_navio}", 0, 1, 'C')
                        self.set_font('Arial', '', 12)
                        self.cell(0, 10, f"Responsável: {st.session_state.cozinheiro}", 0, 1, 'C')
                        self.ln(5)

                    def footer(self):
                        self.set_y(-15)
                        self.set_font('Arial', 'I', 8)
                        self.cell(0, 10, f'Gerado em {pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")}', 0, 0, 'C')

                pdf = PDF(orientation='L', unit='mm', format='A4')
                pdf.add_page()
                
                # Cabeçalho da tabela
                pdf.set_font("Arial", "B", 9)
                pdf.set_fill_color(255, 140, 0)
                larguras = [12, 28, 55, 32, 22, 22, 25, 28, 35]  # Ajustado
                headers = ["ID", "CÓDIGO", "PROTEÍNA", "TIPO", "UNID", "ESTOQUE", "PREDEF", "CONFIRMA", "TOTAL"]
                
                for i, header in enumerate(headers):
                    pdf.cell(larguras[i], 10, header, 1, 0, "C", True)
                pdf.ln()

                # Dados das linhas + cálculo de total
                pdf.set_font("Arial", "", 8)
                total_geral = 0
                for index, row in df_editavel.iterrows():
                    total_item = float(row["CONFIRMA"]) * float(row["PREDEFINIDO"]) if float(row["CONFIRMA"]) > 0 else 0
                    total_geral += total_item
                    
                    pdf.cell(larguras[0], 8, str(row["ID"]), 1, 0, "C")
                    pdf.cell(larguras[1], 8, str(row["CÓDIGO"]), 1, 0, "C")
                    pdf.cell(larguras[2], 8, str(row["PROTEÍNA"])[:25], 1, 0, "L")  # Limitar texto
                    pdf.cell(larguras[3], 8, str(row["TIPO"]), 1, 0, "C")
                    pdf.cell(larguras[4], 8, str(row["UNID. MED"]), 1, 0, "C")
                    pdf.cell(larguras[5], 8, f"{row['ESTOQUE']:.1f}", 1, 0, "C")
                    pdf.cell(larguras[6], 8, f"{row['PREDEFINIDO']:.1f}", 1, 0, "C")
                    pdf.set_font("Arial", "B", 9)
                    pdf.cell(larguras[7], 8, f"{row['CONFIRMA']:.1f}", 1, 0, "C")
                    pdf.set_font("Arial", "", 8)
                    pdf.cell(larguras[8], 8, f"{total_item:.1f}", 1, 1, "C")

                # Total geral
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, f"TOTAL GERAL: {total_geral:.1f} UNIDADES", 1, 1, "C")
                
                # ✅ SAÍDA EM BYTES CORRETA
                pdf_bytes = pdf.output(dest='S').encode('latin-1', errors='ignore')
                
                st.session_state.df_lista = df_editavel  # Salva dados editados
                st.success(f"✅ Dados salvos para {unidade_navio}! Total: {total_geral:.1f}")
                
                st.download_button(
                    label="📥 BAIXAR PDF AGORA",
                    data=pdf_bytes,
                    file_name=f"Rancho_{unidade_navio}_{pd.Timestamp.now().strftime('%d%m%Y_%H%M')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
                st.exception(e)

    with col_voltar:
        if st.button("⬅️ VOLTAR AO MENU"):
            st.session_state.pagina = "menu"
            st.rerun()
