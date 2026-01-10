import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime
import unicodedata
from fpdf import FPDF
from PIL import Image
import os
import requests

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
# BLOCO 5: TELA DE TRIPULAÇÃO (VERSÃO FINAL - SEM SOBREPOSIÇÃO)
# =================================================================

elif st.session_state.pagina == "tripulacao":
    st.title("👨‍✈️ Declaração de Reabastecimento")
    
    # Função para capturar onde o cozinheiro está (Totalmente em Português)
    def obter_localizacao_simples():
        try:
            response = requests.get('https://ipapi.co/json/', timeout=3)
            dados = response.json()
            cidade = dados.get('city', 'Cidade desconhecida')
            estado = dados.get('region', 'Estado desconhecido')
            # Se o servidor indicar EUA (Oregon/The Dalles), avisamos que é via satélite
            if dados.get('country') != 'BR':
                return f"{cidade} (Conexão via Satélite)"
            return f"{cidade}/{estado}"
        except:
            return "Localização não identificada"

    if 'pdf_disponivel' not in st.session_state:
        st.session_state.pdf_disponivel = None

    st.subheader("Configuração de Escolta")
    tem_escolta = st.radio("Terá Escolta Armada?", ("Não", "Sim"), horizontal=True)

    if tem_escolta == "Sim":
        dias_nauticos = 12
        st.warning("⚠️ Seu rancho tem que durar por 12 dias.")
    else:
        dias_nauticos = 15
        st.info("ℹ️ O rancho tem que durar até 15 dias.")

    with st.form("form_tripulacao", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Responsável", value=st.session_state.cozinheiro, disabled=True)
            st.text_input("Empurrador", value=st.session_state.navio, disabled=True)
            data_ult_br = datetime.now().strftime("%d/%m/%Y")
            data_ultimo_rancho = st.text_input("Data do Último Rancho", value=data_ult_br)
        
        with col2:
            # Correção da data para formato brasileiro na tela
            data_hoje_br = datetime.now().strftime("%d/%m/%Y")
            data_input_br = st.text_input("Data de Início deste Rancho", value=data_hoje_br)
            origem = st.text_input("De onde está saindo?", placeholder="Ex: Belém/PA")
            destino = st.text_input("Para onde vai?", placeholder="Ex: Santarém/PA")

        st.markdown("---")
        consideracoes = st.text_area("Observações (Itens faltantes ou extras):", height=80)

        st.subheader("✍️ Assinatura (Use o dedo na tela)")
        canvas_result = st_canvas(
            stroke_width=3, stroke_color="#000000", background_color="#eeeeee",
            height=120, drawing_mode="freedraw", key="canvas_v_final"
        )

        btn_gerar = st.form_submit_button("💾 SALVAR E GERAR DOCUMENTO", use_container_width=True)

    if btn_gerar:
        if not origem or not destino:
            st.error("⚠️ Por favor, preencha a Origem e o Destino!")
        elif canvas_result.image_data is None:
            st.error("⚠️ Por favor, faça a assinatura antes de salvar!")
        else:
            local_real = obter_localizacao_simples()
            
            def blindar(t):
                return unicodedata.normalize('NFKD', str(t)).encode('ascii', 'ignore').decode('ascii')

            try:
                pdf = FPDF()
                pdf.add_page()
                
                # CABEÇALHO CORRIGIDO: LOGO E TÍTULO LADO A LADO SEM SOBREPOR
                if os.path.exists("APPRANCHO.png"):
                    pdf.image("APPRANCHO.png", 10, 10, 35) # Logo Zion
                
                pdf.set_font("Arial", "B", 14)
                pdf.set_xy(50, 20) # Começa o texto bem depois da logo
                pdf.cell(0, 10, blindar(f"DECLARACAO DE RANCHO - {st.session_state.navio}"), 0, 1, "L")
                
                pdf.ln(20) # Espaço extra para garantir que o texto não suba na logo
                pdf.set_font("Arial", "", 12)
                
                corpo = (f"A provisao de rancho a ser reabastecida destina-se a cobrir as necessidades "
                         f"nutricionais da tripulacao por um periodo de {dias_nauticos} dias nauticos "
                         f"a partir de {data_input_br}. O ultimo rancho foi recebido em {data_ultimo_rancho}.")
                pdf.multi_cell(0, 8, blindar(corpo))
                
                pdf.ln(5)
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, blindar(f"Saindo de: {origem}"), 0, 1)
                pdf.cell(0, 10, blindar(f"Indo para: {destino}"), 0, 1)
                
                if consideracoes:
                    pdf.ln(5)
                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 10, "OBSERVACOES:", 0, 1)
                    pdf.set_font("Arial", "", 11)
                    pdf.multi_cell(0, 7, blindar(consideracoes), 1, "L")

                # Assinatura Digital
                img_data = canvas_result.image_data.astype('uint8')
                Image.fromarray(img_data, 'RGBA').save("assinatura_temp.png")
                pdf.image("assinatura_temp.png", x=75, y=pdf.get_y()+10, w=60)
                
                pdf.ln(30)
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, blindar(f"Responsavel: {st.session_state.cozinheiro}"), 0, 1, "C")

                # RODAPÉ DE SEGURANÇA (TOTALMENTE EM PORTUGUÊS)
                data_registro = datetime.now().strftime("%d/%m/%Y as %H:%M")
                pdf.set_y(-25)
                pdf.set_font("Arial", "I", 8)
                pdf.set_text_color(100, 100, 100)
                texto_seguranca = (f"Registro Digital realizado em {data_registro}\n"
                                   f"Local da Assinatura: {local_real}")
                pdf.multi_cell(0, 5, blindar(texto_seguranca), 0, "C")

                st.session_state.pdf_disponivel = pdf.output(dest='S').encode('latin-1')
                st.success("✅ Documento gerado com sucesso!")

            except Exception as e:
                st.error(f"Erro ao criar o documento: {e}")

    if st.session_state.pdf_disponivel:
        st.download_button(
            label="📥 CLIQUE AQUI PARA BAIXAR A CARTA",
            data=st.session_state.pdf_disponivel,
            file_name=f"Declaracao_{st.session_state.navio}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    st.markdown("---")
    if st.button("⬅️ VOLTAR AO MENU", use_container_width=True):
        st.session_state.pdf_disponivel = None
        st.session_state.pagina = "menu"
        st.rerun()
