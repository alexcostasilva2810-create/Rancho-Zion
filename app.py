import streamlit as st
import pandas as pd
import requests
import os
from fpdf import FPDF
import unicodedata
from datetime import datetime

# =================================================================
# BLOCO 1: CONFIGURAÇÕES E ESTADO DA SESSÃO
# =================================================================
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state:
    st.session_state.cozinheiro = ""
if 'navio' not in st.session_state:
    st.session_state.navio = ""

COLUNAS_PADRAO = ["ITEM", "DESCRIÇÃO", "TIPO", "UNID MED", "PREDEFINIDO", "CONFIRMA"]

if 'df_lista' not in st.session_state:
    st.session_state.df_lista = pd.DataFrame(columns=COLUNAS_PADRAO)

USUARIOS = {
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "NAVIO 03": {"nome": "Carlos", "senha": "456"}
}

# =================================================================
# BLOCO 2: CONEXÃO COM NOTION (ORDEM CORRETA)
# =================================================================
def carregar_dados_do_notion():
    NOTION_TOKEN = "ntn_jZ6353375938j9kJFqKWjD0N4ONt1rwP515tsIMwxtucHa"
    DATABASE_ID = "2e3025de7b79803abe0efde74f87a2e1"
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            results = response.json().get("results", [])
            dados_notion = []
            for page in results:
                p = page.get("properties", {})
                dados_notion.append({
                    "ITEM": p.get("ITEM", {}).get("title", [{}])[0].get("plain_text", ""),
                    "DESCRIÇÃO": p.get("DESCRIÇÃO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "TIPO": p.get("TIPO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "UNID MED": p.get("UNID MED", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "PREDEFINIDO": p.get("PREDEFINIDO", {}).get("number", 0),
                    "CONFIRMA": 0
                })
            df = pd.DataFrame(dados_notion)
            # Ordenação numérica para garantir sequência 1, 2, 3...
            df['ITEM'] = pd.to_numeric(df['ITEM'], errors='coerce')
            return df.sort_values(by='ITEM').reset_index(drop=True)
        return st.session_state.df_lista
    except:
        return st.session_state.df_lista

# =================================================================
# BLOCO 3: ESTILO VISUAL
# =================================================================
st.markdown("""
    <style>
    .stApp { background-color: #4169E1 !important; }
    h1, h2, h3, p, label { color: white !important; }
    div.stButton > button {
        background-color: #FF8C00 !important;
        color: black !important;
        font-weight: 900 !important;
        border-radius: 10px !important;
        height: 3.5em;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# BLOCO 4: LÓGICA DE NAVEGAÇÃO
# =================================================================

if st.session_state.pagina == "home":
    st.markdown("<h1 style='text-align: center;'>Zion Rancho App</h1>", unsafe_allow_html=True)
    if os.path.exists("APPRANCHO.png"):
        st.image("APPRANCHO.png", use_container_width=True)
    if st.button("INICIAR ACESSO"):
        st.session_state.pagina = "login"
        st.rerun()

elif st.session_state.pagina == "login":
    st.title("🔐 Acesso")
    navio_sel = st.selectbox("Embarcação", [""] + list(USUARIOS.keys()))
    senha = st.text_input("Senha", type="password")
    if st.button("ENTRAR"):
        if navio_sel in USUARIOS and USUARIOS[navio_sel]["senha"] == senha:
            st.session_state.cozinheiro = USUARIOS[navio_sel]["nome"]
            st.session_state.navio = navio_sel
            st.session_state.pagina = "menu"
            st.rerun()

elif st.session_state.pagina == "menu":
    st.title(f"Olá, {st.session_state.cozinheiro}!")
    if st.button("🛒 LISTA DE RANCHO"):
        st.session_state.pagina = "lista"
        st.rerun()
    if st.button("👨‍✈️ TRIPULAÇÃO"):
        st.session_state.pagina = "tripulacao"
        st.rerun()
    if st.button("🚪 SAIR DO SISTEMA"):
        st.session_state.pagina = "home"
        st.rerun()

elif st.session_state.pagina == "lista":
    st.title(f"📋 Rancho - {st.session_state.navio}")
    
    if st.button("🔄 ATUALIZAR DADOS DO NOTION"):
        st.session_state.df_lista = carregar_dados_do_notion()
        st.rerun()

    df_editado = st.data_editor(
        st.session_state.df_lista,
        column_config={
            "ITEM": st.column_config.TextColumn("ITEM", disabled=True),
            "DESCRIÇÃO": st.column_config.TextColumn("DESCRIÇÃO", disabled=True),
            "TIPO": st.column_config.TextColumn("TIPO", disabled=True),
            "UNID MED": st.column_config.TextColumn("UNID.", disabled=True),
            "PREDEFINIDO": st.column_config.NumberColumn("ESTOQUE", disabled=True),
            "CONFIRMA": st.column_config.NumberColumn("CONFIRMA", min_value=0),
        },
        hide_index=True, use_container_width=True
    )

    st.markdown("---")
    
    # PDF PROFISSIONAL COM DATA, HORA E LOGO
    if st.button("📄 GERAR PDF"):
        def blindar_texto(texto):
            txt = str(texto) if texto else ""
            return unicodedata.normalize('NFKD', txt).encode('ascii', 'ignore').decode('ascii')

        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        class PDF(FPDF):
            def header(self):
                if os.path.exists("APPRANCHO.png"): 
                    self.image("APPRANCHO.png", 10, 8, 20)
                self.set_font("Arial", "B", 12)
                self.set_xy(35, 12)
                # Cabeçalho atualizado: Navio e Responsável
                self.cell(0, 10, blindar_texto(f"Checklist de Rancho - {st.session_state.navio} - Responsavel: {st.session_state.cozinheiro}"), 0, 1)
                self.ln(10)
                # Cabeçalho da Tabela
                self.set_font("Arial", "B", 8)
                self.set_fill_color(0, 102, 204) # Azul Zion
                self.set_text_color(255, 255, 255)
                self.cell(12, 10, "ITEM", 1, 0, "C", True)
                self.cell(70, 10, "DESCRICAO", 1, 0, "C", True)
                self.cell(45, 10, "TIPO", 1, 0, "C", True)
                self.cell(15, 10, "UNID", 1, 0, "C", True)
                self.cell(18, 10, "ESTOQUE", 1, 0, "C", True)
                self.cell(30, 10, "CONF.", 1, 1, "C", True)
                self.set_text_color(0, 0, 0)

            def footer(self):
                self.set_y(-15)
                self.set_font("Arial", "I", 7)
                self.set_text_color(128, 128, 128)
                # Rodapé com Data e Hora
                texto_rodape = f"Gerado em: {agora} | Zion Rancho App | Pagina {self.page_no()}"
                self.cell(0, 10, blindar_texto(texto_rodape), 0, 0, "C")

        try:
            pdf = PDF(orientation='P', unit='mm', format='A4')
            pdf.set_auto_page_break(auto=True, margin=20)
            pdf.add_page()
            pdf.set_font("Arial", "", 8)

            for _, row in df_editado.iterrows():
                t_desc = blindar_texto(row["DESCRIÇÃO"])
                t_tipo = blindar_texto(row["TIPO"])
                alt_l = 6
                # Cálculo de altura para evitar quebras de página desalinhadas
                l_desc = (pdf.get_string_width(t_desc) / 70) + 1
                l_tipo = (pdf.get_string_width(t_tipo) / 45) + 1
                h = max(int(l_desc), int(l_tipo)) * alt_l
                
                if pdf.get_y() + h > 270: pdf.add_page()

                x, y = pdf.get_x(), pdf.get_y()
                pdf.cell(12, h, str(int(row["ITEM"])), 1, 0, "C")
                pdf.multi_cell(70, alt_l, t_desc, 1, "L")
                pdf.set_xy(x + 82, y)
                pdf.multi_cell(45, alt_l, t_tipo, 1, "C")
                pdf.set_xy(x + 127, y)
                pdf.cell(15, h, blindar_texto(row["UNID MED"]), 1, 0, "C")
                pdf.cell(18, h, str(row["PREDEFINIDO"]), 1, 0, "C")
                pdf.cell(30, h, str(row["CONFIRMA"]), 1, 1, "C")

            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            st.download_button("📥 BAIXAR PDF", data=pdf_bytes, file_name=f"Rancho_{st.session_state.navio}.pdf", mime="application/pdf")
            st.success("✅ Sua demanda esta pronta favor mandar no grupo de WhatsApp de rancho!")
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {e}")

    # --- BOTÕES DE NAVEGAÇÃO ---
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ VOLTAR AO MENU"):
            st.session_state.pagina = "menu"
            st.rerun()
    with col2:
        if st.button("🚪 SAIR DO SISTEMA"):
            st.session_state.pagina = "home"
            st.rerun()

# =================================================================
# BLOCO 5: TELA DE TRIPULAÇÃO E MANIFESTO DE VIAGEM
# =================================================================

elif st.session_state.pagina == "tripulacao":
    from datetime import datetime
    import unicodedata
    from fpdf import FPDF

    st.title("👨‍✈️ Controle de Tripulação e Viagem")
    st.write("Preencha os dados abaixo para gerar o manifesto.")

    # O 'clear_on_submit=True' garante que os campos limpem após clicar no botão
    with st.form("form_tripulacao", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # Responsável fixo pelo login
            st.text_input("Responsável", value=st.session_state.cozinheiro, disabled=True)
            empurrador = st.text_input("Empurrador / Embarcação", placeholder="Digite o nome da embarcação")
            tripulantes = st.number_input("N° de Tripulantes", min_value=1, step=1)
        
        with col2:
            origem = st.text_input("Origem", placeholder="Cidade de saída")
            destino = st.text_input("Destino", placeholder="Cidade de chegada")
            data_viagem = st.date_input("Data da Viagem", value=datetime.now())

        # Botão que processa tudo
        submit = st.form_submit_button("💾 SALVAR E GERAR PDF")

    if submit:
        if not empurrador or not origem or not destino:
            st.warning("⚠️ Preencha todos os campos (Empurrador, Origem e Destino) antes de gerar o PDF.")
        else:
            def blindar_texto(texto):
                txt = str(texto) if texto else ""
                return unicodedata.normalize('NFKD', txt).encode('ascii', 'ignore').decode('ascii')

            try:
                # Criando o PDF do Manifesto
                pdf = FPDF(orientation='P', unit='mm', format='A4')
                pdf.add_page()
                
                # Cabeçalho com Logo
                if os.path.exists("APPRANCHO.png"):
                    pdf.image("APPRANCHO.png", 10, 8, 25)
                
                pdf.set_font("Arial", "B", 16)
                pdf.set_xy(40, 15)
                pdf.cell(0, 10, "MANIFESTO DE VIAGEM E TRIPULACAO", 0, 1, "C")
                
                pdf.ln(20)
                pdf.set_draw_color(0, 102, 204) # Azul Zion
                pdf.set_line_width(0.8)
                pdf.line(10, 35, 200, 35) # Linha divisória
                
                # Dados do Manifesto
                pdf.set_font("Arial", "B", 12)
                pdf.ln(10)
                
                # Linha 1
                pdf.cell(100, 10, blindar_texto(f"RESPONSAVEL: {st.session_state.cozinheiro}"), 0, 0)
                pdf.cell(90, 10, blindar_texto(f"DATA: {data_viagem.strftime('%d/%m/%Y')}"), 0, 1)
                
                # Linha 2
                pdf.ln(5)
                pdf.cell(100, 10, blindar_texto(f"EMPURRADOR: {empurrador}"), 0, 0)
                pdf.cell(90, 10, blindar_texto(f"N DE TRIPULANTES: {tripulantes}"), 0, 1)
                
                # Linha 3 (Origem e Destino)
                pdf.ln(5)
                pdf.set_fill_color(240, 240, 240)
                pdf.cell(190, 12, blindar_texto(f"ROTA: {origem}  >>>  {destino}"), 1, 1, "C", True)
                
                # Rodapé com timestamp
                agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                pdf.set_y(-20)
                pdf.set_font("Arial", "I", 8)
                pdf.set_text_color(150, 150, 150)
                pdf.cell(0, 10, blindar_texto(f"Documento gerado em: {agora} | Zion Rancho App"), 0, 0, "C")

                pdf_bytes = pdf.output(dest='S').encode('latin-1')
                
                st.success("✅ Manifesto salvo com sucesso! Clique abaixo para baixar.")
                st.download_button(
                    label="📥 BAIXAR MANIFESTO PDF",
                    data=pdf_bytes,
                    file_name=f"Manifesto_{empurrador}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Erro ao gerar o PDF do manifesto: {e}")

    # Botão de retorno
    st.markdown("---")
    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"
        st.rerun()

elif st.session_state.pagina == "tripulacao":
    st.title("👨‍✈️ Tripulação")
    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"
        st.rerun()
