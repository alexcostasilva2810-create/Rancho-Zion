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
# BLOCO 4: LÓGICA DE NAVEGAÇÃO (TELA INICIAL DEFINITIVA)
# =================================================================

if st.session_state.pagina == "lar":
    # 1. Título centralizado
    st.markdown("<h1 style='text-align: center;'>Aplicativo Zion Rancho</h1>", unsafe_allow_html=True)
    
    # 2. Caminho da Imagem (Exatamente como está na sua biblioteca)
    # IMPORTANTE: Se o navegador traduzir para 'SION.jpg', corrija para 'ZION.jpg'
    imagem_robot = "ZION.jpg" 

    if os.path.exists(imagem_robot):
        st.image(imagem_robot, use_container_width=True)
    else:
        # Caso ocorra algum erro de carregamento, ele avisa aqui
        st.error(f"Arquivo '{imagem_robot}' não encontrado. Verifique se o nome está correto.")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 3. Botão de Acesso (Ficará logo abaixo da imagem)
    if st.button("🚀 INICIAR ACESSO", use_container_width=True):
        st.session_state.pagina = "Conecte-se"
        st.rerun()
# =================================================================
# BLOCO 5: TELA DE TRIPULAÇÃO (VERSÃO AJUSTADA E PROFISSIONAL)
# =================================================================

elif st.session_state.pagina == "tripulacao":
    st.title("👨‍✈️ Declaração de Reabastecimento")
    
    def obter_localizacao_simples():
        try:
            response = requests.get('https://ipapi.co/json/', timeout=3)
            dados = response.json()
            cidade = dados.get('city', 'Cidade desconhecida')
            estado = dados.get('region', 'Estado desconhecido')
            if dados.get('country') != 'BR':
                return f"{cidade} (Conexão via Satélite)"
            return f"{cidade}/{estado}"
        except:
            return "Localização não identificada"

    if 'pdf_disponivel' not in st.session_state:
        st.session_state.pdf_disponivel = None

    with st.form("form_tripulacao", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Responsável", value=st.session_state.cozinheiro, disabled=True)
            st.text_input("Empurrador", value=st.session_state.navio, disabled=True)
            data_ult_br = datetime.now().strftime("%d/%m/%Y")
            st.text_input("Data do Último Rancho", value=data_ult_br)
        
        with col2:
            data_hoje_br = datetime.now().strftime("%d/%m/%Y")
            data_input_br = st.text_input("Data de Início", value=data_hoje_br)
            origem = st.text_input("Origem", placeholder="Ex: Belém/PA")
            destino = st.text_input("Destino", placeholder="Ex: Santarém/PA")

        st.markdown("---")
        # Campo de Observação livre de retângulos no PDF
        consideracoes = st.text_area("Observações (Materiais de limpeza, água ou pessoal extra):", height=80)

        st.subheader("✍️ Assinatura (Use o dedo na tela)")
        canvas_result = st_canvas(
            stroke_width=3, stroke_color="#000000", background_color="#eeeeee",
            height=110, drawing_mode="freedraw", key="canvas_v_ajustada"
        )

        btn_gerar = st.form_submit_button("💾 SALVAR E GERAR DOCUMENTO", use_container_width=True)

    if btn_gerar:
        if not origem or not destino:
            st.error("⚠️ Por favor, preencha a Origem e o Destino!")
        elif canvas_result.image_data is None:
            st.error("⚠️ Por favor, realize a assinatura!")
        else:
            local_real = obter_localizacao_simples()
            
            def blindar(t):
                return unicodedata.normalize('NFKD', str(t)).encode('ascii', 'ignore').decode('ascii')

            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_auto_page_break(auto=True, margin=15)
                
                # Cabeçalho: Logo e Título com espaçamento fixo para não sobrepor
                if os.path.exists("APPRANCHO.png"):
                    pdf.image("APPRANCHO.png", 10, 10, 32)
                
                pdf.set_font("Arial", "B", 14)
                pdf.set_xy(45, 22)
                pdf.cell(0, 10, blindar(f"DECLARAÇÃO DE RANCHO - {st.session_state.navio}"), 0, 1, "L")
                
                pdf.ln(18) 
                pdf.set_font("Arial", "", 12)
                
                # Texto com ortografia corrigida
                corpo = (f"A provisão de rancho a ser reabastecida destina-se a cobrir as necessidades "
                         f"nutricionais da tripulação por um período de 15 dias náuticos, a partir de {data_input_br}. "
                         f"O último suprimento foi recebido em {data_ult_br}.")
                pdf.multi_cell(0, 8, blindar(corpo))
                
                pdf.ln(4)
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 8, blindar(f"Origem: {origem}"), 0, 1) # Preferência por 'Origem'
                pdf.cell(0, 8, blindar(f"Destino: {destino}"), 0, 1) # Preferência por 'Destino'
                
                if consideracoes:
                    pdf.ln(4)
                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 8, "OBSERVAÇÕES:", 0, 1)
                    pdf.set_font("Arial", "", 11)
                    # Texto livre sem retângulo
                    pdf.multi_cell(0, 7, blindar(consideracoes), 0, "L")

                # Assinatura Digital
                img_data = canvas_result.image_data.astype('uint8')
                Image.fromarray(img_data, 'RGBA').save("assinatura_temp.png")
                
                # Controle de posição para manter na mesma página
                if pdf.get_y() > 220:
                    pdf.add_page()
                
                pdf.image("assinatura_temp.png", x=75, y=pdf.get_y()+5, w=55)
                pdf.ln(25)
                pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 10, blindar(f"Responsável: {st.session_state.cozinheiro}"), 0, 1, "C")

                # Rodapé de Segurança em Português e na mesma página
                pdf.set_y(-25)
                pdf.set_font("Arial", "I", 8)
                pdf.set_text_color(100, 100, 100)
                data_registro = datetime.now().strftime("%d/%m/%Y às %H:%M")
                pdf.multi_cell(0, 5, blindar(f"Registro Digital realizado em {data_registro}\nLocal da Assinatura: {local_real}"), 0, "C")

                st.session_state.pdf_disponivel = pdf.output(dest='S').encode('latin-1')
                st.success("✅ Declaração gerada com sucesso!")

            except Exception as e:
                st.error(f"Erro ao processar PDF: {e}")

    if st.session_state.pdf_disponivel:
        st.download_button(
            label="📥 BAIXAR DECLARAÇÃO PDF",
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
